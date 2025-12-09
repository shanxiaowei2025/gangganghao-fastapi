from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class OrderItem(Base):
    """订单表"""
    __tablename__ = "sys_order"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(11), nullable=False, index=True, comment="订单编号")
    project_name = Column(String(255), nullable=False, comment="项目名称")
    component = Column(String(255), nullable=False, comment="构件")
    location = Column(String(255), nullable=False, comment="部位")
    component_name = Column(String(255), nullable=True, comment="构件名称")
    number = Column(String(5), nullable=False, comment="编号")
    level_diameter = Column(String(100), nullable=False, comment="级别直径")
    rebar_sketch = Column(String(500), nullable=True, comment="钢筋简图")
    graph_info = Column(String(255), nullable=True, comment="图形信息")
    edge_structure = Column(String(255), nullable=False, comment="边角结构")
    cutting_length_mm = Column(String(100), nullable=False, comment="下料(mm)")
    quantity_pieces = Column(String(100), nullable=False, comment="根数*件数")
    total_quantity = Column(Integer, nullable=False, comment="总根数")
    weight_kg = Column(String(100), nullable=False, comment="重量(kg)")
    remark = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
