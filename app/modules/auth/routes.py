from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt

from database import get_db
from app.modules.auth import verify_password, create_access_token, hash_password, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from app.modules.user.models import SysUser
from app.modules.user.schemas import (
    UserLogin, LoginResponse, UserResponse, 
    ChangePasswordRequest, ChangePasswordResponse,
    UpdateProfileRequest, UpdateProfileResponse
)

router = APIRouter(prefix="/api", tags=["认证"])
security = HTTPBearer()


def get_current_user(credentials = Depends(security), db: Session = Depends(get_db)) -> SysUser:
    """获取当前用户（通过 JWT 令牌验证）"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )
    
    db_user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    return db_user


@router.post("/auth/login", response_model=LoginResponse, summary="用户登录")
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    
    参数:
    - username: 账号
    - password: 密码
    
    返回:
    - code: 状态码 (200: 成功, 401: 失败)
    - message: 返回信息
    - data: 用户信息
    - token: JWT令牌
    """
    
    # 查询用户
    db_user = db.query(SysUser).filter(SysUser.username == user_login.username).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误"
        )
    
    # 验证密码
    if not verify_password(user_login.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误"
        )
    
    # 创建JWT令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username, "user_id": db_user.id},
        expires_delta=access_token_expires
    )
    
    # 构建响应
    user_response = UserResponse.from_orm(db_user)
    
    return LoginResponse(
        code=200,
        message="登录成功",
        data=user_response,
        token=access_token
    )


@router.get("/auth/profile", response_model=UserResponse, summary="获取当前用户信息")
def get_profile(current_user: SysUser = Depends(get_current_user)):
    """
    获取当前用户信息
    
    需要在请求头中提供有效的 JWT 令牌
    Authorization: Bearer <token>
    """
    return current_user


@router.post("/auth/change-password", response_model=ChangePasswordResponse, summary="修改密码")
def change_password(
    change_pwd_request: ChangePasswordRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码
    
    参数:
    - old_password: 旧密码
    - new_password: 新密码
    
    需要在请求头中提供有效的 JWT 令牌
    Authorization: Bearer <token>
    """
    
    # 验证旧密码
    if not verify_password(change_pwd_request.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="旧密码错误"
        )
    
    # 检查新密码是否与旧密码相同
    if change_pwd_request.old_password == change_pwd_request.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同"
        )
    
    # 更新密码
    current_user.password = hash_password(change_pwd_request.new_password)
    db.commit()
    
    return ChangePasswordResponse(
        code=200,
        message="密码修改成功"
    )


@router.put("/auth/profile", response_model=UpdateProfileResponse, summary="修改用户信息")
def update_profile(
    update_request: UpdateProfileRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户信息
    
    参数:
    - real_name: 真实姓名（可选）
    - id_card: 身份证号（可选）
    - phone: 手机号（可选）
    - department: 部门（可选）
    
    需要在请求头中提供有效的 JWT 令牌
    Authorization: Bearer <token>
    """
    
    # 更新非空字段
    if update_request.real_name is not None:
        current_user.real_name = update_request.real_name
    
    if update_request.id_card is not None:
        current_user.id_card = update_request.id_card
    
    if update_request.phone is not None:
        current_user.phone = update_request.phone
    
    if update_request.department is not None:
        current_user.department = update_request.department
    
    # 保存到数据库
    db.commit()
    db.refresh(current_user)
    
    user_response = UserResponse.from_orm(current_user)
    
    return UpdateProfileResponse(
        code=200,
        message="用户信息修改成功",
        data=user_response
    )
