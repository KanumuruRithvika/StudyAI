"""
Pytest configuration for the backend test suite.

Clears checkpoint tables before test sessions so tests
start with a clean state and don't inherit stale state from previous runs.
"""

import sqlite3
import pytest


@pytest.fixture(autouse=True, scope="session")
def clear_checkpoint_db():
    """Clear all records from checkpoint database tables without deleting the file."""
    try:
        conn = sqlite3.connect("learning_checkpoints.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for (table_name,) in tables:
            if not table_name.startswith("sqlite_"):
                cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
        conn.close()
    except Exception:
        pass

    yield
