import google.generativeai as genai
from src.config import Config
import json
import re

class AIGenerator:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # 2025年12月現在の最新安定版 gemini-2.5-flash を利用
        # (gemini-3-flash-preview も利用可能だが、安定性を考慮して 2.5 を選択)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        # もし 2.5 でエラーが出る環境の場合は 'gemini-1.5-flash-latest' に戻してください

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
        lines = response.text.strip().split("\n")
        clean_titles = []
        for line in lines:
            line = line.strip()
            if not line: continue
            # 番号、箇条書き記号、Markdown（**等）を削除
            t = re.sub(r'^[\d\.\-\*縲、)]+\s*', '', line)
            t = t.replace('**', '').replace('"', '').replace("'", '').strip()
            if t:
                clean_titles.append(t)
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

        # セクションを正規表現で柔軟に抽出
        script_match = re.search(r'【Vrew用スクリプト】(.*?)(?=【Midjourneyプロンプト】|$)', full_text, re.DOTALL)
        prompt_match = re.search(r'【Midjourneyプロンプト】(.*)', full_text, re.DOTALL)
        
        script_part = script_match.group(1).strip() if script_match else ""
        prompt_part = prompt_match.group(1).strip() if prompt_match else ""

        # 万が一マッチしなかった場合のフォールバック
        if not script_part and not prompt_part:
            script_part = full_text

        return script_part, prompt_part

