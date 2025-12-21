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

**出力形式 (JSONのみ):**
以下のJSON形式で、**余計な解説文を一切含まずJSONのみ**を出力してください。
{{
  "editorial_notes": "エキスパートによる演出指示や制作意図の日本語解説",
  "title_en": "English Title for #Shorts",
  "title_jp": "日本語タイトル",
  "description": "YouTube Description in English",
  "hashtags": ["#Shorts", "#JHorror", ...],
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

            # Vrew用スクリプトの整形
            script_final = "\n".join(data.get('vrew_script', []))

            # Midjourneyプロンプトの連結
            prompt_list = []
            for item in data.get('mj_prompts', []):
                p = item.get('prompt', '')
                if p:
                    # 共通キーワードの付与
                    if "--ar" not in p:
                        p += " --ar 9:16 --v 6.0"
                    prompt_list.append(p)
            prompts_final = "\n\n".join(prompt_list)

            return {
                "full_text": full_display_text,
                "vrew_script": script_final,
                "mj_prompts": prompts_final
            }
        except Exception as e:
            return {
                "full_text": f"JSON解析エラー: {e}\nRaw Response: {response.text}",
                "vrew_script": "",
                "mj_prompts": ""
            }
