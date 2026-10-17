# 家計簿アプリ（app-kadai-1）

講座課題として1から作成した、個人用の家計簿Webアプリです。日々の収支を記録し、カテゴリ別・月別に集計、グラフ表示や予算管理、CSV入出力ができます。

企画・要件定義の詳細は [docs/proposal.md](docs/proposal.md)・[docs/requirements.md](docs/requirements.md) を、AWSへのデプロイ手順は [docs/deployment.md](docs/deployment.md) を参照してください。

## 主な機能

- 収支データの登録・一覧・編集・削除
- 期間・カテゴリ・キーワードでの検索・絞り込み
- カテゴリ管理（追加・編集・削除、初期カテゴリあり）
- 月別・カテゴリ別の集計表示、グラフ表示（円グラフ・棒グラフ）
- カテゴリ別の予算設定と使用状況の可視化（進捗バー）
- 収支データのCSVエクスポート／インポート

個人利用（単一ユーザー）を前提としており、ログイン機能はありません。

## 技術スタック

| レイヤー | 技術 | バージョン |
|---|---|---|
| 実行環境 | Python | 3.14 |
| 実行環境 | Node.js | 24.x |
| フロントエンド | Vue.js | 3.5 |
| フロントエンド | Vite | 8.3 |
| フロントエンド | Vue Router | 4.6 |
| フロントエンド | Axios | 1.20 |
| フロントエンド | Chart.js / vue-chartjs | 4.5 / 5.3 |
| フロントエンド | @vuepic/vue-datepicker | 14.0 |
| バックエンド | Flask | 3.1 |
| バックエンド | Flask-SQLAlchemy | 3.1 |
| バックエンド | Flask-Migrate | 4.0 |
| バックエンド | Flask-Cors | 5.0 |
| バックエンド | PyMySQL | 1.1 |
| データベース | MySQL | 8.0（本番/Docker）、開発時はMariaDB 10.5互換で動作確認済み |
| テスト | pytest | 8.3 |
| テスト | Vitest / @vue/test-utils | 5.0 / 2.5 |

正確なバージョン指定は [backend/requirements.txt](backend/requirements.txt)・[frontend/package.json](frontend/package.json) を参照してください。

## ディレクトリ構成

```
app-kadai-1/
├── backend/        Flask API
│   ├── app/         アプリ本体（models, routes, config）
│   ├── migrations/  Alembicマイグレーション
│   └── tests/       pytestテスト
├── frontend/        Vue SPA
│   └── src/
│       ├── api/      バックエンドAPI呼び出し
│       ├── views/     画面（収支一覧・カテゴリ管理・集計・予算）
│       └── components/ 共通コンポーネント
└── docs/            企画書・要件定義書
```

## システム構成

フロントエンド（Vue SPA）とバックエンド（Flask API）を分離し、REST APIで連携する構成です。

### ローカル開発環境

```mermaid
flowchart LR
    Browser["ブラウザ"] -->|"http://localhost:5173"| Vite["Vite Dev Server<br/>(Vue 3 SPA)"]
    Vite -->|"Axios: /api/*<br/>http://127.0.0.1:5000/api"| Flask["Flask Dev Server<br/>(python run.py)"]
    Flask -->|SQLAlchemy| DB[("MySQL")]
```

### AWS本番環境（デプロイ確認時）

```mermaid
flowchart LR
    Browser["ブラウザ"] -->|"http://&lt;EC2 Public IP&gt;"| Nginx["nginx :80"]
    Nginx -->|"静的ファイル配信"| Dist["Vue build (dist/)"]
    Nginx -->|"/api/* を<br/>proxy_pass"| Gunicorn["gunicorn :8000<br/>(Flask, systemdで常駐)"]
    Gunicorn -->|SQLAlchemy| MariaDB[("MariaDB :3306<br/>(localhostのみ)")]
```

詳細は [docs/deployment.md](docs/deployment.md) を参照してください。

## 画面

| 画面 | パス | できること |
|---|---|---|
| 収支一覧 | `/` | 収支データの登録・編集・削除、期間/カテゴリ/キーワードでの絞り込み、CSV入出力 |
| カテゴリ管理 | `/categories` | カテゴリの登録・編集・削除 |
| 集計・レポート | `/summary` | 月別の収入・支出・差額、カテゴリ別支出の円グラフ、月別収支推移の棒グラフ |
| 予算設定 | `/budgets` | カテゴリ別の月間予算登録、使用状況の進捗バー表示 |

## 主要API

バックエンドは `/api` 配下にREST APIを提供しています。全エンドポイントの一覧は [docs/requirements.md の API一覧](docs/requirements.md#7-api一覧概要案) を参照してください。

| メソッド | パス | 概要 |
|---|---|---|
| GET | `/api/transactions` | 収支データ一覧（絞り込み対応） |
| POST | `/api/transactions` | 収支データ登録 |
| GET | `/api/categories` | カテゴリ一覧 |
| GET | `/api/summary?month=YYYY-MM` | 月別・カテゴリ別集計 |
| GET | `/api/budgets?month=YYYY-MM` | 予算と使用状況の一覧 |

## 動作確認動画


https://github.com/user-attachments/assets/272d7c83-b91e-42dc-a9a1-3099443f531d




## セットアップ

### 1. データベース（MySQL）を用意する

ローカルにMySQLがない場合は、Dockerで簡単に用意できます。

```
docker run -d --name kakeibo-mysql ^
  -e MYSQL_ROOT_PASSWORD=rootpass ^
  -e MYSQL_DATABASE=kakeibo ^
  -e MYSQL_USER=kakeibo_user ^
  -e MYSQL_PASSWORD=kakeibo_pass ^
  -p 3306:3306 mysql:8
```

### 2. バックエンド（Flask）

**Windowsでは、コマンドプロンプト（cmd）での実行を推奨します。** PowerShellではスクリプト実行がデフォルトで無効になっており、`venv`の有効化や`npm`コマンドがブロックされる場合があります。

```
cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
```

`.env`の`DATABASE_URL`を環境に合わせて編集します（上記Dockerの例の場合）:

```
DATABASE_URL=mysql+pymysql://kakeibo_user:kakeibo_pass@127.0.0.1:3306/kakeibo
```

テーブル作成・初期カテゴリ投入・サーバー起動:

```
set FLASK_APP=run.py
flask db upgrade
flask seed
python run.py
```

`http://127.0.0.1:5000/api/health` で `{"status": "ok"}` が返れば起動成功です。

### 3. フロントエンド（Vue）

別のターミナルで:

```
cd frontend
npm install
npm run dev
```

表示される `http://localhost:5173` をブラウザで開いてください。

## テストの実行

### バックエンド（pytest、24件）

各APIエンドポイントが正しいレスポンスを返すか、想定通りに動作するかを確認するテストです。

- 収支データ・カテゴリ・予算のCRUD（登録・一覧・更新・削除）
- 不正な入力（金額が負の数、存在しないカテゴリなど）に対するエラー処理
- カテゴリ削除時に、紐づく収支データが「未分類」になり、予算が連動して削除されること
- 月別集計・グラフ用データの計算結果
- CSVのエクスポート・インポート（一部の行が不正な場合の挙動を含む）

```
cd backend
venv\Scripts\activate.bat
pip install -r requirements-dev.txt
pytest
```

### フロントエンド（Vitest、19件）

画面（コンポーネント）が表示すべき内容を正しく表示し、ボタン操作で意図した処理が呼ばれるかを確認するテストです。バックエンドへの通信はモック（偽のAPI応答）に置き換えてテストしています。

- 一覧の表示、データが0件のときの表示、通信エラー時の表示
- 登録・削除ボタンを押したときに正しい内容でAPIが呼ばれること
- 入力エラー時にエラーメッセージが表示されること
- 予算の進捗率に応じて「順調」「もうすぐ上限」「予算超過」の表示が切り替わること

```
cd frontend
npm run test
```

## よく使うコマンド

| やりたいこと | コマンド（`backend`ディレクトリで実行） |
|---|---|
| バックエンド起動 | `python run.py` |
| DBスキーマを最新化 | `flask db upgrade` |
| 初期カテゴリを投入 | `flask seed` |
| モデル変更後のマイグレーション作成 | `flask db migrate -m "説明"` |
| バックエンドのテスト実行 | `pytest` |

| やりたいこと | コマンド（`frontend`ディレクトリで実行） |
|---|---|
| フロントエンド起動（開発用） | `npm run dev` |
| 本番用にビルド | `npm run build` |
| フロントエンドのテスト実行 | `npm run test` |

## 開発の進め方

`main`ブランチから機能ごとにブランチを切り、Pull Requestを作成してレビュー・マージする流れで開発しました。バックエンドAPI → フロントエンド画面 → 自動テスト → 仕上げ、の順に段階的に実装しています。
