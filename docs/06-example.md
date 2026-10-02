# A worked OpenSpec change

The equipment-lending example lives in `examples/equipment-lending/`. It shows a
fictional baseline and one proposed return-condition change. There is no application
implementation or accepted delivery evidence; all seven delivery tasks remain open.

Read `examples/equipment-lending/openspec/README.md` for the project entry point and
`examples/equipment-lending/openspec/worked-change.md` for the reading order and
commentary. The example keeps its system handbook, main specs, deltas, design, tasks,
proposed ADR, and verification record in their own OpenSpec locations.

To browse the example as its own mdBook, run from the guide's root with mdBook on
`PATH`:

```sh
mdbook serve examples/equipment-lending
```

`mdbook build examples/equipment-lending` writes static HTML to
`examples/equipment-lending/build/book/`. The book's
navigation is `openspec/SUMMARY.md`; its architecture entry point remains
`openspec/system-architecture/README.md`.

## Try the native commands

From this guide's root, prepare a disposable copy at a path that does not exist yet:

```sh
cp -R examples/equipment-lending /tmp/lending-ddd-demo
python3 build.py
mkdir -p /tmp/lending-ddd-demo/openspec/schemas
cp -R build/schemas/legacy /tmp/lending-ddd-demo/openspec/schemas/openspec-ddd
cp -R src/helpers/ddd /tmp/lending-ddd-demo/openspec/
cd /tmp/lending-ddd-demo
openspec schema validate openspec-ddd
openspec validate --all --strict --no-interactive
openspec status --change record-return-condition
openspec instructions apply --change record-return-condition --json
python3 openspec/ddd/ddd.py impact lending.domain
```

Expect planning artifacts to be present and **seven tasks remaining**. The integration
tests additionally demonstrate archive merging on another temporary copy. They test
text merging only, preserve unaffected requirements and architecture, and leave the
source example unfinished.
