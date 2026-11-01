
import pandas as pd
import pytest

import projeto.extract as extract_module

from projeto.extract import (
    extract_dataset,
    inspect_dataset,
)


def test_extract_dataset_orders(tmp_path, monkeypatch):
    """Testa a extração de um CSV de pedidos."""

    csv_file = tmp_path / "orders.csv"

    csv_file.write_text(
        "order_id,order_status\n"
        "001,delivered\n"
        "002,canceled\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        extract_module,
        "RAW_DATA_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        extract_module,
        "DATASETS",
        {"orders": "orders.csv"},
    )

    result = extract_dataset("orders")

    assert len(result) == 2
    assert list(result.columns) == [
        "order_id",
        "order_status",
    ]

    assert result.loc[0, "order_id"] == "001"
    assert result.loc[1, "order_status"] == "canceled"

    # Confirma que os dados foram lidos como texto.
    assert all(
        dtype == "string"
        for dtype in result.dtypes
    )


def test_extract_dataset_invalid_name():
    """Testa o comportamento para dataset desconhecido."""

    with pytest.raises(
        ValueError,
        match="Dataset não reconhecido",
    ):
        extract_dataset("dataset_inexistente")


def test_extract_dataset_file_not_found(tmp_path, monkeypatch):
    """Testa o comportamento quando o CSV não existe."""

    monkeypatch.setattr(
        extract_module,
        "RAW_DATA_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        extract_module,
        "DATASETS",
        {"orders": "arquivo_inexistente.csv"},
    )

    with pytest.raises(
        FileNotFoundError,
        match="Arquivo não encontrado",
    ):
        extract_dataset("orders")


def test_extract_dataset_preserves_leading_zeros(tmp_path, monkeypatch):
    """Verifica se códigos com zeros à esquerda são preservados."""

    csv_file = tmp_path / "products.csv"

    csv_file.write_text(
        "product_id\n"
        "00123\n"
        "00045\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        extract_module,
        "RAW_DATA_DIR",
        tmp_path,
    )

    monkeypatch.setattr(
        extract_module,
        "DATASETS",
        {"products": "products.csv"},
    )

    result = extract_dataset("products")

    assert result.loc[0, "product_id"] == "00123"
    assert result.loc[1, "product_id"] == "00045"


def test_inspect_dataset(capsys):
    """Testa a inspeção e a saída no terminal."""

    df = pd.DataFrame({
        "order_id": ["001", "002", "002"],
        "order_status": [
            "delivered",
            "canceled",
            "canceled",
        ],
    })

    inspect_dataset(df, "orders")

    output = capsys.readouterr().out

    assert "ANÁLISE DO DATASET: ORDERS" in output
    assert "Quantidade de registros: 3" in output
    assert "Quantidade de colunas: 2" in output
    assert "Registros totalmente duplicados: 1" in output
    assert "order_id" in output
    assert "order_status" in output


def test_inspect_dataset_with_null_values(capsys):
    """Verifica se a inspeção apresenta valores nulos."""

    df = pd.DataFrame({
        "product_id": ["001", None],
        "product_category_name": ["cama_banho", None],
    })

    inspect_dataset(df, "products")

    output = capsys.readouterr().out

    assert "VALORES NULOS" in output
    assert "product_id" in output
    assert "product_category_name" in output


def test_inspect_dataset_empty_dataframe(capsys):
    """Testa a inspeção de um DataFrame vazio."""

    df = pd.DataFrame(
        columns=["order_id", "order_status"]
    )

    inspect_dataset(df, "orders")

    output = capsys.readouterr().out

    assert "Quantidade de registros: 0" in output
    assert "Quantidade de colunas: 2" in output


def test_inspect_dataset_without_columns(capsys):
    """Testa a inspeção de um DataFrame sem colunas."""

    df = pd.DataFrame()

    inspect_dataset(df, "vazio")

    output = capsys.readouterr().out

    assert "Quantidade de registros: 0" in output
    assert "Quantidade de colunas: 0" in output
