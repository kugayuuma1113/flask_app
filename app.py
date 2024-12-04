from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user,login_required,logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
import os




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)#整数型で識別,主キー    
    title = db.Column(db.String(50), nullable=False)#文字列型でタイトル,空文字不可
    body = db.Column(db.String(300), nullable=False)#文字列型で本文,300文字以内,空文字不可
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))#日付型で作成日時,空文字不可


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)#整数型で識別,主キー
    username = db.Column(db.String(30), nullable=False, unique=True)#文字列型でユーザー名,空文字不可,重複不可
    password = db.Column(db.String(12), nullable=False)#文字列型でパスワード,空文字不可

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.created_at.desc()).all()#created_atの降順で全ての投稿を取得
        return render_template('index.html', posts=posts)
    else:
        return redirect('/create')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']#name=usernameの値を取得 
        password = request.form['password']#name=passwordの値を取得
        user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))#Userクラスのインスタンスを作成
        db.session.add(user)#データベースに追加
        db.session.commit()#データベースに反映
        return redirect('/login')#リダイレクト
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']#name=usernameの値を取得
        password = request.form['password']#name=passwordの値を取得
        user = User.query.filter_by(username=username).first()#ユーザー名が一致するユーザーを取得
        if  check_password_hash(user.password, password):#パスワードが一致しているか確認
            login_user(user)#ログイン
            return redirect('/')#リダイレクト
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']#name=titleの値を取得
        body = request.form['body']#name=bodyの値を取得
        post = Post(title=title, body=body)#Postクラスのインスタンスを作成
        db.session.add(post)#データベースに追加
        db.session.commit()#データベースに反映
        return redirect('/')#リダイレクト
    return render_template('create.html')

@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form['title']
        post.body = request.form['body']
        db.session.commit()
        return redirect('/')

@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

