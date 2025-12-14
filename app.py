from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for session and flash messages

# Sample in-memory user storage (replace with DB later if needed)
users = [
    {"username": "admin", "password": "admin123"},
    {"username": "user1", "password": "pass123"}
]

# Sample in-memory lost and found items
found_items = []
missing_items = []

@app.route('/')
def home():
    return render_template('home.html', found_items=found_items, missing_items=missing_items)

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check for empty fields
        if not username or not password:
            flash("Please enter both username and password.", "error")
            return redirect(url_for('login'))

        # Validate credentials
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            session['username'] = username
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return redirect(url_for('signup'))

        # Check if username exists
        if any(u['username'] == username for u in users):
            flash("Username already exists.", "error")
            return redirect(url_for('signup'))

        users.append({"username": username, "password": password})
        flash("Account created successfully! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Please login first.", "error")
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['username'],
                           found_items=found_items, missing_items=missing_items)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

# ---------------- ADD FOUND ITEM ----------------
@app.route('/found', methods=['GET', 'POST'])
def found():
    if 'username' not in session:
        flash("Please login first.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash("Item name is required.", "error")
            return redirect(url_for('found'))

        found_items.append({"name": name, "description": description, "user": session['username']})
        flash("Found item submitted successfully.", "success")
        return redirect(url_for('dashboard'))

    return render_template('found.html')

# ---------------- ADD MISSING ITEM ----------------
@app.route('/missing', methods=['GET', 'POST'])
def missing():
    if 'username' not in session:
        flash("Please login first.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash("Item name is required.", "error")
            return redirect(url_for('missing'))

        missing_items.append({"name": name, "description": description, "user": session['username']})
        flash("Missing item reported successfully.", "success")
        return redirect(url_for('dashboard'))

    return render_template('missing.html')

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)

