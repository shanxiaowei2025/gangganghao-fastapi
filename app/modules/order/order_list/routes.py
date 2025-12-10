from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Union
from datetime import datetime

from database import get_db
from app.modules.auth.routes import get_current_user
from app.modules.user.models import SysUser
from app.modules.order.order_list.models import OrderItem
from app.modules.order.order_list.schemas import (
    OrderItemCreateRequest, OrderItemBatchCreateRequest, OrderItemUpdateRequest, OrderItemResponse,
    OrderItemListResponse, OrderItemDetailResponse, OrderItemBatchCreateResponse, OrderItemDeleteResponse,
    OrderNumberListResponse, OrderNumberItem
)
from app.modules.order.order_list.excel_parser import ExcelParser

router = APIRouter(prefix="/api/order", tags=["订单管理-订单列表"])


@router.post("", summary="创建订单项（支持单条和批量）")
def create_order_item(
    data: Union[OrderItemCreateRequest, OrderItemBatchCreateRequest],
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    创建订单项（支持单条和批量创建）
    
    单条创建示例:
    {
        "order_number": "20251209002",
        "project_name": "项目名称",
        "component": "构件",
        "location": "部位",
        "component_name": "构件名称",
        "number": "编号",
        "level_diameter": "级别直径",
        "edge_structure": "边角结构",
        "cutting_length_mm": "下料(mm)",
        "quantity_pieces": "根数*件数",
        "total_quantity": 10,
        "weight_kg": "重量(kg)"
    }
    
    批量创建示例:
    {
        "items": [
            {...},
            {...}
        ]
    }
    """
    
    try:
        # 判断是单条还是批量创建
        if isinstance(data, OrderItemBatchCreateRequest):
            # 批量创建
            created_items = []
            for item_data in data.items:
                new_order_item = OrderItem(
                    order_number=item_data.order_number,
                    project_name=item_data.project_name,
                    component=item_data.component,
                    location=item_data.location,
                    component_name=item_data.component_name,
                    number=item_data.number,
                    level_diameter=item_data.level_diameter,
                    rebar_sketch=item_data.rebar_sketch,
                    graph_info=item_data.graph_info,
                    edge_structure=item_data.edge_structure,
                    cutting_length_mm=item_data.cutting_length_mm,
                    quantity_pieces=item_data.quantity_pieces,
                    total_quantity=item_data.total_quantity,
                    weight_kg=item_data.weight_kg,
                    remark=item_data.remark
                )
                db.add(new_order_item)
                created_items.append(new_order_item)
            
            db.commit()
            
            # 刷新所有项目以获取ID
            for item in created_items:
                db.refresh(item)
            
            responses = [OrderItemResponse.from_orm(item) for item in created_items]
            
            return OrderItemBatchCreateResponse(
                code=200,
                message=f"批量创建成功，共创建 {len(responses)} 条记录",
                data=responses
            )
        else:
            # 单条创建
            new_order_item = OrderItem(
                order_number=data.order_number,
                project_name=data.project_name,
                component=data.component,
                location=data.location,
                component_name=data.component_name,
                number=data.number,
                level_diameter=data.level_diameter,
                rebar_sketch=data.rebar_sketch,
                graph_info=data.graph_info,
                edge_structure=data.edge_structure,
                cutting_length_mm=data.cutting_length_mm,
                quantity_pieces=data.quantity_pieces,
                total_quantity=data.total_quantity,
                weight_kg=data.weight_kg,
                remark=data.remark
            )
            
            db.add(new_order_item)
            db.commit()
            db.refresh(new_order_item)
            
            order_item_response = OrderItemResponse.from_orm(new_order_item)
            
            return OrderItemDetailResponse(
                code=200,
                message="订单项创建成功",
                data=order_item_response
            )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建失败: {str(e)}"
        )


@router.get("", response_model=OrderItemListResponse, summary="获取订单项列表")
def list_order_items(
    page: int = 1,
    pagesize: int = 10,
    order_number: str = None,
    project_name: str = None,
    component: str = None,
    location: str = None,
    component_name: str = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取订单项列表（分页 + 模糊查询）
    
    参数:
    - page: 页码（默认1）
    - pagesize: 每页记录数（默认10）
    - order_number: 订单编号（模糊查询，可选）
    - project_name: 项目名称（模糊查询，可选）
    - component: 构件（模糊查询，可选）
    - location: 部位（模糊查询，可选）
    - component_name: 构件名称（模糊查询，可选）
    """
    
    # 验证参数
    if page < 1:
        page = 1
    if pagesize < 1:
        pagesize = 10
    
    # 构建查询条件
    query = db.query(OrderItem)
    
    # 添加模糊查询条件
    if order_number:
        query = query.filter(OrderItem.order_number.ilike(f"%{order_number}%"))
    if project_name:
        query = query.filter(OrderItem.project_name.ilike(f"%{project_name}%"))
    if component:
        query = query.filter(OrderItem.component.ilike(f"%{component}%"))
    if location:
        query = query.filter(OrderItem.location.ilike(f"%{location}%"))
    if component_name:
        query = query.filter(OrderItem.component_name.ilike(f"%{component_name}%"))
    
    # 查询总数
    total = query.count()
    
    # 计算偏移量
    skip = (page - 1) * pagesize
    
    # 查询分页数据
    order_items = query.offset(skip).limit(pagesize).all()
    
    order_item_responses = [OrderItemResponse.from_orm(item) for item in order_items]
    
    return OrderItemListResponse(
        code=200,
        message="获取订单项列表成功",
        data=order_item_responses,
        total=total,
        page=page,
        pagesize=pagesize
    )


@router.get("/next-order-number", summary="获取下一个订单编号")
def get_next_order_number(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取下一个订单编号（查询数据库中当天的最大订单编号）
    
    返回:
    - 11位订单编号（YYYYMMDD + 3位序列号）
    """
    try:
        today = datetime.now().strftime('%Y%m%d')
        
        # 查询当天最大的订单编号
        max_order = db.query(OrderItem).filter(
            func.substr(OrderItem.order_number, 1, 8) == today
        ).order_by(OrderItem.order_number.desc()).first()
        
        if max_order:
            # 提取当前最大订单号的后三位，加1
            current_seq = int(max_order.order_number[-3:])
            next_seq = current_seq + 1
        else:
            # 当天没有订单，从001开始
            next_seq = 1
        
        # 生成新的订单编号
        order_number = today + str(next_seq).zfill(3)
        
        return {
            "code": 200,
            "message": "获取订单编号成功",
            "data": {
                "order_number": order_number
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单编号失败: {str(e)}"
        )


@router.get("/{order_id}", response_model=OrderItemDetailResponse, summary="获取订单项详情")
def get_order_item(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    获取指定订单项的详细信息
    
    参数:
    - order_id: 订单ID
    """
    
    db_order_item = db.query(OrderItem).filter(OrderItem.id == order_id).first()
    
    if not db_order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单项不存在"
        )
    
    order_item_response = OrderItemResponse.from_orm(db_order_item)
    
    return OrderItemDetailResponse(
        code=200,
        message="获取订单项详情成功",
        data=order_item_response
    )


@router.patch("/{order_id}", response_model=OrderItemDetailResponse, summary="更新订单项")
def update_order_item(
    order_id: int,
    order_item_update: OrderItemUpdateRequest,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    更新订单项信息（部分更新）
    
    参数:
    - order_id: 订单ID
    - 其他字段均为可选
    """
    
    db_order_item = db.query(OrderItem).filter(OrderItem.id == order_id).first()
    
    if not db_order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单项不存在"
        )
    
    # 更新非空字段
    if order_item_update.order_number is not None:
        db_order_item.order_number = order_item_update.order_number
    
    if order_item_update.project_name is not None:
        db_order_item.project_name = order_item_update.project_name
    
    if order_item_update.component is not None:
        db_order_item.component = order_item_update.component
    
    if order_item_update.location is not None:
        db_order_item.location = order_item_update.location
    
    if order_item_update.component_name is not None:
        db_order_item.component_name = order_item_update.component_name
    
    if order_item_update.number is not None:
        db_order_item.number = order_item_update.number
    
    if order_item_update.level_diameter is not None:
        db_order_item.level_diameter = order_item_update.level_diameter
    
    if order_item_update.rebar_sketch is not None:
        db_order_item.rebar_sketch = order_item_update.rebar_sketch
    
    if order_item_update.graph_info is not None:
        db_order_item.graph_info = order_item_update.graph_info
    
    if order_item_update.edge_structure is not None:
        db_order_item.edge_structure = order_item_update.edge_structure
    
    if order_item_update.cutting_length_mm is not None:
        db_order_item.cutting_length_mm = order_item_update.cutting_length_mm
    
    if order_item_update.quantity_pieces is not None:
        db_order_item.quantity_pieces = order_item_update.quantity_pieces
    
    if order_item_update.total_quantity is not None:
        db_order_item.total_quantity = order_item_update.total_quantity
    
    if order_item_update.weight_kg is not None:
        db_order_item.weight_kg = order_item_update.weight_kg
    
    if order_item_update.remark is not None:
        db_order_item.remark = order_item_update.remark
    
    db.commit()
    db.refresh(db_order_item)
    
    order_item_response = OrderItemResponse.from_orm(db_order_item)
    
    return OrderItemDetailResponse(
        code=200,
        message="订单项更新成功",
        data=order_item_response
    )


@router.delete("/{order_id}", response_model=OrderItemDeleteResponse, summary="删除订单项")
def delete_order_item(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    删除指定订单项
    
    参数:
    - order_id: 订单ID
    """
    
    db_order_item = db.query(OrderItem).filter(OrderItem.id == order_id).first()
    
    if not db_order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单项不存在"
        )
    
    db.delete(db_order_item)
    db.commit()
    
    return OrderItemDeleteResponse(
        code=200,
        message="订单项删除成功"
    )


@router.post("/import/excel", summary="解析 Excel 文件")
def import_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    解析 Excel 文件为订单数据
    
    参数:
    - file: Excel 文件（.xlsx 格式）
    
    返回:
    - 解析后的订单数据列表
    """
    try:
        # 读取上传的文件
        file_content = file.file.read()
        
        # 解析 Excel 文件
        data_list = ExcelParser.parse_excel(file_content)
        
        if not data_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Excel 文件中没有数据"
            )
        
        return {
            "code": 200,
            "message": "Excel 文件解析成功",
            "data": data_list,
            "total": len(data_list)
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件处理失败: {str(e)}"
        )


def generate_order_number(db: Session) -> str:
    """
    生成订单编号
    格式：YYYYMMDD + 3位序列号
    同一批数据使用相同的订单编号
    
    Returns:
        11位订单编号
    """
    today = datetime.now().strftime('%Y%m%d')
    
    # 查询当天最大的订单编号
    max_order = db.query(OrderItem).filter(
        func.substr(OrderItem.order_number, 1, 8) == today
    ).order_by(OrderItem.order_number.desc()).first()
    
    if max_order:
        # 提取当前最大订单号的后三位，加1
        current_seq = int(max_order.order_number[-3:])
        next_seq = current_seq + 1
    else:
        # 当天没有订单，从001开始
        next_seq = 1
    
    # 生成新的订单编号
    order_number = today + str(next_seq).zfill(3)
    return order_number


@router.get("/distinct/order-numbers", response_model=OrderNumberListResponse, summary="获取订单编号唯一值及对应项目名称")
def get_distinct_order_numbers(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user)
):
    """
    查询 sys_order 表中订单编号的唯一值，和各唯一值对应的项目名称、创建时间和更新时间
    
    返回:
    - 数组，数组内为字典，字典中有订单编号、项目名称、创建时间和更新时间
    """
    try:
        # 查询订单编号和项目名称的唯一组合，以及最新的创建时间和更新时间
        results = db.query(
            OrderItem.order_number,
            OrderItem.project_name,
            func.min(OrderItem.created_at).label('created_at'),
            func.max(OrderItem.updated_at).label('updated_at')
        ).group_by(OrderItem.order_number, OrderItem.project_name).all()
        
        # 将结果转换为字典列表
        data = [
            OrderNumberItem(
                order_number=result.order_number,
                project_name=result.project_name,
                created_at=result.created_at,
                updated_at=result.updated_at
            )
            for result in results
        ]
        
        return OrderNumberListResponse(
            code=200,
            message="获取订单编号唯一值成功",
            data=data
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询失败: {str(e)}"
        )
