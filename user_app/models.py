from sqlalchemy import Sequence , Integer , String
from sqlalchemy.orm import Mapped, mapped_column
from app.databases import Base

class UserModel(Base):
    __tablename__ = 'telegram_user'

    id : Mapped[int] =  mapped_column(Sequence('user_id_seq'), primary_key=True, index=True, autoincrement=True)
    username : Mapped[int] = mapped_column(String , primary_key=True)
    