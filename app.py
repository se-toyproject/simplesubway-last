from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

        print(f"Received signup data: username={username}, email={email}, password={password}")  # 디버깅용

        if not username or not email or not password:
            return jsonify({'error': '모든 칸에 기입하여주십시오.'}), 400

        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            message = "이미 사용중인 이메일입니다." if existing_user.email == email else "이미 사용중인 아이디입니다."
            return jsonify({"error": message}), 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "회원가입이 완료되었습니다."}), 201

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Received login attempt with username: {username} and password: {password}")  # 디버깅용

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['logged_in'] = True
            return jsonify({"message": "로그인이 되었습니다."}), 200
        else:
            return jsonify({"error": "로그인에 실패하였습니다."}), 401

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('logged_in', None)
    return redirect(url_for('search'))

@app.route('/favorites', methods=['POST'])
@login_required
def add_favorite():
    user_id = session['user_id']
    station = request.form.get('station')

    if Favorite.query.filter_by(user_id=user_id, station=station).first():
        return jsonify({"error": "이미 즐겨찾기에 추가된 항목입니다."}), 400

    new_favorite = Favorite(station=station, user_id=user_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"message": "즐겨찾기에 추가되었습니다."}), 201

@app.route('/favorites', methods=['GET'])
@login_required
def get_favorites():
    user_id = session['user_id']
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    favorite_list = [fav.station for fav in favorites]
    return jsonify({"favorites": favorite_list}), 200

@app.route('/favorites_page')
@login_required
def favorites_page():
    return render_template('favorites.html')

@app.route('/favorites/<string:station>', methods=['DELETE'])
@login_required
def remove_favorite(station):
    user_id = session['user_id']
    favorite = Favorite.query.filter_by(user_id=user_id, station=station).first()

    if not favorite:
        return jsonify({"error": "즐겨찾기에서 찾을 수 없습니다."}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "즐겨찾기에서 삭제되었습니다."}), 200

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/search')
def search():
    return render_template('search.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)