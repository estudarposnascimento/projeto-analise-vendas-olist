
import sqlite3

import pytest

import projeto.validate as validate_module

from projeto.validate import count_query


@pytest.fixture
def bronze_database(tmp_path, monkeypatch):
    """Cria um banco temporário com tabelas Bronze."""

    database_path = tmp_path / "bronze_test.db"

    monkeypatch.setattr(
        validate_module,
        "DATABASE_PATH",
        database_path,
    )

    with sqlite3.connect(database_path) as connection:

        connection.executescript("""
            CREATE TABLE bronze_orders (
                order_id TEXT,
                order_status TEXT
            );

            CREATE TABLE bronze_products (
                product_id TEXT,
                product_category_name TEXT
            );

            CREATE TABLE bronze_order_items (
                order_id TEXT,
                order_item_id TEXT,
                product_id TEXT
            );
        """)

        # Pedidos válidos e um pedido duplicado.
        connection.executemany(
            "INSERT INTO bronze_orders VALUES (?, ?)",
            [
                ("001", "delivered"),
                ("002", "canceled"),
                ("002", "canceled"),
                (None, "created"),
            ],
        )

        # Produtos válidos e um produto duplicado.
        connection.executemany(
            "INSERT INTO bronze_products VALUES (?, ?)",
            [
                ("P001", "cama_banho"),
                ("P002", "beleza"),
                ("P002", "beleza"),
                (None, "nao_informado"),
            ],
        )

        # Itens com chave composta duplicada,
        # pedido inexistente e produto inexistente.
        connection.executemany(
            "INSERT INTO bronze_order_items VALUES (?, ?, ?)",
            [
                ("001", "1", "P001"),
                ("001", "1", "P001"),
                ("002", "1", "P002"),
                ("999", "1", "P001"),
                ("001", "2", "P999"),
            ],
        )

    return database_path


def test_count_query(bronze_database):
    """Verifica a execução de uma consulta de contagem."""

    with sqlite3.connect(bronze_database) as connection:

        result = count_query(
            connection,
            "SELECT COUNT(*) FROM bronze_orders",
        )

    assert result == 4


def test_count_query_returns_zero(bronze_database):
    """Verifica o retorno zero quando não existem registros."""

    with sqlite3.connect(bronze_database) as connection:

        result = count_query(
            connection,
            """
            SELECT COUNT(*)
            FROM bronze_orders
            WHERE order_id = '999'
            """,
        )

    assert result == 0


def test_validate_bronze_detects_integrity_problems(
    bronze_database,
    capsys,
):
    """Verifica se as sete regras identificam os problemas."""

    validate_module.validate_bronze()

    output = capsys.readouterr().out

    # Chaves nulas.
    assert "Orders com order_id nulo: 1" in output
    assert "Products com product_id nulo: 1" in output

    # Chaves duplicadas.
    assert "Orders com order_id duplicado: 1" in output
    assert "Products com product_id duplicado: 1" in output

    # Chave composta duplicada.
    assert "Order Items com chave composta duplicada: 1" in output

    # Integridade referencial.
    assert "Order Items sem pedido correspondente: 1" in output
    assert "Order Items sem produto correspondente: 1" in output

    assert "VERIFICAR" in output
    assert "Validação concluída." in output


def test_validate_bronze_with_valid_data(
    bronze_database,
    capsys,
):
    """Verifica se dados íntegros são aprovados."""

    with sqlite3.connect(bronze_database) as connection:

        connection.execute("DELETE FROM bronze_order_items")
        connection.execute("DELETE FROM bronze_orders")
        connection.execute("DELETE FROM bronze_products")

        connection.executemany(
            "INSERT INTO bronze_orders VALUES (?, ?)",
            [
                ("001", "delivered"),
                ("002", "canceled"),
            ],
        )

        connection.executemany(
            "INSERT INTO bronze_products VALUES (?, ?)",
            [
                ("P001", "cama_banho"),
                ("P002", "beleza"),
            ],
        )

        connection.executemany(
            "INSERT INTO bronze_order_items VALUES (?, ?, ?)",
            [
                ("001", "1", "P001"),
                ("002", "1", "P002"),
            ],
        )

    validate_module.validate_bronze()

    output = capsys.readouterr().out

    assert output.count("OK |") == 7
    assert "VERIFICAR" not in output
    assert "Validação concluída." in output


def test_validate_bronze_with_empty_tables(
    bronze_database,
    capsys,
):
    """Verifica o comportamento com tabelas vazias."""

    with sqlite3.connect(bronze_database) as connection:

        connection.execute("DELETE FROM bronze_order_items")
        connection.execute("DELETE FROM bronze_orders")
        connection.execute("DELETE FROM bronze_products")

    validate_module.validate_bronze()

    output = capsys.readouterr().out

    assert output.count("OK |") == 7
    assert "VERIFICAR" not in output
