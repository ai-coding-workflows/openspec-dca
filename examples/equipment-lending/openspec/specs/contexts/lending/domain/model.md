# Lending domain model

This companion records the illustrative baseline model. It is owned by the lending
domain; it is not a separate OpenSpec capability or requirement-sync target.

## Loan

A loan identifies one equipment item and one borrower. Its state is active or
returned. A return changes an active loan to returned.

## Return condition

The baseline does not record a condition when a loan is returned. The active
`record-return-condition` change proposes a domain concept and new behavior; those
proposals are not part of this accepted baseline until implemented and deliberately
reviewed into the model.
