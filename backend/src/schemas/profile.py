from pydantic import BaseModel
from typing import Optional
from pydantic import ConfigDict

class ProfileRead(BaseModel):
    member_id: str
    grade: Optional[str] = None
    department: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

