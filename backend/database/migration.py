from sqlalchemy import inspect, text

from database.connection import engine


def _add_column(
    connection,
    table: str,
    column: str,
    definition: str,
) -> None:
    """Add a column only when it does not already exist."""
    columns = {
        item["name"]
        for item in inspect(connection).get_columns(table)
    }

    if column not in columns:
        connection.execute(
            text(
                f"ALTER TABLE {table} "
                f"ADD COLUMN {column} {definition}"
            )
        )


def migrate_database() -> None:
    """Apply lightweight migrations required by the current schema."""
    with engine.begin() as connection:
        inspector = inspect(connection)
        tables = inspector.get_table_names()

        if "users" not in tables:
            return

        _add_column(
            connection,
            "users",
            "name",
            "VARCHAR(100)",
        )
        _add_column(
            connection,
            "users",
            "email",
            "VARCHAR(255)",
        )
        _add_column(
            connection,
            "users",
            "password_hash",
            "VARCHAR(255)",
        )

        connection.execute(
            text(
                """
                UPDATE users
                SET name = 'Existing User'
                WHERE name IS NULL
                """
            )
        )

        connection.execute(
            text(
                """
                UPDATE users
                SET email = id || '@local.invalid'
                WHERE email IS NULL
                """
            )
        )

        connection.execute(
            text(
                """
                UPDATE users
                SET password_hash = ''
                WHERE password_hash IS NULL
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS
                ix_users_email_unique
                ON users(email)
                """
            )
        )