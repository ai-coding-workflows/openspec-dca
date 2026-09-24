## 1. Establish target contracts in code

- [ ] 1.1 Implement lending.domain condition validation and historical unrecorded handling; verify valid, missing, unknown, and historical cases with domain tests.
- [ ] 1.2 Extend lending.loan-store input and contract tests; verify state and condition succeed together and failures leave the original loan unchanged.

## 2. Deliver the return flow

- [ ] 2.1 After 1.2, migrate lending.database and implement atomic persistence; verify port conformance, partial-write failure, and historical-row migration.
- [ ] 2.2 After 1.1 and 1.2, update lending.return; verify success, invalid condition, unknown/repeated loan, and storage failure cases.
- [ ] 2.3 After 2.2, update lending.http and controlled callers; verify the request field, all response mappings, and a full return through the real storage adapter after 2.1.

## 3. Complete documentation and evidence

- [ ] 3.1 Update the runtime and database architecture fragments, decide ADR-LENDING-001, and register its durable path in the catalog; review these against the implemented design.
- [ ] 3.2 Run applicable application, migration, OpenSpec, and documentation checks; record actual results, acceptance coverage, and remaining gaps in verification.md.
