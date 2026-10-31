
import sqlite3

from projeto.config import DATABASE_PATH


def check_database() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:

        query = """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name;
        """

        tables = connection.execute(query).fetchall()

        print("\nTABELAS DO BANCO SQLITE")

        for (table_name,) in tables:

            total = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()[0]

            print(f"{table_name}: {total:,} registros")


if __name__ == "__main__":
    check_database()
