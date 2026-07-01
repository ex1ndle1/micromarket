from fastapi import FastAPI, Request
from redis import Redis
from json import load , dump
import httpx
import geoip2.database
from pathlib import Path
from currency import get_curr

READER = geoip2.database.Reader('/home/ex1ndle/fast api/GeoLite2-Country.mmdb')
app = FastAPI()

redis = Redis(host='localhost', port=6379, decode_responses=True)


def get_country(ip_address) -> str:
    
        response = READER.country(ip_address)
        
        country_code = response.country.iso_code
        return country_code
        
    

@app.get("/my-ip")
async def get_my_ip(request: Request):

    external_ip = redis.get('user:local:ip')
    curr = redis.get('user:local:curr')
    if  not external_ip or  not curr:
       
   
    # 2. Узнаем реальный внешний IP через бесплатный public API
      async with httpx.AsyncClient() as client:
        
            response = await client.get("https://api.ipify.org?format=json", timeout=3.0)
            external_ip = response.json().get("ip")
            print(f'=========================================================================={external_ip}')
            redis.set('user:local:ip' ,  external_ip , ex=20)
            
            cnt = get_country(external_ip)
            curr = get_curr(cnt)
            redis.set('user:local:curr', curr , ex=20)
            
            
        
        


    return {
        "your_real_external_ip": external_ip,
        "your currency is " : curr
    }