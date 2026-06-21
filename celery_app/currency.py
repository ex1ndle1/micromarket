from celery import Celery
from httpx import get , post
import httpx
from redis import Redis
from dotenv import load_dotenv
import os

load_dotenv()

redis = Redis(host='localhost', port=6379, decode_responses=True)
app = Celery('get_currencies', broker='redis://redis:6379/0')

def get_cur():
    res = httpx.get(f'https://api.currencyfreaks.com/v2.0/rates/latest?apikey={os.getenv("CURRENCY_API")}').json()['rates']
    return  res

def set_cache(dct):
    redis.hset(name='currencies' , mapping=dct)
    

def get_cache(dct):
    return redis.hgetall(dct)



@app.task
def main():
    datas = get_cur()
    set_cache(datas)
    
app.conf.beat_schedule = {
    'refresh-currency-every-15-seconds': {
        'task': 'celery_app.currency.main',  
        'schedule': 3600.0,              
    },
}

app.conf.timezone = 'UTC'