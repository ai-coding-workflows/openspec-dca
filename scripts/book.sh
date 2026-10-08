#!/bin/sh
set -eu
script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
  python=python3
elif command -v python >/dev/null 2>&1; then
  python=python
else
  echo "book requires Python 3.11+ (or Python 3.10 with tomli)." >&2
  exit 127
fi
exec "$python" "${BOOK_BUILDER:-$script_dir/md-book-builder/book.py}" "$@"
