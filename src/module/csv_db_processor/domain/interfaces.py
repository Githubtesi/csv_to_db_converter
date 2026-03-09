import pandas as pd
import sqlite3

from typing import List, Optional, Protocol, Union


# 仮のドメインモデル定義
# 後でentities.pyに移動します
class SimpleProduct(Protocol):
    product_code: str
    product_name: str
    supplier: str
    supplier_code: str
    customer: str
    customer_code: str


# 仮のドメインモデル定義
# 後でentities.pyに移動します
class EnvironmentalResearchItem(Protocol):
    product_code: str
    product_name: str
    customer: str
    supplier: str
    supplier_mail_addresses: str
    person_in_charge: str

class IEnvironmentalResearchRepository(Protocol):
    """
    環境調査情報ドメインモデルの永続化（読み込み）を抽象化するインターフェース。
    """
    def find_all_environmental_research_items(self) -> List[EnvironmentalResearchItem]:
        """全てのEnvironmentalResearchItemをDBから取得します。"""
        ...

    def find_environmental_research_item_by_product_code(self, product_code: str) -> Optional[EnvironmentalResearchItem]:
        """商品コードでEnvironmentalResearchItemを検索します。"""
        ...


class IProductRepository(Protocol):
    """
    商品ドメインモデルの永続化（読み込み）を抽象化するインターフェース。
    """

    def find_all_simple_products(self) -> List[SimpleProduct]:
        """全てのSimpleProductをDBから取得します。"""
        ...

    def find_simple_product_by_code(self, product_code: str) -> Optional[SimpleProduct]:
        """商品コードでSimpleProductを検索します。"""


class ILogger(Protocol):
    """
    ロギング操作を抽象化するインターフェース。
    インフラストラクチャ層で具体的なロギングライブラリ（Pythonのloggingモジュールなど）の実装を提供します。
    """

    def error(self, message: str, *args, **kwargs) -> None:
        """エラーメッセージをログに出力します。"""
        ...

    def warning(self, message: str, *args, **kwargs) -> None:
        """警告メッセージをログに出力します。"""
        ...

    def info(self, message: str, *args, **kwargs) -> None:
        """情報メッセージをログに出力します。"""
        ...

    def debug(self, message: str, *args, **kwargs) -> None:
        """デバッグメッセージをログに出力します。"""
        ...


class CsvConfig(Protocol):
    """
    CSVファイルのメタデータを保持する値オブジェクトのインターフェース。
    ドメイン層で利用されるCSV設定の抽象表現を提供します。
    """
    file_name: str
    table_name: str
    encoding: str


class ICsvRepository(Protocol):
    """
    CSVファイルへのデータアクセスを抽象化するインターフェース。
    インフラストラクチャ層でPandasなどを用いた具体的な実装を提供します。
    """

    def get_csv_file_path(self, base_path: str, file_name: str) -> str:
        """指定されたベースパスとファイル名からCSVファイルの絶対パスを返します。"""
        ...

    def get_latest_modification_time(self, csv_configs: List[CsvConfig], base_path: str) -> float:
        """
        指定されたCSV設定リスト内の全てのCSVファイルの中から、
        最も新しい更新日時（Unixタイムスタンプ）を返します。
        ファイルが存在しない場合は CsvFileError を発生させます。
        """
        ...

    def read_csv_to_dataframe(self, file_path: str, encoding: str) -> pd.DataFrame:
        """
        指定されたパスとエンコーディングでCSVファイルを読み込み、Pandas DataFrameを返します。
        ファイルの読み込みに失敗した場合は CsvFileError を発生させます。
        """
        ...


class IDbRepository(Protocol):
    """
    SQLiteデータベースへのデータアクセスと操作を抽象化するインターフェース。
    インフラストラクチャ層でsqlite3モジュールを用いた具体的な実装を提供します。
    """

    def connect(self, db_path: str) -> sqlite3.Connection:
        """
        指定されたパスのSQLiteデータベースに接続し、コネクションオブジェクトを返します。
        接続に失敗した場合は DbConnectionError を発生させます。
        """
        ...

    def close(self, conn: sqlite3.Connection) -> None:
        """
        指定されたデータベースコネクションを閉じます。
        """
        ...

    def create_table_from_dataframe(self, conn: sqlite3.Connection, df: pd.DataFrame, table_name: str) -> None:
        """
        Pandas DataFrameから指定されたテーブル名でデータベースにテーブルを作成または上書きします。
        操作に失敗した場合は DbOperationError を発生させます。
        """
        ...

    def execute_query(self, conn: sqlite3.Connection, query: str) -> None:
        """
        指定されたSQLクエリを実行し、トランザクションをコミットします。
        クエリの実行に失敗した場合は DbOperationError を発生させます。
        """
        ...

    def get_db_modification_time(self, db_path: str) -> Union[float, None]:
        """
        指定されたDBファイルの最終更新日時（Unixタイムスタンプ）を返します。
        ファイルが存在しない場合は None を返します。
        """
        ...


class IDbBrowserLauncher(Protocol):
    """
    DB Browser for SQLiteアプリケーションの起動を抽象化するインターフェース。
    インフラストラクチャ層でsubprocessモジュールを用いた具体的な実装を提供します。
    """

    def launch(self, application_path: str, db_file_path: str, is_read_only:bool) -> None:
        """
        指定されたDBファイルでDB Browser for SQLiteアプリケーションを起動します。
        起動に失敗した場合は DbBrowserLaunchError を発生させます。
        """
        ...
