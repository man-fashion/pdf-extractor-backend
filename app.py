# flask basic boiler plate 
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from flask_cors import CORS
from utils.s3Operations import upload_file_to_s3, delete_file_from_s3, get_bucket_contents
from pdf_parser import process_pdf_data
import requests
import datetime
from utils.storedata import store_data, group_addresses_by_pincode, group_similar_addresses
from celery_config import make_celery   


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config.update(
    CELERY_BROKER_URL='redis://redis:6379/0',
    CELERY_RESULT_BACKEND='redis://redis:6379/0'
)


celery = make_celery(app)
CORS(app)

def download_pdf(url, save_path="user_bill.pdf"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PDF ",url," downloaded successfully to ",save_path)
        return True
    else:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Failed to download PDF",url,". Status code:", response.status_code)
        return False


@app.route('/')
def index():
    return jsonify({'message': 'Hello World!'})

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == "POST":
        if request.files:
            file = request.files["file"]
            bucket_name = os.environ.get("Bucket_Name")
            print(bucket_name)
            output = upload_file_to_s3(file, bucket_name)
            
            return jsonify({'message': 'File uploaded successfully', 'url': output})

# this route will take s3 url in request download the pdf and extract the details and will save it into the db
@app.route('/get-details', methods=['POST'])
def get_details():
    if request.method == "POST":
        data = request.json
        url = data.get('url')
        filename = "user_bill.pdf"
        res = download_pdf(url)
        if res:
            from tasks import process_pdf
            task = process_pdf.delay(filename)
            # Return the task ID for tracking
            return jsonify({"response": True, 'message': 'PDF Queued Successfully', 'taskId': task.id})
        else:
            return jsonify({"response": False, 'message': 'Failed To Queue PDF', 'taskId': 'NA'})


@app.route('/get-addresses-by-pincode', methods=['GET'])
def get_addresses_by_pincode():
    return jsonify(group_addresses_by_pincode())

# create a route to get similar addresses
@app.route('/get-similar-addresses', methods=['GET'])
def get_similar_addresses():
    return jsonify(group_similar_addresses())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)




