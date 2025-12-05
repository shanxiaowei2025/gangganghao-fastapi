from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class RoleResponse(BaseModel):
    id: int
    role_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class DepartmentResponse(BaseModel):
    id: int
    department_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: str
    id_card: str
    phone: str
    department: DepartmentResponse
    roles: List[RoleResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    code: int
    message: str
    data: Optional[UserResponse] = None
    token: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    code: int
    message: str


class UpdateProfileRequest(BaseModel):
    real_name: Optional[str] = None
    id_card: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None


class UpdateProfileResponse(BaseModel):
    code: int
    message: str
    data: Optional[UserResponse] = None


class UserCreateRequest(BaseModel):
    username: str
    password: str
    real_name: str
    id_card: str
    phone: str
    department_id: int
    role_ids: Optional[List[int]] = None


class UserUpdateRequest(BaseModel):
    real_name: Optional[str] = None
    id_card: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None


class UserListResponse(BaseModel):
    code: int
    message: str
    data: List[UserResponse] = []
    total: int = 0
    page: int = 1
    pagesize: int = 10


class UserDetailResponse(BaseModel):
    code: int
    message: str
    data: Optional[UserResponse] = None


class UserDeleteResponse(BaseModel):
    code: int
    message: str
