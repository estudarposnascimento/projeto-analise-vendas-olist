
import sqlite3

import pandas as pd

from projeto.config import DATABASE_PATH


def read_bronze(
    connection: sqlite3.Connection,
    table_name: str,
) -> pd.DataFrame:
    """Lê uma tabela Bronze do SQLite."""

    return pd.read_sql_query(
        f"SELECT * FROM {table_name}",
        connection,
        dtype="string",
    )


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma os dados dos pedidos."""

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    df = df.copy()

    for column in date_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
        )

    df["order_status"] = (
        df["order_status"]
        .str.strip()
        .str.lower()
    )

    return df


def transform_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma os dados dos itens dos pedidos."""

    df = df.copy()

    df["order_item_id"] = pd.to_numeric(
        df["order_item_id"],
        errors="coerce",
    ).astype("Int64")

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce",
    )

    df["freight_value"] = pd.to_numeric(
        df["freight_value"],
        errors="coerce",
    )

    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"],
        errors="coerce",
    )

    return df


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    """Transforma os dados dos produtos."""

    df = df.copy()

    numeric_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        ).astype("Int64")

    df["product_category_name"] = (
        df["product_category_name"]
        .str.strip()
        .str.lower()
        .fillna("nao_informado")
    )

    return df


def get_sql_types(
    dataframe: pd.DataFrame,
    table_name: str,
) -> dict:
    """Define os tipos de armazenamento no SQLite."""

    types = {
        column: "TEXT"
        for column in dataframe.columns
    }

    if table_name == "silver_orders":

        date_columns = [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ]

        for column in date_columns:
            types[column] = "DATETIME"

    elif table_name == "silver_order_items":

        types["order_item_id"] = "INTEGER"
        types["price"] = "REAL"
        types["freight_value"] = "REAL"
        types["shipping_limit_date"] = "DATETIME"

    elif table_name == "silver_products":

        numeric_columns = [
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ]

        for column in numeric_columns:
            types[column] = "INTEGER"

    return types


def load_silver(
    dataframe: pd.DataFrame,
    table_name: str,
    connection: sqlite3.Connection,
) -> None:
    """Carrega os dados transformados na camada Silver."""

    dataframe.to_sql(
        name=table_name,
        con=connection,
        if_exists="replace",
        index=False,
        dtype=get_sql_types(dataframe, table_name),
    )

    print(
        f"{table_name}: "
        f"{len(dataframe):,} registros carregados"
    )


def run_silver() -> None:
    """Executa a transformação e carga Silver."""

    transformations = {
        "orders": (
            "bronze_orders",
            "silver_orders",
            transform_orders,
        ),
        "order_items": (
            "bronze_order_items",
            "silver_order_items",
            transform_order_items,
        ),
        "products": (
            "bronze_products",
            "silver_products",
            transform_products,
        ),
    }

    with sqlite3.connect(DATABASE_PATH) as connection:

        for (
            dataset_name,
            (source_table, target_table, transform_function),
        ) in transformations.items():

            print(f"\nProcessando: {dataset_name}")

            dataframe = read_bronze(
                connection,
                source_table,
            )

            transformed = transform_function(dataframe)

            load_silver(
                transformed,
                target_table,
                connection,
            )

    print("\nCamada Silver concluída!")


if __name__ == "__main__":
    run_silver()
