from pydantic import BaseModel, Field, ConfigDict


class TelegramMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    
    author_id: int = Field(gt=0)
    text: str = Field(min_length=1)
