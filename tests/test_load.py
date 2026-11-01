
import sqlite3

import pandas as pd

import projeto.load as load_module


def test_create_database(tmp_path, monkeypatch, capsys):
    """Verifica a criação do diretório e do banco SQLite."""

    database_dir = tmp_path / "database"
    database_path = database_dir / "teste.db"

    monkeypatch.setattr(
        load_module,
        "DATABASE_DIR",
        database_dir,
    )

    monkeypatch.setattr(
        load_module,
        "DATABASE_PATH",
        database_path,
    )

    load_module.create_database()

    assert database_dir.exists()
    assert database_path.exists()

    output = capsys.readouterr().out

    assert "Banco de dados disponível em:" in output


def test_load_bronze(tmp_path, monkeypatch, capsys):
    """Verifica a carga dos três datasets na camada Bronze."""

    database_dir = tmp_path / "database"
    database_path = database_dir / "teste.db"

    monkeypatch.setattr(
        load_module,
        "DATABASE_DIR",
        database_dir,
    )

    monkeypatch.setattr(
        load_module,
        "DATABASE_PATH",
        database_path,
    )

    # Simula os três datasets extraídos.
    datasets = {
        "orders": pd.DataFrame({
            "order_id": ["001", "002"],
            "order_status": ["delivered", "canceled"],
        }),
        "order_items": pd.DataFrame({
            "order_id": ["001", "002"],
            "order_item_id": ["1", "1"],
            "price": ["100.50", "200.00"],
        }),
        "products": pd.DataFrame({
            "product_id": ["P001", "P002"],
            "product_category_name": ["cama_banho", "beleza"],
        }),
    }

    monkeypatch.setattr(
        load_module,
        "DATASETS",
        {
            "orders": "orders.csv",
            "order_items": "order_items.csv",
            "products": "products.csv",
        },
    )

    monkeypatch.setattr(
        load_module,
        "extract_dataset",
        lambda dataset_name: datasets[dataset_name],
    )

    # Executa a carga Bronze.
    load_module.load_bronze()

    assert database_path.exists()

    with sqlite3.connect(database_path) as connection:

        # Verifica a existência das três tabelas.
        tables = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            """,
            connection,
        )["name"].tolist()

        assert "bronze_orders" in tables
        assert "bronze_order_items" in tables
        assert "bronze_products" in tables

        # Verifica a quantidade de registros.
        for dataset_name, dataframe in datasets.items():

            table_name = f"bronze_{dataset_name}"

            result = pd.read_sql_query(
                f"SELECT COUNT(*) AS total FROM {table_name}",
                connection,
            )

            assert result.iloc[0]["total"] == len(dataframe)

        # Verifica se as colunas foram criadas como TEXT.
        columns = connection.execute(
            "PRAGMA table_info(bronze_orders)"
        ).fetchall()

        column_types = {
            column[1]: column[2]
            for column in columns
        }

        assert column_types["order_id"] == "TEXT"
        assert column_types["order_status"] == "TEXT"

        # Confirma que os valores foram carregados corretamente.
        orders = pd.read_sql_query(
            "SELECT * FROM bronze_orders ORDER BY order_id",
            connection,
        )

        assert orders.loc[0, "order_id"] == "001"
        assert orders.loc[1, "order_status"] == "canceled"

    output = capsys.readouterr().out

    assert "bronze_orders carregada: 2 registros" in output
    assert "bronze_order_items carregada: 2 registros" in output
    assert "bronze_products carregada: 2 registros" in output
    assert "Carga Bronze concluída com sucesso!" in output


def test_load_bronze_replaces_existing_tables(
    tmp_path,
    monkeypatch,
):
    """Verifica se a carga substitui tabelas já existentes."""

    database_dir = tmp_path / "database"
    database_path = database_dir / "teste.db"

    database_dir.mkdir(parents=True)

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "CREATE TABLE bronze_orders "
            "(order_id TEXT)"
        )

        connection.execute(
            "INSERT INTO bronze_orders VALUES ('antigo')"
        )

    monkeypatch.setattr(
        load_module,
        "DATABASE_DIR",
        database_dir,
    )

    monkeypatch.setattr(
        load_module,
        "DATABASE_PATH",
        database_path,
    )

    monkeypatch.setattr(
        load_module,
        "DATASETS",
        {"orders": "orders.csv"},
    )

    monkeypatch.setattr(
        load_module,
        "extract_dataset",
        lambda dataset_name: pd.DataFrame({
            "order_id": ["novo_001", "novo_002"],
        }),
    )

    load_module.load_bronze()

    with sqlite3.connect(database_path) as connection:

        result = pd.read_sql_query(
            "SELECT * FROM bronze_orders",
            connection,
        )

    assert len(result) == 2
    assert result.loc[0, "order_id"] == "novo_001"
    assert result.loc[1, "order_id"] == "novo_002"
