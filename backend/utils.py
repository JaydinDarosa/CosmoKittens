import bcrypt
import secrets
from datetime import datetime, timedelta
import jwt
import re

SECRET = secrets.token_hex(32)

def get_hashed_password(plain_text_password: str):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password.encode(), bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password.encode(), hashed_password)

def sign(obj):
    return jwt.encode(obj | {'exp': datetime.now() + timedelta(hours=24)}, SECRET, algorithm="HS256")

def decode(token):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception as e:
        return None
    
def check_username(username):
	if re.search(r'^[a-zA-Z0-9]*$', username) and 2<=len(username)<=32:
		return True
	else:
		return False
