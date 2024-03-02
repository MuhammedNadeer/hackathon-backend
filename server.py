import os
import google.generativeai as genai
from flask import Flask , request , jsonify
from flask_cors import CORS, cross_origin




genai.configure(api_key="AIzaSyB8pS_bC4LNB-t-27f-eRrsQb-mBWlBfQQ")



app = Flask(__name__)
CORS(app)
gemini_model = genai.GenerativeModel('gemini-pro')



@app.route('/summarize', methods=["POST"])
def summarize():
    text = request.json
    print(text)
    summary = gemini_model.generate_content(f"Summarize this {text}")
    return jsonify({"msg": summary.text}), 200




if __name__ == "__main__":
    app.run(debug=True)