from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

# In-memory storage (replace with DB for production)
users = {}  # username: password
missing_items = []
found_items = []

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
        if username in users:
            return render_template("signup.html", error="Username already exists")
        users[username] = password
        session["user"] = username
        return redirect(url_for("home"))
    return render_template("signup.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username] == password:
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
        item = request.form.get("item")
        missing_items.append(item)
        return redirect(url_for("missing"))
    return render_template("missing.html", items=missing_items)

# Submit found item
@app.route("/found", methods=["GET", "POST"])
def found():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        item = request.form.get("item")
        found_items.append(item)
        return redirect(url_for("found"))
    return render_template("found.html", items=found_items)

# Claim a found item
@app.route("/claim/<item>")
def claim(item):
    if "user" not in session:
        return redirect(url_for("login"))
    if item in found_items:
        found_items.remove(item)
        return redirect(url_for("found"))
    return "Item not found"

if __name__ == "__main__":
    app.run(debug=True)

