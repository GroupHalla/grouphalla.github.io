#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PRIVATE_KEY="${1:-}"
if [[ -z "$PRIVATE_KEY" || ! -f "$PRIVATE_KEY" ]]; then
  echo "Uso: $0 /caminho/para/Halla-Badges-Ed25519-Private.pem" >&2
  exit 2
fi

python3 "$ROOT/tools/validate_badges.py"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
openssl pkeyutl -sign -rawin -inkey "$PRIVATE_KEY" \
  -in "$ROOT/badges/v1/badges.json" -out "$tmp"
base64 -w0 "$tmp" > "$ROOT/badges/v1/badges.json.sig"
printf '\n' >> "$ROOT/badges/v1/badges.json.sig"
python3 "$ROOT/tools/validate_badges.py" --verify-signature
