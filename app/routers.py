from fastapi import APIRouter, status, Depends, HTTPException, Request, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from decimal import Decimal, ROUND_HALF_UP

from app.databases import get_db
from app.models import ProductModel
from app.schemas import ProductValid

import httpx
import geoip2.database
import os
from redis import Redis

redis = Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=2)
path = os.getenv('geo_lite_path')
READER = geoip2.database.Reader(path)
message_router = APIRouter(prefix='/market')


def get_country(ip):
    response = READER.country(ip)
    return response.country.iso_code


def get_curr_code(cnt_code):
    return redis.hget('country_currency_code', cnt_code)


def get_curr(curr_code):
    return redis.hget('currencies', curr_code)


def price_decimal_rounding(price: float, curr: float) -> float:
    curr = Decimal(str(curr))
    price = Decimal(str(price))
    rounded_price = price.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    rounded_curr = curr.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    return float(rounded_curr * rounded_price)


@message_router.post('/product', status_code=status.HTTP_201_CREATED)
async def post_product(msg: ProductValid, db: AsyncSession = Depends(get_db)):
    new_product = ProductModel(title=msg.title, price=msg.price)
    try:
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return {"created"}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='conflict with data')


@message_router.get('/products')
async def list_products(db: AsyncSession = Depends(get_db)):
    query = select(ProductModel).order_by(ProductModel.id)
    res = await db.scalars(query)
    return res.all()


@message_router.get('/product')
async def get_product(
    request: Request,
    id: int = Query(..., description='Product ID'),
    db: AsyncSession = Depends(get_db),
):
    try:
        query = select(ProductModel).where(ProductModel.id == id)
        res = await db.scalars(query)
        res = res.all()

        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='product not found')

        user_ip = request.state.user_ip
        curr = None

        if user_ip == '127.0.0.1':
            curr = redis.get('user:local:curr')
            if not curr:
                async with httpx.AsyncClient() as client:
                    response = await client.get("https://api.ipify.org?format=json", timeout=3.0)
                    external_ip = response.json().get("ip")
                    cnt = get_country(external_ip)
                    curr_code = get_curr_code(cnt)
                    curr = get_curr(curr_code)
                    redis.set('user:local:curr', curr, ex=28800)
        else:
            cnt = get_country(user_ip)
            curr_code = get_curr_code(cnt)
            curr = get_curr(curr_code)
            redis.set(f'user:{user_ip}:curr', curr, ex=28800)

        if not curr:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='could not determine currency')

        price = res[0].price
        res[0].price = price_decimal_rounding(price=price, curr=curr)
        return res

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
