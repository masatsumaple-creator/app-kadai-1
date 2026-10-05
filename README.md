# app-kadai-1

個人用家計簿Webアプリ（講座課題）。詳細は [docs/requirements.md](docs/requirements.md) を参照。

## 技術スタック

- フロントエンド: Vue.js 3 + Vite
- バックエンド: Python + Flask
- データベース: MySQL

## セットアップ

### バックエンド

```
cd backend
python -m venv venv
./venv/Scripts/activate  # Windows
pip install -r requirements.txt
cp .env.example .env  # DATABASE_URL を環境に合わせて編集
python run.py
```

`http://127.0.0.1:5000/api/health` で動作確認できます。

### フロントエンド

```
cd frontend
npm install
npm run dev
```
