"""Protected order/trade/account path snapshots."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from trading_core.equity_build_repeatability.repeatability_config import PROTECTED_PATHS, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_protected_path_snapshot(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    snapshot_phase: str,
) -> dict:
    paths = default_paths(paths)
    entries = []
    for rel in PROTECTED_PATHS:
        root = paths.project_root / rel
        files = [p for p in root.rglob("*") if p.is_file()] if root.exists() else []
        dirs = [p for p in root.rglob("*") if p.is_dir()] if root.exists() else []
        file_entries = [_file_entry(paths, root, p) for p in sorted(files)]
        latest = max((entry["modified_at"] for entry in file_entries if entry["modified_at"]), default=None)
        entries.append({
            "path": rel,
            "exists": root.exists(),
            "file_count": len(files),
            "dir_count": len(dirs),
            "sha256_tree_hash": _tree_hash(file_entries),
            "latest_modified_at": latest,
            "sample_files": [entry["path"] for entry in file_entries[:10]],
            "files": file_entries,
        })
    return {
        "snapshot_id": f"A-SHARE-PROTECTED-PATH-{snapshot_phase.upper()}-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "snapshot_phase": snapshot_phase,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "entries": entries,
    }


def build_protected_path_modification_check(
    *,
    as_of_date: str,
    pre_snapshot: dict,
    post_snapshot: dict,
) -> dict:
    pre = {entry["path"]: entry for entry in pre_snapshot.get("entries", [])}
    post = {entry["path"]: entry for entry in post_snapshot.get("entries", [])}
    preexisting = sorted(path for path, entry in pre.items() if entry.get("exists"))
    new_paths = sorted(path for path, entry in post.items() if entry.get("exists") and not pre.get(path, {}).get("exists"))
    modified: list[str] = []
    created: list[str] = []
    deleted: list[str] = []
    for path in sorted(set(pre) | set(post)):
        pre_files = {item["path"]: item for item in pre.get(path, {}).get("files", [])}
        post_files = {item["path"]: item for item in post.get(path, {}).get("files", [])}
        for file_path in sorted(set(pre_files) | set(post_files)):
            if file_path not in pre_files:
                created.append(file_path)
            elif file_path not in post_files:
                deleted.append(file_path)
            elif pre_files[file_path].get("sha256") != post_files[file_path].get("sha256"):
                modified.append(file_path)
    blocking = []
    if new_paths:
        blocking.append("new_protected_paths_created")
    if modified:
        blocking.append("protected_files_modified")
    if created:
        blocking.append("protected_files_created")
    if deleted:
        blocking.append("protected_files_deleted")
    return {
        "check_id": "A-SHARE-PROTECTED-PATH-MODIFICATION-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "preexisting_protected_paths_allowed": True,
        "protected_path_modifications_allowed": False,
        "preexisting_protected_paths": preexisting,
        "new_protected_paths_created": new_paths,
        "protected_files_modified": modified,
        "protected_files_created": created,
        "protected_files_deleted": deleted,
        "protected_path_modifications_detected": bool(new_paths or modified or created or deleted),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [f"preexisting_protected_path:{path}" for path in preexisting],
    }


def _file_entry(paths: ProjectPaths, root: Path, path: Path) -> dict:
    stat = path.stat()
    return {
        "path": relative(path, paths.project_root),
        "relative_to_protected_root": path.relative_to(root).as_posix(),
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat().replace("+00:00", "Z"),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _tree_hash(file_entries: list[dict]) -> str | None:
    if not file_entries:
        return None
    digest = hashlib.sha256()
    for entry in file_entries:
        digest.update(entry["relative_to_protected_root"].encode("utf-8"))
        digest.update((entry.get("sha256") or "").encode("utf-8"))
    return digest.hexdigest()

