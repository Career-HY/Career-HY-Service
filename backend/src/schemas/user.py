from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from pydantic import ConfigDict

class UserCreate(BaseModel):
    email: str
    pwd: str

class UserLogin(BaseModel):
    email: str
    pwd: str

class UserRead(BaseModel):
    id: str
    email: str
    signup_date: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

