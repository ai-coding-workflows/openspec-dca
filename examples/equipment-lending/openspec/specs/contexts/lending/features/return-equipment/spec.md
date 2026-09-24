# Return equipment

## Purpose

Let a borrower complete an active equipment loan and receive an explicit return outcome.

## Requirements

### Requirement: Complete an active return
The return feature SHALL accept a loan identifier and report success only after the loan-store contract's Save completed return guarantee is satisfied.
Storage failure MUST be reported as an unsuccessful return.

#### Scenario: Return succeeds
- **WHEN** a caller returns an existing active loan and storage succeeds
- **THEN** the feature reports a completed return

#### Scenario: Storage fails
- **WHEN** saving the return fails
- **THEN** the feature reports an unsuccessful return

### Requirement: Reject unavailable loans
The feature SHALL reject unknown or already returned loans without changing stored state.

#### Scenario: Unknown loan
- **WHEN** the identifier does not name an existing loan
- **THEN** the return is rejected without changing stored state

#### Scenario: Already returned loan
- **WHEN** the loan has already been returned
- **THEN** the return is rejected without changing stored state
