from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class ProductValid(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title : str  = Field(min_length=1)
    price : Decimal = Field(max_digits=10 , decimal_places=2, gt=0)
