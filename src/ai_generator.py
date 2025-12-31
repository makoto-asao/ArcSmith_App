import google.generativeai as genai
from src.config import Config
import json
import re
from src.deepl_translator import DeepLTranslator

class AIGenerator:
    def __init__(self, model_name='gemini-3-flash-preview'):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # 2025年12月現在の最新プレビュー版（gemini-3-flash-preview）
        self.model = genai.GenerativeModel(model_name)

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

    def generate_script_and_prompts(self, title, context=None, expert_persona=None, video_mode="Shorts"):
        """【モードB：制作実行】3人のエキスパートによる共同制作"""
        
        # パーソナ設定の適用
        persona_logic = expert_persona if expert_persona else """
1. **Viral Architect (YouTube Shortsマーケター)**: 視聴維持率とクリック率（CTR）の鬼。冒頭1秒の「フック」と、スマホ表示で途切れない魅力的なタイトルの作成に命をかける。
2. **The Whisperer (ホラー作家)**: 日本特有の「湿り気のある恐怖」を英語の短い台本に昇華させる。
3. **The Visionary (映像監督)**: Midjourneyを完璧に操る呪文（プロンプト）の魔術師。単なる映像化ではなく、台本の物語性（ストーリーアーク）や象徴的なキーワードを視覚的なメタファーに変換する。
"""
        
        # ビデオモードに応じた制約の設定
        if video_mode == "Long-form":
            length_constraints = """
**Title (EN):**
- 文字数: **50〜80文字（推奨）**、最大100文字。
- 視聴者の好奇心を刺激しつつ、内容が伝わる魅力的なタイトル。
- パワーワード（Shocking, Secret, Warning, Never before seen...）を効果的に使用。
- **注意**: #Shorts は含めないでください。

**Description:**
- 文字数: **500文字以上**（推奨）
- 冒頭150文字に動画の内容を凝縮し、詳細な背景情報や視聴者への問いかけを含める。
- SEOキーワード（Japanese Horror, Urban Legend, Creepy, Supernatural）を自然に含める。

**Vrew Script:**
- 目標時間: **3分〜5分**
- 台本の行数（シーン数）: **無制限**（30〜60行程度を目安に、ストーリーが完結するまで展開してください）
- 各行: **10〜15単語程度**

**Midjourney Prompts:**
- 台本の各行に1対1で対応。
"""
            hashtags_instruction = '["#JapaneseHorror", "#UrbanLegend", "#ScaryStories", ...]'
        else:  # Shorts
            length_constraints = """
**Title (EN):**
- 文字数: **30〜50文字（推奨）**、最大100文字。
- **重要**: スマートフォンで表示した際にタイトルが途切れないよう、最も重要なフック（キーワードやパワーワード）を最初の40文字以内に配置してください。
- パワーワード（Shocking, Secret, Warning, Never before seen...）を効果的に使用。
- 例: "The Secret of the Cursed Village #Shorts"

**Description:**
- 文字数: **300文字以上**（必須）
- **重要**: 最初の150文字（1〜2行）が「もっと見る」を押さずに見える範囲です。ここに動画の核心と、視聴者がコメントしたくなるような問いかけを含めてください。
- SEOキーワード（Japanese Horror, Urban Legend, Creepy, Supernatural）を自然に含める。
- ハッシュタグは含めない（別フィールド）。

**Vrew Script:**
- 台本の行数: 10-20行程度（YouTube Shorts 60秒に収まる範囲で柔軟に）
- 各行: 10-15単語程度

**Midjourney Prompts:**
- 台本の各行に1対1で対応。
"""
            hashtags_instruction = '["#Shorts", "#JHorror", "#UrbanLegend", ...]'

        # コンテキストの準備
        context_str = ""
        if context:
            overview = context.get('overview', '')
            horror_point = context.get('horror_point', '')
            context_str = f"\n【背景情報】\n概要: {overview}\n恐怖ポイント: {horror_point}\n"
            
            # --- ユーザーからの追加詳細 (Title, Hook, Outline) ---
            user_title = context.get('title')
            user_hook = context.get('hook')
            user_outline = context.get('outline')
            
            if user_title or user_hook or user_outline:
                context_str += "\n【⚠️ ユーザーからの最優先指示（監督指示）】\n"
                if user_title:
                    context_str += f"- 製作したいタイトル/テーマ: {user_title}\n"
                if user_hook:
                    context_str += f"- 必須のフック（冒頭の引き）: {user_hook}\n"
                if user_outline:
                    context_str += f"- 指定のアウトライン（構成）: {user_outline}\n"
                context_str += "※ AIはこれらユーザーの指示を「絶対的なルール」として最優先に反映し、その上で専門知識を活かして補完してください。\n"

        prompt = f"""
あなたはYouTube動画制作特化の「Jホラー動画制作スタジオ」の統括AIです。
現在は「**{video_mode}**」モードで制作を行っています。
以下のテーマと背景情報に基づき、3人のエキスパートを召喚して最高品質の台本を作成してください。

テーマ：「{title}」
{context_str}

### 👥 召喚するエキスパート
{persona_logic}

### 🎯 制作プロセス (2-Round System)
最高のクオリティを担保するため、以下の「2段階会議」を経て制作を行ってください。

#### Round 1: Drafting (粗案作成)
- 3人のエキスパートが協力し、一旦完了形のドラフト（タイトル、台本、プロンプト）を作成する。
- この段階では勢いを重視する。

#### Round 2: Critique & Refine (批判と修正)
- 作成されたドラフトに対し、3人がそれぞれの視点で**厳しく批判**を行う。
  - **Viral Architect**: 「タイトルは本当にクリックしたくなるか？」「冒頭のフックは弱いのではないか？」
  - **The Whisperer**: 「ありきたりな怪談になっていないか？」「日本特有の湿度や不気味さが足りないのではないか？」
  - **The Visionary**: 「プロンプトは具体的か？」「映像として面白味が足りないのではないか？（単なるキャラの立ち絵になっていないか？）」
- これらの批判に基づき、ドラフトを**全面的に書き直して**最終版とする。

#### Final: Output
- 修正された最終成果物のみをJSONとして出力する。
- **重要**: `editorial_notes` には、「Round 2でどのような批判があり、それをどう改善したか」の要約を必ず含めること。

### 📏 品質基準と制約（{video_mode}モード）
{length_constraints}

### 🎬 重要：Vrew台本のフォーマット規則
**vrew_script**は音声合成ソフトウェアVrewで直接読み上げられます。以下の規則を厳守してください：

✅ **良い例（このように生成してください）:**
[
  "Beyond this sign the law fades",
  "A path swallowed by whispers",
  "Ancient barks echo through the mist",
  "What secrets did they leave behind"
]

❌ **悪い例（絶対に避けてください）:**
[
  "Beyond this sign, the law fades.",  // 句点(.)は含めない
  "[Eerie dog barks begin softly, increasing in intensity]",  // 音響効果の指示は含めない
  "\"Beyond this sign... the law fades.\"",  // 引用符は使わない
  "SFX: Thunder rumbles",  // 効果音の指示は含めない
]

**規則:**
1. 各行は純粋なナレーション文のみ（音響効果の指示 `[...]` や `SFX:` は含めない）
2. 引用符 `"` は使わない（そのまま読み上げられてしまう）
3. 1行は短く、リズミカルに（{video_mode}モードの単語数制約に従う）
4. 音響効果や演出指示は `editorial_notes` に記載する
5. 各行に句点（.）は絶対に含めない（Vrewでの意図しない分割を防ぐため、文末のピリオドを削除してください）

### 🎨 重要：Midjourneyプロンプトの対応規則
**mj_prompts**は台本の各行（シーン）に1対1で対応する必要があります：

**規則:**
1. **台本の行数 = Midjourneyプロンプトの数**（必ず一致させる）
2. **タイトルカードやイントロ用の画像生成は禁止**（最初のプロンプトは必ず台本の1行目に対応させること）
3. 各プロンプトは、対応する台本の行（ナレーション）の内容、感情、および**そこに登場する重要なキーワード（名詞）**を確実に視覚化すること
4. **文脈の維持**: 全シーンを通じてキャラクター、場所の雰囲気、光源設定の一貫性を保ちつつ、物語の進行（恐怖の増大など）を視覚的に表現すること
5. シーン番号は1から順番に付ける
6. 技術的な指定を含める（cinematography, photorealistic, 8k, 35mm lens, grainy film, high contrast, moody lighting, etc.）

**出力形式 (JSONのみ):**
以下のJSON形式で、**余計な解説文を一切含まずJSONのみ**を出力してください。
{{
  "editorial_notes": "【重要】Round 2での3人による批判内容（ダメ出し）と、それを受けてどう改善したかの日本語解説。演出指示も含む。",
  "title_en": "English Title (Refined)",
  "title_jp": "日本語タイトル (Refined)",
  "description": "YouTube Description in English (Refined)",
  "hashtags": {hashtags_instruction},
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

            # --- 同期ズレの補正 (New!) ---
            raw_prompts = data.get('mj_prompts', [])
            vrew_script = data.get('vrew_script', [])
            title_en = data.get('title_en', '')
            
            fixed_prompts = self._fix_sync_issues(vrew_script, raw_prompts, title_en)

            # Midjourneyプロンプトをシーンごとにリスト化
            prompt_list = []
            for item in fixed_prompts:
                p = item.get('prompt', '')
                if p:
                    # 共通キーワードの付与
                    if "--ar" not in p:
                        p += " --ar 9:16 --v 6.0"
                    prompt_list.append(p)

            # --- 日本語翻訳の追加 ---
            script_jp_list = []
            try:
                translator = DeepLTranslator()
                for line in data.get('vrew_script', []):
                    script_jp_list.append(translator.translate(line))
            except Exception as e:
                print(f"Translation integration error: {e}")
                script_jp_list = ["" for _ in data.get('vrew_script', [])]

            return {
                "title_en": data.get('title_en', ''),
                "title_jp": data.get('title_jp', ''),
                "description": data.get('description', ''),
                "hashtags": ' '.join(data.get('hashtags', [])),
                "editorial_notes": data.get('editorial_notes', ''),
                "vrew_script": "\n".join(data.get('vrew_script', [])),
                "script_jp_list": script_jp_list, # シーンごとの翻訳リスト
                "mj_prompts_list": prompt_list,  # シーンごとのリスト
                "full_text": full_display_text  # 従来の表示用（後方互換性）
            }
        except Exception as e:
            return {
                "title_en": "",
                "title_jp": "",
                "description": "",
                "hashtags": "",
                "editorial_notes": f"JSON解析エラー: {e}\\nRaw Response: {response.text}",
                "vrew_script": "",
                "mj_prompts_list": [],
                "full_text": f"JSON解析エラー: {e}\\nRaw Response: {response.text}"
            }

    def _fix_sync_issues(self, vrew_script, mj_prompts, title_en):
        """
        AIが生成したスクリプトとプロンプトの同期ズレを補正する内部メソッド
        よくあるパターン: プロンプトが1つ多い（タイトルカード用が含まれている）
        """
        len_script = len(vrew_script)
        len_prompts = len(mj_prompts)

        if len_script == len_prompts:
            return mj_prompts

        # パターンA: プロンプトが1つ多い (タイトルカードが先頭に含まれている可能性が高い)
        if len_prompts == len_script + 1:
            # 先頭のプロンプトがタイトルやイントロっぽいかチェック
            first_prompt = mj_prompts[0].get('prompt', '').lower()
            suspicious_keywords = ['title', 'intro', 'text', 'typography', title_en.lower()]
            
            is_title_card = any(k in first_prompt for k in suspicious_keywords)
            
            if is_title_card:
                print("DEBUG: Detected possible Title Card prompt. Removing 1st prompt to sync with script.")
                # シーン番号を振り直して返す
                fixed_prompts = []
                for i, p_data in enumerate(mj_prompts[1:], 1):
                    p_data['scene'] = i
                    fixed_prompts.append(p_data)
                return fixed_prompts
            
            # 末尾が多い場合もあるかもしれないが、まずは先頭を疑う。
            # それでもダメなら単純に長さ合わせを行う（下部）

        # パターンB: どうしても合わない場合は、短い方に合わせる（クラッシュ防止）
        print(f"WARNING: Sync mismatch detected. Script: {len_script}, Prompts: {len_prompts}. Truncating to min length.")
        min_len = min(len_script, len_prompts)
        
        # プロンプトをスライスしてシーン番号を振り直し
        fixed_prompts = []
        for i in range(min_len):
            p_data = mj_prompts[i]
            p_data['scene'] = i + 1
            fixed_prompts.append(p_data)
            
        return fixed_prompts
