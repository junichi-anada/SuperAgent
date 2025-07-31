# Super Agent コンポーネント設計

## 概要
このドキュメントでは、Super Agentプロジェクトにおけるフロントエンドコンポーネントの設計方針を、Atomic Designの考え方に基づいて定義します。

## Atomic Design アーキテクチャ

### 1. Atoms（原子）
最小単位の再利用可能なコンポーネント。単一の責任を持ち、プロジェクト全体で一貫性を保つための基礎要素。

#### 具体例：
- **Button**: プライマリー、セカンダリー、デンジャーなどのバリエーション
- **Input**: テキスト入力、パスワード入力、検索ボックス
- **Label**: フォームラベル、タグラベル
- **Icon**: SVGアイコンコンポーネント（送信、設定、削除など）
- **Avatar**: ユーザー/エージェントのプロフィール画像表示
- **Spinner**: ローディングインジケーター
- **Badge**: ステータス表示（オンライン、新着など）
- **Typography**: 見出し、本文、キャプションなどのテキストスタイル

### 2. Molecules（分子）
複数のAtomsを組み合わせた、より複雑な機能を持つコンポーネント。

#### 具体例：
- **FormField**: Label + Input + エラーメッセージの組み合わせ
- **SearchBar**: Icon + Input + Buttonの組み合わせ
- **MessageBubble**: Avatar + テキスト + タイムスタンプ
- **AgentCard**: Avatar + 名前 + 説明文 + Badgeの組み合わせ
- **NavigationItem**: Icon + Label + 選択状態表示
- **Modal**: オーバーレイ + コンテンツエリア + 閉じるボタン
- **Dropdown**: トリガーボタン + メニューリスト
- **ToggleSwitch**: ラベル + スイッチコンポーネント

### 3. Organisms（有機体）
複数のMoleculesやAtomsを組み合わせた、独立した機能を持つセクション。

#### 具体例：
- **Header**: ロゴ + NavigationMenu + UserProfile
- **ChatInterface**: MessageList + MessageInput + TypingIndicator
- **AgentCreationForm**: 複数のFormField + 画像アップロード + 送信ボタン
- **AgentGallery**: AgentCardのグリッド表示 + フィルター機能
- **Sidebar**: NavigationItemのリスト + ユーザー情報
- **MessageInput**: テキストエリア + 送信ボタン + 画像添付ボタン
- **UserProfile**: Avatar + ユーザー情報 + 編集ボタン
- **ChatHistory**: メッセージリスト + 日付区切り + スクロール機能

### 4. Templates（テンプレート）
ページの構造を定義するレイアウトコンポーネント。実際のコンテンツは含まない。

#### 具体例：
- **MainLayout**: Header + Sidebar + メインコンテンツエリア
- **AuthLayout**: 認証画面用のセンタリングレイアウト
- **ChatLayout**: チャットインターフェース専用のレイアウト
- **DashboardLayout**: ダッシュボード用のグリッドレイアウト

### 5. Pages（ページ）
Templatesに実際のデータを流し込んで完成したページコンポーネント。

#### 具体例：
- **HomePage**: ランディングページ
- **LoginPage**: ログイン画面
- **SignupPage**: サインアップ画面
- **DashboardPage**: ユーザーダッシュボード
- **ChatPage**: チャット画面
- **AgentCreationPage**: エージェント作成画面
- **AgentListPage**: エージェント一覧画面
- **SettingsPage**: 設定画面

## ディレクトリ構造
```
frontend/
├── components/
│   ├── atoms/
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.styles.ts
│   │   │   └── index.ts
│   │   ├── Input/
│   │   ├── Avatar/
│   │   └── ...
│   ├── molecules/
│   │   ├── FormField/
│   │   ├── MessageBubble/
│   │   └── ...
│   ├── organisms/
│   │   ├── Header/
│   │   ├── ChatInterface/
│   │   └── ...
│   └── templates/
│       ├── MainLayout/
│       ├── AuthLayout/
│       └── ...
├── pages/
│   ├── index.tsx
│   ├── login.tsx
│   ├── chat/[agentId].tsx
│   └── ...
└── styles/
    ├── theme.ts
    └── globals.css
```

## 設計原則

1. **単一責任の原則**: 各コンポーネントは1つの明確な責任を持つ
2. **再利用性**: 特にAtoms、Moleculesレベルでは高い再利用性を確保
3. **疎結合**: コンポーネント間の依存関係を最小限に保つ
4. **Props Interface**: TypeScriptを使用し、全てのコンポーネントに明確な型定義を行う
5. **スタイリング**: Tailwind CSSまたはCSS-in-JSを使用し、コンポーネントごとにスタイルをカプセル化
6. **アクセシビリティ**: ARIA属性、キーボードナビゲーション対応を考慮
7. **レスポンシブデザイン**: モバイルファーストアプローチで設計

## 実装優先順位

### Phase 1（MVP）
1. 必須Atoms: Button, Input, Avatar, Typography
2. 必須Molecules: FormField, MessageBubble, AgentCard
3. 必須Organisms: Header, ChatInterface, AgentCreationForm
4. 必須Templates: MainLayout, AuthLayout

### Phase 2（機能拡張）
1. 追加Atoms: Badge, Icon, Spinner
2. 追加Molecules: SearchBar, Dropdown, Modal
3. 追加Organisms: AgentGallery, Sidebar, ChatHistory

## 状態管理
- グローバル状態: Redux Toolkit または Zustand
- ローカル状態: React Hooks (useState, useReducer)
- サーバー状態: React Query または SWR

## テスト戦略
- Unit Tests: 各Atomsコンポーネント
- Integration Tests: Molecules、Organisms
- E2E Tests: 主要なユーザーフロー