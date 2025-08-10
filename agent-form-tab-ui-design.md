# エージェント編集フォーム タブUI設計

## 1. 概要

エージェント編集フォームのUIを、左側にナビゲーションメニューを持つタブ形式に変更する。
これにより、ユーザーはフォームの全体像を把握しやすくなり、各設定項目へのアクセス性も向上する。

## 2. ファイル構造案

新しいUIを実現するために、以下のファイル構造を提案する。

```
frontend/
└── components/
    ├── AgentForm/
    │   ├── AgentForm.js          # (変更) タブコンポーネントを統括するメインコンポーネント
    │   ├── TabNavigation.js      # (新規) 左側のタブメニュー
    │   ├── BasicInfoTab.js       # (新規) 「基本情報」タブのフォーム内容
    │   ├── AppearanceTab.js      # (新規) 「外見」タブのフォーム内容
    │   └── PersonalityTab.js     # (新規) 「性格・口調」タブのフォーム内容
    └── AgentForm.js              # (旧) このファイルを上記の構造にリファクタリングする
```

## 3. コンポーネント設計

### `AgentForm.js` (メインコンポーネント)

-   **役割**:
    -   エージェントデータの状態（`name`, `description`など）を一元管理する。
    -   現在アクティブなタブの状態を管理する。
    -   `TabNavigation`コンポーネントと、現在アクティブなタブのコンテンツコンポーネント（`BasicInfoTab`など）を描画する。
    -   各タブコンポーネントに必要なデータと、データを更新するための関数をPropsとして渡す。
    -   保存、キャンセル、削除ボタンの処理ロジックを持つ。

### `TabNavigation.js`

-   **役割**:
    -   「基本情報」「外見」「性格・口調」のタブメニューを表示する。
    -   各タブがクリックされたときに、`AgentForm.js`に通知し、アクティブなタブを切り替える。
    -   現在アクティブなタブを視覚的にハイライトする。

### `BasicInfoTab.js`

-   **役割**:
    -   「基本情報」に関連するフォームフィールド（名前、説明、関係、一人称、背景設定など）を表示する。
    -   `AgentForm.js`から渡されたデータと更新関数を使って、フィールドの表示と更新を行う。

### `AppearanceTab.js`

-   **役割**:
    -   「外見」に関連するフォームフィールド（性別、年齢、身長、系統、体型、髪型、髪の色、目の色、服装など）を表示する。
    -   画像生成に関連するボタンとロジックもこのコンポーネントに含める。

### `PersonalityTab.js`

-   **役割**:
    -   「性格・口調」に関連するフォームフィールド（性格、職業、口調のタグ選択）を表示する。

## 4. データフロー

1.  `AgentForm.js`がエージェントデータをAPIから取得し、stateとして保持する。
2.  `AgentForm.js`は、アクティブなタブに対応するコンポーネント（例: `BasicInfoTab`）を描画し、必要なデータと更新関数をpropsとして渡す。
3.  ユーザーがフォームフィールドを編集すると、各タブコンポーネントはpropsで渡された更新関数を呼び出し、`AgentForm.js`のstateを更新する。
4.  ユーザーが`TabNavigation.js`でタブを切り替えると、`AgentForm.js`がアクティブなタブのstateを更新し、対応するタブコンポーネントを再描画する。
5.  ユーザーが保存ボタンをクリックすると、`AgentForm.js`がAPIにデータを送信する。

## 5. Mermaidダイアグラムによるコンポーネント関係図

```mermaid
graph TD
    subgraph "AgentForm Component"
        direction LR
        State["(state) agentData, activeTab"]
        TabNav[TabNavigation]
        subgraph "Tab Content"
            direction TB
            BasicTab[BasicInfoTab]
            AppearanceTab[AppearanceTab]
            PersonalityTab[PersonalityTab]
        end
    end

    State -- "props" --> TabNav
    State -- "props" --> BasicTab
    State -- "props" --> AppearanceTab
    State -- "props" --> PersonalityTab

    TabNav -- "onTabChange" --> State
    BasicTab -- "onFieldChange" --> State
    AppearanceTab -- "onFieldChange" --> State
    PersonalityTab -- "onFieldChange" --> State