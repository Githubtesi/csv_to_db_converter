import os
import pandas as pd
from typing import List

from src.module.csv_db_processor.domain.entities import CSVConfig
from src.module.csv_db_processor.domain.interfaces import ICsvRepository
from src.module.shared.exceptions import CsvFileError


class CsvPandasRepository(ICsvRepository):
    """
    Pandasライブラリを使用してCSVファイルへのデータアクセスを実装するリポジトリ。
    ICsvRepositoryインターフェースを実装します。
    """

    def get_csv_file_path(self, base_path: str, file_name: str) -> str:
        """
        指定されたベースパスとファイル名からCSVファイルの絶対パスを返します。
        """
        return os.path.join(base_path, file_name)

    def get_latest_modification_time(self, csv_configs: List[CSVConfig], base_path: str) -> float:
        """
        指定されたCSV設定リスト内の全てのCSVファイルの中から、
        最も新しい更新日時（Unixタイムスタンプ）を返します。
        ファイルが存在しない場合は CsvFileError を発生させます。
        """
        csv_update_unix_time: List[float] = []
        for csv_config in csv_configs:
            target_csv_path = self.get_csv_file_path(base_path, csv_config.file_name)

            if not os.path.exists(target_csv_path):
                raise CsvFileError(f"CSVファイルが見つかりません: {target_csv_path}")

            update_date_unix_time = os.path.getmtime(target_csv_path)
            csv_update_unix_time.append(update_date_unix_time)

        if not csv_update_unix_time:
            raise CsvFileError("処理対象のCSVファイルが指定されていません。")

        return max(csv_update_unix_time)

    def read_csv_to_dataframe(self, file_path: str, encoding: str) -> pd.DataFrame:
        """
        指定されたパスとエンコーディングでCSVファイルを読み込み、Pandas DataFrameを返します。
        ファイルの読み込みに失敗した場合は CsvFileError を発生させます。
        """
        try:
            # low_memory=Falseは削除するという要件があったため、ここでは指定しない
            # ただし、大きなファイルを扱う際にはメモリ消費に注意が必要
            return pd.read_csv(file_path, encoding=encoding)
        except FileNotFoundError:
            raise CsvFileError(f"CSVファイルが見つかりません: {file_path}")
        except Exception as e:
            raise CsvFileError(f"CSVファイル '{file_path}' の読み込み中にエラーが発生しました: {e}")