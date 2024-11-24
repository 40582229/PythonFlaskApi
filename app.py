from flask import Flask, request, make_response, g
from flask_cors import CORS
import json
import sqlite3
import bcrypt
import jwt
import os
from jwtGenerator import generateJwtToken
api = Flask(__name__)
dbLocation = 'db/sqlite3.db'
CORS(api)

def getDb():
    db = getattr(g, 'db', None)
    if db is None:
        db = sqlite3.connect(dbLocation)
        g.db = db
    
    return db

@api.teardown_appcontext
def closeDbConnection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def initDb():
    with api.app_context():
        db =  getDb()
        with api.open_resource('db/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@api.route("/login", methods=['POST'])
def users():
    loginData = request.get_json()
    username = loginData['username']
    password = loginData['password']

    db = getDb()
    getUser = "SELECT * FROM user WHERE username = ?"
    user = db.cursor().execute(getUser,(username,)).fetchall()

    if len(user)==0:
        db = closeDbConnection(exception=None)
        data = {"error":"Wrong Username Or Password"}
        response = api.response_class(response=json.dumps(data), status=400, mimetype='application/json')
        return response
    
    userPassword = user[0][2]
    if  userPassword != bcrypt.hashpw(password.encode ("utf -8 "), userPassword):
        db = closeDbConnection(exception=None)
        data = {"error":"Wrong Username Or Password"}
        response = api.response_class(response=json.dumps(data), status=400, mimetype='application/json')
        return response
    
    db = closeDbConnection(exception=None)

    userUsername = user[0][1]
    data = {"success":"Login Succesfull", "token": generateJwtToken(userUsername)}
    response = api.response_class(response=json.dumps(data), status=200, mimetype='application/json')

    return response

@api.route("/register", methods=['POST'])
def register():

    registerData = request.get_json()
    username = registerData['username']
    password = registerData['password']

    if len(username) < 4 or len(username) > 20 :
        data = {"error":"Username must be between 4 and 20 character long"}
        response = api.response_class(response=json.dumps(data), status=400, mimetype='application/json')
        return response
    if len(password) < 8 or len(password) > 50 :
        data = {"error":"Password must be between 8 and 50 characters long"}
        response = api.response_class(response=json.dumps(data), status=400, mimetype='application/json')
        return response
    
    db = getDb()
    sql_getUsersByUsername = "SELECT * FROM user WHERE username = ?"
    
    sqlRows_getUsersByUsernameLength = db.cursor().execute(sql_getUsersByUsername, (username,)).fetchall()
    sqlRows_getUsersByUsernameLength = len(sqlRows_getUsersByUsernameLength)
    if sqlRows_getUsersByUsernameLength>0:
        return json.dumps({"error":"Username already taken"})

    passwordHash = bcrypt.hashpw(password.encode ("utf -8 "), bcrypt.gensalt())
    
    db.cursor().execute(
    'INSERT INTO user (username, password, token) VALUES (?, ?, ?)', 
    (username, passwordHash, None))

    db.commit()
    db = closeDbConnection(exception=None)

    data = {"success":"Account Created"}
    response = api.response_class(response=json.dumps(data), status=200, mimetype='application/json')

    return response

@api.route("/excersise", methods=['POST'])
def excersise():

    registerData = request.get_json()
    userToken = registerData['token']
    excersise = registerData['excersise']
    flaskSecret = os.getenv('flaskSecret')
    algorithm = os.getenv('algorithm')

    decodedToken = jwt.decode(userToken, flaskSecret, algorithms=[algorithm])
    db = getDb()
    getUser = "SELECT * FROM user WHERE username = ?"
    l = decodedToken['userId']
    user = db.cursor().execute(getUser,(decodedToken['userId'],)).fetchall()
    if len(user)==0:
        db = closeDbConnection(exception=None)
        data = {"error":"Bad Request"}
        response = api.response_class(response=json.dumps(data), status=400, mimetype='application/json')
        return response
    
    db.cursor().execute(
    'INSERT INTO excersises (excersisename,userid, reps, eSets, crdate) VALUES (?, ?, ?, ?, ?)', 
    (excersise['name'],user[0][0], excersise['reps'],excersise['sets'], None))

    db.commit()
    db = closeDbConnection(exception=None)
    response = api.response_class(response=json.dumps({"success":"Excersise Added"}), status=200, mimetype='application/json')

    return response

@api.route("/getExcersise", methods=['POST'])
def getExcersise():

    registerData = request.get_json()
    userToken = registerData['token']
    flaskSecret = os.getenv('flaskSecret')
    algorithm = os.getenv('algorithm')

    decodedToken = jwt.decode(userToken, flaskSecret, algorithms=[algorithm])
    db = getDb()
    getUserExcersises = "SELECT * FROM excersises WHERE userid = ?"
    getUserUserId = "select userid from user where username = ?"
    userId = db.cursor().execute(getUserUserId,(decodedToken['userId'],)).fetchall()
    if len(userId)==0:
        db = closeDbConnection(exception=None)
        data = {"error":"Bad Request"}
        response = api.response_class(response=json.dumps(data), status=400, mimetype='application/json')
        return response

    userExcersises = db.cursor().execute(getUserExcersises,(userId[0][0],)).fetchall()
    proccesedUserExcersises = []
    for excersise in userExcersises:
        tempEx = {'name': excersise[1], 'reps':excersise[3], 'sets':excersise[4]}
        proccesedUserExcersises.append(tempEx)

    db.commit()
    db = closeDbConnection(exception=None)
    response = api.response_class(response=json.dumps({"excersises":proccesedUserExcersises}), status=200, mimetype='application/json')

    return response