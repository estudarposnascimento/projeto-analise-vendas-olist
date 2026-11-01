
import sqlite3

from projeto.config import DATABASE_PATH, PROJECT_ROOT


SQL_FILE = PROJECT_ROOT / "sql" / "gold" / "02_gold_indicadores.sql"


def main():
    if not SQL_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo SQL não encontrado: {SQL_FILE}"
        )

    with sqlite3.connect(DATABASE_PATH) as connection:
        with SQL_FILE.open(encoding="utf-8") as file:
            sql_script = file.read()

        connection.executescript(sql_script)

    print("Indicadores Gold criados com sucesso!")


if __name__ == "__main__":
    main()
