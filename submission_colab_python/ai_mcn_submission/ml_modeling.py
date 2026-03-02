from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

os.environ.setdefault(
    "MPLCONFIGDIR",
    str((Path(__file__).resolve().parents[1] / "artifacts" / "cache" / "mpl")),
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from .utils import min_max_scale

try:
    from lightgbm import LGBMRegressor
    LIGHTGBM_AVAILABLE = True
except Exception:
    LIGHTGBM_AVAILABLE = False

try:
    import shap
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False


@dataclass
class MLArtifacts:
    cv_results: pd.DataFrame
    best_model_name: str
    channel_potential: pd.DataFrame
    pred_actual: pd.DataFrame
    shap_summary: pd.DataFrame
    shap_dependence: pd.DataFrame
    model_plot_path: str | None
    pred_plot_path: str | None
    shap_plot_paths: list[str]
    notes: list[str]


def _build_feature_matrix(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    max_features: int,
    svd_components: int,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    numeric_cols = [
        "log_views",
        "log_likes",
        "log_comments",
        "days_since_publish",
        "title_len",
        "desc_len",
        "hashtag_count",
        "tag_count",
    ]

    x_train_num = train_df[numeric_cols].fillna(0.0).to_numpy(dtype=float)
    x_test_num = test_df[numeric_cols].fillna(0.0).to_numpy(dtype=float)

    scaler = StandardScaler()
    x_train_num = scaler.fit_transform(x_train_num)
    x_test_num = scaler.transform(x_test_num)

    x_train = np.nan_to_num(x_train_num, nan=0.0, posinf=0.0, neginf=0.0)
    x_test = np.nan_to_num(x_test_num, nan=0.0, posinf=0.0, neginf=0.0)
    x_train = np.clip(x_train, -1e6, 1e6)
    x_test = np.clip(x_test, -1e6, 1e6)

    x_train = pd.DataFrame(x_train, columns=numeric_cols, index=train_df.index)
    x_test = pd.DataFrame(x_test, columns=numeric_cols, index=test_df.index)
    feature_names = numeric_cols
    return x_train, x_test, feature_names


def _model_factories(random_state: int) -> list[tuple[str, Callable[[], object], str]]:
    models: list[tuple[str, Callable[[], object], str]] = [
        ("LinearRegression", lambda: LinearRegression(), "linear"),
        ("LASSO", lambda: Lasso(alpha=0.0005, max_iter=2000), "linear"),
        ("Ridge", lambda: Ridge(alpha=1.0, random_state=random_state), "linear"),
        ("CART", lambda: DecisionTreeRegressor(max_depth=8, min_samples_leaf=10, random_state=random_state), "tree"),
        ("RandomForest", lambda: RandomForestRegressor(
            n_estimators=90,
            max_depth=10,
            min_samples_leaf=8,
            random_state=random_state,
            n_jobs=1,
        ), "tree"),
    ]
    if LIGHTGBM_AVAILABLE:
        models.append(("LightGBM", lambda: LGBMRegressor(
            n_estimators=350,
            learning_rate=0.05,
            max_depth=-1,
            num_leaves=31,
            random_state=random_state,
            objective="regression",
            n_jobs=1,
        ), "tree"))
    else:
        models.append(("LightGBM", lambda: None, "unavailable"))
    return models


def _score(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    mse = float(mean_squared_error(y_true, y_pred))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mse)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def _plot_cv_results(cv_df: pd.DataFrame, out_dir: Path) -> str | None:
    valid = cv_df[cv_df["status"] == "ok"].copy()
    if valid.empty:
        return None

    valid = valid.sort_values("rmse_mean", ascending=True)
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.bar(valid["model"], valid["rmse_mean"], color="#4C9BE8")
    ax.set_ylabel("CV RMSE")
    ax.set_title("Model Comparison (5-Fold Group CV)")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()

    out_path = out_dir / "model_cv_rmse.png"
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return str(out_path)


def _plot_pred_vs_actual(y_true: np.ndarray, y_pred: np.ndarray, model_name: str, out_dir: Path) -> str:
    fig, ax = plt.subplots(1, 1, figsize=(6.5, 6.0))
    ax.scatter(y_true, y_pred, alpha=0.25, s=12)
    minv = float(min(np.min(y_true), np.min(y_pred)))
    maxv = float(max(np.max(y_true), np.max(y_pred)))
    ax.plot([minv, maxv], [minv, maxv], color="red", linestyle="--", linewidth=1.2)
    ax.set_xlabel("Actual log1p(engagement_rate)")
    ax.set_ylabel("Predicted")
    ax.set_title(f"Predicted vs Actual ({model_name})")
    fig.tight_layout()

    out_path = out_dir / f"pred_vs_actual_{model_name}.png"
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return str(out_path)


def _try_shap(
    model: object,
    x_sample: np.ndarray,
    feature_names: list[str],
    out_dir: Path,
    model_name: str,
) -> tuple[list[str], pd.DataFrame, pd.DataFrame]:
    empty_summary = pd.DataFrame(columns=["feature", "mean_abs_shap"])
    empty_dep = pd.DataFrame(columns=["feature", "feature_value", "shap_value"])
    if not SHAP_AVAILABLE or x_sample.shape[0] == 0:
        return [], empty_summary, empty_dep

    paths: list[str] = []
    summary_df = empty_summary
    dep_df = empty_dep
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(x_sample)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        shap_values = np.asarray(shap_values)
        if shap_values.ndim == 1:
            shap_values = shap_values.reshape(-1, 1)

        n_features = min(shap_values.shape[1], len(feature_names))
        use_names = feature_names[:n_features]
        shap_values = shap_values[:, :n_features]

        abs_mean = np.abs(shap_values).mean(axis=0)
        summary_df = (
            pd.DataFrame({"feature": use_names, "mean_abs_shap": abs_mean})
            .sort_values("mean_abs_shap", ascending=False)
            .reset_index(drop=True)
        )

        plt.figure(figsize=(8.5, 5.2))
        shap.summary_plot(shap_values, x_sample[:, :n_features], feature_names=use_names, show=False)
        out1 = out_dir / f"shap_summary_{model_name}.png"
        plt.tight_layout()
        plt.savefig(out1, dpi=140, bbox_inches="tight")
        plt.close()
        paths.append(str(out1))

        # Dependence plots for top 3 absolute SHAP features.
        top_idx = np.argsort(abs_mean)[::-1][:3]
        dep_rows: list[dict[str, float | str]] = []
        for idx in top_idx:
            plt.figure(figsize=(7.0, 4.5))
            shap.dependence_plot(int(idx), shap_values, x_sample[:, :n_features], feature_names=use_names, show=False)
            out_dep = out_dir / f"shap_dependence_{model_name}_{use_names[int(idx)]}.png"
            plt.tight_layout()
            plt.savefig(out_dep, dpi=140, bbox_inches="tight")
            plt.close()
            paths.append(str(out_dep))
            dep_rows.extend(
                [
                    {
                        "feature": str(use_names[int(idx)]),
                        "feature_value": float(x_sample[i, int(idx)]),
                        "shap_value": float(shap_values[i, int(idx)]),
                    }
                    for i in range(shap_values.shape[0])
                ]
            )
        if dep_rows:
            dep_df = pd.DataFrame(dep_rows)
    except Exception:
        return [], empty_summary, empty_dep

    return paths, summary_df, dep_df


def run_ml_suite(
    videos_df: pd.DataFrame,
    out_dir: Path,
    random_state: int = 42,
    tfidf_max_features: int = 1200,
    svd_components: int = 50,
    max_rows: int = 5000,
    include_models: list[str] | None = None,
) -> MLArtifacts:
    out_dir.mkdir(parents=True, exist_ok=True)

    df = videos_df.copy()
    df["ml_text"] = (
        df["video_title"].fillna("").astype(str)
        + " "
        + df["tags_text"].fillna("").astype(str)
        + " "
        + df["video_description"].fillna("").astype(str)
    )

    target_col = "engagement_target"
    required_cols = [
        "_channel_id",
        target_col,
        "ml_text",
        "log_views",
        "log_likes",
        "log_comments",
        "days_since_publish",
        "title_len",
        "desc_len",
        "hashtag_count",
        "tag_count",
    ]
    df = df.dropna(subset=["_channel_id", target_col])
    df = df[required_cols + ["engagement_rate"]].copy()
    if len(df) > max_rows:
        df = df.sample(max_rows, random_state=random_state)

    y = df[target_col].to_numpy(dtype=float)
    groups = df["_channel_id"].astype(str).to_numpy()

    baseline_pred = np.full_like(y, fill_value=float(np.median(y)))
    baseline_score = _score(y, baseline_pred)

    gkf = GroupKFold(n_splits=5)
    records: list[dict] = []
    oof_store: dict[str, np.ndarray] = {}
    model_meta: dict[str, dict] = {}
    notes: list[str] = []

    model_defs = _model_factories(random_state)
    if include_models:
        requested = {str(m).strip() for m in include_models if str(m).strip()}
        model_defs = [m for m in model_defs if m[0] in requested]
        missing = sorted(requested - {m[0] for m in model_defs})
        if missing:
            notes.append(f"Requested models not recognized: {', '.join(missing)}")
    if not model_defs:
        raise RuntimeError("No ML models selected for training.")

    for model_name, factory, model_type in model_defs:
        if model_type == "unavailable":
            records.append({
                "model": model_name,
                "status": "unavailable",
                "mae_mean": np.nan,
                "mae_std": np.nan,
                "rmse_mean": np.nan,
                "rmse_std": np.nan,
                "r2_mean": np.nan,
                "r2_std": np.nan,
            })
            notes.append("LightGBM is unavailable in this runtime. Install lightgbm to enable it.")
            continue

        try:
            fold_scores = []
            oof_pred = np.zeros(len(df), dtype=float)
            fold_feature_names: list[str] | None = None

            for train_idx, test_idx in gkf.split(df, y, groups):
                train_df = df.iloc[train_idx]
                test_df = df.iloc[test_idx]

                x_train, x_test, feature_names = _build_feature_matrix(
                    train_df=train_df,
                    test_df=test_df,
                    max_features=tfidf_max_features,
                    svd_components=svd_components,
                )
                fold_feature_names = feature_names

                model = factory()
                model.fit(x_train, y[train_idx])
                pred = model.predict(x_test)
                pred = np.nan_to_num(pred, nan=0.0, posinf=0.0, neginf=0.0)
                if not np.isfinite(pred).all():
                    raise ValueError("Non-finite predictions encountered.")
                oof_pred[test_idx] = pred

                fold_scores.append(_score(y[test_idx], pred))

            fold_df = pd.DataFrame(fold_scores)
            records.append({
                "model": model_name,
                "status": "ok",
                "mae_mean": float(fold_df["mae"].mean()),
                "mae_std": float(fold_df["mae"].std()),
                "rmse_mean": float(fold_df["rmse"].mean()),
                "rmse_std": float(fold_df["rmse"].std()),
                "r2_mean": float(fold_df["r2"].mean()),
                "r2_std": float(fold_df["r2"].std()),
            })
            oof_store[model_name] = oof_pred
            model_meta[model_name] = {"type": model_type, "feature_names": fold_feature_names or []}
        except Exception as e:
            records.append({
                "model": model_name,
                "status": "failed",
                "mae_mean": np.nan,
                "mae_std": np.nan,
                "rmse_mean": np.nan,
                "rmse_std": np.nan,
                "r2_mean": np.nan,
                "r2_std": np.nan,
            })
            notes.append(f"{model_name} failed during CV: {e}")
            continue

    cv_df = pd.DataFrame(records)
    cv_df = cv_df.sort_values(["status", "rmse_mean"], ascending=[False, True], na_position="last").reset_index(drop=True)

    valid_df = cv_df[cv_df["status"] == "ok"].copy()
    if valid_df.empty:
        raise RuntimeError("No valid ML model finished training.")

    best_model_name = valid_df.sort_values("rmse_mean").iloc[0]["model"]

    model_plot_path = _plot_cv_results(cv_df, out_dir)
    pred_plot_path = _plot_pred_vs_actual(y, oof_store[best_model_name], best_model_name, out_dir)

    # Fit best model on full data for downstream channel potential score.
    x_full, _, feature_names_full = _build_feature_matrix(
        train_df=df,
        test_df=df,
        max_features=tfidf_max_features,
        svd_components=svd_components,
    )
    best_factory = [f for n, f, _ in _model_factories(random_state) if n == best_model_name][0]
    best_model = best_factory()
    best_model.fit(x_full, y)

    pred_full = best_model.predict(x_full)
    pred_engagement = np.expm1(pred_full)
    pred_engagement = np.clip(pred_engagement, 0, None)

    channel_potential = (
        pd.DataFrame({
            "_channel_id": df["_channel_id"].values,
            "ml_pred_engagement": pred_engagement,
        })
        .groupby("_channel_id", as_index=False)
        .agg(ml_pred_engagement=("ml_pred_engagement", "median"))
    )
    channel_potential["ml_potential_score"] = min_max_scale(channel_potential["ml_pred_engagement"])

    # SHAP only for tree models.
    shap_paths: list[str] = []
    shap_summary_df = pd.DataFrame(columns=["feature", "mean_abs_shap"])
    shap_dependence_df = pd.DataFrame(columns=["feature", "feature_value", "shap_value"])
    if model_meta.get(best_model_name, {}).get("type") == "tree":
        sample_n = min(600, x_full.shape[0])
        rng = np.random.default_rng(seed=random_state)
        idx = rng.choice(np.arange(x_full.shape[0]), size=sample_n, replace=False)
        x_sample = x_full.iloc[idx].to_numpy(dtype=float)
        shap_paths, shap_summary_df, shap_dependence_df = _try_shap(
            best_model,
            x_sample,
            feature_names_full,
            out_dir,
            best_model_name,
        )

    # Baseline comparison note.
    best_rmse = float(valid_df.sort_values("rmse_mean").iloc[0]["rmse_mean"])
    baseline_rmse = baseline_score["rmse"]
    gain = (baseline_rmse - best_rmse) / baseline_rmse if baseline_rmse > 0 else 0.0
    notes.append(f"Baseline RMSE={baseline_rmse:.6f}, Best({best_model_name}) RMSE={best_rmse:.6f}, Relative gain={gain:.2%}")

    baseline_row = {
        "model": "BaselineMedian",
        "status": "reference",
        "mae_mean": baseline_score["mae"],
        "mae_std": 0.0,
        "rmse_mean": baseline_score["rmse"],
        "rmse_std": 0.0,
        "r2_mean": baseline_score["r2"],
        "r2_std": 0.0,
    }
    cv_df = pd.concat([cv_df, pd.DataFrame([baseline_row])], ignore_index=True)
    pred_actual_df = pd.DataFrame(
        {
            "actual": y,
            "predicted": oof_store[best_model_name],
        }
    )

    return MLArtifacts(
        cv_results=cv_df,
        best_model_name=best_model_name,
        channel_potential=channel_potential,
        pred_actual=pred_actual_df,
        shap_summary=shap_summary_df,
        shap_dependence=shap_dependence_df,
        model_plot_path=model_plot_path,
        pred_plot_path=pred_plot_path,
        shap_plot_paths=shap_paths,
        notes=notes,
    )
