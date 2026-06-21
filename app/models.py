from sqlalchemy import Integer, String , Sequence , DECIMAL , Numeric , Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.interfaces import MapperOption
from app.databases import Base


class ProductModel(Base):
    __tablename__ = 'market_product'
    id : Mapped[int] = mapped_column(Integer  ,Sequence('model_id_seq',data_type=Integer) ,primary_key=True, index=True,autoincrement=True )
    title : Mapped[str] = mapped_column(String ,  index=True)
    price : Mapped[DECIMAL] = mapped_column(Numeric(precision=12, scale=1))
