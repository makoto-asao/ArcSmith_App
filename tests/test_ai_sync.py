import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock google.generativeai before importing src.ai_generator if it has top-level side effects
# (It doesn't seem to, but good practice if imports fail)
sys.modules['google.generativeai'] = MagicMock()

from src.ai_generator import AIGenerator

class TestAISync:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Patch genai.configure and GenerativeModel in the class where they are used
        with patch('src.ai_generator.genai') as mock_genai:
            self.mock_genai = mock_genai
            self.ai = AIGenerator() 
            yield

    def test_sync_perfect_match(self):
        """正常系: 数が一致している場合"""
        script = ["Line 1", "Line 2", "Line 3"]
        prompts = [
            {"scene": 1, "prompt": "Prompt 1"},
            {"scene": 2, "prompt": "Prompt 2"},
            {"scene": 3, "prompt": "Prompt 3"}
        ]
        title = "Test Title"
        
        # _fix_sync_issues is an instance method
        fixed = self.ai._fix_sync_issues(script, prompts, title)
        assert len(fixed) == 3
        assert fixed[0]["prompt"] == "Prompt 1"

    def test_sync_extra_intro_prompt(self):
        """異常系: プロンプトが1つ多く、先頭がタイトルの場合"""
        script = ["Line 1", "Line 2"]
        prompts = [
            {"scene": 1, "prompt": "Title text in cinematic lighting"},
            {"scene": 2, "prompt": "Prompt for Line 1"},
            {"scene": 3, "prompt": "Prompt for Line 2"}
        ]
        title = "Title"
        
        fixed = self.ai._fix_sync_issues(script, prompts, title)
        
        # 期待値: 先頭が削除され、残り2つになり、シーン番号が振り直されていること
        assert len(fixed) == 2
        assert fixed[0]["prompt"] == "Prompt for Line 1"
        assert fixed[0]["scene"] == 1
        assert fixed[1]["prompt"] == "Prompt for Line 2"
        assert fixed[1]["scene"] == 2

    def test_sync_mismatch_truncation(self):
        """異常系: プロンプトが多すぎるがタイトル判定できない場合 -> 切り捨て"""
        script = ["Line 1"]
        prompts = [
            {"scene": 1, "prompt": "Prompt 1"},
            {"scene": 2, "prompt": "Prompt 2"},
            {"scene": 3, "prompt": "Prompt 3"}
        ]
        title = "Test"
        
        fixed = self.ai._fix_sync_issues(script, prompts, title)
        
        assert len(fixed) == 1
        assert fixed[0]["prompt"] == "Prompt 1"
