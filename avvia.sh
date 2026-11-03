#!/usr/bin/env bash
CARTELLA="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$CARTELLA" || exit 1
[ -x "$CARTELLA/.venv/bin/python" ] || { echo "Crea prima il venv: vedi README"; exit 1; }
exec "$CARTELLA/.venv/bin/python" "$CARTELLA/CODICE/app.py" "$@"
