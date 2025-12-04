from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from app.modules.auth.utils import hash_password
from app.modules.auth.routes import get_current_user
from app.modules.user.models import SysUser
from app.modules.user.schemas import (
    UserCreateRequest, UserUpdateRequest, UserResponse,
    UserListResponse, UserDetailResponse, UserDeleteResponse
)

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.post("", response_model=UserDetailResponse, summary="创建用户")
def create_user(
    user_create: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建新用户
    
    参数:
    - username: 账号（唯一）
    - password: 密码
    - real_name: 真实姓名
    - id_card: 身份证号（唯一）
    - phone: 手机号
    - department: 部门
    
    需要管理员权限
    """
    
    # 检查用户名是否已存在
    existing_user = db.query(SysUser).filter(SysUser.username == user_create.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查身份证号是否已存在
    existing_id_card = db.query(SysUser).filter(SysUser.id_card == user_create.id_card).first()
    if existing_id_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="身份证号已存在"
        )
    
    # 创建新用户
    new_user = SysUser(
        username=user_create.username,
        password=hash_password(user_create.password),
        real_name=user_create.real_name,
        id_card=user_create.id_card,
        phone=user_create.phone,
        department=user_create.department
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    user_response = UserResponse.from_orm(new_user)
    
    return UserDetailResponse(
        code=200,
        message="用户创建成功",
        data=user_response
    )


@router.get("", response_model=UserListResponse, summary="获取用户列表")
def list_users(
    page: int = 1,
    pagesize: int = 10,
    username: str = None,
    real_name: str = None,
    id_card: str = None,
    phone: str = None,
    department: str = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取用户列表（分页 + 模糊查询）
    
    参数:
    - page: 页码（默认1）
    - pagesize: 每页记录数（默认10）
    - username: 账号（模糊查询，可选）
    - real_name: 真实姓名（模糊查询，可选）
    - id_card: 身份证号（模糊查询，可选）
    - phone: 手机号（模糊查询，可选）
    - department: 部门（模糊查询，可选）
    """
    
    # 验证参数
    if page < 1:
        page = 1
    if pagesize < 1:
        pagesize = 10
    
    # 构建查询条件
    query = db.query(SysUser)
    
    # 添加模糊查询条件
    if username:
        query = query.filter(SysUser.username.ilike(f"%{username}%"))
    if real_name:
        query = query.filter(SysUser.real_name.ilike(f"%{real_name}%"))
    if id_card:
        query = query.filter(SysUser.id_card.ilike(f"%{id_card}%"))
    if phone:
        query = query.filter(SysUser.phone.ilike(f"%{phone}%"))
    if department:
        query = query.filter(SysUser.department.ilike(f"%{department}%"))
    
    # 查询总数
    total = query.count()
    
    # 计算偏移量
    skip = (page - 1) * pagesize
    
    # 查询分页数据
    users = query.offset(skip).limit(pagesize).all()
    
    user_responses = [UserResponse.from_orm(user) for user in users]
    
    return UserListResponse(
        code=200,
        message="获取用户列表成功",
        data=user_responses,
        total=total,
        page=page,
        pagesize=pagesize
    )


@router.get("/{user_id}", response_model=UserDetailResponse, summary="获取用户详情")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取指定用户的详细信息
    
    参数:
    - user_id: 用户ID
    """
    
    db_user = db.query(SysUser).filter(SysUser.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_response = UserResponse.from_orm(db_user)
    
    return UserDetailResponse(
        code=200,
        message="获取用户详情成功",
        data=user_response
    )


@router.patch("/{user_id}", response_model=UserDetailResponse, summary="更新用户信息")
def update_user(
    user_id: int,
    user_update: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新用户信息（部分更新）
    
    参数:
    - user_id: 用户ID
    - real_name: 真实姓名（可选）
    - id_card: 身份证号（可选）
    - phone: 手机号（可选）
    - department: 部门（可选）
    """
    
    db_user = db.query(SysUser).filter(SysUser.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查身份证号是否被其他用户使用
    if user_update.id_card is not None and user_update.id_card != db_user.id_card:
        existing_id_card = db.query(SysUser).filter(
            SysUser.id_card == user_update.id_card,
            SysUser.id != user_id
        ).first()
        if existing_id_card:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="身份证号已被其他用户使用"
            )
    
    # 更新非空字段
    if user_update.real_name is not None:
        db_user.real_name = user_update.real_name
    
    if user_update.id_card is not None:
        db_user.id_card = user_update.id_card
    
    if user_update.phone is not None:
        db_user.phone = user_update.phone
    
    if user_update.department is not None:
        db_user.department = user_update.department
    
    db.commit()
    db.refresh(db_user)
    
    user_response = UserResponse.from_orm(db_user)
    
    return UserDetailResponse(
        code=200,
        message="用户信息更新成功",
        data=user_response
    )


@router.delete("/{user_id}", response_model=UserDeleteResponse, summary="删除用户")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    删除指定用户
    
    参数:
    - user_id: 用户ID
    """
    
    db_user = db.query(SysUser).filter(SysUser.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 防止删除自己
    if db_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    db.delete(db_user)
    db.commit()
    
    return UserDeleteResponse(
        code=200,
        message="用户删除成功"
    )
