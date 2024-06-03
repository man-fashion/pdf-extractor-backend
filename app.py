# flask basic boiler plate 
from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from flask_cors import CORS
from utils.s3Operations import upload_file_to_s3, delete_file_from_s3, get_bucket_contents
from parser_1 import process_pdf_data
import requests
from utils.storedata import store_data, group_addresses_by_pincode, group_similar_addresses

app = Flask(__name__)
CORS(app)

def download_pdf(url, save_path="user_bill.pdf"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print("PDF downloaded successfully")
        return True
    else:
        print("Failed to download PDF. Status code:", response.status_code)
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

        if res==True:
            data = process_pdf_data(filename)
            for items in data:

                try:
                    store_data(items)
                except Exception as e:
                    print("An error occurred while storing data:", e)

            os.remove(filename)
            return jsonify({"response":True,'message': 'Data Added successfully'})
        else:
            return jsonify({"response":False, 'message': 'Failed to extract data'})
        


@app.route('/get-addresses-by-pincode', methods=['GET'])
def get_addresses_by_pincode():
    return jsonify(group_addresses_by_pincode())

# create a route to get similar addresses
@app.route('/get-similar-addresses', methods=['GET'])
def get_similar_addresses():
    return jsonify(group_similar_addresses())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)




