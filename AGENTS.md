# Maintaining OpenSpec DDD

Read `docs/05-change-workflow.md` and `docs/09-tooling.md` for the project's model.
This repository is a guide and reusable bundle, not the equipment-lending application.

- Keep OpenSpec's native change lifecycle and generated agent integrations. Extend
  schema instructions instead of vendoring or editing upstream command prompts.
- The canonical schema sources live under `src/schemas/`, with DDD helpers under
  `src/schemas/ddd/helpers/` and the shared docs orchestrator under
  `src/schemas/helper-packs/docs/`. Composed v3 schemas include their helpers;
  the historical five-artifact legacy schema adds none automatically.
  Build all variants with `python3 build.py`;
  generated schemas under `build/schemas/` are never edited or committed. The example uses
  the separately retained five-artifact legacy schema. Install shared sources into
  temporary example copies; do not add divergent schema copies.
- Example baseline specs and proposed deltas must stay distinct. Its delivery tasks
  are intentionally unchecked; guide checks do not establish application acceptance.
- Preserve the difference between artifact readiness, task completion, and verified
  delivery. Architecture, ADRs, and catalog updates are separate from spec sync.
- Keep the handbook generalizable and English. Avoid application-specific paths or
  commands outside the explicitly fictional example.

For changes, run `python3 -m unittest discover -s tests -v`. For schema/workflow
changes, use OpenSpec 1.13.1 on PATH or set `OPENSPEC_BIN` and confirm the integration
tests ran instead of skipping. They mutate temporary copies only.

Run `./scripts/book.sh build` and `python3 scripts/md-book-builder/check.py --rendered`,
then inspect affected rendered chapters. Native mdBook is the default; use
`scripts/book.sh --docker` for the pinned Docker toolchain. The canonical CLI is
`scripts/md-book-builder/book.py`; see `scripts/book.md`. Root `book-builder.toml`
is authoritative when present; otherwise the runner discovers root `book.toml`
and `book.*.toml`. The checker remains single-book, defaulting to root `book.toml`,
and supports `--config` and `--book`. Output paths come from each native book
configuration. Do not edit or commit generated output under those directories.
The old docs wrappers and `scripts/md-book/docs.py`/`check.py` remain forwarders. Native OpenSpec schema interfaces can change; validate upgrades
against the real CLI and refresh docs.
