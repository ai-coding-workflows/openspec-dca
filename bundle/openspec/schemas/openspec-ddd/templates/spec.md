<!-- One file per owning capability. Retain only applicable sections.
New capabilities start with a descriptive ## Purpose section.
For existing requirements copy the full block and exact name into MODIFIED.
Use ADDED for new requirements. Do not copy empty sections into the result. -->

## ADDED Requirements

### Requirement: {stable descriptive name}
{Owner} SHALL {observable guarantee}.

#### Scenario: {observable case}
- **WHEN** {trigger and conditions}
- **THEN** {observable result}

## MODIFIED Requirements

### Requirement: {exact existing name}
{Complete updated requirement, including still-valid guarantees.}

#### Scenario: {observable case}
- **WHEN** {trigger and conditions}
- **THEN** {observable result}

## REMOVED Requirements

### Requirement: {exact existing name}
**Reason**: {why removed}
**Migration**: {consumer migration or explicit explanation that none is needed}

## RENAMED Requirements

- FROM: `### Requirement: {old name}`
- TO: `### Requirement: {new name}`
