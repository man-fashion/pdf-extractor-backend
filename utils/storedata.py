from pymongo import MongoClient
import jsonschema
from bson import json_util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import os

MONGO_URI=os.environ.get("MONGO_URI")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client['Man_Fashion_Invoice_Data']
collection = db['invoice-data']

# Schema definition
schema = {
    "type": "object",
    "properties": {
        "Name": {"type": "string"},
        "address": {"type": "string"},
        "city": {"type": "string"},
        "pincode": {
            "anyOf": [
                {"type": "string", "pattern": "^\d{6}$"},
                {"type": "string", "pattern": "^NA$"}
            ]
        },
        "state": {"type": "string"},
        "qty": {"type": "integer"}

    },
    "required": ["Name", "address", "city", "pincode", "state"]
}

def store_data(data):
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - start store data - Method")
    try:
        jsonschema.validate(data, schema)
        collection.insert_one(data)
    except jsonschema.exceptions.ValidationError as e:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Data validation failed. Error:", e)
    except Exception as e:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} An error occurred while storing data:", e)
    finally:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - End store data - Method")


def get_address_vectors(addresses):
    # Combine address, city, state, and pincode into a single string
    combined_addresses = [' '.join([address['address'], address['city'], address['state'], address['pincode']]) for address in addresses]

    if not any(combined_addresses):
        return None
    # Vectorize the combined addresses
    vectorizer = TfidfVectorizer()
    address_vectors = vectorizer.fit_transform(combined_addresses)

    return address_vectors

# get all the data from db and store it into list. now in that list check where the pincode is same and then for all such adreses create a list map it with that particular pincode and create a dict

def group_addresses_by_pincode():
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - group_address_by_pincode function called")
    data = list(collection.find())
    pincode_map = {}
    for address in data:
        pincode = address.get('pincode')
        if pincode:
            if pincode not in pincode_map:
                pincode_map[pincode] = []
            pincode_map[pincode].append(address)

    # Convert ObjectId to string representation for JSON serialization
    pincode_map_serializable = {
        pincode: json_util.dumps(addresses) for pincode, addresses in pincode_map.items()
    }
    return pincode_map_serializable


# now similarly get adress address+city+state+pincode and check is if similar address exsists using vector similarity and if yes then create a mapping like {"01": [address1, address2, address3]}

def group_similar_addresses(threshold=0.7):

    addresses = list(collection.find())

    address_vectors = get_address_vectors(addresses)

    if address_vectors is None:
        return {}
    
    similarity_matrix = cosine_similarity(address_vectors)
    grouped_addresses = {}

    for i in range(len(addresses)):
        similar_indices = [j for j, sim in enumerate(similarity_matrix[i]) if sim > threshold and j != i]
        if similar_indices:
            key = str(i).zfill(2)
            grouped_addresses[key] = [json_util.dumps(addresses[i])] + [json_util.dumps(addresses[j]) for j in similar_indices]

    return grouped_addresses

