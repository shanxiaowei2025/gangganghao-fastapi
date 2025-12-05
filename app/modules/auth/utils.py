from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def check_permission(user, permission_code: str, db: Session) -> tuple:
    """
    检查用户是否拥有指定权限
    
    参数:
    - user: 当前用户对象
    - permission_code: 权限代码（如 'user:create'）
    - db: 数据库会话
    
    返回:
    - (True, permission_name): 用户拥有该权限，返回权限名称
    - (False, None): 用户不拥有该权限
    """
    # 导入模型（避免循环导入）
    from app.modules.permission.models import SysPermission
    from app.modules.role.models import role_permission_association
    
    # 获取用户的所有角色ID
    user_role_ids = [role.id for role in user.roles]
    
    if not user_role_ids:
        return (False, None)
    
    # 检查该权限是否被分配给用户的任何一个角色
    from app.modules.role.models import SysRole
    permission = db.query(SysPermission).filter(
        SysPermission.permission_code == permission_code,
        SysPermission.roles.any(SysRole.id.in_(user_role_ids))
    ).first()
    
    if permission is not None:
        return (True, permission.permission_name)
    else:
        # 即使用户没有权限，也要获取权限名称用于错误提示
        permission_info = db.query(SysPermission).filter(
            SysPermission.permission_code == permission_code
        ).first()
        permission_name = permission_info.permission_name if permission_info else permission_code
        return (False, permission_name)


def require_permission(permission_code: str):
    """
    权限检查装饰器工厂函数
    
    使用方式:
    @require_permission('user:create')
    def create_user(...):
        ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_user和db
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未授权"
                )
            
            # 检查权限
            if not check_permission(current_user, permission_code, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足，需要权限: {permission_code}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
