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

### バックエンド（pytest）

```
cd backend
venv\Scripts\activate.bat
pip install -r requirements-dev.txt
pytest
```

### フロントエンド（Vitest）

```
cd frontend
npm run test
```

## 開発の進め方

`main`ブランチから機能ごとにブランチを切り、Pull Requestを作成してレビュー・マージする流れで開発しました。バックエンドAPI → フロントエンド画面 → 自動テスト → 仕上げ、の順に段階的に実装しています。
