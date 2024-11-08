from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_cors import CORS
import logging
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({"error": "로그인이 필요합니다."}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('search'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            app.logger.warning("회원가입 실패: 필수 정보 누락")
            return jsonify({'error': '모든 칸에 기입하여주십시오.'}), 400
        
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            message = "이미 사용중인 이메일입니다." if existing_user.email == email else "이미 사용중인 아이디입니다."
            app.logger.warning(f"회원가입 실패: {message}")
            return jsonify({"error": message}), 400
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        app.logger.info(f"새 사용자 등록: {username}")
        return jsonify({"message": "회원가입이 완료되었습니다."}), 201
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['logged_in'] = True
            return jsonify({"message": "로그인이 되었습니다."}), 200
        else:
            app.logger.warning(f"로그인 실패: 사용자 {username}")
            return jsonify({"error": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('search'))

@app.route('/favorites', methods=['POST'])
@login_required
def add_favorite():
    try:
        user_id = session['user_id']
        station = request.form.get('station')

        if not station:
            return jsonify({"error": "역 이름이 제공되지 않았습니다."}), 400

        if Favorite.query.filter_by(user_id=user_id, station=station).first():
            return jsonify({"error": "이미 즐겨찾기에 추가된 항목입니다."}), 400

        new_favorite = Favorite(station=station, user_id=user_id)
        db.session.add(new_favorite)
        db.session.commit()

        return jsonify({"message": "즐겨찾기에 추가되었습니다."}), 201
    except Exception as e:
        app.logger.error(f"Add favorite error: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

@app.route('/favorites', methods=['GET'])
@login_required
def get_favorites():
    try:
        user_id = session['user_id']
        favorites = Favorite.query.filter_by(user_id=user_id).all()
        favorite_list = [fav.station for fav in favorites]
        return jsonify({"favorites": favorite_list}), 200
    except Exception as e:
        app.logger.error(f"Get favorites error: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

@app.route('/favorites_page')
@login_required
def favorites_page():
    return render_template('favorites.html')

@app.route('/favorites/<string:station>', methods=['DELETE'])
@login_required
def remove_favorite(station):
    try:
        user_id = session['user_id']
        favorite = Favorite.query.filter_by(user_id=user_id, station=station).first()
        if not favorite:
            return jsonify({"error": "즐겨찾기에서 찾을 수 없습니다."}), 404

        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "즐겨찾기에서 삭제되었습니다."}), 200
    except Exception as e:
        app.logger.error(f"Remove favorite error: {str(e)}")
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 error: {str(error)}")
    return jsonify({"error": "내부 서버 오류가 발생했습니다."}), 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)