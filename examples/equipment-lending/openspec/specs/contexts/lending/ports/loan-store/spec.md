# Loan storage contract

## Purpose

Define the persistence guarantees consumed by lending use cases and implemented by storage adapters.

## Requirements

### Requirement: Save completed return
The storage port SHALL report success only after the loan's returned state is durably saved.
A failed save MUST report failure and leave the previously stored loan unchanged.

#### Scenario: Successful save
- **WHEN** an active loan is saved as returned
- **THEN** success is reported only after the returned state is durable

#### Scenario: Failed save
- **WHEN** persistence fails while saving a return
- **THEN** the caller receives failure and the previously stored loan remains unchanged
