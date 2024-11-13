from flask import Flask, request, make_response
from flask_cors import CORS
api = Flask(__name__)
CORS(api)

@api.route("/login", methods=['POST'])
def users():
    loginData = request.get_json()
    if loginData['username'] =='rokas':
        return {1:'rokas'}
    return {"error":"Wrong Username Or Password"}