from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import sys

sys.path.append(r'C:\Users\luxsh\Desktop\Diabetic Project\diabetic-retinopathy-detection\Retinal_blindness_detection_Pytorch')
from model import Model

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['DATABASE'] = os.path.join(os.getcwd(), 'image_database.db')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def create_database():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS images
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       timestamp TEXT,
                       google_id TEXT,
                       username TEXT,
                       image BLOB,
                       output_image BLOB,
                       result TEXT)''')
    conn.commit()
    conn.close()

def drop_database():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS images')
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def insert_image(google_id, username, file):
    image_data = file.read()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('INSERT INTO images (timestamp, google_id, username, image) VALUES (?, ?, ?, ?)', 
                   (timestamp, google_id, username, image_data))
    conn.commit()
    image_id = cursor.lastrowid
    conn.close()
    return image_id

def get_image(image_id):
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('SELECT id, timestamp, google_id, username, image FROM images WHERE id = ?', (image_id,))
    id, timestamp, google_id, username, image_data = cursor.fetchone()
    conn.close()
    return id, timestamp, google_id, username, image_data

def store_output(id, output_image_data, result_text):
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('UPDATE images SET output_image = ?, result = ? WHERE id = ?', 
                   (output_image_data, result_text, id))
    conn.commit()
    conn.close()

def process_with_ml_model(image_data):
    classes = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR']
    model = Model(num_classes=5)
    model.load_model(r"C:\Users\luxsh\Desktop\Diabetic Project\diabetic-retinopathy-detection\Retinal_blindness_detection_Pytorch\classifier.pt\classifier.pt")
    
    input_image_path = 'temp_input_image.jpg'
    with open(input_image_path, 'wb') as f:
        f.write(image_data)
    
    value, out_img = model.test_with_single_image(input_image_path, classes)
    
    output_image_path = os.path.join(app.config['PROCESSED_FOLDER'], f"processed_output_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.jpg")
    plt.imshow(np.array(out_img))
    plt.axis('off')
    plt.title(f'Analysis Result: {classes[value]}')
    plt.savefig(output_image_path, bbox_inches='tight', pad_inches=0)
    plt.close()
    
    with open(output_image_path, 'rb') as f:
        output_image_data = f.read()

    return value, classes[value], output_image_data, output_image_path

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    token = data.get('token')
    google_id = data.get('google_id')
    username = data.get('name')
    
    if not token or not google_id or not username:
        return jsonify({'error': 'Invalid login data'}), 400

    # Handle login logic if needed

    return jsonify({'success': True}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    create_database()
    
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']
    google_id = request.form.get('google_id')
    username = request.form.get('name')

    if not google_id or not username:
        return jsonify({'error': 'Missing user details'}), 400

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print(f"Image '{filename}' successfully uploaded")

        file.seek(0)
        image_id = insert_image(google_id, username, file)
        
        _, _, _, _, image_data = get_image(image_id)
        
        analysis_result_value, analysis_result_text, output_image_data, output_image_path = process_with_ml_model(image_data)
        
        store_output(image_id, output_image_data, analysis_result_text)
        
        result_image_url = request.host_url + 'uploads/' + filename
        processed_image_url = request.host_url + 'processed/' + os.path.basename(output_image_path)
        return jsonify({'analysisResult': analysis_result_text, 'imageUrl': result_image_url, 'processedImageUrl': processed_image_url}), 200

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    uploads_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    try:
        return send_from_directory(uploads_dir, filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/processed/<filename>')
def processed_file(filename):
    processed_dir = os.path.join(os.getcwd(), app.config['PROCESSED_FOLDER'])
    try:
        return send_from_directory(processed_dir, filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    drop_database()  # Drop the existing table (use cautiously)
    create_database()  # Create the table with the new schema
    app.run(debug=True)
