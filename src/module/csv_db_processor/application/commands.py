from dataclasses import dataclass
from typing import List

from src.module.csv_db_processor.domain.entities import CSVConfig


@dataclass(frozen=True)
class DatabaseUpdateCommand:
    """
    データベース更新処理を開始するためのコマンド（入力データ転送オブジェクト）。
    アプリケーション層のサービスに渡される、処理に必要な全ての情報をカプセル化します。
    frozen=True により不変性が保証されます。
    """
    server_csv_dir_path: str
    db_file_path: str
    smile_csv_configs: List[CSVConfig]
    my_csv_configs: List[CSVConfig]
    db_browser_app_path: str
    create_simple_product_master_view_query: str
    create_environmental_research_view_query: str