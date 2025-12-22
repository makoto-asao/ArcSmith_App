import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DraftManager:
    """モードBのドラフトデータを管理するクラス"""
    
    DRAFTS_DIR = os.path.join("data", "saved_scripts")
    
    def __init__(self):
        """ドラフト保存ディレクトリを初期化"""
        os.makedirs(self.DRAFTS_DIR, exist_ok=True)
        logger.info(f"DraftManager initialized. Drafts directory: {self.DRAFTS_DIR}")
    
    def save_draft(self, data: Dict[str, Any], draft_name: str, 
                   tags: Optional[List[str]] = None, memo: Optional[str] = None) -> str:
        """
        ドラフトを保存
        
        Args:
            data: 保存するデータ(title_en, title_jp, description, hashtags, vrew_script, mj_prompts_list等)
            draft_name: ドラフトの名前
            tags: タグのリスト(オプション)
            memo: メモ(オプション)
            
        Returns:
            str: 保存されたドラフトのID
        """
        try:
            draft_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            draft = {
                "id": draft_id,
                "draft_name": draft_name,
                "created_at": now,
                "updated_at": now,
                "tags": tags or [],
                "memo": memo or "",
                "data": data
            }
            
            file_path = os.path.join(self.DRAFTS_DIR, f"{draft_id}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(draft, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Draft saved: {draft_name} (ID: {draft_id})")
            return draft_id
            
        except Exception as e:
            logger.error(f"Error saving draft: {e}")
            raise
    
    def load_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """
        ドラフトを読み込み
        
        Args:
            draft_id: ドラフトのID
            
        Returns:
            Dict: ドラフトデータ、存在しない場合はNone
        """
        try:
            file_path = os.path.join(self.DRAFTS_DIR, f"{draft_id}.json")
            
            if not os.path.exists(file_path):
                logger.warning(f"Draft not found: {draft_id}")
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                draft = json.load(f)
            
            logger.info(f"Draft loaded: {draft.get('draft_name')} (ID: {draft_id})")
            return draft
            
        except Exception as e:
            logger.error(f"Error loading draft {draft_id}: {e}")
            return None
    
    def list_drafts(self, filter_tags: Optional[List[str]] = None, 
                    limit: Optional[int] = None, 
                    offset: int = 0) -> List[Dict[str, Any]]:
        """
        保存済みドラフトの一覧を取得（ページネーション対応）
        
        Args:
            filter_tags: フィルタリングするタグのリスト(オプション)
            limit: 取得する最大件数(オプション、Noneの場合は全件)
            offset: スキップする件数(ページネーション用)
            
        Returns:
            List[Dict]: ドラフトのメタデータリスト(データ本体は含まない)
        """
        try:
            drafts = []
            
            if not os.path.exists(self.DRAFTS_DIR):
                return drafts
            
            # ファイル一覧を取得してソート（更新日時順）
            files = []
            for filename in os.listdir(self.DRAFTS_DIR):
                if not filename.endswith(".json"):
                    continue
                file_path = os.path.join(self.DRAFTS_DIR, filename)
                mtime = os.path.getmtime(file_path)
                files.append((filename, mtime))
            
            # 更新日時の降順でソート
            files.sort(key=lambda x: x[1], reverse=True)
            
            # ページネーション適用
            if limit is not None:
                files = files[offset:offset + limit]
            else:
                files = files[offset:]
            
            # メタデータのみを読み込み（軽量化）
            for filename, _ in files:
                file_path = os.path.join(self.DRAFTS_DIR, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        draft = json.load(f)
                    
                    # タグフィルタリング
                    if filter_tags:
                        draft_tags = set(draft.get("tags", []))
                        if not any(tag in draft_tags for tag in filter_tags):
                            continue
                    
                    # メタデータのみを含める
                    draft_meta = {
                        "id": draft.get("id"),
                        "draft_name": draft.get("draft_name"),
                        "created_at": draft.get("created_at"),
                        "updated_at": draft.get("updated_at"),
                        "tags": draft.get("tags", []),
                        "memo": draft.get("memo", ""),
                        "title_en": draft.get("data", {}).get("title_en", ""),
                        "title_jp": draft.get("data", {}).get("title_jp", "")
                    }
                    drafts.append(draft_meta)
                    
                except Exception as e:
                    logger.warning(f"Error reading draft file {filename}: {e}")
                    continue
            
            logger.info(f"Listed {len(drafts)} drafts (offset: {offset}, limit: {limit})")
            return drafts
            
        except Exception as e:
            logger.error(f"Error listing drafts: {e}")
            return []
    
    def count_drafts(self, filter_tags: Optional[List[str]] = None) -> int:
        """
        ドラフトの総数を取得（ページネーション用）
        
        Args:
            filter_tags: フィルタリングするタグのリスト(オプション)
            
        Returns:
            int: ドラフトの総数
        """
        try:
            if not os.path.exists(self.DRAFTS_DIR):
                return 0
            
            count = 0
            for filename in os.listdir(self.DRAFTS_DIR):
                if not filename.endswith(".json"):
                    continue
                
                if filter_tags:
                    file_path = os.path.join(self.DRAFTS_DIR, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            draft = json.load(f)
                        draft_tags = set(draft.get("tags", []))
                        if any(tag in draft_tags for tag in filter_tags):
                            count += 1
                    except:
                        continue
                else:
                    count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error counting drafts: {e}")
            return 0
    
    def delete_draft(self, draft_id: str) -> bool:
        """
        ドラフトを削除
        
        Args:
            draft_id: ドラフトのID
            
        Returns:
            bool: 削除成功時True、失敗時False
        """
        try:
            file_path = os.path.join(self.DRAFTS_DIR, f"{draft_id}.json")
            
            if not os.path.exists(file_path):
                logger.warning(f"Draft not found for deletion: {draft_id}")
                return False
            
            os.remove(file_path)
            logger.info(f"Draft deleted: {draft_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting draft {draft_id}: {e}")
            return False
    
    def update_draft(self, draft_id: str, data: Dict[str, Any], 
                     draft_name: Optional[str] = None,
                     tags: Optional[List[str]] = None, 
                     memo: Optional[str] = None) -> bool:
        """
        既存のドラフトを更新
        
        Args:
            draft_id: ドラフトのID
            data: 更新するデータ
            draft_name: 新しいドラフト名(オプション)
            tags: 新しいタグのリスト(オプション)
            memo: 新しいメモ(オプション)
            
        Returns:
            bool: 更新成功時True、失敗時False
        """
        try:
            draft = self.load_draft(draft_id)
            if not draft:
                return False
            
            # 更新
            draft["updated_at"] = datetime.now().isoformat()
            draft["data"] = data
            
            if draft_name is not None:
                draft["draft_name"] = draft_name
            if tags is not None:
                draft["tags"] = tags
            if memo is not None:
                draft["memo"] = memo
            
            # 保存
            file_path = os.path.join(self.DRAFTS_DIR, f"{draft_id}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(draft, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Draft updated: {draft.get('draft_name')} (ID: {draft_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error updating draft {draft_id}: {e}")
            return False
    
    def export_draft(self, draft_id: str, output_path: str) -> bool:
        """
        ドラフトをエクスポート
        
        Args:
            draft_id: ドラフトのID
            output_path: 出力ファイルパス
            
        Returns:
            bool: エクスポート成功時True、失敗時False
        """
        try:
            draft = self.load_draft(draft_id)
            if not draft:
                return False
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(draft, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Draft exported: {draft.get('draft_name')} to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting draft {draft_id}: {e}")
            return False
    
    def import_draft(self, input_path: str) -> Optional[str]:
        """
        ドラフトをインポート
        
        Args:
            input_path: インポートするファイルパス
            
        Returns:
            str: インポートされたドラフトのID、失敗時None
        """
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                draft = json.load(f)
            
            # 新しいIDを生成
            new_id = str(uuid.uuid4())
            draft["id"] = new_id
            draft["updated_at"] = datetime.now().isoformat()
            
            # 保存
            file_path = os.path.join(self.DRAFTS_DIR, f"{new_id}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(draft, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Draft imported: {draft.get('draft_name')} (New ID: {new_id})")
            return new_id
            
        except Exception as e:
            logger.error(f"Error importing draft from {input_path}: {e}")
            return None
