from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# ============================================
# 页面相关 Schemas
# ============================================

class PageCreateRequest(BaseModel):
    page_name: str
    page_display_name: str
    description: Optional[str] = None


class PageUpdateRequest(BaseModel):
    page_name: Optional[str] = None
    page_display_name: Optional[str] = None
    description: Optional[str] = None


class PageResponse(BaseModel):
    id: int
    page_name: str
    page_display_name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PageDetailResponse(BaseModel):
    code: int
    message: str
    data: Optional[PageResponse] = None


class PageListResponse(BaseModel):
    code: int
    message: str
    data: List[PageResponse] = []
    total: int = 0
    page: int = 1
    pagesize: int = 10


class PageDeleteResponse(BaseModel):
    code: int
    message: str


# ============================================
# 权限相关 Schemas
# ============================================

class PermissionCreateRequest(BaseModel):
    permission_code: str
    permission_name: str
    page_id: int
    description: Optional[str] = None


class PermissionUpdateRequest(BaseModel):
    permission_code: Optional[str] = None
    permission_name: Optional[str] = None
    page_id: Optional[int] = None
    description: Optional[str] = None


class PageSimpleResponse(BaseModel):
    id: int
    page_name: str
    page_display_name: str

    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    id: int
    permission_code: str
    permission_name: str
    page_id: int
    page: Optional[PageSimpleResponse] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PermissionDetailResponse(BaseModel):
    code: int
    message: str
    data: Optional[PermissionResponse] = None


class PermissionListResponse(BaseModel):
    code: int
    message: str
    data: List[PermissionResponse] = []
    total: int = 0
    page: int = 1
    pagesize: int = 10


class PermissionDeleteResponse(BaseModel):
    code: int
    message: str


# ============================================
# 角色权限分配相关 Schemas
# ============================================

class RolePermissionAssignRequest(BaseModel):
    permission_ids: List[int]


class RolePermissionAssignResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None


class RolePermissionSimpleResponse(BaseModel):
    id: int
    permission_code: str
    page_id: int

    class Config:
        from_attributes = True


class RolePermissionsResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None


# ============================================
# 批量获取权限相关 Schemas
# ============================================

class BatchRolePermissionsRequest(BaseModel):
    role_ids: List[int]


class BatchRolePermissionsResponse(BaseModel):
    code: int
    message: str
    data: dict  # {role_id: [permissions]}
