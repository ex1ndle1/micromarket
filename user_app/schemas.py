from annotated_types import Gt
from pydantic import Field, BaseModel 


class UserValidation(BaseModel):
   
    username : str= Field(gt=2)
    card_number : int = Field(ge=1)
