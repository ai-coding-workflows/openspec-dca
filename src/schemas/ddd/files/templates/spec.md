# Delta: {capability}

<!-- Keep only applicable native sections. For a new capability add ## Purpose.
Preserve exact requirement names. Place domain rules, use-case behavior, port
contracts, and meaningful adapter guarantees with their authoritative owners.
A port contract addresses input/output meaning, failures, consistency and retries
where needed, without exposing a database/framework representation to the core. -->

## ADDED Requirements
### Requirement: {stable descriptive name}
{The owning capability SHALL/MUST provide an observable guarantee.}

#### Scenario: {observable case}
- **WHEN** {condition and action}
- **THEN** {observable result}

## MODIFIED Requirements
### Requirement: {exact existing name}
{Full replacement requirement, including all still-valid behavior and scenarios.}

#### Scenario: {observable case}
- **WHEN** {condition and action}
- **THEN** {observable result}

## REMOVED Requirements
### Requirement: {exact existing name}
**Reason**: {why removed}
**Migration**: {consumer migration or why none is needed}

## RENAMED Requirements
- FROM: `### Requirement: {old exact name}`
- TO: `### Requirement: {new exact name}`

{{hook:template.specs}}
