# app.py
from flask import Flask, render_template, request, jsonify
import requests
import base64
import tempfile
import os
from datetime import datetime

app = Flask(__name__)

WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/21224512/2z8ra5a/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_image():
    try:
        # Get data from the request
        data = request.get_json()
        image_data = data.get('image')
        submitter_name = data.get('submitter')
        slack_user_id = data.get('slackUserId')
        email = data.get('email')

        # Decode the base64 image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_filename = temp_file.name
            with open(temp_filename, 'wb') as img_file:
                img_file.write(image_bytes)

        # Prepare webhook data
        files = {'file': ('receipt.jpg', open(temp_filename, 'rb'), 'image/jpeg')}
        data = {
            'timestamp': datetime.now().isoformat(),
            'submitter': submitter_name,
            'type': 'receipt_image'
        }
        
        # Add optional fields if provided
        if slack_user_id:
            data['slackUserId'] = slack_user_id
        if email:
            data['email'] = email

        # Send to webhook
        response = requests.post(WEBHOOK_URL, files=files, data=data)

        # Cleanup
        os.remove(temp_filename)

        if response.status_code == 200:
            return jsonify({'message': 'Image and data submitted successfully'})
        else:
            return jsonify({'error': f'Webhook returned status: {response.status_code}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)