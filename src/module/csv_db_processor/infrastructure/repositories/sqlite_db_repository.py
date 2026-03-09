import os
import sqlite3
import pandas as pd
from typing import Union

from src.module.csv_db_processor.domain.interfaces import IDbRepository
from src.module.shared.exceptions import DbConnectionError, DbOperationError


class SqliteDbRepository(IDbRepository):
    """
    sqlite3モジュールを使用してSQLiteデータベースへのデータアクセスを実装するリポジトリ。
    IDbRepositoryインターフェースを実装します。
    """
    def connect(self, db_path: str) -> sqlite3.Connection:
        """
        指定されたパスのSQLiteデータベースに接続し、コネクションオブジェクトを返します。
        接続に失敗した場合は DbConnectionError を発生させます。
        """
        try:
            conn = sqlite3.connect(db_path)
            # パフォーマンス向上のため、ジャーナルモードをWALに設定することが多い
            # conn.execute("PRAGMA journal_mode=WAL;")
            return conn
        except sqlite3.Error as e:
            raise DbConnectionError(f"データベース '{db_path}' への接続に失敗しました: {e}")

    def close(self, conn: sqlite3.Connection) -> None:
        """
        指定されたデータベースコネクションを閉じます。
        """
        if conn:
            conn.close()

    def create_table_from_dataframe(self, conn: sqlite3.Connection, df: pd.DataFrame, table_name: str) -> None:
        """
        Pandas DataFrameから指定されたテーブル名でデータベースにテーブルを作成または上書きします。
        操作に失敗した場合は DbOperationError を発生させます。
        """
        try:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback() # エラー時はロールバック
            raise DbOperationError(f"テーブル '{table_name}' の作成に失敗しました: {e}")

    def execute_query(self, conn: sqlite3.Connection, query: str) -> None:
        """
        指定されたSQLクエリを実行し、トランザクションをコミットします。
        クエリの実行に失敗した場合は DbOperationError を発生させます。
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback() # エラー時はロールバック
            raise DbOperationError(f"SQLクエリの実行に失敗しました: {query[:100]}...。エラー: {e}")

    def get_db_modification_time(self, db_path: str) -> Union[float, None]:
        """
        指定されたDBファイルの最終更新日時（Unixタイムスタンプ）を返します。
        ファイルが存在しない場合は None を返します。
        """
        if not os.path.exists(db_path):
            return None
        try:
            return os.path.getmtime(db_path)
        except OSError as e:
            raise DbOperationError(f"DBファイル '{db_path}' の更新日時取得に失敗しました: {e}")