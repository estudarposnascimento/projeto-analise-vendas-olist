
import sqlite3

from projeto import check_gold


def criar_banco_teste(tmp_path, monkeypatch):
    """Cria um banco SQLite temporário com dados para validação."""
    database_path = tmp_path / "teste_gold.db"

    with sqlite3.connect(database_path) as connection:
        connection.execute("""
            CREATE TABLE gold_vendas (
                order_id TEXT,
                order_item_id INTEGER,
                product_id TEXT,
                price REAL,
                freight_value REAL,
                total_item_value REAL
            )
        """)

        connection.executemany(
            """
            INSERT INTO gold_vendas (
                order_id,
                order_item_id,
                product_id,
                price,
                freight_value,
                total_item_value
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                ("pedido_1", 1, "produto_1", 100.00, 10.00, 110.00),
                ("pedido_1", 1, None, None, 5.00, 5.00),
                ("pedido_2", 1, "produto_1", 200.00, 5.00, 205.00),
            ],
        )

    monkeypatch.setattr(check_gold, "DATABASE_PATH", database_path)

    return database_path


def test_check_gold_displays_all_sections(tmp_path, monkeypatch, capsys):
    criar_banco_teste(tmp_path, monkeypatch)

    check_gold.main()

    output = capsys.readouterr().out

    assert "VALIDAÇÃO DA CAMADA GOLD" in output
    assert "Total de registros:" in output
    assert "Pedidos distintos:" in output
    assert "Produtos distintos:" in output
    assert "Itens duplicados:" in output
    assert "Registros com campos essenciais nulos:" in output
    assert "RESUMO FINANCEIRO" in output


def test_check_gold_displays_record_counts(tmp_path, monkeypatch, capsys):
    criar_banco_teste(tmp_path, monkeypatch)

    check_gold.main()

    output = capsys.readouterr().out

    assert "Total de registros: 3" in output
    assert "Pedidos distintos: 2" in output
    assert "Produtos distintos: 1" in output


def test_check_gold_identifies_duplicates(tmp_path, monkeypatch, capsys):
    criar_banco_teste(tmp_path, monkeypatch)

    check_gold.main()

    output = capsys.readouterr().out

    assert "Itens duplicados: 1" in output


def test_check_gold_identifies_null_values(tmp_path, monkeypatch, capsys):
    criar_banco_teste(tmp_path, monkeypatch)

    check_gold.main()

    output = capsys.readouterr().out

    assert "Registros com campos essenciais nulos: 1" in output


def test_check_gold_displays_financial_summary(
    tmp_path, monkeypatch, capsys
):
    criar_banco_teste(tmp_path, monkeypatch)

    check_gold.main()

    output = capsys.readouterr().out

    assert "Total de produtos: R$ 300.00" in output
    assert "Total de frete: R$ 20.00" in output
    assert "Total com frete: R$ 320.00" in output
