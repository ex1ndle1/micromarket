from datetime import datetime, timedelta, timezone
from typing import Optional
from typing_extensions import deprecated
import jwt
from passlib.context import CryptContext
import os 
from dotenv import load_dotenv

load_dotenv()

sec = os.getenv('KEY')
algo = os.getenv('HS256')
ex = 30

pwd_context = CryptContext(schemes=['bcrypt'] , deprecated='auto')

def varify_pass(passw, hash_passw):
    return pwd_context.verify(passw, hash_passw)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data , ex):
    to_enc : dict = data.copy()
    if ex:
        exp  =  datetime.now(timezone.utc) + ex
    else:
        exp = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_enc.update({"exp":exp})
    encode_jwt = jwt.encode(to_enc , sec , algorithm=algo)
    return encode_jwt