## MODIFIED Requirements

### Requirement: Submit a return
The HTTP adapter SHALL accept POST /loans/{loanId}/return with a JSON condition field and pass loanId and the condition to the return feature.
It MUST return 400 for malformed JSON or a missing, non-string, or domain-invalid condition, without invoking a state-changing return.
It MUST return 204 on success, 404 for an unknown loan, 409 for an already returned loan, and 503 for storage failure.

#### Scenario: Successful HTTP return
- **WHEN** the request supplies a valid condition and the return feature succeeds
- **THEN** the response is HTTP 204

#### Scenario: Invalid request condition
- **WHEN** JSON is malformed or condition is missing, non-string, or invalid under the domain rule
- **THEN** the response is HTTP 400 and stored state is unchanged

#### Scenario: Unknown loan
- **WHEN** a valid request reaches the return feature and it rejects an unknown loan
- **THEN** the response is HTTP 404

#### Scenario: Already returned loan
- **WHEN** a valid request reaches the return feature and it rejects an already returned loan
- **THEN** the response is HTTP 409

#### Scenario: Storage unavailable
- **WHEN** the return feature reports storage failure
- **THEN** the response is HTTP 503
