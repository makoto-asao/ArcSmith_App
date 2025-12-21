import gspread
from src.config import Config
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SheetsHandler:
    def __init__(self):
        try:
            Config.validate()
            self.gc = gspread.service_account(filename=Config.GOOGLE_APPLICATION_CREDENTIALS)
            self.sh = self.gc.open_by_key(Config.SPREADSHEET_ID)
            self.worksheet = self.sh.worksheet("データ") # 「データ」という名前のタブを使用
            logger.info("Successfully connected to Google Sheets and opened 'データ' worksheet.")
        except Exception as e:
            logger.error(f"Failed to initialize SheetsHandler: {e}")
            raise ConnectionError(f"スプレッドシートの接続に失敗しました: {e}")

    def get_all_titles(self):
        """A列（タイトル）を取得（1行目のヘッダーは除外）"""
        try:
            titles = self.worksheet.col_values(1)
            return titles[1:] if len(titles) > 1 else []
        except Exception as e:
            logger.error(f"Error getting titles: {e}")
            return []

    def append_new_titles(self, titles):
        """新しいネタをA列に追加"""
        try:
            rows = [[title] for title in titles]
            self.worksheet.append_rows(rows)
            logger.info(f"Appended {len(titles)} new titles.")
        except Exception as e:
            logger.error(f"Error appending titles: {e}")
            raise

    def get_unprocessed_row(self):
        """完了フラグ（D列）が空の行を検索"""
        try:
            all_records = self.worksheet.get_all_values()
            if not all_records:
                return None, None
                
            for i, row in enumerate(all_records, start=1):
                if i == 1: continue # ヘッダーをスキップ
                
                # row[3] はD列 (0-indexed)
                # 列が不足している場合や空の場合を未処理とみなす
                if len(row) < 4 or not row[3]:
                    return i, row
            return None, None
        except Exception as e:
            logger.error(f"Error looking for unprocessed rows: {e}")
            return None, None

    def update_row_data(self, row_index, script, prompt):
        """B列（台本）とC列（プロンプト）を更新"""
        try:
            self.worksheet.update_cell(row_index, 2, script) # B列
            self.worksheet.update_cell(row_index, 3, prompt) # C列
            logger.info(f"Updated data for row {row_index}.")
        except Exception as e:
            logger.error(f"Error updating row {row_index}: {e}")
            raise

    def mark_as_completed(self, row_index):
        """D列（完了）とE列（作成日）を更新"""
        try:
            import datetime
            today = datetime.date.today().isoformat()
            self.worksheet.update_cell(row_index, 4, "完了") # D列
            self.worksheet.update_cell(row_index, 5, today)  # E列
            logger.info(f"Marked row {row_index} as completed on {today}.")
        except Exception as e:
            logger.error(f"Error marking row {row_index} as completed: {e}")
            raise
