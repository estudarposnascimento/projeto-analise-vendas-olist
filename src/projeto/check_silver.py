
import sqlite3

from projeto.config import DATABASE_PATH


def check_silver() -> None:

    tables = [
        "silver_orders",
        "silver_order_items",
        "silver_products",
    ]

    with sqlite3.connect(DATABASE_PATH) as connection:

        for table in tables:

            print(f"\n{'=' * 50}")
            print(f"TABELA: {table.upper()}")
            print("=" * 50)

            schema = connection.execute(
                f"PRAGMA table_info({table})"
            ).fetchall()

            for column in schema:
                column_name = column[1]
                column_type = column[2]

                print(f"{column_name}: {column_type}")

            total = connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"\nTotal de registros: {total:,}")


if __name__ == "__main__":
    check_silver()
