from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse


DATA_FILES = {
    "videos": "videos_text_ready_combined.csv",
    "comments": "comments_raw_combined.csv",
    "master": "master_prd_slim_combined.csv",
}

ENV_KEYS = {
    "videos": ("GDRIVE_VIDEOS_FILE_ID", "GDRIVE_VIDEOS_URL"),
    "comments": ("GDRIVE_COMMENTS_FILE_ID", "GDRIVE_COMMENTS_URL"),
    "master": ("GDRIVE_MASTER_FILE_ID", "GDRIVE_MASTER_URL"),
}

FOLDER_ENV_KEYS = ("GDRIVE_FOLDER_ID", "GDRIVE_FOLDER_URL")
DEFAULT_GDRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1fB_c_o3ma2eA2ypHP25eFvQvx5P95FX_?usp=drive_link"


def _extract_file_id(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""

    # Plain file id
    if re.fullmatch(r"[-\w]{20,}", text):
        return text

    # URL patterns:
    # - https://drive.google.com/file/d/<id>/view
    # - https://drive.google.com/open?id=<id>
    # - https://drive.google.com/uc?id=<id>
    m = re.search(r"/d/([-\w]{20,})", text)
    if m:
        return m.group(1)

    try:
        parsed = urlparse(text)
        qs = parse_qs(parsed.query)
        if "id" in qs and qs["id"]:
            return str(qs["id"][0]).strip()
    except Exception:
        pass

    return ""


def _extract_folder_id(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""

    if re.fullmatch(r"[-\w]{20,}", text):
        return text

    # URL pattern: https://drive.google.com/drive/folders/<id>
    m = re.search(r"/folders/([-\w]{20,})", text)
    if m:
        return m.group(1)

    try:
        parsed = urlparse(text)
        qs = parse_qs(parsed.query)
        if "id" in qs and qs["id"]:
            return str(qs["id"][0]).strip()
    except Exception:
        pass

    return ""


def _download_gdrive_file(file_id: str, target_path: Path) -> tuple[bool, str]:
    try:
        import gdown  # type: ignore
    except Exception:
        return False, "gdown is not installed"

    url = f"https://drive.google.com/uc?id={file_id}"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        out = gdown.download(url=url, output=str(target_path), quiet=True, fuzzy=True)
    except Exception as e:
        return False, str(e)

    if not out or not target_path.exists() or target_path.stat().st_size <= 0:
        return False, "download produced no file"
    return True, ""


def _download_gdrive_folder(folder_ref: str, output_dir: Path) -> tuple[list[Path], str]:
    try:
        import gdown  # type: ignore
    except Exception:
        return [], "gdown is not installed"

    folder_ref = str(folder_ref or "").strip()
    if not folder_ref:
        return [], "missing folder id/url"
    if folder_ref.startswith("http"):
        folder_url = folder_ref
    else:
        folder_url = f"https://drive.google.com/drive/folders/{folder_ref}"

    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        try:
            out = gdown.download_folder(
                url=folder_url,
                output=str(output_dir),
                quiet=True,
                remaining_ok=True,
            )
        except TypeError:
            out = gdown.download_folder(
                url=folder_url,
                output=str(output_dir),
                quiet=True,
            )
    except Exception as e:
        return [], str(e)

    paths = [Path(p) for p in (out or []) if p]
    if not paths:
        paths = [p for p in output_dir.rglob("*") if p.is_file()]
    if not paths:
        return [], "folder download produced no files"
    return paths, ""


def ensure_full_data_from_gdrive(data_dir: Path, force: bool = False) -> dict[str, object]:
    data_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {
        "complete": True,
        "downloaded": [],
        "skipped_existing": [],
        "missing_env": [],
        "errors": [],
        "folder_used": False,
        "default_folder_used": False,
    }

    pending_folder: list[tuple[str, str, Path]] = []
    for key, filename in DATA_FILES.items():
        target = data_dir / filename
        if target.exists() and target.stat().st_size > 0 and not force:
            report["skipped_existing"].append(filename)
            continue

        env_id_key, env_url_key = ENV_KEYS[key]
        raw = os.getenv(env_id_key, "").strip() or os.getenv(env_url_key, "").strip()
        if not raw:
            pending_folder.append((key, filename, target))
            continue

        file_id = _extract_file_id(raw)
        if not file_id:
            report["errors"].append(f"{filename}: invalid Google Drive id/url")
            continue

        ok, err = _download_gdrive_file(file_id=file_id, target_path=target)
        if ok:
            report["downloaded"].append(filename)
        else:
            report["errors"].append(f"{filename}: {err}")

    if pending_folder:
        folder_raw = os.getenv(FOLDER_ENV_KEYS[0], "").strip() or os.getenv(FOLDER_ENV_KEYS[1], "").strip()
        if not folder_raw:
            folder_raw = DEFAULT_GDRIVE_FOLDER_URL
            report["default_folder_used"] = True
        folder_id = _extract_folder_id(folder_raw)
        if not folder_raw or not folder_id:
            for key, filename, _ in pending_folder:
                env_id_key, env_url_key = ENV_KEYS[key]
                report["missing_env"].append(
                    f"{filename}: set file-specific env ({env_id_key}/{env_url_key}) "
                    f"or folder env ({FOLDER_ENV_KEYS[0]}/{FOLDER_ENV_KEYS[1]})"
                )
        else:
            tmp_dir = None
            try:
                tmp_dir = Path(tempfile.mkdtemp(prefix="gdrive_full_", dir=str(data_dir)))
                files, err = _download_gdrive_folder(folder_raw, tmp_dir)
                if err:
                    report["errors"].append(f"folder download failed: {err}")
                else:
                    report["folder_used"] = True
                    by_name: dict[str, Path] = {}
                    for p in files:
                        name = p.name
                        # Prefer larger file when duplicate names exist.
                        if name not in by_name or p.stat().st_size > by_name[name].stat().st_size:
                            by_name[name] = p
                    for _, filename, target in pending_folder:
                        src = by_name.get(filename)
                        if not src:
                            report["errors"].append(f"{filename}: not found in folder download")
                            continue
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, target)
                        if target.exists() and target.stat().st_size > 0:
                            report["downloaded"].append(filename)
                        else:
                            report["errors"].append(f"{filename}: copy from folder failed")
            except Exception as e:
                report["errors"].append(f"folder download failed: {e}")
            finally:
                if tmp_dir is not None:
                    shutil.rmtree(tmp_dir, ignore_errors=True)

    required = [data_dir / name for name in DATA_FILES.values()]
    report["complete"] = all(p.exists() and p.stat().st_size > 0 for p in required)
    return report
