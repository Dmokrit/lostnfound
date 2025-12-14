from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # max 16 MB files

# In-memory storage (replace later with a real database)
found_items = []

# Home page
@app.route('/')
def index():
    return render_template('index.html', items=found_items)

# Submit found item
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        # Handle image
        image_file = request.files.get('image')
        filename = None
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Save item
        item = {
            'id': len(found_items) + 1,
            'name': name,
            'description': description,
            'image': filename,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        found_items.append(item)
        return redirect(url_for('index'))

    return render_template('submit.html')

# View single item
@app.route('/found/<int:item_id>')
def found(item_id):
    item = next((x for x in found_items if x['id'] == item_id), None)
    if not item:
        return "Item not found", 404
    return render_template('found.html', item=item)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)

