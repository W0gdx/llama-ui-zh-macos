#!/bin/zsh
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
exec /usr/bin/python3 "$PATCH_DIR/manage.py" restore
