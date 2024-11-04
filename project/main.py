from flask import Flask, request, jsonify, render_template, send_from_directory
import base64
import re
import os
import requests
from image_rec import recognize_qr_code  # Import the QR code recognition function

vt_key = '300dabb04260bfe8723b6795168368798a3e9357017709f63e14aa96ffda9630'

def get_analysis(analysis_id):
    # define URL for the vt API analysis endpoint
    analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    headers = {
        "x-apikey": vt_key
    }
    response = requests.get(analysis_url, headers=headers)
    
    if response.status_code == 200:
        analysis_data = response.json()
        
        # display results in readable format
        stats = analysis_data['data']['attributes']['stats']

        danger_type = "Harmless"
        if stats['malicious'] > 0:
            danger_type = "Malicious"
        elif stats['suspicious'] > 0:
            danger_type = "Suspicious"
        elif stats['harmless'] == 0:
            danger_type = "Undetected"
        
        return analysis_data, danger_type
    else:
        print("Error:", response.status_code)
        return None

def scan_url(url_to_scan):
    global vt_key
    # Define the URL for the VirusTotal API endpoint
    vt_url = "https://www.virustotal.com/api/v3/urls"

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
        analysis_id = response.json()['data']['id']
        return get_analysis(analysis_id)  # Return JSON data for the scan result
    else:
        print("Error:", response.status_code)
        return None

app = Flask(__name__)

UPLOAD_FOLDER = 'project/static/uploads'
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
        if qr_present:
            qr_all_data, qr_simple_data = scan_url(qr_text)

        return jsonify({
            'status': 'success',
            'qr_code_detected': qr_present,
            'qr_danger_status': f"Status: {qr_simple_data} | URL: {qr_text}",
            'qr_advanced_data': qr_all_data,
            'image_url': f'static/uploads/captured_image.png'
        })
    except Exception as e:
        return jsonify({'status': 'failure', 'message': str(e)})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
