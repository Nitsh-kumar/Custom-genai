"""Bounded, read-only queries for the local SQLite prototype."""

import sqlite3
from pathlib import Path

MAX_ROWS = 500
MAX_PROGRESS_CALLBACKS = 1000
DB_PATH = Path(__file__).resolve().parent / "MYdb.db"

COLUMN_LABELS = {
    "EBELN": "Document Number",
    "MATNR": "Material",
    "MAKTX": "Material Description",
    "BUKRS": "Company code",
    "AEDAT": "Document Creation Date",
    "BSTYP": "Document Type",
    "MTART": "Material Type",
    "ERSDA": "Material Creation Date",
}


def _authorize(action, arg1, arg2, database_name, trigger_name):
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
    if action not in allowed:
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_READ and database_name != "main":
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION and (arg2 or "").lower() in {
        "load_extension", "readfile", "writefile",
    }:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def execute_read_query(query, db_path=DB_PATH, max_rows=MAX_ROWS):
    """Return rows and labels; reject writes and excessive result sets/work."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Provide a non-empty SELECT query.")
    if not isinstance(max_rows, int) or not 1 <= max_rows <= MAX_ROWS:
        raise ValueError(f"Row limit must be between 1 and {MAX_ROWS}.")
    path = Path(db_path).resolve()
    if not path.is_file():
        raise ValueError("The demo database is missing. Provide approved synthetic data.")
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    progress_calls = 0

    def bound_work():
        nonlocal progress_calls
        progress_calls += 1
        return int(progress_calls > MAX_PROGRESS_CALLBACKS)

    try:
        connection.execute("PRAGMA query_only = ON")
        connection.set_authorizer(_authorize)
        connection.set_progress_handler(bound_work, 1000)
        cursor = connection.execute(query)
        if cursor.description is None:
            raise ValueError("Only result-producing read queries are supported.")
        rows = cursor.fetchmany(max_rows + 1)
        if len(rows) > max_rows:
            raise ValueError(f"Query exceeds {max_rows} rows. Use a smaller LIMIT or aggregate.")
        labels = [COLUMN_LABELS.get(column[0], column[0]) for column in cursor.description]
        return rows, labels
    except sqlite3.Error:
        raise ValueError("Query rejected or could not be completed. Use a bounded SELECT query.") from None
    finally:
        connection.close()


def read_sql_query(st, sql):
    """Retain the existing UI contract without automatic database seeding."""
    return execute_read_query(sql)
