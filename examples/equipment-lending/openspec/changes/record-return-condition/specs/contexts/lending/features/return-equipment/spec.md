## MODIFIED Requirements

### Requirement: Complete an active return
The return feature SHALL accept a loan identifier and a condition satisfying the lending domain's Recorded return condition rule.
It MUST reject an invalid condition before saving and report success only after the loan-store contract's Save completed return guarantee is satisfied.
Storage failure MUST be reported as an unsuccessful return.

#### Scenario: Return succeeds
- **WHEN** a caller returns an existing active loan with a valid condition and storage succeeds
- **THEN** the feature reports a completed return with the recorded condition

#### Scenario: Storage fails
- **WHEN** saving the return fails
- **THEN** the feature reports an unsuccessful return

#### Scenario: Invalid condition
- **WHEN** the supplied condition fails the domain rule
- **THEN** the feature rejects the request without saving a return
