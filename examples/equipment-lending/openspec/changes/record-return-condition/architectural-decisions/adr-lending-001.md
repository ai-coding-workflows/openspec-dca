# ADR-LENDING-001: Save return state and condition atomically

Status: Proposed
Date: 2026-09-21
Scope: Lending storage and return feature

## Context

A returned state without its newly required condition would violate the target
contract. Storage failures can occur between separate writes.

## Decision and Alternatives

Use one transaction to persist both values. Reject separate commits followed by
best-effort repair because callers could observe an incomplete completed return.

## Consequences

The adapter needs migration and failure tests. Existing returns remain unrecorded.
Promote this decision to the durable lending scope only when accepted; synchronize
architecture separately from OpenSpec requirement deltas.
