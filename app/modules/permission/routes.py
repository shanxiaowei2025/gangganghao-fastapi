from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db
from app.modules.auth.routes import get_current_user
from app.modules.user.models import SysUser
from app.modules.role.models import SysRole
from app.modules.permission.models import SysPage, SysPermission, rel_role_permission
from app.modules.permission.schemas import (
    PageResponse, PageListResponse,
    PermissionResponse, PermissionListResponse,
    RolePermissionAssignRequest, RolePermissionAssignResponse, RolePermissionsResponse,
    BatchRolePermissionsRequest, BatchRolePermissionsResponse
)

router = APIRouter(prefix="/api/permissions", tags=["权限管理"])


# ============================================
# 页面管理接口
# ============================================

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
    """
    
    # 验证参数
    if page < 1:
        page = 1
    if pagesize < 1:
        pagesize = 10
    
    # 构建查询条件
    query = db.query(SysPage)
    
    # 添加模糊查询条件
    if page_name:
        query = query.filter(
            (SysPage.page_name.ilike(f"%{page_name}%")) |
            (SysPage.page_display_name.ilike(f"%{page_name}%"))
        )
    
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
        total=total,
        page=page,
        pagesize=pagesize
    )




# ============================================
# 权限管理接口
# ============================================

@router.get("", response_model=PermissionListResponse, summary="获取权限列表")
def list_permissions(
    page_id: int = None,
    page: int = 1,
    pagesize: int = 10,
    permission_code: str = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取权限列表（分页 + 模糊查询）
    
    参数:
    - page_id: 页面ID（可选，为空则获取所有权限）
    - page: 页码（默认1）
    - pagesize: 每页记录数（默认10）
    - permission_code: 权限代码（模糊查询，可选）
    """
    
    # 验证参数
    if page < 1:
        page = 1
    if pagesize < 1:
        pagesize = 10
    
    # 构建查询条件
    query = db.query(SysPermission)
    
    # 按页面ID过滤
    if page_id is not None:
        query = query.filter(SysPermission.page_id == page_id)
    
    # 添加模糊查询条件
    if permission_code:
        query = query.filter(SysPermission.permission_code.ilike(f"%{permission_code}%"))
    
    # 查询总数
    total = query.count()
    
    # 计算偏移量
    skip = (page - 1) * pagesize
    
    # 查询分页数据
    permissions = query.offset(skip).limit(pagesize).all()
    
    permission_responses = [PermissionResponse.from_orm(p) for p in permissions]
    
    return PermissionListResponse(
        code=200,
        message="获取权限列表成功",
        data=permission_responses,
        total=total,
        page=page,
        pagesize=pagesize
    )




# ============================================
# 角色权限分配接口
# ============================================

@router.get("/roles/{role_id}/permissions", response_model=RolePermissionsResponse, summary="获取角色的权限列表")
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取指定角色拥有的所有权限
    
    参数:
    - role_id: 角色ID
    """
    
    # 检查角色是否存在
    role = db.query(SysRole).filter(SysRole.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 获取角色的所有权限
    permissions = db.query(SysPermission).join(
        rel_role_permission,
        SysPermission.id == rel_role_permission.c.permission_id
    ).filter(
        rel_role_permission.c.role_id == role_id
    ).all()
    
    permission_list = [
        {
            "id": p.id,
            "permission_code": p.permission_code,
            "permission_name": p.permission_name,
            "page_id": p.page_id,
            "page": {
                "id": p.page.id,
                "page_name": p.page.page_name,
                "page_display_name": p.page.page_display_name
            }
        }
        for p in permissions
    ]
    
    return RolePermissionsResponse(
        code=200,
        message="获取角色权限列表成功",
        data={
            "role_id": role_id,
            "role_name": role.role_name,
            "permissions": permission_list
        }
    )


@router.post("/roles/{role_id}/assign", response_model=RolePermissionAssignResponse, summary="为角色分配权限")
def assign_role_permissions(
    role_id: int,
    assign_request: RolePermissionAssignRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    为指定角色分配权限（覆盖式更新）
    
    参数:
    - role_id: 角色ID
    - permission_ids: 权限ID数组，传入该角色应该拥有的所有权限ID
    
    说明:
    - 这是覆盖式更新，会删除未包含的权限
    """
    
    # 检查角色是否存在
    role = db.query(SysRole).filter(SysRole.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 检查所有权限是否存在
    permissions = db.query(SysPermission).filter(
        SysPermission.id.in_(assign_request.permission_ids)
    ).all()
    
    if len(permissions) != len(assign_request.permission_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部分权限不存在"
        )
    
    # 删除该角色的所有现有权限
    db.query(rel_role_permission).filter(
        rel_role_permission.c.role_id == role_id
    ).delete()
    
    # 添加新权限
    for permission_id in assign_request.permission_ids:
        db.execute(
            rel_role_permission.insert().values(
                role_id=role_id,
                permission_id=permission_id
            )
        )
    
    db.commit()
    
    return RolePermissionAssignResponse(
        code=200,
        message="权限分配成功",
        data={
            "role_id": role_id,
            "assigned_permissions": len(assign_request.permission_ids),
            "permission_ids": assign_request.permission_ids
        }
    )


@router.post("/roles/batch-permissions", response_model=BatchRolePermissionsResponse, summary="批量获取多个角色的权限")
def batch_get_role_permissions(
    batch_request: BatchRolePermissionsRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    批量获取多个角色的权限（性能优化）
    
    参数:
    - role_ids: 角色ID数组
    """
    
    result = {}
    
    for role_id in batch_request.role_ids:
        # 获取该角色的所有权限
        permissions = db.query(SysPermission).join(
            rel_role_permission,
            SysPermission.id == rel_role_permission.c.permission_id
        ).filter(
            rel_role_permission.c.role_id == role_id
        ).all()
        
        result[str(role_id)] = [
            {
                "id": p.id,
                "permission_code": p.permission_code,
                "page_id": p.page_id
            }
            for p in permissions
        ]
    
    return BatchRolePermissionsResponse(
        code=200,
        message="批量获取角色权限成功",
        data=result
    )
