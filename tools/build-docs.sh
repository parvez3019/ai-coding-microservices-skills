#!/usr/bin/env bash
# Assemble the MkDocs source tree (build/site-src/) from docs/, source/, sample/ and friends.
# The Python script holds the logic; this wrapper keeps tools/ uniform. Never commit build/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/tools/build_docs.py" "$@"
