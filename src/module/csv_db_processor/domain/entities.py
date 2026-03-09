from dataclasses import dataclass
from typing import List, Literal, Self, Union


@dataclass(frozen=True)
class CSVConfig:
    """
    CSVファイルのメタデータを保持する値オブジェクト。
    ファイル名、テーブル名、エンコーディングという不変の組み合わせを定義します。
    frozen=True により不変性が保証されます。
    """
    file_name: str
    table_name: str
    encoding: Literal["utf-16", "utf-8-sig"]  # 想定されるエンコーディングをLiteralで厳密に指定


@dataclass(frozen=True)
class DbFileUpdateStatus:
    """
    DBファイルが更新されるべきかどうかを判断し、その状態を保持する値オブジェクト。
    """
    needs_update: bool
    reason: str

    @classmethod
    def create(cls, db_modified_time: Union[float, None], latest_csv_time: float) -> Self:
        """
        DBファイルとCSVファイルの更新日時を比較し、DbFileUpdateStatusオブジェクトを生成します。

        Args:
            db_modified_time: DBファイルの最終更新日時 (Unixタイムスタンプ)。存在しない場合は None。
            latest_csv_time: 全てのCSVファイルの中で最も新しい最終更新日時 (Unixタイムスタンプ)。

        Returns:
            DbFileUpdateStatus: 更新の要否と理由を示すオブジェクト。
        """
        if db_modified_time is None:
            return cls(needs_update=True, reason="DBファイルが存在しないため、新規作成します。")
        elif db_modified_time < latest_csv_time:
            return cls(needs_update=True, reason="DBファイルがCSVファイルよりも古いため、更新します。")
        else:
            return cls(needs_update=False, reason="DBファイルが最新のため、更新不要です。")