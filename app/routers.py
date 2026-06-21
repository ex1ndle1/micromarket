from contextlib import redirect_stderr
from socket import MsgFlag
from fastapi import APIRouter, status, Depends, HTTPException, Query , Request
from kombu import message
from sqlalchemy import select, exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.coercions import expect
from app.databases import get_db
from app.models import ProductModel
from app.schemas import ProductValid
from sqlalchemy.exc import IntegrityError
from decimal import Decimal , ROUND_HALF_UP
import httpx
import geoip2.database
import os
from redis import Redis

redis = Redis(host='localhost', port=6379, decode_responses=True)
path = os.getenv('geo_lite_path')
READER = geoip2.database.Reader(path)
message_router = APIRouter(prefix='/product')




def get_country(ip):
    response = READER.country(ip)
        
    country_code = response.country.iso_code
    return country_code


def get_curr_code(cnt_code) :
    curr = redis.hget('country_currency_code' , cnt_code)
    return curr

def get_curr(curr_code):
    curr = redis.hget('currencies' , curr_code)
    return curr

def price_decimal_rounding(price : float, curr : float) -> float:
    curr = Decimal(str(curr))
    price = Decimal(str(price))
    rounded_price = price.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    rounded_curr= curr.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    res = rounded_curr * rounded_price
    return float(res)






@message_router.post('/post', status_code=status.HTTP_201_CREATED)
async def post_product(msg  : ProductValid, db : AsyncSession = Depends(get_db)):
    new_product = ProductModel(title=msg.title , price=msg.price)
    try: 
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return {"created"}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='conflict with data')


@message_router.get('/get')
async def get_product(msg : Request , db : AsyncSession = Depends(get_db)):
    try:
        product_id = msg.query_params.get('id')
        product_id=int(product_id)
        query = select(ProductModel).where(ProductModel.id == product_id)
        res  = await db.scalars(query)

        user_ip = msg.state.user_ip
        
        if user_ip == '127.0.0.1':
           curr = redis.get('user:local:curr')
           if not curr:
            async with httpx.AsyncClient() as client:
        
              response = await client.get("https://api.ipify.org?format=json", timeout=3.0)
              external_ip = response.json().get("ip")
              cnt = get_country(external_ip)
              curr_code : str = get_curr_code(cnt)
              redis.set('user:local:curr', curr , ex=28800)

        # will return there when add jwt for authentification
        else:
            # curr = get_curr(user_ip)
            # redis.set(f'user:local:user_id', curr , ex=28800)
            pass

        curr = get_curr(curr_code)
        res = res.all()
        price = res[0].price
        res[0].price = price_decimal_rounding(price=price, curr=curr)
        return res
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)