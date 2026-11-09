#!/usr/bin/env python3
"""Preserve and retire a shadowed OpenCode JSON config.

The JSONC file wins, so differing JSON values were never active. The
backup is published before deletion. Every earlier failure preserves the
original file.
"""

from __future__ import annotations

import os
from pathlib import Path


def retire_legacy_config(config_dir: Path) -> bool:
    """Retire opencode.json. Return whether it was removed."""
    source = config_dir / "opencode.json"
    backup = config_dir / "opencode.json.pre-jsonc-backup"
    winning = config_dir / "opencode.jsonc"

    if not source.exists():
        return False
    if not winning.is_file():
        raise RuntimeError(
            "Cannot retire opencode.json: the winning opencode.jsonc is "
            "missing. Nothing was moved or deleted."
        )
    if backup.exists():
        raise RuntimeError(
            "Cannot retire opencode.json: opencode.json.pre-jsonc-backup "
            "already exists. Nothing was moved or deleted."
        )

    payload = source.read_bytes()
    temporary = config_dir / f".{backup.name}.{os.getpid()}"
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if temporary.read_bytes() != payload:
            raise RuntimeError(
                "Backup verification failed; the original was preserved."
            )

        # Publish without overwriting a backup another process created.
        os.link(temporary, backup)
        if backup.read_bytes() != payload:
            raise RuntimeError(
                "Published backup verification failed; the original was preserved."
            )
    finally:
        temporary.unlink(missing_ok=True)

    source.unlink()
    return True


def main() -> None:
    config_dir = Path(os.environ["CHEZMOI_DEST_DIR"]) / ".config" / "opencode"
    try:
        removed = retire_legacy_config(config_dir)
    except (OSError, RuntimeError) as error:
        raise SystemExit(f"retire_legacy_config: {error}") from error
    if removed:
        print("RETIRED: preserved opencode.json.pre-jsonc-backup")
    else:
        print("UNCHANGED: no legacy opencode.json")


if __name__ == "__main__":
    main()
