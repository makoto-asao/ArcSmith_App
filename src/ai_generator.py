import google.generativeai as genai
from src.config import Config
import json
import re

class AIGenerator:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # 2025年12月現在の最新安定版（構造化出力対応）
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
1. **論議**: 3人がそれぞれの視点から議論する。
2. **提案**: 既存ネタとは重複しない、海外でバズりそうな日本のホラー・都市伝説・怪異のネタを5つ提案してください。

**出力形式 (JSONのみ):**
以下のJSONスキーマに従って、**余計な解説文を一切含まずJSONのみ**を出力してください。
{{
  "discussion": "3名による議論の要約",
  "ideas": [
    {{
      "title": "日本語タイトル (English Title)",
      "overview": "具体的な内容を日本語で",
      "horror_point": "なぜ海外視聴者が怖いと感じるのか"
    }}
  ]
}}
"""
        response = self.model.generate_content(
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        
        try:
            # AIがマークダウンでJSONを囲って出力した場合のクリーニング
            raw_text = response.text
            # 正規表現で一番最初に見つかる ```json ... ``` または ``` ... ``` を抽出
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_text, re.DOTALL)
            if match:
                clean_json = match.group(1)
            else:
                clean_json = raw_text.strip("` \n")
                
            data = json.loads(clean_json)
            ideas_data = {item["title"]: {"overview": item["overview"], "horror_point": item["horror_point"]} for item in data.get("ideas", [])}
            full_text = f"### 👥 エキスパートによる議論\n{data.get('discussion', '')}\n\n"
            for item in data.get("ideas", []):
                full_text += f"#### {item['title']}\n- **概要**: {item['overview']}\n- **恐怖ポイント**: {item['horror_point']}\n\n"
        except Exception as e:
            return {}, f"JSON解析エラー: {e}\nRaw Response: {response.text}"

        return ideas_data, full_text

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

### 🎯 制作プロセス
以下の手順で3人のエキスパートが協力して制作を進めてください：

1. **Viral Architect**がタイトルとフックを提案
2. **The Whisperer**が台本とストーリー展開を執筆
3. **The Visionary**が各シーンの映像プロンプトを設計
4. 3人で最終調整と品質チェック

### 📏 品質基準と文字数制約

**Title (EN):**
- 文字数: **100文字以下**（必須）
- YouTube Shortsで目を引く、インパクトのあるタイトル
- SEOキーワードを含める（例: Japanese Horror, Creepy, Haunted, Urban Legend）
- 例: "The Cursed Forest Where Dogs Never Stop Barking | Japanese Urban Legend #Shorts"

**Description:**
- 文字数: **300文字以上**（必須）
- 動画の内容を詳しく説明
- SEOキーワードを自然に含める
- 視聴者の興味を引く文章
- ハッシュタグは含めない（別フィールド）

**Vrew Script:**
- 台本の行数: 8-12行程度（YouTube Shorts 60秒に最適）
- 各行: 10-15単語程度

**Midjourney Prompts:**
- 台本の各行に1対1で対応
- 技術的な指定を含める

### 🎬 重要：Vrew台本のフォーマット規則
**vrew_script**は音声合成ソフトウェアVrewで直接読み上げられます。以下の規則を厳守してください：

✅ **良い例（このように生成してください）:**
[
  "Beyond this sign, the law fades.",
  "A path swallowed by whispers.",
  "Ancient barks echo through the mist.",
  "What secrets did they leave behind?"
]

❌ **悪い例（絶対に避けてください）:**
[
  "[Eerie dog barks begin softly, increasing in intensity]",  // 音響効果の指示は含めない
  "\\"Beyond this sign... the law fades.\\"",  // 引用符は使わない
  "SFX: Thunder rumbles",  // 効果音の指示は含めない
]

**規則:**
1. 各行は純粋なナレーション文のみ（音響効果の指示 `[...]` や `SFX:` は含めない）
2. 引用符 `"` は使わない（そのまま読み上げられてしまう）
3. 1行は短く、リズミカルに（10-15単語程度）
4. 音響効果や演出指示は `editorial_notes` に記載する

### 🎨 重要：Midjourneyプロンプトの対応規則
**mj_prompts**は台本の各行（シーン）に1対1で対応する必要があります：

**規則:**
1. **台本の行数 = Midjourneyプロンプトの数**（必ず一致させる）
2. 各プロンプトは対応する台本の行の視覚的表現を記述
3. シーン番号は1から順番に付ける
4. 技術的な指定を含める（cinematic lighting, photorealistic, 8k, 35mm lens, grainy film, etc.）

**例:**
台本が4行の場合、mj_promptsも4つ必要：
```
vrew_script: [
  "Beyond this sign, the law fades.",      // シーン1
  "A path swallowed by whispers.",         // シーン2
  "Ancient barks echo through the mist.",  // シーン3
  "What secrets did they leave behind?"    // シーン4
]

mj_prompts: [
  {{ "scene": 1, "prompt": "Weathered warning sign at forest entrance, ominous atmosphere, cinematic lighting, photorealistic, 8k, 35mm lens" }},
  {{ "scene": 2, "prompt": "Dark overgrown forest path disappearing into mist, eerie silence, cinematic lighting, photorealistic, 8k" }},
  {{ "scene": 3, "prompt": "Misty Japanese forest with ancient trees, mysterious shadows, cinematic lighting, photorealistic, 8k, grainy film" }},
  {{ "scene": 4, "prompt": "Abandoned shrine deep in forest, decaying torii gate, haunting atmosphere, cinematic lighting, photorealistic, 8k" }}
]
```

**出力形式 (JSONのみ):**
以下のJSON形式で、**余計な解説文を一切含まずJSONのみ**を出力してください。
{{
  "editorial_notes": "3人のエキスパートによる協議内容、演出指示、制作意図の日本語解説（音響効果の指示もここに含める）",
  "title_en": "English Title for #Shorts (100文字以下)",
  "title_jp": "日本語タイトル",
  "description": "YouTube Description in English (300文字以上)",
  "hashtags": ["#Shorts", "#JHorror", "#UrbanLegend", ...],
  "vrew_script": ["English line 1", "English line 2", ...],
  "mj_prompts": [
    {{
      "scene": 1,
      "prompt": "Technical prompt in English with cinematic lighting, photorealistic, 8k, etc."
    }}
  ]
}}
"""
        response = self.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        try:
            # AIがマークダウンでJSONを囲って出力した場合のクリーニング
            raw_text = response.text
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_text, re.DOTALL)
            if match:
                clean_json = match.group(1)
            else:
                clean_json = raw_text.strip("` \n")

            data = json.loads(clean_json)
            
            # UI表示用のテキストを構築
            full_display_text = f"## 🎬 Production Notes\n{data.get('editorial_notes', '')}\n\n"
            full_display_text += f"## 📝 Video Info\n- **Title (EN)**: {data.get('title_en', '')}\n- **Title (JP)**: {data.get('title_jp', '')}\n"
            full_display_text += f"- **Hashtags**: {' '.join(data.get('hashtags', []))}\n\n"
            full_display_text += "## 📜 Script (EN)\n" + "\n".join(data.get('vrew_script', []))

            # Midjourneyプロンプトをシーンごとにリスト化
            prompt_list = []
            for item in data.get('mj_prompts', []):
                p = item.get('prompt', '')
                if p:
                    # 共通キーワードの付与
                    if "--ar" not in p:
                        p += " --ar 9:16 --v 6.0"
                    prompt_list.append(p)

            return {
                "title_en": data.get('title_en', ''),
                "title_jp": data.get('title_jp', ''),
                "description": data.get('description', ''),
                "hashtags": ' '.join(data.get('hashtags', [])),
                "editorial_notes": data.get('editorial_notes', ''),
                "vrew_script": "\n".join(data.get('vrew_script', [])),
                "mj_prompts_list": prompt_list,  # シーンごとのリスト
                "full_text": full_display_text  # 従来の表示用（後方互換性）
            }
        except Exception as e:
            return {
                "title_en": "",
                "title_jp": "",
                "description": "",
                "hashtags": "",
                "editorial_notes": f"JSON解析エラー: {e}\nRaw Response: {response.text}",
                "vrew_script": "",
                "mj_prompts_list": [],
                "full_text": f"JSON解析エラー: {e}\nRaw Response: {response.text}"
            }
