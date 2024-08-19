from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

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

        # 새로운 사용자 생성
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully!'}), 201

    return render_template('signup.html')

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
    app.run(debug=True)
