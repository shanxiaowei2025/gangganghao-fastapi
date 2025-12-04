from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class RoleResponse(BaseModel):
    id: int
    role_name: str
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
    phone: str
    department: str
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
    phone: Optional[str] = None
    department: Optional[str] = None


class UpdateProfileResponse(BaseModel):
    code: int
    message: str
    data: Optional[UserResponse] = None
