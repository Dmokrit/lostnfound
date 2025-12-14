from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.utils import secure_filename
import sqlite3, os, hashlib

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS lost (id INTEGER PRIMARY KEY, name TEXT, description TEXT, photo TEXT, user TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS found (id INTEGER PRIMARY KEY, name TEXT, description TEXT, photo TEXT, claimed INTEGER DEFAULT 0, claimed_by TEXT)''')
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid login!")
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = hash_password(request.form['password'])
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?,?)', (username,password))
        conn.commit()
        flash("Signup successful! Login now.")
    except sqlite3.IntegrityError:
        flash("Username already exists!")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    lost_items = conn.execute('SELECT * FROM lost').fetchall()
    found_items = conn.execute('SELECT * FROM found').fetchall()
    return render_template('dashboard.html', lost_items=lost_items, found_items=found_items, username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/report_lost', methods=['POST'])
def report_lost():
    if 'username' not in session:
        return redirect(url_for('login'))
    name = request.form['name']
    desc = request.form['description']
    file = request.files['photo']
    filename = secure_filename(file.filename) if file else None
    if filename:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    conn = get_db()
    conn.execute('INSERT INTO lost (name, description, photo, user) VALUES (?,?,?,?)',
                 (name, desc, filename, session['username']))
    conn.commit()
    return redirect(url_for('dashboard'))

@app.route('/report_found', methods=['POST'])
def report_found():
    if 'username' not in session:
        return redirect(url_for('login'))
    name = request.form['name']
    desc = request.form['description']
    file = request.files['photo']
    filename = secure_filename(file.filename) if file else None
    if filename:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    conn = get_db()
    conn.execute('INSERT INTO found (name, description, photo) VALUES (?,?,?)', (name, desc, filename))
    conn.commit()
    return redirect(url_for('dashboard'))

@app.route('/claim/<int:item_id>')
def claim(item_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('UPDATE found SET claimed=1, claimed_by=? WHERE id=?', (session['username'], item_id))
    conn.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

