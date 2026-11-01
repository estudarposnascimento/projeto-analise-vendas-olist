
import sqlite3

from projeto.config import DATABASE_PATH, PROJECT_ROOT


SQL_FILE = PROJECT_ROOT / "sql" / "gold" / "01_gold_vendas.sql"


def main():
    if not SQL_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo SQL não encontrado: {SQL_FILE}"
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        with open(SQL_FILE, encoding="utf-8") as file:
            sql_script = file.read()

        connection.executescript(sql_script)

    print("Tabela gold_vendas criada com sucesso!")


if __name__ == "__main__":
    main()
