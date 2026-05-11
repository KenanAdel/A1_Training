from pydantic import BaseModel
from typing import Optional
from schemas.user import UserResponse

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    owner_id: int

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None


class ProjectResponse(ProjectBase):
    id: int
    owner: UserResponse

    class Config:
        orm_mode = True