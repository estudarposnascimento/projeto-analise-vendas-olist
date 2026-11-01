
import sqlite3

import pytest

from projeto import validate_silver


@pytest.fixture
def silver_database(tmp_path, monkeypatch):
    """Cria um banco SQLite temporário com as tabelas da camada Silver."""
    database_path = tmp_path / "silver_test.db"

    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE silver_orders (
                order_id TEXT,
                order_purchase_timestamp TEXT,
                order_estimated_delivery_date TEXT
            );

            CREATE TABLE silver_order_items (
                order_id TEXT,
                order_item_id INTEGER,
                product_id TEXT,
                price REAL,
                freight_value REAL
            );

            CREATE TABLE silver_products (
                product_id TEXT,
                product_weight_g INTEGER,
                product_length_cm INTEGER,
                product_height_cm INTEGER,
                product_width_cm INTEGER
            );
            """
        )

    monkeypatch.setattr(
        validate_silver,
        "DATABASE_PATH",
        database_path,
    )

    return database_path


def test_validate_silver_without_failures(silver_database, capsys):
    """Todas as validações devem retornar OK quando os dados estão íntegros."""
    with sqlite3.connect(silver_database) as connection:
        connection.executescript(
            """
            INSERT INTO silver_orders VALUES (
                'order_1', '2026-01-01', '2026-01-10'
            );

            INSERT INTO silver_order_items VALUES (
                'order_1', 1, 'product_1', 100.0, 15.0
            );

            INSERT INTO silver_products VALUES (
                'product_1', 1000, 20, 10, 15
            );
            """
        )

    validate_silver.main()

    output = capsys.readouterr().out

    assert output.count("OK") == 13
    assert "VERIFICAR" not in output
    assert "13" in output
    assert "0" in output


def test_validate_silver_detects_data_problems(silver_database, capsys):
    """As 13 validações devem identificar problemas nos dados."""
    with sqlite3.connect(silver_database) as connection:
        connection.executescript(
            """
            -- Orders: identificadores nulos, vazios e duplicados.
            INSERT INTO silver_orders VALUES
                (NULL, NULL, NULL),
                ('', '2026-01-01', '2026-01-10'),
                ('order_dup', '2026-01-01', '2026-01-10'),
                ('order_dup', '2026-01-02', '2026-01-11');

            -- Items: chave duplicada, valores negativos e referências ausentes.
            INSERT INTO silver_order_items VALUES
                ('order_missing', 1, 'product_missing', -10, -5),
                ('order_missing', 1, 'product_missing', 20, 10);

            -- Products: identificadores nulos, vazios e duplicados.
            INSERT INTO silver_products VALUES
                (NULL, -100, -20, -10, -15),
                ('', 100, 20, 10, 15),
                ('product_dup', 100, 20, 10, 15),
                ('product_dup', 100, 20, 10, 15);
            """
        )

    validate_silver.main()

    output = capsys.readouterr().out

    assert output.count("VERIFICAR") == 13
    assert "Ocorr" in output
    assert "13" in output


def test_validate_silver_has_thirteen_validations():
    """Confirma que o módulo possui as 13 regras esperadas."""
    assert len(validate_silver.VALIDATIONS) == 13


def test_validate_silver_database_error(tmp_path, monkeypatch):
    """Verifica o comportamento quando o banco não existe."""
    database_path = tmp_path / "inexistente.db"

    monkeypatch.setattr(
        validate_silver,
        "DATABASE_PATH",
        database_path,
    )

    # SQLite cria um banco vazio, mas as tabelas não existem.
    with pytest.raises(sqlite3.OperationalError):
        validate_silver.main()
