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
        try:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
        except Exception as e:
            return jsonify({'error': 'Invalid input data!'}), 400

        # 입력 값 검증
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required!'}), 400

        # 사용자 이름과 이메일 중복 검사
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            if existing_user.email == email:
                return jsonify({'error': 'Email already exists!'}), 400
            else:
                return jsonify({'error': 'Username already exists!'}), 400

        try:
            # 비밀번호 해시화 (pbkdf2:sha256 사용)
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # 새로운 사용자 생성
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            return jsonify({'message': 'User registered successfully!'}), 201
        except Exception as e:
            db.session.rollback()
            # 오류 메시지를 자세히 출력 (개발 중에만 사용)
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    # GET 요청의 경우, 회원가입 페이지 반환
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
            session['logged_in'] = True  # 로그인 상태를 세션에 저장
            return jsonify({'message': 'Login successful!'}), 200
        else:
            return jsonify({'error': 'Invalid credentials!'}), 401

    # GET 요청의 경우, 로그인 페이지 반환
    return render_template('login.html')

@app.route('/logout')
def logout():
    # 세션에서 사용자 정보 제거
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('logged_in', None)
    return redirect(url_for('search'))

@app.route('/favorites')
def favorites():
    return render_template('favorites.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/search')
def search():
    return render_template('search.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)