from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class OrderItemCreateRequest(BaseModel):
    """订单项创建请求"""
    order_number: str
    project_name: str
    component: str
    location: str
    component_name: Optional[str] = None
    number: str
    level_diameter: str
    rebar_sketch: Optional[str] = None
    graph_info: Optional[str] = None
    edge_structure: str
    cutting_length_mm: str
    quantity_pieces: str
    total_quantity: int
    weight_kg: str
    remark: Optional[str] = None


class OrderItemBatchCreateRequest(BaseModel):
    """订单项批量创建请求"""
    items: List[OrderItemCreateRequest]


class OrderItemUpdateRequest(BaseModel):
    """订单项更新请求"""
    order_number: Optional[str] = None
    project_name: Optional[str] = None
    component: Optional[str] = None
    location: Optional[str] = None
    component_name: Optional[str] = None
    number: Optional[str] = None
    level_diameter: Optional[str] = None
    rebar_sketch: Optional[str] = None
    graph_info: Optional[str] = None
    edge_structure: Optional[str] = None
    cutting_length_mm: Optional[str] = None
    quantity_pieces: Optional[str] = None
    total_quantity: Optional[int] = None
    weight_kg: Optional[str] = None
    remark: Optional[str] = None


class OrderItemResponse(BaseModel):
    """订单项响应"""
    id: int
    order_number: str
    project_name: str
    component: str
    location: str
    component_name: Optional[str] = None
    number: str
    level_diameter: str
    rebar_sketch: Optional[str] = None
    graph_info: Optional[str] = None
    edge_structure: str
    cutting_length_mm: str
    quantity_pieces: str
    total_quantity: int
    weight_kg: str
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderItemListResponse(BaseModel):
    """订单项列表响应"""
    code: int
    message: str
    data: List[OrderItemResponse] = []
    total: int = 0
    page: int = 1
    pagesize: int = 10


class OrderItemDetailResponse(BaseModel):
    """订单项详情响应"""
    code: int
    message: str
    data: Optional[OrderItemResponse] = None


class OrderItemBatchCreateResponse(BaseModel):
    """订单项批量创建响应"""
    code: int
    message: str
    data: List[OrderItemResponse] = []


class OrderItemDeleteResponse(BaseModel):
    """订单项删除响应"""
    code: int
    message: str


class OrderNumberItem(BaseModel):
    """订单编号、项目名称、创建时间和更新时间"""
    order_number: str
    project_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrderNumberListResponse(BaseModel):
    """订单编号列表响应"""
    code: int
    message: str
    data: List[OrderNumberItem] = []
