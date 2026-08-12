#!/usr/bin/env python3
"""Validate the public Halla badge registry and its detached signature."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "badges" / "v1" / "badges.json"
SIGNATURE = ROOT / "badges" / "v1" / "badges.json.sig"
PUBLIC_KEY = ROOT / "badges" / "v1" / "signing-public-key.pem"
BADGE_ID = re.compile(r"^[a-z0-9_]{1,32}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    raise SystemExit(f"badge registry invalid: {message}")


def validate() -> dict:
    raw = REGISTRY.read_bytes()
    if len(raw) > 1024 * 1024:
        fail("badges.json exceeds 1 MiB")
    try:
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"invalid UTF-8/JSON: {exc}")
    if not isinstance(data, dict) or data.get("version") != 1:
        fail("version must be 1")
    if not isinstance(data.get("updatedAt"), str) or len(data["updatedAt"]) > 40:
        fail("updatedAt is missing or too long")

    badges = data.get("badges")
    users = data.get("users")
    if not isinstance(badges, dict) or len(badges) > 64:
        fail("badges must be an object with at most 64 entries")
    if not isinstance(users, dict) or len(users) > 100_000:
        fail("users must be an object with at most 100000 entries")

    for badge_id, badge in badges.items():
        if not BADGE_ID.fullmatch(badge_id) or not isinstance(badge, dict):
            fail(f"invalid badge id: {badge_id!r}")
        for field, limit in (("name", 64), ("description", 256)):
            if not isinstance(badge.get(field), str) or not (1 <= len(badge[field]) <= limit):
                fail(f"{badge_id}.{field} is invalid")
        priority = badge.get("priority")
        if not isinstance(priority, int) or not (-10000 <= priority <= 10000):
            fail(f"{badge_id}.priority is invalid")
        icon = badge.get("icon")
        if not isinstance(icon, str):
            fail(f"{badge_id}.icon is missing")
        pure = PurePosixPath(icon)
        if pure.is_absolute() or ".." in pure.parts or len(pure.parts) != 2 or pure.parts[0] != "icons":
            fail(f"{badge_id}.icon must be a safe path below icons/")
        icon_path = REGISTRY.parent / pure
        if not icon_path.is_file() or icon_path.stat().st_size > 128 * 1024:
            fail(f"{badge_id}.icon is missing or too large")
        icon_bytes = icon_path.read_bytes()
        if not icon_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            fail(f"{badge_id}.icon must be PNG")
        digest = badge.get("iconSha256")
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            fail(f"{badge_id}.iconSha256 is invalid")
        if hashlib.sha256(icon_bytes).hexdigest() != digest:
            fail(f"{badge_id}.iconSha256 does not match")

    for uid, assigned in users.items():
        if not isinstance(uid, str) or not (1 <= len(uid) <= 128) or any(ord(ch) < 0x20 for ch in uid):
            fail("invalid UID key")
        if not isinstance(assigned, list) or not (1 <= len(assigned) <= 8):
            fail(f"UID {uid!r} must have between 1 and 8 badges")
        if len(assigned) != len(set(assigned)):
            fail(f"UID {uid!r} contains duplicate badges")
        unknown = [badge_id for badge_id in assigned if badge_id not in badges]
        if unknown:
            fail(f"UID {uid!r} references unknown badges: {unknown}")
    return data


def verify_signature() -> None:
    try:
        signature = base64.b64decode(SIGNATURE.read_text(encoding="ascii").strip(), validate=True)
    except Exception as exc:
        fail(f"invalid detached signature encoding: {exc}")
    if len(signature) != 64:
        fail("Ed25519 signature must be 64 bytes")
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(signature)
        tmp.flush()
        result = subprocess.run(
            ["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(PUBLIC_KEY),
             "-rawin", "-in", str(REGISTRY), "-sigfile", tmp.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    if result.returncode != 0:
        fail(f"signature verification failed: {result.stdout.strip()}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-signature", action="store_true")
    args = parser.parse_args()
    data = validate()
    if args.verify_signature:
        verify_signature()
    print(f"badge registry OK: {len(data['badges'])} definitions, {len(data['users'])} users")


if __name__ == "__main__":
    main()
