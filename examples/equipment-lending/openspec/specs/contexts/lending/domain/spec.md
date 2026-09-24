# Lending domain

## Purpose

Define the shared meaning and invariants of loans in the equipment-lending context.

## Requirements

### Requirement: Loan identity
A loan SHALL identify one equipment item and one borrower, and have an active or returned state.

#### Scenario: Active loan
- **WHEN** an equipment item is lent to a borrower
- **THEN** its active loan identifies that item and that borrower
