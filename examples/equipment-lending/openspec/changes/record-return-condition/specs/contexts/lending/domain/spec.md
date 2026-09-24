## ADDED Requirements

### Requirement: Recorded return condition
A newly completed return SHALL record exactly one condition: usable or needs-inspection.
Missing or unknown values MUST be rejected before the return changes state.
A historical return completed before condition recording was introduced SHALL remain explicitly unrecorded; its condition MUST NOT be inferred during migration.

#### Scenario: Supported condition
- **WHEN** a new return supplies usable or needs-inspection
- **THEN** the value is valid for the completed return

#### Scenario: Missing or unknown condition
- **WHEN** a new return supplies no condition or an unknown value
- **THEN** the return is rejected before changing state

#### Scenario: Historical return
- **WHEN** an existing completed return is migrated to the new model
- **THEN** its condition is unrecorded and no condition is guessed
