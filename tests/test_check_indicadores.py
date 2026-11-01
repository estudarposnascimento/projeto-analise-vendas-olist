
import sqlite3

from projeto import check_indicadores


def criar_banco_teste(tmp_path, monkeypatch):
    """Cria um banco temporário para testar os indicadores Gold."""
    database_path = tmp_path / "teste_indicadores.db"

    with sqlite3.connect(database_path) as connection:
        # Criação das três tabelas de indicadores
        for table in check_indicadores.TABLES:
            connection.execute(
                f"CREATE TABLE {table} (id INTEGER)"
            )

        connection.executemany(
            "INSERT INTO gold_vendas_mensais VALUES (?)",
            [(1,), (2,)],
        )

        connection.executemany(
            "INSERT INTO gold_vendas_categorias VALUES (?)",
            [(1,), (2,), (3,)],
        )

        connection.executemany(
            "INSERT INTO gold_top_produtos VALUES (?)",
            [(1,), (2,), (3,), (4,)],
        )

        # Tabela com vendas entregues e outros status
        connection.execute("""
            CREATE TABLE gold_vendas (
                order_id TEXT,
                order_status TEXT,
                price REAL,
                freight_value REAL
            )
        """)

        connection.executemany(
            """
            INSERT INTO gold_vendas (
                order_id,
                order_status,
                price,
                freight_value
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                ("pedido_1", "delivered", 100.00, 10.00),
                ("pedido_1", "delivered", 50.00, 5.00),
                ("pedido_2", "delivered", 150.00, 15.00),
                ("pedido_3", "canceled", 200.00, 20.00),
            ],
        )

    monkeypatch.setattr(
        check_indicadores,
        "DATABASE_PATH",
        database_path,
    )

    return database_path


def test_check_indicadores_displays_all_sections(
    tmp_path, monkeypatch, capsys
):
    criar_banco_teste(tmp_path, monkeypatch)

    check_indicadores.main()

    output = capsys.readouterr().out

    assert "VALIDAÇÃO DOS INDICADORES GOLD" in output
    assert "RESUMO DAS VENDAS ENTREGUES" in output
    assert "Pedidos entregues:" in output
    assert "Itens entregues:" in output
    assert "Valor dos produtos:" in output
    assert "Valor do frete:" in output
    assert "Ticket médio:" in output


def test_check_indicadores_displays_table_counts(
    tmp_path, monkeypatch, capsys
):
    criar_banco_teste(tmp_path, monkeypatch)

    check_indicadores.main()

    output = capsys.readouterr().out

    assert "gold_vendas_mensais: 2 registros" in output
    assert "gold_vendas_categorias: 3 registros" in output
    assert "gold_top_produtos: 4 registros" in output


def test_check_indicadores_counts_delivered_orders(
    tmp_path, monkeypatch, capsys
):
    criar_banco_teste(tmp_path, monkeypatch)

    check_indicadores.main()

    output = capsys.readouterr().out

    assert "Pedidos entregues: 2" in output
    assert "Itens entregues: 3" in output


def test_check_indicadores_calculates_financial_values(
    tmp_path, monkeypatch, capsys
):
    criar_banco_teste(tmp_path, monkeypatch)

    check_indicadores.main()

    output = capsys.readouterr().out

    assert "Valor dos produtos: R$ 300.00" in output
    assert "Valor do frete: R$ 30.00" in output
    assert "Ticket médio: R$ 150.00" in output


def test_check_indicadores_ignores_other_order_status(
    tmp_path, monkeypatch, capsys
):
    criar_banco_teste(tmp_path, monkeypatch)

    check_indicadores.main()

    output = capsys.readouterr().out

    # O pedido cancelado de R$ 200 não deve entrar nos indicadores.
    assert "Valor dos produtos: R$ 300.00" in output
    assert "Valor do frete: R$ 30.00" in output
