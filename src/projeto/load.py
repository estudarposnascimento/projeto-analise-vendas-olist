
import sqlite3

import pandas as pd

from projeto.config import DATABASE_DIR, DATABASE_PATH, DATASETS
from projeto.extract import extract_dataset


def create_database() -> None:
    """
    Cria o diretório e o arquivo do banco SQLite.
    """

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH):
        pass

    print(f"Banco de dados disponível em: {DATABASE_PATH}")


def load_bronze() -> None:
    """
    Carrega os datasets originais nas tabelas Bronze.
    """

    create_database()

    with sqlite3.connect(DATABASE_PATH) as connection:

        for dataset_name in DATASETS:

            dataframe = extract_dataset(dataset_name)

            table_name = f"bronze_{dataset_name}"

            # Todas as colunas serão armazenadas como TEXT
            column_types = {
                column: "TEXT"
                for column in dataframe.columns
            }

            dataframe.to_sql(
                name=table_name,
                con=connection,
                if_exists="replace",
                index=False,
                dtype=column_types,
            )

            total_records = pd.read_sql_query(
                f"SELECT COUNT(*) AS total FROM {table_name}",
                connection,
            ).iloc[0]["total"]

            print(
                f"Tabela {table_name} carregada: "
                f"{total_records:,} registros"
            )

    print("\nCarga Bronze concluída com sucesso!")


if __name__ == "__main__":
    load_bronze()
