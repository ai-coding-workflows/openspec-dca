## MODIFIED Requirements

### Requirement: Save completed return
The storage port SHALL report success only after the loan's returned state and domain-valid recorded condition are durably saved together.
A failed save MUST report failure and leave the previously stored loan unchanged, without a partially saved return.

#### Scenario: Successful save
- **WHEN** an active loan is saved as returned with a domain-valid condition
- **THEN** success is reported only after both state and condition are durable

#### Scenario: Failed save
- **WHEN** persistence fails while saving a return
- **THEN** the caller receives failure and the previously stored loan remains unchanged

#### Scenario: No partial return
- **WHEN** storing the condition fails after an attempt to write the returned state
- **THEN** neither part of the new return is committed
