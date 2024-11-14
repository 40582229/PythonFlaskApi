from flask import Flask, request, make_response, g
from flask_cors import CORS
import sqlite3
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

    return data

@api.route("/register", methods=['POST'])
def register():
    registerData = request.get_json()
    username = registerData['username']
    password = registerData['password']
    db = getDb()
    db.cursor().execute(
    'INSERT INTO user (username, password, token) VALUES (?, ?, ?)', 
    (username, password, None))
    db.commit()
    db = closeDbConnection(exception=None)
    return {"message":"success"}