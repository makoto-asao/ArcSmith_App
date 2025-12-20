import google.generativeai as genai
from src.config import Config
import json
import re

class AIGenerator:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # 404エラー対策として -latest を指定
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def generate_new_ideas(self, existing_titles):
        """新しいネタを5つ生成"""
        prompt = f"""
あなたはJホラー動画の専門プロデューサーです。
現在、以下のネタが既に存在します：
{json.dumps(existing_titles, ensure_ascii=False)}

これらと重複せず、かつ現代のSNSでバズる可能性が高いJホラーの新しいネタ（タイトル）を5つ提案してください。
出力は、1行に1つのタイトルだけを記述してください。余計な説明は不要です。
"""
        response = self.model.generate_content(prompt)
        titles = response.text.strip().split("\n")
        # クリーニング（番号等がついている場合を考慮）
        clean_titles = [re.sub(r'^\d+\.\s*', '', t).strip() for t in titles if t.strip()]
        return clean_titles[:5]

    def generate_script_and_prompts(self, title):
        """指定されたネタから台本と画像プロンプトを生成"""
        prompt = f"""
あなたは伝説的なJホラー映画監督であり、SNSマーケターです。
ネタ：「{title}」をもとに、ショート動画用の構成案を作成してください。

以下の形式で出力してください：

【Vrew用スクリプト】
（ここにナレーションと字幕用のテキストを記述。30〜60秒程度の尺になるように）

【Midjourneyプロンプト】
Scene 1: (英文プロンプト)
Scene 2: (英文プロンプト)
Scene 3: (英文プロンプト)
Scene 4: (英文プロンプト)
... (4〜6シーン程度)

※プロンプトは、Jホラー特有の不気味さ、湿り気、暗さを強調し、フォトリアルな描写にしてください。
"""
        response = self.model.generate_content(prompt)
        full_text = response.text

        # パース処理
        script_part = ""
        prompt_part = ""
        
        if "【Vrew用スクリプト】" in full_text and "【Midjourneyプロンプト】" in full_text:
            parts = full_text.split("【Midjourneyプロンプト】")
            script_part = parts[0].replace("【Vrew用スクリプト】", "").strip()
            prompt_part = parts[1].strip()
        else:
            # フォールバック（うまくパースできなかった場合）
            script_part = full_text

        return script_part, prompt_part

