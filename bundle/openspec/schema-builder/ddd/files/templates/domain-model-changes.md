# Domain model changes: {change}

## What changes

Disposition: {Change required / Reuse existing / Not affected}

{Two or three plain-language sentences: what changes, why, and what stays the same.}

<!-- Always produce this assessment, also with skip_specs. For Reuse existing or
Not affected, a short explanation and actual references are enough; omit unused
sections. When several scopes differ, assess each and use Change required overall
if any changes. This assessment is not approval, a code diff, or a new spec owner. -->

## Change overview

| Model or mapping | Change | Meaning for the reader | Details |
| --- | --- | --- | --- |
| {Concept or external mapping} | {Add / Change / Remove / Rename / Document existing / Reuse / Not yet determined} | {One short sentence} | {Local section or single draft} |

Removed: {Names of removed elements, None proposed, or Not yet established}
Unchanged: {Only relevant existing meanings that were actually reviewed; cite sources}

<!-- Reading labels, not native delta operations or schema enums. Do not claim
Add merely because a definition is undocumented; code may already contain it.
Do not infer Unchanged from silence. Keep paths out of dense overview cells.
Separate domain meaning from an external-system mapping and from execution rules.
Reference impact's scope inventory rather than maintaining a second owner catalog. -->

## {M1: name of one affected model or mapping}

Role: {Domain meaning / External mapping / Other, with a brief explanation}
Current source: {Reference from Sources, or No maintained definition found}
Proposed content: {This section, OR one linked change-local draft}
Later destination: {Reference from Publication targets; pending is allowed if explicit}

### Current understanding

{What the cited source actually establishes. Separate documented meaning, observed
code, and unknown behavior. Missing documentation does not mean missing software.}

### Proposed change

| Part | Current understanding | Proposed meaning |
| --- | --- | --- |
| {Identity, relationship, field, state, or removed element} | {Known value and source, or Not established} | {Exact change, removal, or explicitly retained meaning} |

{Put essential qualifications below the table in short paragraphs or a small
focused list. Keep exact identifiers and values. Do not fabricate field names.}

### Rules and consequences

{Link the owning delta requirements and technical design. Explain why they matter,
without authoring an independent copy of the same obligations. State relevant
consumer, old-data, or migration effects.}

<!-- Repeat this detail section only for models/mappings with useful changes.
Define the proposed meaning once, either here or in models/<scope>/model.md.
Use domain-model.md for a substantial draft and link it instead of repeating its
full contents. A small overview may summarize, but the detailed section is the
source for the proposal. A meaningful identity need not be a storage lookup key. -->

## Compatibility and limits

| Situation | What is preserved or changed | Remaining limit / reference |
| --- | --- | --- |
| {Historical data, consumers, new commands, missing values, or concurrency} | {Concrete consequence} | {Exact limitation or source} |

<!-- Include only material cases. Stored historical states and newly allowed
operations are different questions. Preserve failure and retry limitations; do
not turn lookup behavior into a concurrency or duplicate-prevention guarantee.
Changed obligations still need delta specs and removal of skip_specs. -->

## Questions and checks still needed

| Question or unchecked fact | Work it blocks | How it will be resolved |
| --- | --- | --- |
| {Specific unknown, not a generic risk} | {Model agreement / field mapping / implementation slice / publication / none, with reason} | {Source or actual check} |

<!-- "No unresolved model decision" does not imply no implementation prerequisites.
Distinguish a policy decision from verifying field names or an external response.
Do not claim a date is an immutable revision or a planned check has already passed. -->

## Sources

### {S1: short descriptive label}

Path: `{existing project-relative path}`
Inspected basis: {commit plus relevant diff, or exact snapshot; identify missing detail}
Supports: {What this source establishes and what was not checked}

<!-- List each useful source once. Use short local labels/links in the overview and
details. Do not invent a citation, commit, existing model, or source path. -->

## Publication targets — not Apply work

### {P1: short label and related model section}

Current source: {Source reference and known baseline, or Not yet present}
Change-local content: {Section of this document or exact change-relative draft path}
Later destination: `{project-relative maintained file and section, or Pending: reason}`
Before publication: {Review/approval, concurrent changes, remaining mapping decision}

<!-- This is the exact source-to-target mapping, not an additional task list. The
Integration handoff in tasks.md references it. Keep maintained models, main specs,
architecture documentation, ADRs, and catalog read-only during planning/Apply. Reconcile against the
then-current target before separately authorized publication. Do not create an
empty target to make a reference look complete or replace newer content with a
stale full draft. No native automatic model merge is implied. -->

{{hook:template.domain-model}}
