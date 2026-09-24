## Starting Point and Context

Start from `lending.return`. Read the domain model and `lending.domain`, then
`lending.loan-store`, then the feature. Read its runtime fragment and the database
mapping listed in the catalog. This example has no earlier accepted ADRs.

## Owner and Consumer Review

| Owner / exact capability path | Relationship | Disposition | Reason / needed change |
| --- | --- | --- | --- |
| lending.domain / contexts/lending/domain | Shared prerequisite | Contract delta | Add proposed ReturnCondition values and historical-data meaning to the model; state the new-return obligation in the delta |
| lending.loan-store / contexts/lending/ports/loan-store | Consumes domain | Contract delta | Save state and condition together |
| lending.return / contexts/lending/features/return-equipment | Consumes domain and port | Contract delta | Require condition and preserve rejection/failure behavior |
| lending.http / contexts/lending/adapters/in/http | Consumes return feature | Contract delta | Required request field and HTTP 400 mapping |
| lending.database / contexts/lending/adapters/out/database | Implements port | Implementation only | Existing spec delegates guarantees to the port; mapping and storage must change |
| Team-controlled callers | External consumer, absent from catalog | Implementation only | Supply the condition before the coordinated rollout |
| Application composition | Wires the existing adapters | Unchanged | No provider or interface binding is replaced |

## Proposed Model Edits

The maintained baseline model does not yet include return conditions. The proposed definition and distinction between the two recorded values and
historical `unrecorded` data are written in the change design. The domain delta states
the new-return obligation against that proposed model; after acceptance, update
`domain/model.md` in the same delivery and review its consumers. The model companion is not merged by spec sync.

## Additional Owners

Domain and storage-port deltas are necessary to make the requested feature coherent.
Report both alongside the requested feature; HTTP is also affected. The database
adapter is reviewed but does not need a duplicate normative rule.

## Compatibility and Decisions

The teaching scenario assumes caller coordination is accepted. A real project must
confirm this or design a compatible transition before implementation. Existing
returns remain unrecorded; they are never backfilled with an invented value.

## Architecture and Delivery Consequences

Update the feature runtime and database mapping after implementation. A proposed
atomic-save decision is in decisions/adr-lending-001.md inside this change.
Domain and port behavior is understood first; tasks then coordinate storage, use case,
HTTP, and caller work. They do not form separate per-spec backlogs.
