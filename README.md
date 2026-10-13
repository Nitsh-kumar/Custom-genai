# SAP Data Assistant — SQL and OData Prototypes

A Streamlit experiment for translating natural-language questions into queries over SAP-style data.

**Status:** prototype. The SQL and OData variants are on separate branches; they are not one verified production integration.

## Branch map

| Branch | Scope |
| --- | --- |
| `master` | Local SQLite query generation, tables, and charts |
| [`api_integration`](https://github.com/Nitsh-kumar/Custom-genai/tree/api_integration) | OData request/integration experiment |
| `saurav` | Earlier SQL variant |
| `portfolio/read-only-query-safety` | Proposed local query-safety/configuration fixes |

The default branch does not fetch live SAP data. It uses a local SQLite database and prompts referring to SAP-style tables.

## Local workflow

Question → Gemini-generated query → SQLite execution → pandas result → Streamlit table/chart.

- [app.py](app.py): application entry point.
- [generate.py](generate.py): prompts and provider call.
- [database.py](database.py): local query boundary.
- [output.py](output.py): result rendering.
- [prompts.txt](prompts.txt): query-generation instructions.

## Setup for this review branch

Create and activate a Python virtual environment, then install the manifest and the directly imported pandas dependency:

```bash
python -m pip install -r requirements.txt
python -m pip install pandas
```

Set `GEMINI_API_KEY` in the process environment. The app does not automatically load `.env`; [.env.example](.env.example) documents the variable. Do not put a provider key in the source.

The existing code names a provider model and uses a legacy SDK. Model availability and dependency compatibility still require verification; this is not a confirmed clean-start recipe.

Provide an approved synthetic `MYdb.db` matching the prompt schema. The tracked database's provenance has not been established. This branch does not auto-create a missing database.

```bash
python -m streamlit run app.py
python -m unittest discover -s tests -v
```

## Query boundaries in this branch

SQLite opens read-only. An authorizer rejects writes/control operations; a row cap and instruction budget constrain results and work. These protections are not row-level authorization and do not prevent reading sensitive data already present in the database.

Five synthetic regression tests passed during the earlier safety change. Live Gemini inference, UI behavior, and OData connectivity were not exercised.

## Credential and integration follow-up

Previously committed issued keys must be revoked or rotated. The OData branch and Git history require separate review; removing a key from this branch does not invalidate it.

Use synthetic data until ownership and privacy are clear. Preserve alternate-branch work before consolidation. See [query-safety notes](SAFETY.md) and [project status](docs/PROJECT_STATUS.md).

## Validation

This documentation was checked against repository files on 13 October 2026. Notebooks, application runs, refreshes, and test suites were not executed during this documentation pass. Saved outputs are historical evidence, not a fresh run.
