#!/usr/bin/env bash
CARTELLA="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$CARTELLA" || exit 1
export LD_LIBRARY_PATH="$HOME/.local/lib:${LD_LIBRARY_PATH:-}"
exec "$CARTELLA/.venv/bin/python" "$CARTELLA/CODICE/app.py" "$@"
