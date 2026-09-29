## 1. Establish target contracts in code

- [ ] 1.1 Add domain tests for valid, missing, unknown, and historical cases; observe the expected failures, then implement lending.domain condition validation and historical unrecorded handling.
- [ ] 1.2 Add or adapt loan-store contract tests for atomic state-and-condition saves and failure preservation; observe expected failures, then extend lending.loan-store input and behavior.

## 2. Deliver the return flow

- [ ] 2.1 After 1.2, add migration and real-adapter conformance checks for partial-write failure and historical rows; observe expected failures, then migrate lending.database and implement atomic persistence.
- [ ] 2.2 After 1.1 and 1.2, add feature tests for success, invalid condition, unknown/repeated loan, and storage failure; observe expected failures, then update lending.return.
- [ ] 2.3 After 2.2, add HTTP and caller checks for the request field and response mappings; observe expected failures, then update lending.http and controlled callers; after 2.1, verify a full return through the real storage adapter.

## 3. Complete documentation and evidence

- [ ] 3.1 Update the accepted domain model, runtime and database architecture fragments; decide ADR-LENDING-001 and register its durable path in the catalog; review affected system-architecture handbook sections and decision index against the implemented design.
- [ ] 3.2 Run applicable application, migration, OpenSpec, and documentation checks; record actual results, acceptance coverage, and remaining gaps in verification.md.
