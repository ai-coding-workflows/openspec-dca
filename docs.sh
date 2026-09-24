#!/bin/sh
set -eu
cd "$(dirname "$0")"
action=${1:-build}
case "$action" in
  build|serve) ;;
  *) echo 'Usage: ./docs.sh [build|serve]' >&2; exit 2 ;;
esac
mkdir -p build
export GUIDE_UID="$(id -u)" GUIDE_GID="$(id -g)"
docker compose build handbook
if [ "$action" = serve ]; then
  exec docker compose run --rm --no-deps --service-ports handbook serve --hostname 0.0.0.0 --port 3002
fi
docker compose run --rm --no-deps handbook build
uv run --no-cache --project tooling/book-exporter python tooling/book-exporter/export_book.py book.toml
