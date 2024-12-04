# app.py の中で定義された Flask アプリケーションと db をインポート
from app import app, db

# アプリケーションコンテキストを設定
with app.app_context():
    db.create_all()
