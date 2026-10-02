<!-- One delta file per changed owning capability. Keep only applicable sections.
New capabilities start with a descriptive ## Purpose section. Existing Purpose
metadata is not changed by requirement deltas. Do not generate placeholder rules.

Tailor obligations to the owner: domain invariants/transitions, feature outcomes and
rejections, port guarantees/failure semantics, or adapter representations/mappings.
A feature normally owns behavior offered through inbound ports; do not duplicate it
for folder symmetry. Contexts, technical capabilities, and system responsibilities
use the same contract rules. Keep explanatory meanings in an authoritative model
when useful. Read domain-model-changes.md and its linked proposed definitions or
explicitly reused sources. A semantic change cannot conceal an obligation change.
Keep new/modified requirements inside this change's specs/; do not create or edit
main specs during planning/Apply, including for new owners. Intended model links
are reconciled during later authorized publication, not by making placeholder files.

For MODIFIED, read and copy the full original block and exact name, retaining still-
valid behavior and scenarios. An optional ID does not replace exact-name matching;
adding one to an existing heading requires deliberate renaming. Distinguish supported
historical data from permitted new transitions. Keep implementation design elsewhere.

Use at least one WHEN/THEN scenario for each added/modified rule. Include meaningful
rejection/failure/compatibility cases; examples are not passing tests and need not all
be E2E tests. With skip_specs: true, create no delta files or empty sections. -->

## ADDED Requirements

### Requirement: {stable descriptive name}
{Owner} SHALL {observable guarantee}.

#### Scenario: {observable case}
- **WHEN** {trigger and conditions}
- **THEN** {observable result}

## MODIFIED Requirements

### Requirement: {exact existing name}
{Complete updated requirement, including still-valid guarantees.}

#### Scenario: {observable case}
- **WHEN** {trigger and conditions}
- **THEN** {observable result}

## REMOVED Requirements

### Requirement: {exact existing name}
**Reason**: {why removed}
**Migration**: {consumer migration or explicit explanation that none is needed}

## RENAMED Requirements

- FROM: `### Requirement: {old name}`
- TO: `### Requirement: {new name}`

{{hook:template.specs}}
