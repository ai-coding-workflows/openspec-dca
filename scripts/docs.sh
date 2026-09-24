#!/bin/sh
set -eu
cd "$(dirname "$0")"
action=${1:-build}
case "$action" in
  build|serve) ;;
  *) echo "Usage: ./scripts/docs.sh [build|serve]" >&2; exit 2 ;;
esac
cd ..
mkdir -p build
export GUIDE_UID="$(id -u)" GUIDE_GID="$(id -g)"
compose_file=scripts/md-book/compose.yml
docker compose -f "$compose_file" build handbook
if [ "$action" = serve ]; then
  exec docker compose -f "$compose_file" run --rm --no-deps --service-ports handbook serve --hostname 0.0.0.0 --port 3002
fi
docker compose -f "$compose_file" run --rm --no-deps handbook build
uv run --no-cache --project scripts/book-exporter python scripts/book-exporter/export_book.py book.toml
