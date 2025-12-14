from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecretkey"

# SQLite database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lostnfound.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database models
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

class ClaimedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# Home
@app.route("/")
def home():
    return render_template("home.html")

# Sign-Up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            return render_template("signup.html", error="Username already exists")
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        session["user"] = username
        return redirect(url_for("home"))
    return render_template("signup.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# Submit missing item
@app.route("/missing", methods=["GET", "POST"])
def missing():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        item_name = request.form.get("item")
        new_item = MissingItem(name=item_name)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for("missing"))
    items = MissingItem.query.all()
    return render_template("missing.html", items=items)

# Submit found item
@app.route("/found", methods=["GET", "POST"])
def found():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        item_name = request.form.get("item")
        new_item = FoundItem(name=item_name)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for("found"))
    items = FoundItem.query.all()
    return render_template("found.html", items=items)

# Claim a found item
@app.route("/claim/<int:item_id>")
def claim(item_id):
    if "user" not in session:
        return redirect(url_for("login"))

    item = FoundItem.query.get(item_id)
    if item:
        user = User.query.filter_by(username=session["user"]).first()
        claimed = ClaimedItem(item_name=item.name, user=user)
        db.session.add(claimed)
        db.session.delete(item)
        db.session.commit()
        return redirect(url_for("found"))

    return "Item not found"

# View claimed items history
@app.route("/history")
def history():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()
    items = user.claimed_items
    return render_template("history.html", items=items)

if __name__ == "__main__":
    app.run(debug=True)

