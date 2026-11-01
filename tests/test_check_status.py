
import sqlite3

from projeto import check_status


def create_status_database(database_path):
    """Cria um banco temporário para testar as consultas de status."""
    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE silver_orders (
                order_id TEXT,
                order_status TEXT
            );

            CREATE TABLE silver_order_items (
                order_id TEXT,
                order_item_id INTEGER
            );

            CREATE TABLE gold_vendas (
                order_id TEXT,
                order_status TEXT,
                price REAL,
                freight_value REAL,
                total_item_value REAL
            );

            INSERT INTO silver_orders VALUES
                ('order_1', 'delivered'),
                ('order_2', 'delivered'),
                ('order_3', 'canceled'),
                ('order_4', 'shipped'),
                ('order_5', 'unavailable');

            INSERT INTO silver_order_items VALUES
                ('order_1', 1),
                ('order_1', 2),
                ('order_2', 1),
                ('order_4', 1);

            INSERT INTO gold_vendas VALUES
                ('order_1', 'delivered', 100.00, 15.00, 115.00),
                ('order_1', 'delivered', 50.00, 10.00, 60.00),
                ('order_2', 'delivered', 200.00, 20.00, 220.00),
                ('order_4', 'shipped', 80.00, 12.00, 92.00);
            """
        )


def test_check_status_displays_all_sections(
    tmp_path, monkeypatch, capsys
):
    """Verifica se as três seções da análise são exibidas."""
    database_path = tmp_path / "status.db"
    create_status_database(database_path)

    monkeypatch.setattr(
        check_status,
        "DATABASE_PATH",
        database_path,
    )

    check_status.main()

    output = capsys.readouterr().out

    assert "ANÁLISE DE STATUS DOS PEDIDOS" in output
    assert "DISTRIBUIÇÃO DE TODOS OS PEDIDOS" in output
    assert "PEDIDOS PRESENTES NA GOLD" in output
    assert "PEDIDOS SEM ITENS" in output


def test_check_status_displays_order_distribution(
    tmp_path, monkeypatch, capsys
):
    """Verifica a distribuição de pedidos na Silver."""
    database_path = tmp_path / "status.db"
    create_status_database(database_path)

    monkeypatch.setattr(
        check_status,
        "DATABASE_PATH",
        database_path,
    )

    check_status.main()

    output = capsys.readouterr().out

    assert "delivered: 2" in output
    assert "canceled: 1" in output
    assert "shipped: 1" in output
    assert "unavailable: 1" in output


def test_check_status_displays_gold_values(
    tmp_path, monkeypatch, capsys
):
    """Verifica os pedidos, produtos, frete e total da Gold."""
    database_path = tmp_path / "status.db"
    create_status_database(database_path)

    monkeypatch.setattr(
        check_status,
        "DATABASE_PATH",
        database_path,
    )

    check_status.main()

    output = capsys.readouterr().out

    assert "Pedidos: 2" in output
    assert "Produtos: R$ 350.00" in output
    assert "Frete: R$ 45.00" in output
    assert "Total: R$ 395.00" in output


def test_check_status_displays_orders_without_items(
    tmp_path, monkeypatch, capsys
):
    """Verifica os pedidos que não possuem itens associados."""
    database_path = tmp_path / "status.db"
    create_status_database(database_path)

    monkeypatch.setattr(
        check_status,
        "DATABASE_PATH",
        database_path,
    )

    check_status.main()

    output = capsys.readouterr().out

    assert "canceled: 1" in output
    assert "unavailable: 1" in output


def test_check_status_with_empty_tables(
    tmp_path, monkeypatch, capsys
):
    """Verifica o comportamento quando não existem pedidos."""
    database_path = tmp_path / "empty.db"

    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE silver_orders (
                order_id TEXT,
                order_status TEXT
            );

            CREATE TABLE silver_order_items (
                order_id TEXT,
                order_item_id INTEGER
            );

            CREATE TABLE gold_vendas (
                order_id TEXT,
                order_status TEXT,
                price REAL,
                freight_value REAL,
                total_item_value REAL
            );
            """
        )

    monkeypatch.setattr(
        check_status,
        "DATABASE_PATH",
        database_path,
    )

    check_status.main()

    output = capsys.readouterr().out

    assert "DISTRIBUIÇÃO DE TODOS OS PEDIDOS" in output
    assert "PEDIDOS PRESENTES NA GOLD" in output
    assert "PEDIDOS SEM ITENS" in output
