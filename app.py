from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# 세션을 위한 비밀 키 설정
app.config['SECRET_KEY'] = 'your_secret_key_here'

# SQLite 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 사용자 모델 정의
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# 데이터베이스 초기화
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('search'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # 이메일로 사용자 검색
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return jsonify({'error': 'User already exists!'}), 400

        # 비밀번호 해시화
        hashed_password = generate_password_hash(password, method='sha256')

        # 새로운 사용자 생성
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully!'}), 201

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # 사용자 이름으로 사용자 검색
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # 로그인 성공, 세션에 사용자 정보 저장
            session['user_id'] = user.id
            session['username'] = user.username
            return jsonify({'message': 'Login successful!'}), 200
        else:
            return jsonify({'error': 'Invalid credentials!'}), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    # 세션에서 사용자 정보 제거
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('favorites.html')

@app.route('/results')
def results():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('results.html')

@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
