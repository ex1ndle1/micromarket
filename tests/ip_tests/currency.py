from pathlib import Path
from json import load
from redis import Redis
import geoip2.database


READER = geoip2.database.Reader('/home/ex1ndle/fast api/GeoLite2-Country.mmdb')

redis = Redis(host='localhost', port=6379, decode_responses=True)


def get_country(ip_address) :
    
        response = READER.country(ip_address)
        
        country_code = response.country.iso_code
        return country_code

def get_curr(cnt_code) :
    curr= redis.hget('country_currency_code' , cnt_code)
    return curr




def dump_datas():
    parent_dir = Path(__file__).resolve().parent.parent.parent
    json_path = parent_dir / "countries.json"
 
    with open(json_path , 'r') as f:
     datas  = load(f)


    for e in datas:
     redis.hset('country_currency_code' , e['countryCode'] , e['currencyCode'])
