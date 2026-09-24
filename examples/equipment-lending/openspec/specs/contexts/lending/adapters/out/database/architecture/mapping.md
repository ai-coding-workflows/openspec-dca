# Loan persistence: fictional baseline

Status: Current in the illustrative baseline; no application implementation is supplied.

Each loan stores an equipment identifier, borrower identifier, and active/returned
state. A return saves its state in one database transaction. There is currently
no recorded return condition. The adapter implements the loan-store contract;
SQL and schema choices belong in this architecture view rather than the port spec.
