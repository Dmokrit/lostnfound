import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lostnfound.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    claimed_items = db.relationship("ClaimedItem", backref="user")

class MissingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    image = db.Column(db.String(200))

class ClaimedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    image = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("signup"))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        session["user"] = username
        flash("Account created successfully!", "success")
        return redirect(url_for("home"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user"] = username
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        flash("Invalid credentials!", "error")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out!", "success")
    return redirect(url_for("home"))

@app.route("/missing", methods=["GET", "POST"])
def missing():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        item_name = request.form.get("item")
        new_item = MissingItem(name=item_name)
        db.session.add(new_item)
        db.session.commit()
        flash("Missing item submitted!", "success")
        return redirect(url_for("missing"))
    items = MissingItem.query.all()
    return render_template("missing.html", items=items)

@app.route("/found", methods=["GET", "POST"])
def found():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        item_name = request.form.get("item")
        file = request.files.get("image")
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_item = FoundItem(name=item_name, image=filename)
        db.session.add(new_item)
        db.session.commit()
        flash("Found item submitted!", "success")
        return redirect(url_for("found"))
    items = FoundItem.query.all()
    return render_template("found.html", items=items)

@app.route("/claim/<int:item_id>")
def claim(item_id):
    if "user" not in session:
        return redirect(url_for("login"))
    item = FoundItem.query.get(item_id)
    if item:
        user = User.query.filter_by(username=session["user"]).first()
        claimed = ClaimedItem(item_name=item.name, image=item.image, user=user)
        db.session.add(claimed)
        db.session.delete(item)
        db.session.commit()
        flash(f"You claimed '{claimed.item_name}'!", "success")
        return redirect(url_for("found"))
    flash("Item not found!", "error")
    return redirect(url_for("found"))

@app.route("/history")
def history():
    if "user" not in session:
        return redirect(url_for("login"))
    user = User.query.filter_by(username=session["user"]).first()
    items = user.claimed_items
    return render_template("history.html", items=items)

if __name__ == "__main__":
    app.run(debug=True)

