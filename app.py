# flask basic boiler plate 

from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from flask_cors import CORS
from utils.s3Operations import upload_file_to_s3, delete_file_from_s3, get_bucket_contents

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({'message': 'Hello World!'})

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == "POST":
        if request.files:
            file = request.files["file"]
            bucket_name = os.environ.get("Bucket_Name")
            output = upload_file_to_s3(file, bucket_name)
            return jsonify({'message': 'File uploaded successfully', 'url': output})

if __name__ == '__main__':
    app.run(debug=True)




