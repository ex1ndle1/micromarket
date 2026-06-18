from sqlalchemy.ext.asyncio import AsyncSession
from user_app.schemas import UserValidation
from fastapi import APIRouter, status, Depends, HTTPException, Query , Request
from user_app.databases import get_db
from user_app.models import UserModel


user_router  =  APIRouter(prefix='/user')

@user_router.post('/register')
async def post_user(msg : UserValidation ,  db : AsyncSession= Depends(get_db) ):
    new_user = UserModel(
        username=msg.username,
        card_number=msg.card_number
    )
    try: 
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return {'created'}
    except HTTPException as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='this message from user already exists')

