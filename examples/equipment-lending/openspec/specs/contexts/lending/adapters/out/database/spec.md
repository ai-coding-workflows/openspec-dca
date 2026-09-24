# Database loan adapter

## Purpose

Provide the loan-store port guarantees through the service's persistent database boundary.

## Requirements

### Requirement: Implement the loan-store guarantees
The database adapter SHALL satisfy the lending loan-store contract, including its Save completed return guarantee and failure behavior.

#### Scenario: Storage contract conformance
- **WHEN** the loan-store contract tests execute against the database adapter
- **THEN** the adapter satisfies each success and failure guarantee defined by that contract
