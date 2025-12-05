from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from app.modules.auth.utils import check_permission
from app.modules.auth.routes import get_current_user
from app.modules.user.models import SysUser
from app.modules.permission.models import SysPage, SysPermission
from app.modules.role.models import SysRole
from app.modules.permission.schemas import (
    PageCreateRequest, PageUpdateRequest, PageResponse, PageListResponse, PageDetailResponse, PageDeleteResponse,
    PermissionCreateRequest, PermissionUpdateRequest, PermissionDetailResponse, PermissionListResponse,
    PermissionDetailResponseWrapper, PermissionDeleteResponse, RolePermissionAssignRequest, RolePermissionResponse
)

router = APIRouter(prefix="/api/permissions", tags=["权限管理"])


# ==================== 页面管理 ====================

@router.post("/pages", response_model=PageDetailResponse, summary="创建页面")
def create_page(
    page_create: PageCreateRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建新页面
    
    参数:
    - page_name: 页面名称（唯一）
    - page_display_name: 页面显示名称
    - description: 页面描述（可选）
    
    需要权限: permission:create
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'permission:create', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
    # 检查页面名称是否已存在
    existing_page = db.query(SysPage).filter(SysPage.page_name == page_create.page_name).first()
    if existing_page:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="页面名称已存在"
        )
    
    # 创建新页面
    new_page = SysPage(
        page_name=page_create.page_name,
        page_display_name=page_create.page_display_name,
        description=page_create.description
    )
    
    db.add(new_page)
    db.commit()
    db.refresh(new_page)
    
    page_response = PageResponse.from_orm(new_page)
    
    return PageDetailResponse(
        code=200,
        message="页面创建成功",
        data=page_response
    )


@router.get("/pages", response_model=PageListResponse, summary="获取页面列表")
def list_pages(
    page: int = 1,
    pagesize: int = 10,
    page_name: str = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取页面列表（分页 + 模糊查询）
    
    参数:
    - page: 页码（默认1）
    - pagesize: 每页记录数（默认10）
    - page_name: 页面名称（模糊查询，可选）
    
    需要权限: permission:read
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'permission:read', db)
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
    query = db.query(SysPage)
    
    # 添加模糊查询条件
    if page_name:
        query = query.filter(SysPage.page_name.ilike(f"%{page_name}%"))
    
    # 查询总数
    total = query.count()
    
    # 计算偏移量
    skip = (page - 1) * pagesize
    
    # 查询分页数据
    pages = query.offset(skip).limit(pagesize).all()
    
    page_responses = [PageResponse.from_orm(p) for p in pages]
    
    return PageListResponse(
        code=200,
        message="获取页面列表成功",
        data=page_responses,
        total=total
    )


@router.get("/pages/{page_id}", response_model=PageDetailResponse, summary="获取页面详情")
def get_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取指定页面的详细信息
    
    参数:
    - page_id: 页面ID
    
    需要权限: permission:read
    """
    
    # 检查权限
    if not check_permission(current_user, 'permission:read', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要权限: permission:read"
        )
    
    db_page = db.query(SysPage).filter(SysPage.id == page_id).first()
    
    if not db_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="页面不存在"
        )
    
    page_response = PageResponse.from_orm(db_page)
    
    return PageDetailResponse(
        code=200,
        message="获取页面详情成功",
        data=page_response
    )


@router.patch("/pages/{page_id}", response_model=PageDetailResponse, summary="更新页面信息")
def update_page(
    page_id: int,
    page_update: PageUpdateRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新页面信息（部分更新）
    
    参数:
    - page_id: 页面ID
    - page_display_name: 页面显示名称（可选）
    - description: 页面描述（可选）
    
    需要权限: permission:update
    """
    
    # 检查权限
    if not check_permission(current_user, 'permission:update', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要权限: permission:update"
        )
    
    db_page = db.query(SysPage).filter(SysPage.id == page_id).first()
    
    if not db_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="页面不存在"
        )
    
    # 更新非空字段
    if page_update.page_display_name is not None:
        db_page.page_display_name = page_update.page_display_name
    
    if page_update.description is not None:
        db_page.description = page_update.description
    
    db.commit()
    db.refresh(db_page)
    
    page_response = PageResponse.from_orm(db_page)
    
    return PageDetailResponse(
        code=200,
        message="页面信息更新成功",
        data=page_response
    )


@router.delete("/pages/{page_id}", response_model=PageDeleteResponse, summary="删除页面")
def delete_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    删除指定页面
    
    参数:
    - page_id: 页面ID
    
    需要权限: permission:delete
    """
    
    # 检查权限
    if not check_permission(current_user, 'permission:delete', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要权限: permission:delete"
        )
    
    db_page = db.query(SysPage).filter(SysPage.id == page_id).first()
    
    if not db_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="页面不存在"
        )
    
    # 检查是否有关联的权限
    if db_page.permissions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法删除：该页面仍有关联的权限"
        )
    
    db.delete(db_page)
    db.commit()
    
    return PageDeleteResponse(
        code=200,
        message="页面删除成功"
    )


# ==================== 权限管理 ====================

@router.post("", response_model=PermissionDetailResponseWrapper, summary="创建权限")
def create_permission(
    permission_create: PermissionCreateRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建新权限
    
    参数:
    - permission_code: 权限代码（唯一，如 user:create）
    - permission_name: 权限名称
    - page_id: 所属页面ID
    - description: 权限描述（可选）
    
    需要权限: permission:create
    """
    
    # 检查权限
    if not check_permission(current_user, 'permission:create', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要权限: permission:create"
        )
    
    # 检查权限代码是否已存在
    existing_permission = db.query(SysPermission).filter(
        SysPermission.permission_code == permission_create.permission_code
    ).first()
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="权限代码已存在"
        )
    
    # 检查页面是否存在
    page = db.query(SysPage).filter(SysPage.id == permission_create.page_id).first()
    if not page:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="页面不存在"
        )
    
    # 创建新权限
    new_permission = SysPermission(
        permission_code=permission_create.permission_code,
        permission_name=permission_create.permission_name,
        page_id=permission_create.page_id,
        description=permission_create.description
    )
    
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    
    permission_response = PermissionDetailResponse.from_orm(new_permission)
    
    return PermissionDetailResponseWrapper(
        code=200,
        message="权限创建成功",
        data=permission_response
    )


@router.get("", response_model=PermissionListResponse, summary="获取权限列表")
def list_permissions(
    page: int = 1,
    pagesize: int = 10,
    permission_code: str = None,
    permission_name: str = None,
    page_id: int = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取权限列表（分页 + 模糊查询）
    
    参数:
    - page: 页码（默认1）
    - pagesize: 每页记录数（默认10）
    - permission_code: 权限代码（模糊查询，可选）
    - permission_name: 权限名称（模糊查询，可选）
    - page_id: 页面ID（精确查询，可选）
    
    需要权限: permission:read
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'permission:read', db)
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
    query = db.query(SysPermission)
    
    # 添加查询条件
    if permission_code:
        query = query.filter(SysPermission.permission_code.ilike(f"%{permission_code}%"))
    if permission_name:
        query = query.filter(SysPermission.permission_name.ilike(f"%{permission_name}%"))
    if page_id:
        query = query.filter(SysPermission.page_id == page_id)
    
    # 查询总数
    total = query.count()
    
    # 计算偏移量
    skip = (page - 1) * pagesize
    
    # 查询分页数据
    permissions = query.offset(skip).limit(pagesize).all()
    
    permission_responses = [PermissionDetailResponse.from_orm(p) for p in permissions]
    
    return PermissionListResponse(
        code=200,
        message="获取权限列表成功",
        data=permission_responses,
        total=total
    )


@router.get("/{permission_id}", response_model=PermissionDetailResponseWrapper, summary="获取权限详情")
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取指定权限的详细信息
    
    参数:
    - permission_id: 权限ID
    
    需要权限: permission:read
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'permission:read', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
    db_permission = db.query(SysPermission).filter(SysPermission.id == permission_id).first()
    
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    
    permission_response = PermissionDetailResponse.from_orm(db_permission)
    
    return PermissionDetailResponseWrapper(
        code=200,
        message="获取权限详情成功",
        data=permission_response
    )


@router.patch("/{permission_id}", response_model=PermissionDetailResponseWrapper, summary="更新权限信息")
def update_permission(
    permission_id: int,
    permission_update: PermissionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新权限信息（部分更新）
    
    参数:
    - permission_id: 权限ID
    - permission_name: 权限名称（可选）
    - description: 权限描述（可选）
    
    需要权限: permission:update
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'permission:update', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
    db_permission = db.query(SysPermission).filter(SysPermission.id == permission_id).first()
    
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    
    # 更新非空字段
    if permission_update.permission_name is not None:
        db_permission.permission_name = permission_update.permission_name
    
    if permission_update.description is not None:
        db_permission.description = permission_update.description
    
    db.commit()
    db.refresh(db_permission)
    
    permission_response = PermissionDetailResponse.from_orm(db_permission)
    
    return PermissionDetailResponseWrapper(
        code=200,
        message="权限信息更新成功",
        data=permission_response
    )


@router.delete("/{permission_id}", response_model=PermissionDeleteResponse, summary="删除权限")
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    删除指定权限
    
    参数:
    - permission_id: 权限ID
    
    需要权限: permission:delete
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'permission:delete', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
    db_permission = db.query(SysPermission).filter(SysPermission.id == permission_id).first()
    
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在"
        )
    
    db.delete(db_permission)
    db.commit()
    
    return PermissionDeleteResponse(
        code=200,
        message="权限删除成功"
    )


# ==================== 角色权限分配 ====================

@router.post("/roles/{role_id}/assign", response_model=RolePermissionResponse, summary="为角色分配权限")
def assign_permissions_to_role(
    role_id: int,
    assign_request: RolePermissionAssignRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    为指定角色分配权限
    
    参数:
    - role_id: 角色ID
    - permission_ids: 权限ID列表
    
    需要权限: role:assign
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'role:assign', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
    # 检查角色是否存在
    db_role = db.query(SysRole).filter(SysRole.id == role_id).first()
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 检查所有权限是否存在
    permissions = db.query(SysPermission).filter(SysPermission.id.in_(assign_request.permission_ids)).all()
    if len(permissions) != len(assign_request.permission_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部分权限不存在"
        )
    
    # 清空原有权限并分配新权限
    db_role.permissions = permissions
    
    db.commit()
    db.refresh(db_role)
    
    return RolePermissionResponse(
        code=200,
        message="权限分配成功",
        data={
            "role_id": db_role.id,
            "role_name": db_role.role_name,
            "permission_count": len(db_role.permissions)
        }
    )


@router.get("/roles/{role_id}/permissions", response_model=RolePermissionResponse, summary="获取角色的权限列表")
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取指定角色的所有权限
    
    参数:
    - role_id: 角色ID
    
    需要权限: role:read
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'role:read', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
    # 检查角色是否存在
    db_role = db.query(SysRole).filter(SysRole.id == role_id).first()
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    permissions = [
        {
            "id": p.id,
            "permission_code": p.permission_code,
            "permission_name": p.permission_name,
            "page_id": p.page_id,
            "page_name": p.page.page_name,
            "page_display_name": p.page.page_display_name
        }
        for p in db_role.permissions
    ]
    
    return RolePermissionResponse(
        code=200,
        message="获取角色权限成功",
        data={
            "role_id": db_role.id,
            "role_name": db_role.role_name,
            "permissions": permissions
        }
    )
