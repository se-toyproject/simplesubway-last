from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db) 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    favorites = db.Column(db.JSON, default=lambda: [])

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
            return jsonify({'error': '입력이 잘못되었습니다.'}), 400

        if not username or not email or not password:
            return jsonify({'error': '모든 칸에 기입하여 주십시오.'}), 400

        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            if existing_user.email == email:
                return jsonify({'error': '이미 사용중인 이메일입니다.'}), 400
            else:
                return jsonify({'error': '이미 사용중인 아이디입니다.'}), 400

        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, email=email, password=hashed_password, favorites=[])
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'message': '회원가입이 완료되었습니다.'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['logged_in'] = True
            return jsonify({'message': '로그인이 되었습니다.'}), 200
        else:
            return jsonify({'error': '로그인에 실패하였습니다.'}), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('logged_in', None)
    return redirect(url_for('search'))

@app.route('/favorites', methods=['GET', 'POST', 'DELETE'])
def favorites():
    if 'user_id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404

    if request.method == 'GET':
        return jsonify(user.favorites or [])

    elif request.method == 'POST':
        new_favorite = request.json.get('favorite')
        if new_favorite and new_favorite not in user.favorites:
            user.favorites.append(new_favorite)
            db.session.commit()
        return jsonify(user.favorites)

    elif request.method == 'DELETE':
        favorite_to_remove = request.json.get('favorite')
        if favorite_to_remove in user.favorites:
            user.favorites.remove(favorite_to_remove)
            db.session.commit()
        return jsonify(user.favorites)

    return render_template('favorites.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/search')
def search():
    return render_template('search.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)