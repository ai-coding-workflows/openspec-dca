# Maintaining OpenSpec DDD

Read `docs/05-change-workflow.md` and `docs/09-tooling.md` for the project's model.
This repository is a guide and reusable bundle, not the equipment-lending application.

- Keep OpenSpec's native change lifecycle and generated agent integrations. Extend
  schema instructions instead of vendoring or editing upstream command prompts.
- The canonical schema and helper live under `bundle/openspec/`. The example shares
  them by installation into a temporary copy; do not add divergent schema copies.
- Example baseline specs and proposed deltas must stay distinct. Its delivery tasks
  are intentionally unchecked; guide checks do not establish application acceptance.
- Preserve the difference between artifact readiness, task completion, and verified
  delivery. Architecture, ADRs, and catalog updates are separate from spec sync.
- Keep the handbook generalizable and English. Avoid application-specific paths or
  commands outside the explicitly fictional example.

For changes, run `python3 -m unittest discover -s tests -v`. For schema/workflow
changes, use OpenSpec 1.13.1 on PATH or set `OPENSPEC_BIN` and confirm the integration
tests ran instead of skipping. They mutate temporary copies only.

Run `./docs.sh build` and `python3 tooling/check.py --rendered`, then inspect affected
rendered chapters. Docker is the default toolchain; a locally installed mdBook 0.5.4
also works. Do not edit or commit generated `build/` output. Native OpenSpec schema
interfaces can change; validate upgrades against the real CLI and refresh docs.
