# app.py
from flask import Flask, jsonify, render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename
import onnxruntime as ort
import numpy as np
import json
import os
from PIL import Image
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
import magic

class UploadForm(FlaskForm):
    file = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Allowed file types are jpg and png')
    ])

app = Flask(__name__)

#File uploading 
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']
app.config['UPLOAD_PATH'] = 'uploads'
app.config['SAMPLE_FOLDER'] = 'static/samples'

os.makedirs(app.config['UPLOAD_PATH'], exist_ok=True)


#minor

# Loading the ONNX model
ort_session = ort.InferenceSession("MNIST_digit_classifier.onnx")
# Map numeric labels to class names
class_mapping = {0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9"}

def open_img(img_pth):
  #loading image
  IMG = Image.open(img_pth)
  #convert to grayscale
  IMG = IMG.convert('L')
  #resizing to 28x28 
  IMG = IMG.resize((28,28))
  IMG = np.array(IMG,dtype = np.float32)
  return IMG
def predict(IMG):
  #normalization
  IMG = IMG/ 255.0
  #reshaping
  IMG = IMG.reshape(1,1,28,28)
  #using the ONNX model
  ort_inputs= {ort_session.get_inputs()[0].name: IMG.astype(np.float32)}
  ort_outputs= ort_session.run(None, ort_inputs)
  pred_number = np.argmax(ort_outputs[0], axis=1)[0]
  scores = ort_outputs[0][0]
  confidence_scores = np.exp(scores) / np.sum(np.exp(scores))
  return {
        "class_id": int(pred_number),
        "class_name": class_mapping[pred_number],
        "probabilities": {class_mapping[i]: float(score) for i, score in enumerate(confidence_scores)}
    }

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def validate_file(file):
    if not file or file.filename == '':
        raise ValueError('No file selected')
    if not allowed_file(file.filename):
        raise ValueError('File type not allowed')


#@apps

@app.errorhandler(413)
def too_large(e):
    return "The File is too large", 450

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    return jsonify({
        'error': 'Unexpected Error Occured',
        'message': str(error)
    }), 480

#Homepage
@app.route('/')
def home():
    sample_images = [f for f in os.listdir(app.config['SAMPLE_FOLDER']) if allowed_file(f)]
    return render_template('index.html', sample_images =sample_images )

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

#predict (POST endpoint)
@app.route('/predict', methods=['POST'])
def predict_endpoint():
    if request.is_json and 'sample_image' in request.json:
        sample_image = request.get_json()['sample_image']
        sample_path = os.path.join(app.config['SAMPLE_FOLDER'], sample_image)
        if os.path.exists(sample_path):
            s_image = open_img(sample_path)
            result= predict(s_image)
            return jsonify(result)
        else:
            return jsonify({'error': 'Sample image not found'}), 404
    elif 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 405

        # Validate file type
        file_content = file.read(1024)
        file.seek(0)
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file_content)
        allowed_types = ['image/jpeg', 'image/png']

        if file_type not in allowed_types:
            return jsonify({'error': 'Invalid file type'}), 400

        # Check file extension using allowed_file function
        if not allowed_file(file.filename):
            return jsonify({'error': 'File extension not allowed.'}), 400

        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_PATH'], filename)
            file.save(file_path)

            IMG = open_img(file_path)
            result = predict(IMG)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'No image provided'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)