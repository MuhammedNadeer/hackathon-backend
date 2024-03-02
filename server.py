import os
import google.generativeai as genai
from flask import Flask , request , jsonify
from flask_cors import CORS, cross_origin
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import bcrypt



genai.configure(api_key=os.environ.get('API_KEY'))

uri = "mongodb+srv://muhammednadeerpc:h4VZN370co4XgWA0@cluster0.wx3lyw3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['hackathon']
users = db['user-data']

class UserSchema:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.notes = [] 

    def add_note(self, title, content):
        self.notes.append({'title': title, 'content': content})

app = Flask(__name__)
CORS(app)
gemini_model = genai.GenerativeModel('gemini-pro')


@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    user = users.find_one({'email': data['email']})
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401
    


@app.route('/summarize', methods=["POST"])
def summarize():
    text = request.get_data()
    print(text)
    summary = gemini_model.generate_content(f"Summarize this {text}")
    print(summary.text)
    return jsonify({"msg": summary.text}),200
    

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    user_data = {
        'username': data['username'],
        'email': data['email'],
        'password': hashed_password
    }
    users.insert_one(user_data)
    return jsonify({'message': 'User signed up successfully'}), 200

@app.route('/save',methods=["POST"])
def save():
    data = request.json
    email = data.get('email')
    print(email)

    # Check if user exists in the database
    user = users.find_one({'email': email})
    print(user)
    if user:
        # Get note data from request
        title = data.get('title')
        content = data.get('content')

        if 'notes' not in user:
            users.update_one({'email': email}, {'$set': {'notes': []}})
            user = users.find_one({'email': email}) 

        # Add note to user's list of notes
        user['notes'].append({'title': title, 'content': content})
        # Update user data in the database
        users.update_one({'email': email, 'notes.title': {'$ne': title}}, {'$push': {'notes': {'title': title, 'content': content}}})
        
        return jsonify({'message': 'Note added successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


if __name__ == "__main__":
    app.run(debug=True)