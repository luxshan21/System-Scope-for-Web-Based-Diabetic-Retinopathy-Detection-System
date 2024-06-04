from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sqlite3
import numpy as np
import sys

# Add the path to the model.py
sys.path.append(r'C:\Users\luxsh\Desktop\Diabetic Project\diabetic-retinopathy-detection\Retinal_blindness_detection_Pytorch')

from model import Model

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATABASE'] = 'image_analysis.db'

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    """Initialize the SQLite database."""
    print("Initializing database...")
    try:
        with app.app_context():
            conn = sqlite3.connect(app.config['DATABASE'])
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS images 
                              (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                               filename TEXT, 
                               original_data BLOB,
                               processed_data BLOB, 
                               analysis_result TEXT)''')
            conn.commit()
            conn.close()
        print("Database initialization complete.")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_with_ml_model(image_data):
    classes = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR']
    model = Model(num_classes=5)
    model.load_model(r"C:\Users\luxsh\Desktop\Diabetic Project\diabetic-retinopathy-detection\Retinal_blindness_detection_Pytorch\classifier.pt\classifier.pt")
    
    value, out_img = model.test_with_single_image_from_bytes(image_data, classes)
    analysis_result_text = classes[value]
    
    return analysis_result_text

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            # Read the file data
            file_data = file.read()

            # Store original image data in the database
            conn = sqlite3.connect(app.config['DATABASE'])
            cursor = conn.cursor()
            cursor.execute('INSERT INTO images (filename, original_data) VALUES (?, ?)',
                           (file.filename, file_data))
            conn.commit()
            conn.close()
            print("Original image data inserted into database.")

            # Process the uploaded image using the ML model
            analysis_result_text = process_with_ml_model(file_data)
            
            # Update the database with analysis result
            conn = sqlite3.connect(app.config['DATABASE'])
            cursor = conn.cursor()
            cursor.execute('UPDATE images SET analysis_result = ? WHERE filename = ?',
                           (analysis_result_text, file.filename))
            conn.commit()
            conn.close()
            print("Analysis result updated in database.")

            # Return the analysis result along with the response
            return jsonify({'analysisResult': analysis_result_text}), 200

        except Exception as e:
            print(f"Error processing/uploading image: {str(e)}")
            return jsonify({'error': 'Error processing/uploading image', 'details': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
