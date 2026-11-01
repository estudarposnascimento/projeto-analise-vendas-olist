
import sqlite3

from projeto import check_silver


def create_silver_database(database_path):
    """Cria as três tabelas Silver para os testes."""
    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE silver_orders (
                order_id TEXT,
                order_status TEXT,
                order_purchase_timestamp DATETIME
            );

            CREATE TABLE silver_order_items (
                order_id TEXT,
                order_item_id INTEGER,
                price REAL
            );

            CREATE TABLE silver_products (
                product_id TEXT,
                product_weight_g INTEGER,
                product_category_name TEXT
            );

            INSERT INTO silver_orders VALUES
                ('order_1', 'delivered', '2026-01-01'),
                ('order_2', 'shipped', '2026-01-02');

            INSERT INTO silver_order_items VALUES
                ('order_1', 1, 100.0),
                ('order_1', 2, 50.0),
                ('order_2', 1, 80.0);

            INSERT INTO silver_products VALUES
                ('product_1', 1000, 'beleza'),
                ('product_2', 2000, 'informatica');
            """
        )


def test_check_silver_displays_all_tables(
    tmp_path, monkeypatch, capsys
):
    """Verifica se as três tabelas Silver são exibidas."""
    database_path = tmp_path / "silver.db"
    create_silver_database(database_path)

    monkeypatch.setattr(
        check_silver,
        "DATABASE_PATH",
        database_path,
    )

    check_silver.check_silver()

    output = capsys.readouterr().out

    assert "TABELA: SILVER_ORDERS" in output
    assert "TABELA: SILVER_ORDER_ITEMS" in output
    assert "TABELA: SILVER_PRODUCTS" in output


def test_check_silver_displays_columns_and_types(
    tmp_path, monkeypatch, capsys
):
    """Verifica se os nomes e tipos das colunas são exibidos."""
    database_path = tmp_path / "silver.db"
    create_silver_database(database_path)

    monkeypatch.setattr(
        check_silver,
        "DATABASE_PATH",
        database_path,
    )

    check_silver.check_silver()

    output = capsys.readouterr().out

    assert "order_id: TEXT" in output
    assert "order_item_id: INTEGER" in output
    assert "price: REAL" in output
    assert "order_purchase_timestamp: DATETIME" in output
    assert "product_weight_g: INTEGER" in output


def test_check_silver_displays_record_counts(
    tmp_path, monkeypatch, capsys
):
    """Verifica a contagem de registros de cada tabela."""
    database_path = tmp_path / "silver.db"
    create_silver_database(database_path)

    monkeypatch.setattr(
        check_silver,
        "DATABASE_PATH",
        database_path,
    )

    check_silver.check_silver()

    output = capsys.readouterr().out

    assert "Total de registros: 2" in output
    assert "Total de registros: 3" in output


def test_check_silver_with_empty_tables(
    tmp_path, monkeypatch, capsys
):
    """Verifica se tabelas vazias são exibidas corretamente."""
    database_path = tmp_path / "silver_empty.db"

    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE silver_orders (order_id TEXT);
            CREATE TABLE silver_order_items (order_id TEXT);
            CREATE TABLE silver_products (product_id TEXT);
            """
        )

    monkeypatch.setattr(
        check_silver,
        "DATABASE_PATH",
        database_path,
    )

    check_silver.check_silver()

    output = capsys.readouterr().out

    assert output.count("Total de registros: 0") == 3
