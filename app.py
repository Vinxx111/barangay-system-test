from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database setup
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            document_type TEXT NOT NULL,
            appointment TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            id_image_path TEXT
        )''')
        conn.commit()

init_db()

# Route to show frontend HTML (index.html must be in "templates" folder)
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit_request():
    name = request.form['fullName']
    address = request.form['address']
    document_type = request.form['documentType']
    appointment = request.form['appointmentDate']
    image = request.files.get('idImage')
    
    image_path = None
    if image:
        image_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(image_path)

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (name, address, document_type, appointment, id_image_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, address, document_type, appointment, image_path))
        conn.commit()

    return jsonify({'message': 'Request submitted successfully'})

# Route to get all requests (for admin panel)
@app.route('/admin/requests')
def get_requests():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM requests')
        rows = cursor.fetchall()
        requests_list = [
            {
                'id': row[0],
                'name': row[1],
                'address': row[2],
                'document_type': row[3],
                'appointment': row[4],
                'status': row[5],
                'id_image_path': row[6]
            }
            for row in rows
        ]
    return jsonify(requests_list)

if __name__ == '__main__':
    app.run(debug=True)