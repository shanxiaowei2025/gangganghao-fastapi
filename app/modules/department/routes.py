from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from app.modules.auth.utils import check_permission
from app.modules.auth.routes import get_current_user
from app.modules.user.models import SysUser
from app.modules.department.models import SysDepartment
from app.modules.department.schemas import (
    DepartmentCreateRequest, DepartmentUpdateRequest, DepartmentResponse,
    DepartmentListResponse, DepartmentDetailResponse, DepartmentDeleteResponse
)

router = APIRouter(prefix="/api/departments", tags=["部门管理"])


@router.post("", response_model=DepartmentDetailResponse, summary="创建部门")
def create_department(
    dept_create: DepartmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建新部门
    
    参数:
    - department_name: 部门名称（唯一）
    - description: 部门描述（可选）
    - parent_id: 父部门ID（可选）
    
    需要权限: department:create
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'department:create', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
    # 检查部门名称是否已存在
    existing_dept = db.query(SysDepartment).filter(
        SysDepartment.department_name == dept_create.department_name
    ).first()
    if existing_dept:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部门名称已存在"
        )
    
    # 如果指定了父部门，检查父部门是否存在
    if dept_create.parent_id is not None:
        parent_dept = db.query(SysDepartment).filter(
            SysDepartment.id == dept_create.parent_id
        ).first()
        if not parent_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父部门不存在"
            )
    
    # 创建新部门
    new_dept = SysDepartment(
        department_name=dept_create.department_name,
        description=dept_create.description,
        parent_id=dept_create.parent_id
    )
    
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    
    dept_response = DepartmentResponse.from_orm(new_dept)
    
    return DepartmentDetailResponse(
        code=200,
        message="部门创建成功",
        data=dept_response
    )


@router.get("", response_model=DepartmentListResponse, summary="获取部门列表")
def list_departments(
    page: int = 1,
    pagesize: int = 10,
    department_name: str = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取部门列表（分页 + 模糊查询）
    
    参数:
    - page: 页码（默认1）
    - pagesize: 每页记录数（默认10）
    - department_name: 部门名称（模糊查询，可选）
    
    需要权限: department:read
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'department:read', db)
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
    query = db.query(SysDepartment)
    
    # 添加模糊查询条件
    if department_name:
        query = query.filter(SysDepartment.department_name.ilike(f"%{department_name}%"))
    
    # 查询总数
    total = query.count()
    
    # 计算偏移量
    skip = (page - 1) * pagesize
    
    # 查询分页数据
    departments = query.offset(skip).limit(pagesize).all()
    
    dept_responses = [DepartmentResponse.from_orm(dept) for dept in departments]
    
    return DepartmentListResponse(
        code=200,
        message="获取部门列表成功",
        data=dept_responses,
        total=total,
        page=page,
        pagesize=pagesize
    )


@router.get("/{dept_id}", response_model=DepartmentDetailResponse, summary="获取部门详情")
def get_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取指定部门的详细信息
    
    参数:
    - dept_id: 部门ID
    
    需要权限: department:read
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'department:read', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
    db_dept = db.query(SysDepartment).filter(SysDepartment.id == dept_id).first()
    
    if not db_dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    
    dept_response = DepartmentResponse.from_orm(db_dept)
    
    return DepartmentDetailResponse(
        code=200,
        message="获取部门详情成功",
        data=dept_response
    )


@router.patch("/{dept_id}", response_model=DepartmentDetailResponse, summary="更新部门信息")
def update_department(
    dept_id: int,
    dept_update: DepartmentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新部门信息（部分更新）
    
    参数:
    - dept_id: 部门ID
    - department_name: 部门名称（可选）
    - description: 部门描述（可选）
    - parent_id: 父部门ID（可选）
    
    需要权限: department:update
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'department:update', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
    db_dept = db.query(SysDepartment).filter(SysDepartment.id == dept_id).first()
    
    if not db_dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    
    # 检查部门名称是否被其他部门使用
    if dept_update.department_name is not None and dept_update.department_name != db_dept.department_name:
        existing_dept = db.query(SysDepartment).filter(
            SysDepartment.department_name == dept_update.department_name,
            SysDepartment.id != dept_id
        ).first()
        if existing_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门名称已被其他部门使用"
            )
    
    # 如果更新了父部门，检查父部门是否存在
    if dept_update.parent_id is not None and dept_update.parent_id != db_dept.parent_id:
        parent_dept = db.query(SysDepartment).filter(
            SysDepartment.id == dept_update.parent_id
        ).first()
        if not parent_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父部门不存在"
            )
        
        # 防止循环关联（部门不能是自己的父部门）
        if dept_update.parent_id == dept_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门不能是自己的父部门"
            )
    
    # 更新非空字段
    if dept_update.department_name is not None:
        db_dept.department_name = dept_update.department_name
    
    if dept_update.description is not None:
        db_dept.description = dept_update.description
    
    if dept_update.parent_id is not None:
        db_dept.parent_id = dept_update.parent_id
    
    db.commit()
    db.refresh(db_dept)
    
    dept_response = DepartmentResponse.from_orm(db_dept)
    
    return DepartmentDetailResponse(
        code=200,
        message="部门信息更新成功",
        data=dept_response
    )


@router.delete("/{dept_id}", response_model=DepartmentDeleteResponse, summary="删除部门")
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    删除指定部门
    
    参数:
    - dept_id: 部门ID
    
    需要权限: department:delete
    """
    
    # 检查权限
    has_permission, permission_name = check_permission(current_user, 'department:delete', db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要权限: {permission_name}"
        )
    
    db_dept = db.query(SysDepartment).filter(SysDepartment.id == dept_id).first()
    
    if not db_dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    
    # 检查是否有子部门
    if db_dept.children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法删除：该部门仍有子部门"
        )
    
    db.delete(db_dept)
    db.commit()
    
    return DepartmentDeleteResponse(
        code=200,
        message="部门删除成功"
    )
