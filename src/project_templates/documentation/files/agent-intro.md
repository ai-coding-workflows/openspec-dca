Architecture and user documentation serve different audiences and retain their
own sources and navigation. The selected sections below define their responsibilities;
selecting both does not merge the books or make user pages part of the arc42 handbook.
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
