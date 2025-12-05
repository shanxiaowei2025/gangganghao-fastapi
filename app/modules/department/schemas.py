from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class DepartmentCreateRequest(BaseModel):
    department_name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class DepartmentUpdateRequest(BaseModel):
    department_name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


class DepartmentResponse(BaseModel):
    id: int
    department_name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DepartmentDetailResponse(BaseModel):
    code: int
    message: str
    data: Optional[DepartmentResponse] = None


class DepartmentListResponse(BaseModel):
    code: int
    message: str
    data: List[DepartmentResponse] = []
    total: int = 0
    page: int = 1
    pagesize: int = 10


class DepartmentDeleteResponse(BaseModel):
    code: int
    message: str
