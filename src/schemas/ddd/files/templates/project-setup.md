# Project setup prompt

Use this prompt after selecting/installing the composed schema. Fill the inputs
from the actual project request; do not guess a product model to fill empty fields.

---

Establish this project's domain-centered ports-and-adapters foundation using the
selected OpenSpec DDD schema.

Project goal: {actual goal}
Language/framework constraints: {chosen stack, existing repository, or selection authority}
First real use case: {supplied behavior, or explicitly not specified yet}

This request authorizes the foundation change and its code/test/configuration
Apply work. It does not authorize requirement sync, companion publication,
archive, shared-store writes, production operations, or deployment.

1. Inspect the repository, installed CLI, selected schema, configuration and agent
   guidance. Preserve existing work. Merge rather than replace project settings.
   Verify schema resolution and effective design/apply instructions. Do not assume
   an unsupported skip_specs or operation-guidance feature works. The builder's
   Python helpers do not determine the application's language or test framework.
2. Read the selected architecture policy. Use the requested stack or an existing
   compatible one; record consequential choices. Identify only justified contexts.
   Establish the supplied concepts AND named processes, their authoritative model/spec
   definitions and glossary links; reuse an existing index or stage glossary.md.
   Follow the base glossary template for context grouping and alphabetical ordering;
   choose one or several navigable sources without duplicating scoped entries.
   Mark proposals/unknowns and agree important translations; do not invent agreement.
   Define context-first modules/packages where practical and map framework-required
   entry points explicitly. Use functions/protocols/module APIs as ports where
   idiomatic. No empty layers, dummy contracts, generic repository framework, service
   locator, speculative shared kernel or mandatory dependency-injection container.
3. Create a foundation change through the schema. Map one supplied use case from
   driving adapter to application/domain, required ports, real adapters and concrete
   composition. Record exact source locations, allowed dependencies and any narrow
   accepted exceptions. Stage the implementation map and any warranted ADR in the
   change for later authorized publication. Reuse existing decisions; foundation
   work does not automatically require another ADR. Do not write protected targets.
   If no business behavior is supplied, establish the harness and composition only,
   use an explicitly test-only fixture to exercise boundary rules, and report that
   a real business slice has not yet been demonstrated. Do not invent a domain.
4. Establish native test/build commands and separate fast core tests from real
   adapter integration tests. Core tests run without starting the framework or real
   infrastructure. Inject environmental dependencies when behavior needs control.
   Test an actual adapter's promised failure/consistency behavior for the chosen
   slice, and smoke-test production composition through its real entry point.
   Use realistic isolated fixtures, not live credentials or production data.
   Carry recognizable process names through entry points, tests and current docs;
   keep adapter translations and compatibility aliases explicit. Behavior tests must
   preserve process distinctions, not merely check matching words.
5. Add executable architecture rules using the stack's resolved module/compile
   graph or equivalent tested analysis. Detect core-to-infrastructure dependencies,
   application-to-concrete-adapter dependencies, driving-adapter bypasses and
   cross-context internal access. Cover aliases, re-exports, type dependencies and
   generated paths where present. Record unsupported dynamic cases honestly.
   Prove each important rule with a deliberately invalid fixture and a valid control;
   assert the intended diagnostic, not merely any process failure. Keep invalid
   fixtures outside production scan/build roots and ensure real modules are scanned.
6. Make required checks runnable locally and in CI with a clear nonzero failure
   result. Include the architecture rule tests themselves so disabling a rule is
   detected. Check definition links and selected deprecated aliases where useful,
   scoped by context with explicit external/history exceptions; use the selected
   change overlay during Apply. Do not reject every word absent from the glossary.
   Review or lint glossary grouping and alphabetical ordering; record the method.
   For affected documentation follow documentation-policy.md: reuse the project
   profile or record missing audiences, reader needs, sources/outputs and checks in
   existing settings/maps. Installation/setup belong when relevant to those readers.
   Distinguish required structural gates from configurable review signals and safe
   procedure checks; no universal page quota or mandatory documentation tree.
   Templates are not completed pages; do not publish unfilled starter content.
   Record exact commands, prerequisites, exclusions and scope in the
   change-local implementation map. Do not claim remote branch protection is enabled
   merely because a CI file exists. Extend rules and mappings on later boundary changes.
7. Run the checks; record commands, revisions, actual results and limitations in
   verification.md under one current conclusion, with prior attempts dated separately.
   Keep missing checks visible. Prepare the integration handoff
   and integration.json with pending publication, then stop after Apply. Explain
   the first useful slice demonstrated and any domain scope still unspecified.

For later separately authorized integration: re-read the current baseline,
integrate requirement deltas, explicitly publish needed implementation-map/model/
ADR and contract companions, reconcile mapped supporting sections (including
configuration/API references), glossary/translation mappings and dependent
links/anchors/symbols/catalog, fill fresh
closure evidence, and run the closure helper before the final archive move.
Use a project integration wrapper or CI gate for enforcement; schema guidance is
not an automatic archive hook. Do not rerun a non-idempotent native merge blindly.

## Foundation acceptance checklist

- [ ] The selected schema and effective instructions are verified; the concrete
  implementation map describes actual modules, public boundaries and bindings.
- [ ] Supplied concepts and processes have owned definitions and glossary references;
  the index is grouped and alphabetically ordered. Code/tests/current docs preserve
  their distinctions, or unresolved meaning is explicit.
- [ ] Core behavior is testable without the framework/infrastructure; affected real
  adapters and production composition have appropriate executed checks, or a
  precise not-applicable/blocked explanation for an unprovided business slice.
- [ ] Architecture checks scan real code, reject intended invalid fixtures, cover
  the stack's dependency forms, and run with their controls in required CI checks.
- [ ] Affected documentation/glossary has a navigable, audience-appropriate structure;
  actual checks and reviewed exceptions are recorded. Unfilled starters are not
  publishable; missing product evidence stays explicit rather than invented.
- [ ] Actual test results, scope limits and protected-baseline comparisons are
  recorded; the foundation has no unexplained silent skips.
- [ ] Apply stops with honest integration status; later closure checks requirement
  integration, companion publication and reconciled references separately.
