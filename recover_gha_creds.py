#!/usr/bin/env python3
"""Recover one gha-creds file from a BuildKit layer without printing secrets."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("blob")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    raw = Path(args.blob).read_bytes()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    try:
        archive = tarfile.open(fileobj=io.BytesIO(raw), mode="r:")
    except tarfile.TarError:
        return 2
    with archive:
        for member in archive:
            if not member.isfile() or "gha-creds-" not in Path(member.name).name:
                continue
            extracted = archive.extractfile(member)
            if extracted is None:
                continue
            data = extracted.read()
            try:
                parsed = json.loads(data)
                header = parsed["credential_source"]["headers"]["Authorization"]
            except (KeyError, TypeError, json.JSONDecodeError):
                continue
            if not header.startswith("Bearer "):
                continue
            output = Path(args.out)
            output.write_bytes(data)
            output.chmod(0o600)
            print(
                json.dumps(
                    {
                        "member": member.name,
                        "type": parsed.get("type"),
                        "audience": parsed.get("audience"),
                        "bearer_sha256_prefix": hashlib.sha256(
                            header.removeprefix("Bearer ").encode()
                        ).hexdigest()[:16],
                        "has_impersonation_url": bool(
                            parsed.get("service_account_impersonation_url")
                        ),
                    },
                    sort_keys=True,
                )
            )
            return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
