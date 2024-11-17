from flask import Flask, request, make_response, g
from flask_cors import CORS
import json
import sqlite3
import bcrypt
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

    sql = "SELECT * FROM user WHERE username = ?"
    data = []
    db = getDb()
    # Execute the query with `username` as a parameter
    for row in db.cursor().execute(sql, (username,)):
        data.append(str(row))

    db = closeDbConnection(exception=None)
    return data

@api.route("/register", methods=['POST'])
def register():
    registerData = request.get_json()
    username = registerData['username']
    password = registerData['password']
    if len(username) < 4 :
        return json.dumps({"error":"Username must be atleast 4 character long"})
    if len(password) < 8 :
        return json.dumps({"error":"Password must be atleast 8 character long"})
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
    return json.dumps({"success":"Account Created"})