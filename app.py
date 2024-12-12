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

flaskSecret = os.getenv('flaskSecret')
algorithm = os.getenv('algorithm')

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

def updateUserToken(db, username):
    updateToken = "UPDATE user set token = ? where username = ?"
    userToken = generateJwtToken(username)
    db.cursor().execute(updateToken,(userToken,username,))
    db.commit()
    return userToken


def validateCredentials(username, password):
    db = getDb()
    getUser = "SELECT * FROM user WHERE username = ?"
    user = db.cursor().execute(getUser,(username,)).fetchall()
    
    if len(user)==0 :
        db = closeDbConnection(exception=None)
        data = {"error":"Wrong Username Or Password"}
        response = api.response_class(response=json.dumps(data), status=400, mimetype='application/json')
        return response
        
    userPassword = user[0][2]
    if userPassword != bcrypt.hashpw(password.encode ("utf -8 "), userPassword):
        db = closeDbConnection(exception=None)
        data = {"error":"Wrong Username Or Password"}
        response = api.response_class(response=json.dumps(data), status=400, mimetype='application/json')
        return response
    
    userToken = updateUserToken(db,username)
    data = {"success":"Login Succesfull", "token": userToken}
    db = closeDbConnection(exception=None)
    return api.response_class(response=json.dumps(data), status=200, mimetype='application/json')

def verifyUser(db, userToken):
    try:
        decodedToken = jwt.decode(userToken, flaskSecret, algorithms=[algorithm])
        getUserUsername = "select * from user where username = ? and token = ?"
        user = db.cursor().execute(getUserUsername,(decodedToken['userId'],userToken,)).fetchall()
        if len(user) == 0:
            raise jwt.InvalidTokenError
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        print({"Error": e})
        return {"error":"Bad Request"}
    


@api.route("/login", methods=['POST'])
def users():
    loginData = request.get_json()
    username = loginData['username']
    password = loginData['password']

    return validateCredentials(username, password)

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



    db = getDb()
    user = verifyUser(db, userToken)
    if 'error' in user:
        db = closeDbConnection(exception=None)
        response = api.response_class(response=json.dumps(user), status=400, mimetype='application/json')
        return response
    
    
    db.cursor().execute(
    'INSERT INTO excersises (excersisename,userid, reps, weight, eSets, crdate) VALUES (?, ?, ?, ?, ?, ?)', 
    (excersise['name'],user[0][0], excersise['reps'],excersise['weight'],excersise['sets'], excersise['date']))

    db.commit()
    db = closeDbConnection(exception=None)
    response = api.response_class(response=json.dumps({"success":"Excersise Added"}), status=200, mimetype='application/json')

    return response

@api.route("/getExcersise", methods=['POST'])
def getExcersise():

    registerData = request.get_json()
    userToken = registerData['token']

    db = getDb()
    getUserExcersises = "SELECT * FROM excersises WHERE userid = ?"
    
 
    user = verifyUser(db, userToken)
    if 'error' in user:
        db = closeDbConnection(exception=None)
        response = api.response_class(response=json.dumps(user), status=400, mimetype='application/json')
        return response

    userExcersises = db.cursor().execute(getUserExcersises,(user[0][0],)).fetchall()
    proccesedUserExcersises = []
    for excersise in userExcersises:
        tempEx = {'name': excersise[1], 'reps':excersise[3], 'weight':excersise[4],'sets':excersise[5], 'date':excersise[6]}
        proccesedUserExcersises.append(tempEx)

    db.commit()
    db = closeDbConnection(exception=None)
    response = api.response_class(response=json.dumps({"excersises":proccesedUserExcersises}), status=200, mimetype='application/json')

    return response
