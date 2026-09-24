# Lending HTTP boundary

## Purpose

Map equipment return requests and use-case outcomes to the service's HTTP interface.

## Requirements

### Requirement: Submit a return
The HTTP adapter SHALL accept POST /loans/{loanId}/return and pass loanId to the return feature.
It MUST return 204 on success, 404 for an unknown loan, 409 for an already returned loan, and 503 for storage failure.

#### Scenario: Successful HTTP return
- **WHEN** the return feature succeeds
- **THEN** the response is HTTP 204

#### Scenario: Unknown loan
- **WHEN** the return feature rejects an unknown loan
- **THEN** the response is HTTP 404

#### Scenario: Already returned loan
- **WHEN** the return feature rejects an already returned loan
- **THEN** the response is HTTP 409

#### Scenario: Storage unavailable
- **WHEN** the return feature reports storage failure
- **THEN** the response is HTTP 503
