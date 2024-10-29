from flask import Flask, request, jsonify, render_template, send_from_directory
import base64
import re
import os
from image_rec import recognize_qr_code  # Import the QR code recognition function

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    data = request.get_json()

    # Extract base64 image data
    image_data = data['image']
    
    # Remove the image metadata (the "data:image/png;base64," prefix)
    image_data = re.sub('^data:image/.+;base64,', '', image_data)

    # Decode the image
    try:
        image = base64.b64decode(image_data)

        # Save the image in the uploads folder
        image_path = os.path.join(UPLOAD_FOLDER, 'captured_image.png')
        with open(image_path, 'wb') as f:
            f.write(image)

        # Use OpenCV to check for QR code
        qr_present = recognize_qr_code(image_path)

        return jsonify({
            'status': 'success',
            'qr_code_detected': qr_present,
            'image_url': f'/uploads/captured_image.png'
        })
    except Exception as e:
        return jsonify({'status': 'failure', 'message': str(e)})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
