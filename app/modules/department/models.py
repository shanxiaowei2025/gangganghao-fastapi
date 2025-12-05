from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class SysDepartment(Base):
    __tablename__ = "sys_department"

    id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String(100), unique=True, nullable=False, comment="部门名称")
    description = Column(Text, nullable=True, comment="部门描述")
    parent_id = Column(Integer, ForeignKey('sys_department.id'), nullable=True, comment="父部门ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 自关联关系
    parent = relationship("SysDepartment", remote_side=[id], backref="children")
