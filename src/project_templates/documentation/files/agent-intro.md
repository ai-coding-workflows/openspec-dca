Architecture and user documentation have distinct responsibilities; their readers
may overlap. Select navigation and outputs for the actual project. This starter
keeps selected books separate, but that is not a schema requirement for every product.
Selecting both components does not make user pages part of the arc42 model baseline.
The DDD foundation's lifecycle, ownership, protected-publication, and acceptance
boundaries apply to every documentation component.

Use `book-builder.toml` as the selected books list and each native book configuration
as the authority for source and output paths. Build/check only configured books:

```sh
./scripts/book.sh build
python3 openspec/schemas/{{schema-name}}/helpers/docs-check.py --source-only
python3 openspec/schemas/{{schema-name}}/helpers/docs-check.py
```

On Windows use `scripts\book.cmd`. Source/link/rendering checks support review;
they do not establish architectural correctness, successful product procedures,
acceptance, release, or deployment. Keep writing prompts and unknowns explicit until
checked against the actual project. Follow the relevant component's verification
obligations rather than treating a shared green book build as complete evidence.
