from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class RoleCreateRequest(BaseModel):
    role_name: str
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class RoleUpdateRequest(BaseModel):
    role_name: Optional[str] = None
    description: Optional[str] = None


class RoleResponse(BaseModel):
    id: int
    role_name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RoleDetailResponse(BaseModel):
    code: int
    message: str
    data: Optional[RoleResponse] = None


class RoleListResponse(BaseModel):
    code: int
    message: str
    data: List[RoleResponse] = []
    total: int = 0
    page: int = 1
    pagesize: int = 10


class RoleDeleteResponse(BaseModel):
    code: int
    message: str
