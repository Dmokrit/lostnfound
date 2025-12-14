from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLite configuration
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'lostnfound.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload folder configuration
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ------------------ Models ------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class MissingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# ------------------ Login Manager ------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------ Helper Functions ------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None

# ------------------ Routes ------------------
@app.route('/')
def index():
    found_items = FoundItem.query.order_by(FoundItem.created_at.desc()).all()
    missing_items = MissingItem.query.order_by(MissingItem.created_at.desc()).all()
    return render_template('index.html', found_items=found_items, missing_items=missing_items)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please login.")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash("Incorrect username or password.")
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_found = FoundItem.query.filter_by(user_id=current_user.id).order_by(FoundItem.created_at.desc()).all()
    user_missing = MissingItem.query.filter_by(user_id=current_user.id).order_by(MissingItem.created_at.desc()).all()
    return render_template('dashboard.html', user_found=user_found, user_missing=user_missing)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/add_found', methods=['GET', 'POST'])
@login_required
def add_found():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        file = request.files.get('image')
        image_filename = save_file(file)
        item = FoundItem(name=name, description=description, image=image_filename, user_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        flash("Found item added!")
        return redirect(url_for('dashboard'))
    return render_template('add_found.html')

@app.route('/add_missing', methods=['GET', 'POST'])
@login_required
def add_missing():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        file = request.files.get('image')
        image_filename = save_file(file)
        item = MissingItem(name=name, description=description, image=image_filename, user_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        flash("Missing item added!")
        return redirect(url_for('dashboard'))
    return render_template('add_missing.html')

# ------------------ Run App ------------------
if __name__ == '__main__':
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)

