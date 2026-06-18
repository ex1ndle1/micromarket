from annotated_types import Gt
from pydantic import Field, BaseModel 


class UserValidation(BaseModel):
   
    username : str= Field(min_length=2)
    card_number : int = Field(ge=1_000_000_000_000_000, le=9_999_999_999_999_999)
