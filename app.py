from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# MySQL 데이터베이스 연결
db_user = os.environ.get('MYSQLUSER', 'root')
db_password = os.environ.get('MYSQLPASSWORD', '')
db_host = os.environ.get('MYSQLHOST', 'localhost')
db_port = os.environ.get('MYSQLPORT', '3306')
db_name = os.environ.get('MYSQLDATABASE', 'myapp')

DATABASE_URL = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

def init_db():
    with app.app_context():
        db.create_all()

def is_admin():
    return session.get('username') == 'admin'

@app.route('/')
def index():
    if 'username' in session:
        if is_admin():
            return redirect(url_for('admin'))
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/check-id', methods=['POST'])
def check_id():
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()
    return jsonify({'available': user is None})

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception:
        db.session.rollback()
        return redirect(url_for('error', message='이미 존재하는 아이디입니다.'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'admin':
        if ADMIN_PASSWORD and password == ADMIN_PASSWORD:
            session['username'] = 'admin'
            return redirect(url_for('admin'))
        return redirect(url_for('error', message='아이디 또는 비밀번호가 틀렸습니다.'))

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        session['username'] = username
        return redirect(url_for('dashboard'))
    return redirect(url_for('error', message='아이디 또는 비밀번호가 틀렸습니다.'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/admin')
def admin():
    if not is_admin():
        return redirect(url_for('index'))
    users = User.query.order_by(User.id).all()
    return render_template('admin.html', users=users)

@app.route('/admin/add', methods=['POST'])
def admin_add():
    if not is_admin():
        return redirect(url_for('index'))
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    if not username or not password:
        return redirect(url_for('error', message='아이디와 비밀번호를 입력하세요.'))
    try:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return redirect(url_for('error', message='이미 존재하는 아이디입니다.'))
    return redirect(url_for('admin'))

@app.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
def admin_edit(user_id):
    if not is_admin():
        return redirect(url_for('index'))
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('admin'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        try:
            user.username = username
            user.password = password
            db.session.commit()
        except Exception:
            db.session.rollback()
            return redirect(url_for('error', message='이미 존재하는 아이디입니다.'))
        return redirect(url_for('admin'))

    return render_template('admin_edit.html', user=user)

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
def admin_delete(user_id):
    if not is_admin():
        return redirect(url_for('index'))
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/error')
def error():
    message = request.args.get('message', '알 수 없는 오류가 발생했습니다.')
    return render_template('error.html', message=message)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
