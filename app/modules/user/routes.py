from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from app.modules.auth.utils import hash_password, check_permission
from app.modules.auth.routes import get_current_user
from app.modules.user.models import SysUser
from app.modules.department.models import SysDepartment
from app.modules.role.models import SysRole
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
    - department_id: 部门ID
    - role_ids: 角色ID列表（可选）
    
    需要权限: user:create
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'user:create', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
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
    
    # 检查部门是否存在
    department = db.query(SysDepartment).filter(SysDepartment.id == user_create.department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部门不存在"
        )
    
    # 检查角色是否存在（如果提供了角色ID）
    roles = []
    if user_create.role_ids:
        roles = db.query(SysRole).filter(SysRole.id.in_(user_create.role_ids)).all()
        if len(roles) != len(user_create.role_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部分角色不存在"
            )
    
    # 创建新用户
    new_user = SysUser(
        username=user_create.username,
        password=hash_password(user_create.password),
        real_name=user_create.real_name,
        id_card=user_create.id_card,
        phone=user_create.phone,
        department_id=user_create.department_id
    )
    
    # 分配角色
    if roles:
        new_user.roles = roles
    
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
    
    需要权限: user:read
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'user:read', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
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
        query = query.join(SysDepartment).filter(
            SysDepartment.department_name.ilike(f"%{department}%")
        )
    
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
    
    需要权限: user:read
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'user:read', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
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
    
    需要权限: user:update
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'user:update', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
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
    
    if user_update.department_id is not None:
        # 检查部门是否存在
        department = db.query(SysDepartment).filter(SysDepartment.id == user_update.department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门不存在"
            )
        db_user.department_id = user_update.department_id
    
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
    
    需要权限: user:delete
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'user:delete', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
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
