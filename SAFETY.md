# Local SQLite prototype: configuration and query boundaries

The default `master` branch runs natural-language queries against local SQLite. The OData implementation is on a separate branch and is outside this change.

Set `GEMINI_API_KEY` in the process environment before running the app. `.env.example` documents the variable; the app does not automatically load `.env`.

Queries use an existing database opened in read-only mode, a SQLite authorizer, a 500-row result cap, and a progress budget. Writes, attachment, PRAGMA statements, and extension-loading calls are rejected. Missing databases are not created or seeded automatically. Queries that exceed the row cap fail instead of silently truncating results.

Only use approved synthetic data for this demo. Read-only access does not provide row-level permissions or stop a model from selecting sensitive data. The query budget limits SQLite instruction work; it is not a wall-clock timeout or a complete security boundary.

Run the dependency-free regression checks from the repository root:

```bash
python -m unittest discover -s tests -v
```

Before any public deployment, revoke or rotate previously committed issued credentials, inspect every branch and Git history, and verify data ownership. Removing a key from this branch does not revoke it. Existing tracked databases remain tracked despite the new ignore rules; their provenance still needs review.

The provider model and SDK, live inference, Streamlit interface, and alternate OData branch have not been runtime-verified by this change. The project remains a prototype.
