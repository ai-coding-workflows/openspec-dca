# {Project or context}: glossary

<!-- Navigation for the shared domain language, available without arc42. Reuse the
existing glossary; otherwise openspec/glossary.md is a suggested index location.
Do not create a second independently maintained index for an optional handbook.
Follow the Ubiquitous Language section in architecture-policy.md. -->

<!-- Organization and ordering:
Group entries by bounded context/scope. Keep genuinely shared domain terms and
technical terms in separate optional sections; "shared" requires agreed shared meaning.
Sort context sections alphabetically by displayed context name. Within each table,
sort alphabetically by canonical display term, case-insensitively, ignoring Markdown
formatting. Keep translations, code forms and aliases with the canonical entry;
they do not change its sort position. State a collation only when the glossary's
language needs one; apply it consistently rather than relying on machine locale.

Keep Kind as a column by default. For a large scope, optional kind subgroups may
separate concepts/relationships, processes/use cases, actions, states/outcomes and
events. Use a consistent subgroup order and sort entries alphabetically within each
subgroup. No empty sections or compulsory file per term. A context-local glossary
needs only that context's table or kind subgroups, not redundant context headings.
The headings below are a layout starter, not new required domain owners.

Scale by need: one logical glossary may use one file or several linked source units.
Do not require one file per context, kind or term. When a page becomes hard to use,
split by useful scope/kind and keep a short entry point linking to the resulting
pages. Reuse this template only for applicable leaf groups, without empty sections.
Maintain each scoped entry once; extra global/A-Z indexes link to canonical entries
or are generated from them, not independently edited copies. Sort context navigation
and leaf entries using the same rules. No universal entry-count limit applies.
Review affected entry points, definition links and incoming anchors after splits.
Check access in the intended output; a repository-only definition link may not
work in a published handbook. Use approved links or generated read views of the
same owned source, not a second definition. Source units and single-file exports
can differ. Follow documentation-policy.md for review signals and exceptions. -->

## Shared domain terms

<!-- Optional: only meanings explicitly shared across contexts. -->

| Term | Kind | Context / scope | Authoritative definition | Clarification / mapped name (only if useful) |
| --- | --- | --- | --- | --- |

## Bounded contexts

### {Context name}

<!-- Repeat for actual contexts in alphabetical order; sort each table's terms. -->

| Term | Kind | Context / scope | Authoritative definition | Clarification / mapped name (only if useful) |
| --- | --- | --- | --- | --- |

## Technical terms

<!-- Optional: useful technical terms, not a second domain vocabulary. -->

| Term | Kind | Context / scope | Authoritative definition | Clarification / mapped name (only if useful) |
| --- | --- | --- | --- | --- |

<!-- Include important concepts AND named processes/use cases, actions, relationships,
states/outcomes and events where relevant; omit empty categories and template rows.
Use real relative Markdown links to the owning file and section. Concepts belong to
the domain model; process scope and behavior belong to a feature/use-case contract.
A cross-context process points to its explicit owner, then participating contracts.
Do not copy rules, process steps or failure behavior here. Distinguish scoped meanings
rather than force a global one. Add translations, code forms, external mappings or
retired aliases only when they resolve ambiguity; assess compatibility before rename.
Keep unresolved definitions in the active model assessment, not as established facts.
Stage entries whose targets are unpublished; reconcile links at integration.
Historical terms remain identifiable as historical, not silently rewritten. -->
