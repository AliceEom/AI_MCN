from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
import math

import numpy as np
import pandas as pd

from .utils import min_max_scale


def _top_tags(tags: list[str], k: int = 40) -> list[str]:
    if not tags:
        return []
    counts = Counter(tags)
    return [t for t, _ in counts.most_common(k)]


def build_channel_graph(
    channel_df: pd.DataFrame,
    min_shared_tags: int = 2,
    max_channels_per_tag: int = 150,
    max_tag_channel_ratio: float = 0.20,
) -> dict:
    tag_map: dict[str, list[str]] = defaultdict(list)

    for _, row in channel_df.iterrows():
        cid = str(row["_channel_id"])
        for tag in _top_tags(row.get("all_tags", []) or []):
            tag = str(tag).strip().lower()
            if tag:
                tag_map[tag].append(cid)

    n_nodes = int(channel_df["_channel_id"].astype(str).nunique())
    max_by_ratio = max(3, int(math.ceil(max(0.01, max_tag_channel_ratio) * max(n_nodes, 1))))
    max_allowed_per_tag = min(max_channels_per_tag, max_by_ratio)

    edge_counts: Counter[tuple[str, str]] = Counter()
    dropped_too_common = 0
    for channels in tag_map.values():
        unique_channels = sorted(set(channels))
        if len(unique_channels) < 2:
            continue
        if len(unique_channels) > max_allowed_per_tag:
            dropped_too_common += 1
            continue
        for a, b in combinations(unique_channels, 2):
            edge_counts[(a, b)] += 1

    edges = [
        (a, b, w)
        for (a, b), w in edge_counts.items()
        if w >= min_shared_tags
    ]

    edge_df = pd.DataFrame(edges, columns=["source", "target", "weight"])

    nodes = channel_df["_channel_id"].astype(str).unique().tolist()

    return {
        "nodes": nodes,
        "edges": edge_df,
        "meta": {
            "n_nodes": len(nodes),
            "n_edges": len(edge_df),
            "min_shared_tags": int(min_shared_tags),
            "max_allowed_per_tag": int(max_allowed_per_tag),
            "dropped_tags_too_common": int(dropped_too_common),
        },
    }


def _build_adjacency(nodes: list[str], edge_df: pd.DataFrame) -> tuple[dict[str, int], np.ndarray]:
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    a = np.zeros((n, n), dtype=float)

    if not edge_df.empty:
        for _, r in edge_df.iterrows():
            i = idx.get(str(r["source"]))
            j = idx.get(str(r["target"]))
            if i is None or j is None:
                continue
            w = float(r["weight"])
            if not np.isfinite(w):
                w = 0.0
            a[i, j] = w
            a[j, i] = w

    a = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
    return idx, a


def _connected_components(nodes: list[str], edge_df: pd.DataFrame) -> dict[str, int]:
    parent = {n: n for n in nodes}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    if not edge_df.empty:
        for _, r in edge_df.iterrows():
            s = str(r["source"])
            t = str(r["target"])
            if s in parent and t in parent:
                union(s, t)

    roots = sorted({find(n) for n in nodes})
    root_to_id = {r: i for i, r in enumerate(roots)}
    return {n: root_to_id[find(n)] for n in nodes}


def _label_propagation_communities(
    nodes: list[str],
    adj: np.ndarray,
    random_state: int = 42,
    max_iter: int = 70,
) -> dict[str, int]:
    n = len(nodes)
    if n == 0:
        return {}

    labels = np.arange(n, dtype=int)
    rng = np.random.default_rng(seed=random_state)
    order = np.arange(n, dtype=int)

    for _ in range(max_iter):
        rng.shuffle(order)
        changed = 0
        for i in order:
            neigh = np.where(adj[i] > 0)[0]
            if len(neigh) == 0:
                continue

            scores: dict[int, float] = {}
            for j in neigh:
                lbl = int(labels[j])
                scores[lbl] = scores.get(lbl, 0.0) + float(adj[i, j])

            cur = int(labels[i])
            best_lbl = cur
            best_score = scores.get(cur, -1.0)
            for lbl, score in scores.items():
                if score > best_score + 1e-12 or (abs(score - best_score) <= 1e-12 and lbl < best_lbl):
                    best_lbl = int(lbl)
                    best_score = float(score)

            if best_lbl != cur:
                labels[i] = best_lbl
                changed += 1

        if changed == 0:
            break

    uniq, counts = np.unique(labels, return_counts=True)
    order_idx = np.argsort(-counts)
    remap = {int(uniq[idx]): int(new_id) for new_id, idx in enumerate(order_idx)}
    return {nodes[i]: remap[int(labels[i])] for i in range(n)}


def _eigenvector_centrality(adj: np.ndarray, max_iter: int = 200, tol: float = 1e-6) -> np.ndarray:
    n = adj.shape[0]
    if n == 0:
        return np.array([])
    strength = np.clip(adj, 0.0, None).sum(axis=1).astype(float)
    max_strength = float(np.max(strength))
    if max_strength <= 0:
        return np.zeros(n)
    return strength / max_strength


def compute_network_scores(channel_df: pd.DataFrame, graph: dict, min_community_size: int = 3, random_state: int = 42) -> pd.DataFrame:
    out = channel_df.copy()
    nodes = graph.get("nodes", [])
    edge_df = graph.get("edges", pd.DataFrame(columns=["source", "target", "weight"]))

    idx, adj = _build_adjacency(nodes, edge_df)
    n = len(nodes)

    # Degree centrality
    degree_raw = adj.astype(bool).sum(axis=1).astype(float)
    degree = degree_raw / max(n - 1, 1)

    # Betweenness approximation using bridge tendency proxy.
    # proxy = degree * inverse neighbor degree
    inv_neighbor = np.zeros(n)
    for i in range(n):
        neigh = np.where(adj[i] > 0)[0]
        if len(neigh) == 0:
            inv_neighbor[i] = 0.0
        else:
            inv_neighbor[i] = np.mean(1.0 / (degree_raw[neigh] + 1.0))
    between_proxy = degree * inv_neighbor

    eigen = _eigenvector_centrality(adj)

    out["degree_centrality"] = out["_channel_id"].astype(str).map(lambda x: degree[idx[x]] if x in idx else 0.0)
    out["betweenness_centrality"] = out["_channel_id"].astype(str).map(lambda x: between_proxy[idx[x]] if x in idx else 0.0)
    out["eigenvector_centrality"] = out["_channel_id"].astype(str).map(lambda x: eigen[idx[x]] if x in idx else 0.0)

    out["sna_score_raw"] = (
        0.33 * out["degree_centrality"]
        + 0.34 * out["betweenness_centrality"]
        + 0.33 * out["eigenvector_centrality"]
    )
    out["sna_score"] = min_max_scale(out["sna_score_raw"])

    comp_map = _label_propagation_communities(nodes, adj, random_state=random_state)
    out["community_id_raw"] = out["_channel_id"].astype(str).map(lambda x: comp_map.get(x, -1)).astype(int)
    size_map = out["community_id_raw"].value_counts().to_dict()
    out["community_size"] = out["community_id_raw"].map(lambda cid: int(size_map.get(int(cid), 1))).astype(int)

    out["community_id"] = out["community_id_raw"]
    out.loc[out["community_size"] < max(1, int(min_community_size)), "community_id"] = -1

    valid_ids = sorted([int(x) for x in out["community_id"].unique() if int(x) >= 0])
    reindex = {cid: new_id for new_id, cid in enumerate(valid_ids)}
    out["community_id"] = out["community_id"].map(lambda x: reindex.get(int(x), -1)).astype(int)

    out["graph_degree"] = out["_channel_id"].astype(str).map(lambda x: int(degree_raw[idx[x]]) if x in idx else 0).astype(int)
    out["is_isolated"] = out["graph_degree"] == 0

    return out
