
import sqlite3

import pandas as pd
import pytest

from projeto.transform import (
    get_sql_types,
    load_silver,
    read_bronze,
    transform_order_items,
    transform_orders,
    transform_products,
)


def test_read_bronze():
    """Verifica a leitura de uma tabela Bronze."""

    connection = sqlite3.connect(":memory:")

    try:
        connection.execute(
            "CREATE TABLE bronze_orders "
            "(order_id TEXT, order_status TEXT)"
        )

        connection.execute(
            "INSERT INTO bronze_orders VALUES "
            "('pedido_001', 'delivered')"
        )

        result = read_bronze(connection, "bronze_orders")

        assert len(result) == 1
        assert result.loc[0, "order_id"] == "pedido_001"
        assert result.loc[0, "order_status"] == "delivered"

    finally:
        connection.close()


def test_transform_orders():
    """Verifica a conversão de datas e padronização de status."""

    df = pd.DataFrame({
        "order_id": ["001", "002"],
        "order_purchase_timestamp": [
            "2018-01-01 10:00:00",
            "data_invalida",
        ],
        "order_approved_at": [
            "2018-01-01 11:00:00",
            None,
        ],
        "order_delivered_carrier_date": [
            "2018-01-02 10:00:00",
            None,
        ],
        "order_delivered_customer_date": [
            "2018-01-05 10:00:00",
            None,
        ],
        "order_estimated_delivery_date": [
            "2018-01-10 10:00:00",
            "2018-01-11 10:00:00",
        ],
        "order_status": [" DELIVERED ", " CANCELED "],
    })

    result = transform_orders(df)

    assert result.loc[0, "order_status"] == "delivered"
    assert result.loc[1, "order_status"] == "canceled"

    assert isinstance(
        result.loc[0, "order_purchase_timestamp"],
        pd.Timestamp,
    )

    assert pd.isna(result.loc[1, "order_purchase_timestamp"])

    # Confirma que o DataFrame original não foi alterado.
    assert df.loc[0, "order_status"] == " DELIVERED "


def test_transform_order_items():
    """Verifica conversão dos tipos numéricos e da data."""

    df = pd.DataFrame({
        "order_id": ["001", "002"],
        "order_item_id": ["1", "valor_invalido"],
        "price": ["100.50", "200.00"],
        "freight_value": ["15.50", "valor_invalido"],
        "shipping_limit_date": [
            "2018-01-10 10:00:00",
            "data_invalida",
        ],
    })

    result = transform_order_items(df)

    assert str(result["order_item_id"].dtype) == "Int64"
    assert result.loc[0, "order_item_id"] == 1
    assert pd.isna(result.loc[1, "order_item_id"])

    assert result.loc[0, "price"] == pytest.approx(100.50)
    assert result.loc[1, "price"] == pytest.approx(200.00)

    assert result.loc[0, "freight_value"] == pytest.approx(15.50)
    assert pd.isna(result.loc[1, "freight_value"])

    assert isinstance(
        result.loc[0, "shipping_limit_date"],
        pd.Timestamp,
    )

    assert pd.isna(result.loc[1, "shipping_limit_date"])


def test_transform_products():
    """Verifica conversão numérica e padronização das categorias."""

    df = pd.DataFrame({
        "product_id": ["001", "002"],
        "product_name_lenght": ["40", "invalido"],
        "product_description_lenght": ["200", "300"],
        "product_photos_qty": ["3", "2"],
        "product_weight_g": ["500", "1000"],
        "product_length_cm": ["20", "30"],
        "product_height_cm": ["10", "15"],
        "product_width_cm": ["12", "18"],
        "product_category_name": [" Cama_Banho ", None],
    })

    result = transform_products(df)

    assert result.loc[0, "product_category_name"] == "cama_banho"
    assert result.loc[1, "product_category_name"] == "nao_informado"

    assert str(result["product_weight_g"].dtype) == "Int64"
    assert result.loc[0, "product_weight_g"] == 500

    assert pd.isna(result.loc[1, "product_name_lenght"])

    # Confirma que o DataFrame original não foi alterado.
    assert df.loc[0, "product_category_name"] == " Cama_Banho "


def test_get_sql_types_orders():
    """Verifica os tipos SQL da tabela de pedidos."""

    df = pd.DataFrame({
        "order_id": ["001"],
        "order_purchase_timestamp": ["2018-01-01"],
        "order_status": ["delivered"],
    })

    result = get_sql_types(df, "silver_orders")

    assert result["order_id"] == "TEXT"
    assert result["order_purchase_timestamp"] == "DATETIME"
    assert result["order_status"] == "TEXT"


def test_get_sql_types_order_items():
    """Verifica os tipos SQL dos itens dos pedidos."""

    df = pd.DataFrame({
        "order_item_id": [1],
        "price": [100.0],
        "freight_value": [15.0],
        "shipping_limit_date": ["2018-01-01"],
    })

    result = get_sql_types(df, "silver_order_items")

    assert result["order_item_id"] == "INTEGER"
    assert result["price"] == "REAL"
    assert result["freight_value"] == "REAL"
    assert result["shipping_limit_date"] == "DATETIME"


def test_get_sql_types_products():
    """Verifica os tipos SQL dos produtos."""

    df = pd.DataFrame({
        "product_id": ["001"],
        "product_weight_g": [500],
        "product_length_cm": [20],
        "product_category_name": ["cama_banho"],
    })

    result = get_sql_types(df, "silver_products")

    assert result["product_id"] == "TEXT"
    assert result["product_weight_g"] == "INTEGER"
    assert result["product_length_cm"] == "INTEGER"
    assert result["product_category_name"] == "TEXT"


def test_get_sql_types_unknown_table():
    """Verifica o tipo padrão para uma tabela não mapeada."""

    df = pd.DataFrame({
        "codigo": ["001"],
        "descricao": ["Produto"],
    })

    result = get_sql_types(df, "outra_tabela")

    assert result == {
        "codigo": "TEXT",
        "descricao": "TEXT",
    }


def test_load_silver():
    """Verifica a carga de dados em uma tabela Silver."""

    connection = sqlite3.connect(":memory:")

    try:
        df = pd.DataFrame({
            "order_id": ["001", "002"],
            "order_status": ["delivered", "canceled"],
        })

        load_silver(df, "silver_orders", connection)

        result = pd.read_sql_query(
            "SELECT * FROM silver_orders",
            connection,
        )

        assert len(result) == 2
        assert result.loc[0, "order_id"] == "001"
        assert result.loc[1, "order_status"] == "canceled"

    finally:
        connection.close()

def test_run_silver(tmp_path, monkeypatch):
    """Verifica a execução completa da camada Silver."""

    import projeto.transform as transform_module

    # Banco temporário para não alterar o banco original.
    database_path = tmp_path / "teste_silver.db"

    monkeypatch.setattr(
        transform_module,
        "DATABASE_PATH",
        database_path,
    )

    # Cria as tabelas Bronze com dados de teste.
    with sqlite3.connect(database_path) as connection:

        pd.DataFrame({
            "order_id": ["pedido_001"],
            "order_purchase_timestamp": ["2018-01-01 10:00:00"],
            "order_approved_at": ["2018-01-01 11:00:00"],
            "order_delivered_carrier_date": ["2018-01-02 10:00:00"],
            "order_delivered_customer_date": ["2018-01-05 10:00:00"],
            "order_estimated_delivery_date": ["2018-01-10 10:00:00"],
            "order_status": [" DELIVERED "],
        }).to_sql(
            "bronze_orders",
            connection,
            index=False,
        )

        pd.DataFrame({
            "order_id": ["pedido_001"],
            "order_item_id": ["1"],
            "product_id": ["produto_001"],
            "seller_id": ["vendedor_001"],
            "shipping_limit_date": ["2018-01-03 10:00:00"],
            "price": ["100.50"],
            "freight_value": ["15.50"],
        }).to_sql(
            "bronze_order_items",
            connection,
            index=False,
        )

        pd.DataFrame({
            "product_id": ["produto_001"],
            "product_category_name": [" Cama_Banho "],
            "product_name_lenght": ["40"],
            "product_description_lenght": ["200"],
            "product_photos_qty": ["3"],
            "product_weight_g": ["500"],
            "product_length_cm": ["20"],
            "product_height_cm": ["10"],
            "product_width_cm": ["12"],
        }).to_sql(
            "bronze_products",
            connection,
            index=False,
        )

    # Executa todo o processo Silver.
    transform_module.run_silver()

    # Confere os resultados no banco temporário.
    with sqlite3.connect(database_path) as connection:

        orders = pd.read_sql_query(
            "SELECT * FROM silver_orders",
            connection,
        )

        items = pd.read_sql_query(
            "SELECT * FROM silver_order_items",
            connection,
        )

        products = pd.read_sql_query(
            "SELECT * FROM silver_products",
            connection,
        )

    assert len(orders) == 1
    assert orders.loc[0, "order_status"] == "delivered"

    assert len(items) == 1
    assert items.loc[0, "order_item_id"] == 1
    assert items.loc[0, "price"] == pytest.approx(100.50)

    assert len(products) == 1
    assert products.loc[0, "product_category_name"] == "cama_banho"
    assert products.loc[0, "product_weight_g"] == 500
