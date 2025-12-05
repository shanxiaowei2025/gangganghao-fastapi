from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PageResponse(BaseModel):
    id: int
    page_name: str
    page_display_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    id: int
    permission_code: str
    permission_name: str
    page_id: int
    description: Optional[str] = None

    class Config:
        from_attributes = True


class PermissionDetailResponse(BaseModel):
    id: int
    permission_code: str
    permission_name: str
    page: PageResponse
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PageCreateRequest(BaseModel):
    page_name: str
    page_display_name: str
    description: Optional[str] = None


class PageUpdateRequest(BaseModel):
    page_display_name: Optional[str] = None
    description: Optional[str] = None


class PermissionCreateRequest(BaseModel):
    permission_code: str
    permission_name: str
    page_id: int
    description: Optional[str] = None


class PermissionUpdateRequest(BaseModel):
    permission_name: Optional[str] = None
    description: Optional[str] = None


class RolePermissionAssignRequest(BaseModel):
    role_id: int
    permission_ids: List[int]


class RolePermissionResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None


class PageListResponse(BaseModel):
    code: int
    message: str
    data: List[PageResponse] = []
    total: int = 0


class PermissionListResponse(BaseModel):
    code: int
    message: str
    data: List[PermissionDetailResponse] = []
    total: int = 0


class PageDetailResponse(BaseModel):
    code: int
    message: str
    data: Optional[PageResponse] = None


class PermissionDetailResponseWrapper(BaseModel):
    code: int
    message: str
    data: Optional[PermissionDetailResponse] = None


class PageDeleteResponse(BaseModel):
    code: int
    message: str


class PermissionDeleteResponse(BaseModel):
    code: int
    message: str
