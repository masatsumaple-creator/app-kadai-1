# AWSデプロイ手順

本アプリをAWS EC2にデプロイし、動作確認を行った際の構成と手順をまとめる。確認後はコスト発生を避けるため該当リソースは削除済みだが、同じ手順で再現できる。

## 構成

| 項目 | 内容 |
|---|---|
| リージョン | ap-northeast-1（東京） |
| インスタンス | EC2 `t2.micro`（無料利用枠）、Amazon Linux 2023 |
| Webサーバー | nginx（フロントエンドの静的ファイル配信 + `/api/` をバックエンドへリバースプロキシ） |
| アプリケーションサーバー | Flask + gunicorn（systemdサービスとして常駐・自動再起動） |
| データベース | MariaDB（MySQL互換、インスタンス内のみで稼働、外部非公開） |
| ネットワーク | デフォルトVPC上のパブリックサブネットにEC2を配置。セキュリティグループでSSH(22)は自宅IPのみ、HTTP(80)は全体公開 |

```
[ブラウザ] --HTTP(80)--> [nginx]
                           ├─ 静的配信: /opt/app/frontend/dist (Vue build)
                           └─ /api/* をリバースプロキシ --> [gunicorn:8000 (Flask)] --> [MariaDB:3306 (localhost)]
```

### 注意: MySQLではなくMariaDBを使用

Amazon Linux 2023の標準リポジトリにMySQL Community Serverが無いため、MySQL互換のMariaDBで代替した。SQLAlchemy/PyMySQL経由のアクセスであり、アプリケーションコードに変更は不要。

## 手順

### 1. ネットワーク・インスタンス準備

```bash
# キーペア作成
aws ec2 create-key-pair --region ap-northeast-1 --key-name kakeibo-deploy-key \
  --query "KeyMaterial" --output text > kakeibo-deploy-key.pem
chmod 400 kakeibo-deploy-key.pem

# セキュリティグループ作成（SSHは自分のIPのみ、HTTPは公開）
aws ec2 create-security-group --region ap-northeast-1 \
  --group-name kakeibo-app-sg --description "kakeibo app" --vpc-id <VPC_ID>
aws ec2 authorize-security-group-ingress --region ap-northeast-1 --group-id <SG_ID> \
  --protocol tcp --port 22 --cidr <自分のIP>/32
aws ec2 authorize-security-group-ingress --region ap-northeast-1 --group-id <SG_ID> \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

# インスタンス起動（Amazon Linux 2023, t2.micro）
aws ec2 run-instances --region ap-northeast-1 \
  --image-id <AL2023_AMI_ID> --instance-type t2.micro \
  --key-name kakeibo-deploy-key --security-group-ids <SG_ID> \
  --subnet-id <SUBNET_ID> --associate-public-ip-address
```

### 2. パッケージインストール（SSH接続後）

```bash
sudo dnf update -y
sudo dnf install -y git python3.11 python3.11-pip nginx mariadb105-server
# AL2023標準のnodejsは18系でVite 8のビルドに非対応のため22系を使用
sudo dnf remove -y nodejs nodejs-npm
sudo dnf install -y nodejs22 nodejs22-npm
```

### 3. データベース準備

```bash
sudo systemctl enable --now mariadb
sudo mysql -e "
  CREATE DATABASE IF NOT EXISTS kakeibo CHARACTER SET utf8mb4;
  CREATE USER IF NOT EXISTS 'kakeibo_user'@'localhost' IDENTIFIED BY 'kakeibo_pass';
  GRANT ALL PRIVILEGES ON kakeibo.* TO 'kakeibo_user'@'localhost';
  FLUSH PRIVILEGES;
"
```

### 4. バックエンド

```bash
sudo git clone https://github.com/masatsumaple-creator/app-kadai-1.git /opt/app
sudo chown -R ec2-user:ec2-user /opt/app
cd /opt/app/backend

python3.11 -m venv venv
venv/bin/pip install -r requirements.txt gunicorn pymysql cryptography

echo "DATABASE_URL=mysql+pymysql://kakeibo_user:kakeibo_pass@127.0.0.1:3306/kakeibo" > .env
export FLASK_APP=run.py
venv/bin/flask db upgrade
venv/bin/flask seed
```

systemdサービス化（`/etc/systemd/system/kakeibo-backend.service`）:

```ini
[Unit]
Description=Kakeibo Flask backend
After=network.target mariadb.service

[Service]
WorkingDirectory=/opt/app/backend
Environment="DATABASE_URL=mysql+pymysql://kakeibo_user:kakeibo_pass@127.0.0.1:3306/kakeibo"
ExecStart=/opt/app/backend/venv/bin/gunicorn -w 2 -b 127.0.0.1:8000 run:app
Restart=always
User=ec2-user

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kakeibo-backend
```

### 5. フロントエンド

API接続先を相対パス`/api`に変更してビルドする（nginxが同一オリジンでリバースプロキシするため）。

```bash
cd /opt/app/frontend
echo "VITE_API_BASE_URL=/api" > .env.production
npm ci
npm run build
```

### 6. nginx設定

`/etc/nginx/conf.d/kakeibo.conf`:

```nginx
server {
    listen 80;
    server_name _;

    root /opt/app/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
sudo rm -f /etc/nginx/conf.d/default.conf
sudo systemctl enable --now nginx
sudo systemctl restart nginx
```

### 7. 動作確認

```bash
curl http://<EC2のパブリックIP>/api/health
# => {"status": "ok"}
```

ブラウザで `http://<EC2のパブリックIP>/` を開き、収支一覧・カテゴリ管理・集計・予算の各画面が正常に動作することを確認した。

## 後片付け

課金継続を避けるため、確認後に以下を削除した。

```bash
aws ec2 terminate-instances --region ap-northeast-1 --instance-ids <INSTANCE_ID>
aws ec2 delete-security-group --region ap-northeast-1 --group-id <SG_ID>
aws ec2 delete-key-pair --region ap-northeast-1 --key-name kakeibo-deploy-key
```

再度公開する場合は、本手順を再実行すればよい。EC2を再利用する前提であれば、Elastic IPの割り当てやHTTPS（Let's Encrypt等）対応も検討する。
