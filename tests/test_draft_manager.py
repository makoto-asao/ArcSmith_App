import pytest
import os
import json
import tempfile
import shutil
from src.draft_manager import DraftManager


class TestDraftManager:
    """DraftManagerクラスのテスト"""
    
    @pytest.fixture
    def temp_dir(self):
        """テスト用の一時ディレクトリを作成"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def draft_manager(self, temp_dir, monkeypatch):
        """テスト用のDraftManagerインスタンスを作成"""
        # 一時ディレクトリを使用するようにモンキーパッチ
        monkeypatch.setattr(DraftManager, 'DRAFTS_DIR', temp_dir)
        return DraftManager()
    
    @pytest.fixture
    def sample_data(self):
        """テスト用のサンプルデータ"""
        return {
            "selected_title": "Test Horror Story",
            "title_en": "The Haunted House",
            "title_jp": "呪われた家",
            "description": "A scary story about a haunted house",
            "hashtags": "#horror #scary",
            "vrew_script": "This is a test script.",
            "mj_prompts_list": ["prompt1", "prompt2", "prompt3"]
        }
    
    def test_save_draft(self, draft_manager, sample_data):
        """ドラフト保存機能のテスト"""
        draft_id = draft_manager.save_draft(
            data=sample_data,
            draft_name="Test Draft",
            tags=["horror", "test"],
            memo="This is a test memo"
        )
        
        assert draft_id is not None
        assert os.path.exists(os.path.join(draft_manager.DRAFTS_DIR, f"{draft_id}.json"))
    
    def test_load_draft(self, draft_manager, sample_data):
        """ドラフト読み込み機能のテスト"""
        # まず保存
        draft_id = draft_manager.save_draft(
            data=sample_data,
            draft_name="Test Draft",
            tags=["horror"],
            memo="Test memo"
        )
        
        # 読み込み
        loaded = draft_manager.load_draft(draft_id)
        
        assert loaded is not None
        assert loaded["id"] == draft_id
        assert loaded["draft_name"] == "Test Draft"
        assert loaded["tags"] == ["horror"]
        assert loaded["memo"] == "Test memo"
        assert loaded["data"]["title_en"] == sample_data["title_en"]
    
    def test_load_nonexistent_draft(self, draft_manager):
        """存在しないドラフトの読み込みテスト"""
        loaded = draft_manager.load_draft("nonexistent-id")
        assert loaded is None
    
    def test_list_drafts(self, draft_manager, sample_data):
        """ドラフト一覧取得のテスト"""
        # 複数のドラフトを保存
        draft_manager.save_draft(sample_data, "Draft 1", tags=["horror"])
        draft_manager.save_draft(sample_data, "Draft 2", tags=["comedy"])
        draft_manager.save_draft(sample_data, "Draft 3", tags=["horror", "test"])
        
        # 全ドラフトを取得
        all_drafts = draft_manager.list_drafts()
        assert len(all_drafts) == 3
        
        # タグでフィルタリング
        horror_drafts = draft_manager.list_drafts(filter_tags=["horror"])
        assert len(horror_drafts) == 2
    
    def test_delete_draft(self, draft_manager, sample_data):
        """ドラフト削除のテスト"""
        # 保存
        draft_id = draft_manager.save_draft(sample_data, "Draft to Delete")
        
        # 削除
        result = draft_manager.delete_draft(draft_id)
        assert result is True
        
        # 削除されたことを確認
        loaded = draft_manager.load_draft(draft_id)
        assert loaded is None
    
    def test_delete_nonexistent_draft(self, draft_manager):
        """存在しないドラフトの削除テスト"""
        result = draft_manager.delete_draft("nonexistent-id")
        assert result is False
    
    def test_update_draft(self, draft_manager, sample_data):
        """ドラフト更新のテスト"""
        # 保存
        draft_id = draft_manager.save_draft(sample_data, "Original Draft", tags=["original"])
        
        # 更新
        updated_data = sample_data.copy()
        updated_data["title_en"] = "Updated Title"
        
        result = draft_manager.update_draft(
            draft_id,
            data=updated_data,
            draft_name="Updated Draft",
            tags=["updated"]
        )
        
        assert result is True
        
        # 更新されたことを確認
        loaded = draft_manager.load_draft(draft_id)
        assert loaded["draft_name"] == "Updated Draft"
        assert loaded["tags"] == ["updated"]
        assert loaded["data"]["title_en"] == "Updated Title"
    
    def test_export_draft(self, draft_manager, sample_data, temp_dir):
        """ドラフトエクスポートのテスト"""
        # 保存
        draft_id = draft_manager.save_draft(sample_data, "Export Test")
        
        # エクスポート
        export_path = os.path.join(temp_dir, "exported_draft.json")
        result = draft_manager.export_draft(draft_id, export_path)
        
        assert result is True
        assert os.path.exists(export_path)
        
        # エクスポートされたファイルの内容を確認
        with open(export_path, "r", encoding="utf-8") as f:
            exported = json.load(f)
        
        assert exported["id"] == draft_id
        assert exported["draft_name"] == "Export Test"
    
    def test_import_draft(self, draft_manager, sample_data, temp_dir):
        """ドラフトインポートのテスト"""
        # まずエクスポート用のドラフトを作成
        original_id = draft_manager.save_draft(sample_data, "Import Test")
        export_path = os.path.join(temp_dir, "to_import.json")
        draft_manager.export_draft(original_id, export_path)
        
        # インポート
        new_id = draft_manager.import_draft(export_path)
        
        assert new_id is not None
        assert new_id != original_id  # 新しいIDが生成される
        
        # インポートされたドラフトを確認
        loaded = draft_manager.load_draft(new_id)
        assert loaded["draft_name"] == "Import Test"
        assert loaded["data"]["title_en"] == sample_data["title_en"]
    
    def test_draft_sorting(self, draft_manager, sample_data):
        """ドラフトが更新日時の降順でソートされることをテスト"""
        import time
        
        # 複数のドラフトを時間差で保存
        draft_manager.save_draft(sample_data, "Draft 1")
        time.sleep(0.1)
        draft_manager.save_draft(sample_data, "Draft 2")
        time.sleep(0.1)
        draft_manager.save_draft(sample_data, "Draft 3")
        
        drafts = draft_manager.list_drafts()
        
        # 最新のものが最初に来る
        assert drafts[0]["draft_name"] == "Draft 3"
        assert drafts[1]["draft_name"] == "Draft 2"
        assert drafts[2]["draft_name"] == "Draft 1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
