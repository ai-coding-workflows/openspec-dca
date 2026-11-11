# Project-adaptive documentation policy

Apply this policy to affected maintained documentation, including model/architecture
views and glossary navigation. The user-doc component adds reader-facing templates;
this policy does not require that component or a particular publishing tool.

## Audience and scope

Derive coverage from the product, intended readers and their tasks. Users may be
administrators, operators, integrators or developers. Installation, setup, operation,
integration and everyday use belong when relevant; do not categorically include or
exclude any of them. Different roles need distinguishable prerequisites, not
necessarily separate books. Choose language, supported versions and publication
formats from the project, not from example folder names.

## Coherent units and navigation

Organize by understandable topics, procedures or learning paths. Templates are
reusable content types, not mandatory chapters or permanent catch-all filenames.
A tutorial may connect installation, setup and first use; a reference may group
related commands. No mandatory folder tree, one-task-per-file rule or universal
page-size limit applies.

Before extending content, review the whole affected unit and its navigation, not
only added paragraphs. Split or consolidate when independent reader needs, differing
prerequisites or accumulated material impair discovery or maintenance. Keep a
coherent procedure together and retain necessary warnings at the point of action.
Distinguish editable source units from generated pages/books; a single-file export
need not force a single source file. Preserve incoming links/anchors when moving
content, or explicitly map migration and verify affected consumers.

Keep each rule/definition at its authoritative owner. Reference it rather than
maintaining competing explanations of the current contract. Short orientation and
necessary local warnings may repeat. Separate current guidance from historical
change narratives. Do not rewrite accepted history or omit required full MODIFIED
specification deltas in the name of brevity.

## Project profile and checks

Reuse existing documentation settings, implementation-map check commands and the
change's publication/page mapping. Record only missing choices: audiences and reader
needs; roots, editable/generated sources and published outputs; supported versions;
selected checks, severity, scope/exclusions and justified exceptions. No extra
planning artifact or per-page metadata block is required.

- **Deterministic gates:** scoped checks for broken targets/anchors, unreachable
  published content, leaked authoring placeholders, or other explicitly adopted
  structural rules. Exclude template libraries, intentional drafts, includes and
  history as appropriate. Check rendered destinations as well as sources when used.
- **Review signals:** size, growth, heading/table counts, glossary-entry counts or
  suspected duplication. Set useful thresholds by content/output type in the project;
  distinguish prose, code and tables. Resolve findings by splitting, consolidation
  or a justified exception, not arbitrary deletion. No default hard size quota.
- **Content and procedure review:** confirm audience fit, consistency, findability
  and relevant prerequisites, outcomes and recovery. Execute selected risk-relevant
  procedures in authorized isolation; never execute arbitrary documentation blocks.

Published deliverables must not contain unfilled starters. A runnable preview is not
publication readiness. Automated checks must use real supported commands and report
failure/skips; record actual execution versus inspection and unresolved findings in
verification.md. A green render or link check is not proof of semantic correctness.
Use approved tooling; adding a tool, CI gate or deployment requires project authority.
The schema defines obligations, not an automatic CLI hook or an installed linter.
