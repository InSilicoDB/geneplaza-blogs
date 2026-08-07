#!/usr/bin/env bash
# Copy a Reddit answer to the clipboard.
#
#   ./tools/rcopy.sh            list the answers
#   ./tools/rcopy.sh 2          copy answer 2 (no link — weeks 1-2)
#   ./tools/rcopy.sh 2 --link   copy answer 2 with the blog link + disclosure
#
# Weeks 1-2: post WITHOUT the link. Build karma first.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/tools/rcopy.py" "$@"
