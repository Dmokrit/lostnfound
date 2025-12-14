from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key"

# In-memory data stores
users = []  # {username, password}
found_items = []  # {name, image, submitted_by}
missing_items = []  # {name, description, submitted_by}

UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------- ROUTES -------------------- #

@app.route('/')
def index():
    return render_template('index.html', found_items=found_items, missing_items=missing_items)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for('signup'))

        if any(u['username'] == username for u in users):
            flash("Username already exists.", "error")
            return redirect(url_for('signup'))

        users.append({'username': username, 'password': password})
        flash("Signup successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            session['username'] = username
            flash("Logged in successfully.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))

    user_found = [item for item in found_items if item['submitted_by'] == session['username']]
    user_missing = [item for item in missing_items if item['submitted_by'] == session['username']]

    return render_template('dashboard.html', user_found=user_found, user_missing=user_missing)


@app.route('/found', methods=['GET', 'POST'])
def found():
    if 'username' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        item_name = request.form.get('item')
        image = request.files.get('image')

        if not item_name:
            flash("Item name is required.", "error")
            return redirect(url_for('found'))

        image_filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = os.path.join('uploads', filename)

        found_items.append({
            'name': item_name,
            'image': image_filename,
            'submitted_by': session['username']
        })

        flash("Item submitted successfully!", "success")
        return redirect(url_for('found'))

    return render_template('found.html', items=found_items)


@app.route('/missing', methods=['GET', 'POST'])
def missing():
    if 'username' not in session:
        flash("You need to login first.", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        item_name = request.form.get('item')
        description = request.form.get('description')

        if not item_name or not description:
            flash("Both name and description are required.", "error")
            return redirect(url_for('missing'))

        missing_items.append({
            'name': item_name,
            'description': description,
            'submitted_by': session['username']
        })

        flash("Missing item reported successfully!", "success")
        return redirect(url_for('missing'))

    return render_template('missing.html', items=missing_items)


if __name__ == '__main__':
    app.run(debug=True)

