from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from app.modules.auth.routes import get_current_user
from app.modules.user.models import SysUser, SysRole
from app.modules.role.schemas import (
    RoleCreateRequest, RoleUpdateRequest, RoleResponse,
    RoleListResponse, RoleDetailResponse, RoleDeleteResponse
)

router = APIRouter(prefix="/api/roles", tags=["角色管理"])


@router.post("", response_model=RoleDetailResponse, summary="创建角色")
def create_role(
    role_create: RoleCreateRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建新角色
    
    参数:
    - role_name: 角色名称（唯一）
    - description: 角色描述（可选）
    
    需要管理员权限
    """
    
    # 检查角色名称是否已存在
    existing_role = db.query(SysRole).filter(SysRole.role_name == role_create.role_name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名称已存在"
        )
    
    # 创建新角色
    new_role = SysRole(
        role_name=role_create.role_name,
        description=role_create.description
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    role_response = RoleResponse.from_orm(new_role)
    
    return RoleDetailResponse(
        code=200,
        message="角色创建成功",
        data=role_response
    )


@router.get("", response_model=RoleListResponse, summary="获取角色列表")
def list_roles(
    page: int = 1,
    pagesize: int = 10,
    role_name: str = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取角色列表（分页 + 模糊查询）
    
    参数:
    - page: 页码（默认1）
    - pagesize: 每页记录数（默认10）
    - role_name: 角色名称（模糊查询，可选）
    """
    
    # 验证参数
    if page < 1:
        page = 1
    if pagesize < 1:
        pagesize = 10
    
    # 构建查询条件
    query = db.query(SysRole)
    
    # 添加模糊查询条件
    if role_name:
        query = query.filter(SysRole.role_name.ilike(f"%{role_name}%"))
    
    # 查询总数
    total = query.count()
    
    # 计算偏移量
    skip = (page - 1) * pagesize
    
    # 查询分页数据
    roles = query.offset(skip).limit(pagesize).all()
    
    role_responses = [RoleResponse.from_orm(role) for role in roles]
    
    return RoleListResponse(
        code=200,
        message="获取角色列表成功",
        data=role_responses,
        total=total,
        page=page,
        pagesize=pagesize
    )


@router.get("/{role_id}", response_model=RoleDetailResponse, summary="获取角色详情")
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取指定角色的详细信息
    
    参数:
    - role_id: 角色ID
    """
    
    db_role = db.query(SysRole).filter(SysRole.id == role_id).first()
    
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    role_response = RoleResponse.from_orm(db_role)
    
    return RoleDetailResponse(
        code=200,
        message="获取角色详情成功",
        data=role_response
    )


@router.patch("/{role_id}", response_model=RoleDetailResponse, summary="更新角色信息")
def update_role(
    role_id: int,
    role_update: RoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新角色信息（部分更新）
    
    参数:
    - role_id: 角色ID
    - role_name: 角色名称（可选）
    - description: 角色描述（可选）
    """
    
    db_role = db.query(SysRole).filter(SysRole.id == role_id).first()
    
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 检查角色名称是否被其他角色使用
    if role_update.role_name is not None and role_update.role_name != db_role.role_name:
        existing_role = db.query(SysRole).filter(
            SysRole.role_name == role_update.role_name,
            SysRole.id != role_id
        ).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名称已被其他角色使用"
            )
    
    # 更新非空字段
    if role_update.role_name is not None:
        db_role.role_name = role_update.role_name
    
    if role_update.description is not None:
        db_role.description = role_update.description
    
    db.commit()
    db.refresh(db_role)
    
    role_response = RoleResponse.from_orm(db_role)
    
    return RoleDetailResponse(
        code=200,
        message="角色信息更新成功",
        data=role_response
    )


@router.delete("/{role_id}", response_model=RoleDeleteResponse, summary="删除角色")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    删除指定角色
    
    参数:
    - role_id: 角色ID
    """
    
    db_role = db.query(SysRole).filter(SysRole.id == role_id).first()
    
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 检查是否有用户关联此角色
    if db_role.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法删除：该角色仍有用户关联"
        )
    
    db.delete(db_role)
    db.commit()
    
    return RoleDeleteResponse(
        code=200,
        message="角色删除成功"
    )
