"""Repair one apt repository's signing keyring and refuse bad writes.

Called by apps/apt/tasks/keyrings.yaml, once per entry in
`apt_keyrings`.

The previous implementation (deb-get's apt-auth.yaml) saved whatever
the URL returned with `get_url force: true` and reported success. That
left a 0-byte hashicorp keyring and a githubcli keyring without the
current signing key, and apt kept failing with NO_PUBKEY while the
playbook said the keys were repaired. So this helper validates before
it writes: a download that is not an OpenPGP public key never reaches
the destination.

Steps:
  1. Find the source file that references --repo-host and read the
     keyring path from its signed-by= (one-line .list) or Signed-By:
     (deb822 .sources). No source configured means nothing to repair:
     this topic does not add repositories, it only keeps the keys of
     existing ones valid.
  2. Download --url; dearmor it if it is ASCII-armoured, because apt
     reads a .gpg path as a binary keyring.
  3. Validate with `gpg --show-keys` in a throwaway GNUPGHOME, so
     nothing is imported into any real keyring. Zero public keys is a
     hard failure.
  4. Write atomically (temp file + rename) only if the bytes differ.

Prints one JSON object on stdout. Exit 0 on success or
nothing-to-do, 2 when the keyring could not be repaired, with the
reason on stderr.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ARMOR_HEADER = b"-----BEGIN PGP PUBLIC KEY BLOCK-----"


class RepairError(Exception):
    pass


def _list_signed_by(text: str, repo_host: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or repo_host not in stripped:
            continue
        match = re.search(r"signed-by=([^\]\s]+)", stripped)
        return match.group(1) if match else ""
    return None


def _sources_signed_by(text: str, repo_host: str) -> str | None:
    for stanza in re.split(r"\n\s*\n", text):
        fields: dict[str, str] = {}
        key = None
        for line in stanza.splitlines():
            if line.startswith("#"):
                continue
            if line[:1].isspace() and key:
                fields[key] += "\n" + line.strip()
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                fields[key] = value.strip()
        if repo_host not in fields.get("uris", ""):
            continue
        if fields.get("enabled", "yes").lower() == "no":
            continue
        signed_by = fields.get("signed-by", "")
        return signed_by if signed_by.startswith("/") else ""
    return None


def find_keyring_dest(repo_host: str, sources: list[Path]) -> tuple[Path, str] | None:
    """Return (source_file, keyring_path) for the first enabled match.

    The first enabled source naming repo_host wins. keyring_path is ""
    when the source exists but names no keyring file (no signed-by, or
    an inline key block), which the caller treats as unrepairable.
    """
    for path in sources:
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        parser = _sources_signed_by if path.suffix == ".sources" else _list_signed_by
        dest = parser(text, repo_host)
        if dest is not None:
            return path, dest
    return None


def candidate_sources(sources_dir: Path, sources_list: Path) -> list[Path]:
    found = []
    if sources_list.is_file():
        found.append(sources_list)
    if sources_dir.is_dir():
        found.extend(
            sorted(
                p for p in sources_dir.iterdir() if p.suffix in (".list", ".sources")
            )
        )
    return found


def to_binary_keyring(data: bytes) -> bytes:
    if ARMOR_HEADER in data[:200]:
        result = subprocess.run(
            ["gpg", "--dearmor"], input=data, capture_output=True, check=False
        )
        if result.returncode != 0 or not result.stdout:
            detail = result.stderr.decode(errors="replace").strip()
            raise RepairError(f"gpg --dearmor failed: {detail}")
        return result.stdout
    return data


def key_ids(keyring: bytes) -> list[str]:
    """Primary key IDs in a binary keyring; empty if it is not one."""
    if not keyring:
        return []
    with tempfile.TemporaryDirectory() as home:
        path = Path(home) / "candidate.gpg"
        path.write_bytes(keyring)
        result = subprocess.run(
            ["gpg", "--batch", "--show-keys", "--with-colons", str(path)],
            capture_output=True,
            text=True,
            env={**os.environ, "GNUPGHOME": home},
            check=False,
        )
    return [
        line.split(":")[4]
        for line in result.stdout.splitlines()
        if line.startswith("pub:")
    ]


def download(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "dotfiles-apt-keyring/1"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def write_atomic(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dest.parent, prefix=f".{dest.name}.")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.chmod(tmp, 0o644)
        os.replace(tmp, dest)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def describe(path: Path) -> str:
    if not path.exists():
        return "missing"
    size = path.stat().st_size
    if size == 0:
        return "empty"
    ids = key_ids(path.read_bytes())
    return (
        f"valid ({', '.join(ids)})" if ids else f"invalid ({size} bytes, no public key)"
    )


def repair(args: argparse.Namespace, fetch=download) -> dict:
    sources = candidate_sources(Path(args.sources_dir), Path(args.sources_list))
    located = find_keyring_dest(args.repo_host, sources)
    report = {"name": args.name, "repo_host": args.repo_host, "changed": False}
    if located is None:
        report["status"] = "no-source"
        report["detail"] = (
            f"no enabled apt source references {args.repo_host}; nothing to repair"
        )
        return report
    source, dest = located
    report["source"] = str(source)
    if not dest:
        raise RepairError(
            f"{source} references {args.repo_host} but names no keyring file "
            "(no signed-by=, or an inline Signed-By block); fix the source by hand"
        )

    dest_path = Path(dest)
    report["dest"] = dest
    report["before"] = describe(dest_path)

    try:
        raw = fetch(args.url, args.timeout)
    except Exception as exc:
        raise RepairError(f"could not download {args.url}: {exc}") from exc

    keyring = to_binary_keyring(raw)
    ids = key_ids(keyring)
    if not ids:
        preview = raw[:60]
        raise RepairError(
            f"{args.url} did not return an OpenPGP public key "
            f"({len(raw)} bytes, starts {preview!r}); refusing to write {dest}"
        )
    missing = [k for k in args.require_key if k.upper() not in {i.upper() for i in ids}]
    if missing:
        raise RepairError(
            f"{args.url} serves keys {ids} but not the required {missing}; "
            "the upstream signing key may have rotated again"
        )
    report["keys"] = ids

    current = dest_path.read_bytes() if dest_path.is_file() else None
    if current == keyring:
        report["status"] = "ok"
        return report
    report["changed"] = True
    report["status"] = "would-repair" if args.check else "repaired"
    if not args.check:
        write_atomic(dest_path, keyring)
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--name", required=True)
    parser.add_argument("--repo-host", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument(
        "--require-key",
        action="append",
        default=[],
        help="key ID the download must contain (repeatable)",
    )
    parser.add_argument("--sources-dir", default="/etc/apt/sources.list.d")
    parser.add_argument("--sources-list", default="/etc/apt/sources.list")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument(
        "--check", action="store_true", help="report only; write nothing"
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        report = repair(args)
    except RepairError as exc:
        print(
            json.dumps(
                {
                    "name": args.name,
                    "changed": False,
                    "status": "failed",
                    "detail": str(exc),
                }
            )
        )
        print(f"apt_keyring: {args.name}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
