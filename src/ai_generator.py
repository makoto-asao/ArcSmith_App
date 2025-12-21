import google.generativeai as genai
from src.config import Config
import json
import re

class AIGenerator:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # 2025年12月現在の最新安定版を利用
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_new_ideas(self, existing_titles, expert_persona=None):
        """【モードA：企画会議】新しいネタを5つ提案"""
        # パーソナ設定の適用
        persona_logic = expert_persona if expert_persona else """
1. **Viral Architect (YouTube Shortsマーケター)**: 冒頭1秒の「めくり」と視聴維持率に異常にこだわる。
2. **The Whisperer (ホラー作家)**: 日本特有の「湿り気のある恐怖」を英語の短い台本に昇華させる。
3. **The Visionary (映像監督)**: Midjourneyを完璧に操る呪文（プロンプト）の魔術師。
"""
        prompt = f"""
あなたはYouTubeショート特化の「Jホラー動画制作スタジオ」の統括AIです。
以下の3人のエキスパートを召喚し、協力して最高にバズる企画を立案してください。

### 👥 召喚するエキスパート
{persona_logic}

現在の管理表にある既存ネタ：{json.dumps(existing_titles, ensure_ascii=False)}

### 【モードA：企画会議】
1. **論議**: 3人がそれぞれの視点から、どのようなネタが今求められているか、あるいは既存ネタの弱点は何かを1行ずつ議論する。
2. **提案**: 既存ネタとは重複しない、海外でバズりそうな日本のホラー・都市伝説・怪異のネタを5つ提案してください。

**出力フォーマット:**
1. **[テーマ名 (日/英)]**
   - **概要:** (具体的な内容)
   - **恐怖ポイント:** (海外視聴者が恐怖を感じる理由)
   - **映像イメージ:** (冒頭3秒のフック)

...これを5つ。
"""
        response = self.model.generate_content(prompt)
        text = response.text
        
        # タイトルと関連情報を抽出
        ideas_data = {}
        sections = re.split(r'\n\d+\.\s*\*\*\[', text)
        if len(sections) > 1:
            for section in sections[1:]:
                # タイトルの抽出
                title_match = re.search(r'^(.*?)\]\*\*', section)
                if title_match:
                    title = title_match.group(1).strip()
                    # 概要と恐怖ポイントの抽出
                    overview = re.search(r'概要:?\s*\*\*(.*?)\*\*', section) or re.search(r'概要:?\s*(.*?)\n', section)
                    horror_point = re.search(r'恐怖ポイント:?\s*\*\*(.*?)\*\*', section) or re.search(r'恐怖ポイント:?\s*(.*?)\n', section)
                    
                    ideas_data[title] = {
                        "overview": overview.group(1).strip() if overview else "",
                        "horror_point": horror_point.group(1).strip() if horror_point else ""
                    }
        
        # フォールバック (以前の頑健なロジックをベースに辞書化)
        if not ideas_data:
            lines = text.split("\n")
            current_title = None
            for line in lines:
                line_s = line.strip()
                if "**[" in line_s or (re.match(r'^\d[\.\)]', line_s) and "**" in line_s):
                    match = re.search(r'\*\*(.*?)\*\*', line_s)
                    if match:
                        title = match.group(1).strip("[] ")
                        if title and not any(k in title for k in ["概要", "恐怖ポイント", "映像イメージ"]):
                            title = re.sub(r'^\d[\.\)]\s*', '', title)
                            current_title = title
                            ideas_data[current_title] = {"overview": "", "horror_point": ""}
                elif current_title and "概要" in line_s:
                    ideas_data[current_title]["overview"] = line_s
                elif current_title and "恐怖ポイント" in line_s:
                    ideas_data[current_title]["horror_point"] = line_s

        return ideas_data, text

    def generate_script_and_prompts(self, title, context=None, expert_persona=None):
        """【モードB：制作実行】3人のエキスパートによる共同制作"""
        
        # パーソナ設定の適用
        persona_logic = expert_persona if expert_persona else """
1. **Viral Architect (YouTube Shortsマーケター)**: 冒頭1秒の「めくり」と視聴維持率に異常にこだわる。
2. **The Whisperer (ホラー作家)**: 日本特有の「湿り気のある恐怖」を英語の短い台本に昇華させる。
3. **The Visionary (映像監督)**: Midjourneyを完璧に操る呪文（プロンプト）の魔術師。
"""
        
        # コンテキストの準備
        context_str = ""
        if context:
            context_str = f"\n【背景情報】\n概要: {context.get('overview', '')}\n恐怖ポイント: {context.get('horror_point', '')}\n"

        prompt = f"""
あなたはYouTubeショート特化の「Jホラー動画制作スタジオ」の統括AIです。
以下のテーマと背景情報に基づき、3人のエキスパートを召喚して最高品質の台本を作成してください。

テーマ：「{title}」
{context_str}

### 👥 召喚するエキスパート
{persona_logic}

### 🔴 制作フロー
1. **論議**: 3人がそれぞれの視点から、このネタをどう料理すべきか1行ずつ意見を出す。
2. **最終成果物**: 論議を踏まえ、以下のフォーマットで出力する。

**【出力フォーマット】**
## 1. Title Idea
**English:** (英語タイトル案 #Shorts 含む)
**Japanese:** (日本語訳)

## 2. YouTube Description & Hashtags
**English:** (英語の説明文)
**Hashtags:** #Shorts #JHorror #UrbanLegend #Japan #ScaryStories (他3つ)

## 3. Translation & Director's Notes (For Creator)
(英文の意味と、監督からの演出指示を日本語で解説)

**Scene [1]:**
**EN:** [English Text]
**JP:** [Japanese Translation]
...

## 4. Video Script (For Vrew - Copy & Paste)
**【重要】** 英語のナレーションテキストのみをコードブロック内に出力すること。

## 5. Midjourney Prompts
**【重要】** プロンプト本文のみをコードブロックに。Scene文字は外に出す。
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

