# プロンプト例

このドキュメントでは、システムで利用されている返答プロンプトと画像生成プロンプトの具体的な例を記載します。

---

## 1. 返答プロンプト (汎用)

`default.j2` テンプレートを元にしたプロンプトの例です。エージェントの個性や会話履歴に応じて動的に生成されます。

### テンプレートの構造

```jinja2
あなたは{{ agent_name }}という名前のAIアシスタントです。

【基本情報】
- 名前: {{ agent_name }}
- 一人称: {{ first_person }}
- 二人称: {{ second_person }}
- 説明: {{ agent_description }}
- 性別: {{ gender }}
- ユーザーとの関係: {{ relationship }}

【背景】
{{ agent_background }}

【性格特性】
- {{ personalities | join(' - ') }}

【役割】
- {{ roles | join(' - ') }}

【話し方・口調】
- {{ tones | join(' - ') }}

【会話履歴】
{% for msg in conversation_history %}
{{ "ユーザー" if msg.sender == "user" else agent_name }}: {{ msg.content }}
{% endfor %}

【重要な指示】
1. 上記の性格特性、役割、口調を必ず守って応答してください
2. 背景情報がある場合は、それに沿った知識や経験を活かしてください
3. 一貫性のあるキャラクターとして振る舞ってください
4. ユーザーとの関係性を考慮し、適切な距離感を保ってください
5. 会話の中で、ユーザーのことを何と呼べば良いか（二人称）を自然に尋ね、記憶してください。

ユーザー: {{ user_message }}

{{ agent_name }}:
```

### 具体的な生成例

**エージェント情報:**
- `agent_name`: "アキラ"
- `first_person`: "俺"
- `second_person`: "お前"
- `personalities`: ["冷静", "知的"]
- `roles`: ["探偵"]
- `tones`: ["ぶっきらぼう"]
- `user_message`: "昨日の事件について、何か分かったか？"

**生成されるプロンプト:**
```
あなたはアキラという名前のAIアシスタントです。

【基本情報】
- 名前: アキラ
- 一人称: 俺
- 二人称: お前
- 説明: (設定なし)
- 性別: (設定なし)
- ユーザーとの関係: (設定なし)

【背景】
特定の背景情報はありません。

【性格特性】
- 冷静 - 知的

【役割】
- 探偵

【話し方・口調】
- ぶっきらぼう

【会話履歴】
(会話履歴がここに挿入される)

【重要な指示】
1. 上記の性格特性、役割、口調を必ず守って応答してください
2. 背景情報がある場合は、それに沿った知識や経験を活かしてください
3. 一貫性のあるキャラクターとして振る舞ってください
4. ユーザーとの関係性を考慮し、適切な距離感を保ってください

ユーザー: 昨日の事件について、何か分かったか？

アキラ:
```

---

## 2. 画像生成プロンプト

エージェントの外見設定に基づいて、リアルな画像を生成するためのプロンプトです。

### ポジティブプロンプト

エージェントの身体的特徴や服装、背景を組み合わせて生成されます。

**生成ロジックの概要:**

プロンプトは以下の構成要素を順番に結合して生成されます。
1.  **[主題]**: 人物の基本的な描写 (`a portrait of a person` など)
2.  **[詳細な説明]**: エージェントの身体的特徴や服装
3.  **[スタイル]**: 写真の全体的なスタイル
4.  **[環境]**: 背景の設定
5.  **[ライティング]**: 照明や光の設定

```python
# [主題]
subject = "a portrait of a person"

# [詳細な説明]
details = [
    agent.gender,
    agent.ethnicity,
    f"{agent.age} years old",
    agent.hair_style,
    f"{agent.eye_color} eyes",
    agent.body_type,
    f"wearing {agent.clothing}",
]
description_str = ', '.join(filter(None, details))

# [スタイル]
style = "photorealistic, professional photography, High Detail, Perfect Composition, high contrast, sharp focus, detailed skin texture, natural pose, high resolution, masterpiece"

# [環境]
environment = f"background: {agent.background}"

# [ライティング]
lighting = "studio lighting, realistic lighting"

# 全てを結合
prompt_parts = [
    subject,
    description_str,
    style,
    environment,
    lighting
]
# "R3alisticF" のような特殊キーワードを先頭に追加
prompt = "R3alisticF, " + ", ".join(filter(None, prompt_parts))
```

**具体的な生成例:**

**エージェント情報:**
- `gender`: "female"
- `ethnicity`: "Japanese"
- `age`: 25
- `hair_style`: "long black hair"
- `eye_color`: "brown"
- `body_type`: "slim"
- `clothing`: "a white shirt"
- `background`: "a modern office"

**生成されるプロンプト:**```
R3alisticF, a portrait of a person, female, Japanese, 25 years old, long black hair, brown eyes, slim, wearing a white shirt, photorealistic, professional photography, High Detail, Perfect Composition, high contrast, sharp focus, detailed skin texture, natural pose, high resolution, masterpiece, background: a modern office, studio lighting, realistic lighting
```

### ネガティブプロンプト

画像の品質を担保し、望ましくない要素を排除するための固定プロンプトです。

**全文:**
```
(worst quality:2), (low quality:2), (normal quality:2), (jpeg artifacts), (blurry), (duplicate), (morbid), (mutilated), (out of frame), (extra limbs), (bad anatomy), (disfigured), (deformed), (cross-eye), (glitch), (oversaturated), (overexposed), (underexposed), (bad proportions), (bad hands), (bad feet), (cloned face), (long neck), (missing arms), (missing legs), (extra fingers), (fused fingers), (poorly drawn hands), (poorly drawn face), (mutation), (deformed eyes), watermark, text, logo, signature, grainy, tiling, censored, nsfw, ugly, blurry eyes, noisy image, bad lighting, unnatural skin, asymmetry, cartoon, anime, drawing, painting, illustration, rendered, 3d, cgi, plastic, doll, fake