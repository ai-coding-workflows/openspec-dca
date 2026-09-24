# Return runtime: fictional baseline

Status: Current in the illustrative baseline; no application implementation is supplied.

The HTTP adapter passes a loan identifier to the return use case. The use case
loads the loan, rejects unknown or already returned loans, changes its state and
uses the storage port to save it. A failed save is surfaced to the caller.
The current model does not record the condition of returned equipment.
