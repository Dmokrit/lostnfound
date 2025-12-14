from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Make sure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('lostnfound.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            image TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/items')
def items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('items.html', items=items)

@app.route('/post', methods=['GET', 'POST'])
def post_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image_file = request.files['image']
        filename = None
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = get_db_connection()
        conn.execute('INSERT INTO items (name, description, image, timestamp) VALUES (?, ?, ?, ?)',
                     (name, description, filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return redirect(url_for('items'))
    return render_template('post_item.html')

if __name__ == '__main__':
    app.run(debug=True)

