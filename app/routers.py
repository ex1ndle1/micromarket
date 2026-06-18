from fastapi import APIRouter, status, Depends, HTTPException, Query , Request
from sqlalchemy import select, exc
from sqlalchemy.ext.asyncio import AsyncSession
from app.databases import get_db
from app.models import ProductModel
from app.schemas import TelegramMessage

message_router = APIRouter(prefix='/user')


# @message_router.post('/message', status_code=status.HTTP_201_CREATED)
# async def post_message(
#     msg: TelegramMessage,
#     db: AsyncSession = Depends(get_db),
# ):
#     new_msg = TelegramMessageModel(
#         author_id=msg.author_id,
#         text=msg.text
#     )
#     try:
#         db.add(new_msg)
#         await db.commit()
#         await db.refresh(new_msg)
#         return {'created'}
#     except exc.IntegrityError:
#         await db.rollback()
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='this message from user already exists')

# @message_router.get('/message', response_model=list[TelegramMessage], status_code=status.HTTP_200_OK)
# async def get_user_message(
#     req : Request ,
#     db: AsyncSession = Depends(get_db),
# ):
    
#     try:
#         author_id = req.query_params.get('author_id')
#         author_id = int(author_id)
#         query = select(TelegramMessageModel).where(TelegramMessageModel.author_id == author_id)
#         res = await db.scalars(query)
#         messages = res.all()
#         return messages
#     except  Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)