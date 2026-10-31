
import pandas as pd

from projeto.config import DATASETS, RAW_DATA_DIR


def extract_dataset(dataset_name: str) -> pd.DataFrame:
    """
    Extrai um arquivo CSV da pasta data/raw.

    Os dados são lidos como texto para preservar
    os valores originais durante a extração.
    """

    if dataset_name not in DATASETS:
        raise ValueError(
            f"Dataset não reconhecido: {dataset_name}"
        )

    file_path = RAW_DATA_DIR / DATASETS[dataset_name]

    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {file_path}"
        )

    dataframe = pd.read_csv(
        file_path,
        dtype="string",
        encoding="utf-8",
    )

    return dataframe


def inspect_dataset(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> None:
    """
    Apresenta informações básicas sobre o dataset.
    """

    print("\n" + "=" * 60)
    print(f"ANÁLISE DO DATASET: {dataset_name.upper()}")
    print("=" * 60)

    print(f"\nQuantidade de registros: {len(dataframe):,}")
    print(f"Quantidade de colunas: {len(dataframe.columns)}")

    print("\nCOLUNAS:")
    print(dataframe.columns.tolist())

    print("\nTIPOS DE DADOS:")
    print(dataframe.dtypes)

    print("\nVALORES NULOS:")
    print(dataframe.isnull().sum())

    print(
        f"\nRegistros totalmente duplicados: "
        f"{dataframe.duplicated().sum()}"
    )

    print("\nPRIMEIROS REGISTROS:")
    print(dataframe.head())


def main() -> None:
    """
    Executa a extração e inspeção dos três datasets.
    """

    for dataset_name in DATASETS:
        dataframe = extract_dataset(dataset_name)

        inspect_dataset(
            dataframe,
            dataset_name,
        )


if __name__ == "__main__":
    main()
