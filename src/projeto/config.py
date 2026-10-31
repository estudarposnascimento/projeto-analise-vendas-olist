from pathlib import Path

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Diretório dos dados originais
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Arquivos que serão utilizados no projeto
DATASETS = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
}

# Banco de dados SQLite
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "olist.db"
