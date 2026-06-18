from celery import Celery
from httpx import get , post
import httpx
from redis import Redis
from dotenv import load_dotenv
import os

load_dotenv()

redis = Redis(host='localhost', port=6379, decode_responses=True)
app = Celery('get_currencies' , broker='redis://localhost:6379/0')

def get_cur():
    res = httpx.get(f'https://v6.exchangerate-api.com/v6/{os.getenv("CURRENCY_API")}/latest/USD').json()['conversion_rates']
    res_dic = {}
    need_cur = ['EUR', 'UZS' , 'RUB' , 'USD']
    for e , k in res.items():
        if e in need_cur: 
            res_dic.update({e:k})
    return  res_dic

def set_cache(dct):
    redis.hset(name='currencies' , mapping=dct)
    

def get_cache(dct):
    return redis.hgetall(dct)

    

@app.task
def main():
    datas = get_cur()
    set_cache(datas)
    redis.set('ALIce','1')
    
app.conf.beat_schedule = {
    'refresh-currency-every-15-seconds': {
        'task': 'app.currency.main',  
        'schedule': 10.0,              
    },
}

