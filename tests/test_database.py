import sqlite3
import tempfile
import unittest
from pathlib import Path

from database import execute_read_query


class ReadQueryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "synthetic.db"
        with sqlite3.connect(self.path) as connection:
            connection.execute("CREATE TABLE materials (MATNR TEXT, amount INTEGER)")
            connection.executemany("INSERT INTO materials VALUES (?, ?)", [("A", 10), ("B", 20)])

    def test_reads_and_preserves_aggregate_label(self):
        self.assertEqual(execute_read_query("SELECT MATNR FROM materials ORDER BY MATNR", self.path),
                         ([("A",), ("B",)], ["Material"]))
        self.assertEqual(execute_read_query("SELECT SUM(amount) AS total FROM materials", self.path),
                         ([(30,)], ["total"]))

    def test_rejects_mutations_and_control_statements(self):
        for query in ["DELETE FROM materials", "UPDATE materials SET amount=0",
                      "INSERT INTO materials VALUES ('C', 30)", "DROP TABLE materials",
                      "ATTACH DATABASE ':memory:' AS other", "PRAGMA table_info(materials)",
                      "SELECT load_extension('anything')", "SELECT 1; DELETE FROM materials"]:
            with self.subTest(query=query), self.assertRaises(ValueError):
                execute_read_query(query, self.path)
        with sqlite3.connect(self.path) as connection:
            self.assertEqual(connection.execute("SELECT SUM(amount) FROM materials").fetchone(), (30,))

    def test_rejects_excess_rows(self):
        with self.assertRaisesRegex(ValueError, "exceeds"):
            execute_read_query("SELECT * FROM materials", self.path, max_rows=1)

    def test_bounds_expensive_recursive_query(self):
        with self.assertRaises(ValueError):
            execute_read_query("WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n) SELECT SUM(x) FROM n", self.path)

    def test_missing_database_is_not_created(self):
        missing = Path(self.directory.name) / "missing.db"
        with self.assertRaises(ValueError):
            execute_read_query("SELECT 1", missing)
        self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
