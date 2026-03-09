import os
from typing import List

from src.module.csv_db_processor.domain.entities import CSVConfig

# DB Browser for SQLiteのパス
LOCAL_APPLICATION_PATH: str = r"C:\Program Files\DB Browser for SQLite\DB Browser for SQLite.exe"

# smileから出力されるフォルダ (共有フォルダ)
SERVER_CSV_DIR_PATH: str = r"\\IRS5\irs5_public\個人用フォルダ\Smile_db\csv\from_smile"

# DBファイル名
DB_FILE_NAME: str = "smile_master.db"

# DBファイルのフルパス
SERVER_TARGET_DB_PATH: str = os.path.join(SERVER_CSV_DIR_PATH, DB_FILE_NAME)

# smileのCSV設定リスト
SMILE_CSV_CONFIGS: List[CSVConfig] = [
    CSVConfig(file_name="zyutuu_simle.csv", table_name="zyutuu_simle", encoding="utf-16"),
    CSVConfig(file_name="product_master.csv", table_name="product_master", encoding="utf-16"),
    CSVConfig(file_name="shiire_list_smile.csv", table_name="shiire_list_smile", encoding="utf-16"),
    CSVConfig(file_name="hattyuu_list_smile.csv", table_name="hattyuu_list_smile", encoding="utf-16"),
    CSVConfig(file_name="uriage_list_smile.csv", table_name="uriage_list_smile", encoding="utf-16"),
]

# 自作のCSV設定リスト
MY_CSV_CONFIGS: List[CSVConfig] = [
    CSVConfig(file_name="environmental_research.csv", table_name="environmental_research", encoding="utf-8-sig"),
]

# ビュー作成クエリ (定数として定義)
CREATE_SIMPLE_PRODUCT_MASTER_VIEW_QUERY: str = """
      CREATE VIEW IF NOT EXISTS simple_product_master
      AS
      SELECT product_master.商品ｺｰﾄﾞ     AS product_code,
             product_master.商品略称     AS product_name,
             product_master.主仕入先名   AS supplier,
             product_master.主仕入先ｺｰﾄﾞ AS supplier_code,
             product_master.得意先名     AS customer,
             product_master.得意先ｺｰﾄﾞ   AS customer_code
      from product_master;
"""

CREATE_ENVIRONMENTAL_RESEARCH_VIEW_QUERY: str = """
       CREATE VIEW IF NOT EXISTS '環境調査'
       AS
       SELECT simple_product_master.product_code,
              simple_product_master.product_name,
              simple_product_master.customer,
              simple_product_master.supplier,
              environmental_research.supplier_mail_addresses,
              environmental_research.person_in_charge
       FROM simple_product_master
                LEFT OUTER JOIN environmental_research
                                ON simple_product_master.supplier = environmental_research.supplier;
"""

# エラーログファイル名
ERROR_LOG_FILE_NAME: str = "error.log"


# 読み込み専用
IS_READ_ONLY = False