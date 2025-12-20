import google.generativeai as genai
from src.config import Config
import json
import re

class AIGenerator:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # 2025年12月現在の最新安定版を利用
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_new_ideas(self, existing_titles):
        """【モードA：企画会議】新しいネタを5つ提案"""
        prompt = f"""
あなたはYouTubeショート特化の「Jホラー動画制作スタジオ」の統括AIです。
現在の管理表にある既存ネタ：{json.dumps(existing_titles, ensure_ascii=False)}

### 【モードA：企画会議】
1. 重複チェック: 既存ネタとは重複しないこと。
2. 提案: 海外でバズりそうな日本のホラー・都市伝説・怪異のネタを5つ提案してください。

**出力フォーマット:**
1. **[テーマ名 (日/英)]**
   - **概要:** (1行で)
   - **恐怖ポイント:** (海外受けする理由)
   - **映像イメージ:** (冒頭3秒のフック)

...これを5つ。
"""
        response = self.model.generate_content(prompt)
        # 単純なタイトルリストとして抽出（後続処理のため）
        lines = response.text.strip().split("\n")
        clean_titles = []
        for line in lines:
            if line.startswith("1. **") or line.startswith("2. **") or line.startswith("3. **") or line.startswith("4. **") or line.startswith("5. **"):
                title = re.search(r'\*\*(.*?)\*\*', line)
                if title:
                    clean_titles.append(title.group(1))
        
        # マッチしなかった場合のフォールバック
        if not clean_titles:
            clean_titles = [re.sub(r'^[\d\.\-\*縲、)]+\s*', '', l).strip() for l in lines if l.strip()][:5]
            
        return clean_titles, response.text

    def generate_script_and_prompts(self, title):
        """【モードB：制作実行】台本とプロンプトを生成"""
        prompt = f"""
あなたはYouTubeショート特化の「Jホラー動画制作スタジオ」の統括AIです。
テーマ：「{title}」

### 🔴 【モードB：制作実行】
指定されたテーマに対し、監督とマーケターの視点を取り入れたコンテンツを作成してください。

**【制作ルール】**
- シーン数: 8〜12シーン。
- 英語台本: Vrew貼り付け用に1文を短く区切り、US単位(Feet/Miles)を使用。

**【出力フォーマット】**
議論ログは非表示にし、以下の形式で出力してください。

## 1. Title Idea
**English:** (英語タイトル案 #Shorts 含む)
**Japanese:** (日本語訳)

## 2. YouTube Description & Hashtags
**English:** (英語の説明文)
**Hashtags:** #Shorts #JHorror #UrbanLegend #Japan #ScaryStories (他3つ追加)
**Japanese:** (日本語訳)

## 3. Translation & Director's Notes (For Creator)
(英文の意味と演出指示を日本語で解説)

**Scene [1]:**
**EN:** [English Text]
**JP:** [Japanese Translation]
...

## 4. Video Script (For Vrew - Copy & Paste)
**【重要ルール】**
1. 英語のナレーションテキストのみをコードブロック内に出力すること（日本語、Scene番号、前置き、記号は一切禁止）。
2. 各Sceneの文章ごとに必ず改行すること。

## 5. Midjourney Prompts
**【重要】プロンプト本文のみをコードブロックに入れてください。「Scene [X]:」の文字はコードブロックの【外】に出してください。**
(末尾に "photorealistic, 8k, cinematic lighting, horror atmosphere, dark style, --ar 9:16 --v 6.0" を付与)
"""
        response = self.model.generate_content(prompt)
        text = response.text

        # 各セクションの抽出
        # 1. Video Script (Vrew用)
        script_block = re.search(r'## 4\. Video Script.*?```(?:python|text|)\n(.*?)```', text, re.DOTALL)
        script_content = script_block.group(1).strip() if script_block else ""
        
        # ユーザーの要望通り「Scene 1:」などのプレフィックスを除去
        clean_script = []
        for line in script_content.split("\n"):
            line = re.sub(r'^Scene\s*\d+\s*[:：]\s*', '', line).strip()
            if line:
                clean_script.append(line)
        script_final = "\n".join(clean_script)

        # 2. Midjourney Prompts
        prompts = []
        prompt_sections = re.findall(r'\*\*Scene \[\d+\]:\*\*\n```(?:text|)\n(.*?)\n```', text, re.DOTALL)
        if not prompt_sections:
            # 代替パターン
            prompt_sections = re.findall(r'Scene \[\d+\]:\n```(?:text|)\n(.*?)\n```', text, re.DOTALL)
        
        prompts_final = "\n\n".join(prompt_sections) if prompt_sections else ""

        return {
            "full_text": text,
            "vrew_script": script_final,
            "mj_prompts": prompts_final
        }

