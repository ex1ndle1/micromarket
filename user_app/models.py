from sqlalchemy import Sequence, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from user_app.databases import Base

class UserModel(Base):
    __tablename__ = 'market_users'

    id: Mapped[int] = mapped_column(
        BigInteger, 
        Sequence('user_id_seq', data_type=BigInteger),
        primary_key=True, 
        index=True, 
        autoincrement=True
    )
    
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    card_number: Mapped[int] = mapped_column(BigInteger , unique=True , index=True)