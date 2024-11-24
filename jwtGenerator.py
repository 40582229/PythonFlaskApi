import jwt
import time
import os
import dotenv
from datetime import timedelta,datetime, timezone

def generateJwtToken(username):
    flaskSecret = os.getenv('flaskSecret')
    algorithm = os.getenv('algorithm')

    payload = {
        'userId':username,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=6000)
    }
    token = jwt.encode(payload, flaskSecret, algorithm)

    return token
