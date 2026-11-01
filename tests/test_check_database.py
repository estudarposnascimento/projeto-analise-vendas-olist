
import sqlite3

from projeto import check_database


def test_check_database_displays_tables_and_counts(tmp_path, monkeypatch, capsys):
    """Exibe os nomes das tabelas e suas respectivas quantidades."""
    database_path = tmp_path / "test.db"

    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE bronze_orders (order_id TEXT);
            CREATE TABLE bronze_products (product_id TEXT);

            INSERT INTO bronze_orders VALUES
                ('order_1'),
                ('order_2'),
                ('order_3');

            INSERT INTO bronze_products VALUES
                ('product_1'),
                ('product_2');
            """
        )

    monkeypatch.setattr(
        check_database,
        "DATABASE_PATH",
        database_path,
    )

    check_database.check_database()

    output = capsys.readouterr().out

    assert "TABELAS DO BANCO SQLITE" in output
    assert "bronze_orders: 3 registros" in output
    assert "bronze_products: 2 registros" in output


def test_check_database_without_tables(tmp_path, monkeypatch, capsys):
    """Verifica o comportamento quando o banco não possui tabelas."""
    database_path = tmp_path / "empty.db"

    with sqlite3.connect(database_path):
        pass

    monkeypatch.setattr(
        check_database,
        "DATABASE_PATH",
        database_path,
    )

    check_database.check_database()

    output = capsys.readouterr().out

    assert "TABELAS DO BANCO SQLITE" in output
    assert "registros" not in output


def test_check_database_with_empty_tables(tmp_path, monkeypatch, capsys):
    """Exibe zero registros para tabelas vazias."""
    database_path = tmp_path / "empty_tables.db"

    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE bronze_orders (order_id TEXT);
            CREATE TABLE bronze_products (product_id TEXT);
            """
        )

    monkeypatch.setattr(
        check_database,
        "DATABASE_PATH",
        database_path,
    )

    check_database.check_database()

    output = capsys.readouterr().out

    assert "bronze_orders: 0 registros" in output
    assert "bronze_products: 0 registros" in output


def test_check_database_formats_large_counts(tmp_path, monkeypatch, capsys):
    """Verifica a formatação de milhares com separador de milhar."""
    database_path = tmp_path / "large.db"

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "CREATE TABLE bronze_orders (order_id INTEGER)"
        )
        connection.executemany(
            "INSERT INTO bronze_orders VALUES (?)",
            [(number,) for number in range(1000)],
        )

    monkeypatch.setattr(
        check_database,
        "DATABASE_PATH",
        database_path,
    )

    check_database.check_database()

    output = capsys.readouterr().out

    assert "bronze_orders: 1,000 registros" in output
