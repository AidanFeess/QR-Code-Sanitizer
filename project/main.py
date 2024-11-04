from flask import Flask, request, jsonify, render_template, send_from_directory
import base64
import re
import os
import vt
import requests
from image_rec import recognize_qr_code  # Import the QR code recognition function

vt_key = ''

def scan_url(url_to_scan):
    global vt_key
    # Define the URL for the VirusTotal API endpoint
    vt_url = "https://www.virustotal.com/api/v3/urls"
    
    # Encode the URL to be scanned (VirusTotal requires URL-safe base64 encoding)
    url_id = base64.urlsafe_b64encode(url_to_scan.encode()).decode().strip("=")

    # Set up headers with the API key
    headers = {
        "x-apikey": vt_key
    }

    data = {
        "url": url_to_scan
    }

    # Send the request to scan the URL
    response = requests.post(vt_url, headers=headers, data=data)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()  # Return JSON data for the scan result
    else:
        print("Error:", response.status_code)
        return None

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
        qr_present, qr_text = recognize_qr_code(image_path)
        print(scan_url(qr_text))

        return jsonify({
            'status': 'success',
            'qr_code_detected': qr_text,
            'image_url': f'/uploads/captured_image.png'
        })
    except Exception as e:
        return jsonify({'status': 'failure', 'message': str(e)})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
