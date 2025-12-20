import gspread
from src.config import Config

class SheetsHandler:
    def __init__(self):
        self.gc = gspread.service_account(filename=Config.GOOGLE_APPLICATION_CREDENTIALS)
        self.sh = self.gc.open_by_key(Config.SPREADSHEET_ID)
        self.worksheet = self.sh.get_worksheet(0) # 1枚目のシートを使用

    def get_all_titles(self):
        """A列（タイトル）を取得"""
        return self.worksheet.col_values(1)

    def append_new_titles(self, titles):
        """新しいネタをA列に追加"""
        rows = [[title] for title in titles]
        self.worksheet.append_rows(rows)

    def get_unprocessed_row(self):
        """完了フラグ（D列）が空の行を検索"""
        all_records = self.worksheet.get_all_values()
        for i, row in enumerate(all_records, start=1):
            if i == 1: continue # ヘッダーをスキップ
            # row[3] はD列 (0-indexed)
            if len(row) < 4 or not row[3]:
                return i, row
        return None, None

    def update_row_data(self, row_index, script, prompt):
        """B列（台本）とC列（プロンプト）を更新"""
        self.worksheet.update_cell(row_index, 2, script) # B列
        self.worksheet.update_cell(row_index, 3, prompt) # C列

    def mark_as_completed(self, row_index):
        """D列（完了）とE列（作成日）を更新"""
        import datetime
        today = datetime.date.today().isoformat()
        self.worksheet.update_cell(row_index, 4, "完了") # D列
        self.worksheet.update_cell(row_index, 5, today)  # E列
