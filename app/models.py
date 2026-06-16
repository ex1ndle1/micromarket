from sqlalchemy import Integer, String , Sequence
from sqlalchemy.orm import Mapped, mapped_column
from app.databases import Base


class TelegramMessageModel(Base):
    __tablename__ = 'telegram_messages'
         
    id: Mapped[int] = mapped_column(Sequence('msg_id_seq'), primary_key=True, index=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(Integer, autoincrement=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
