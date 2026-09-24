## ADDED Requirements

### Requirement: Recorded return condition
A newly completed return SHALL record exactly one value defined for `ReturnCondition` in the lending domain model.
A missing value or one not defined by that model MUST be rejected before the return changes state.
A historical return completed before condition recording was introduced SHALL remain explicitly unrecorded; its condition MUST NOT be inferred during migration.

#### Scenario: Defined condition
- **WHEN** a new return supplies one condition defined by the lending domain model
- **THEN** the value is valid for the completed return

#### Scenario: Missing or unknown condition
- **WHEN** a new return supplies no condition or one not defined by the model
- **THEN** the return is rejected before changing state

#### Scenario: Historical return
- **WHEN** an existing completed return is migrated to the new model
- **THEN** its condition is unrecorded and no condition is guessed
