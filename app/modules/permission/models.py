from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class SysPage(Base):
    __tablename__ = "sys_page"

    id = Column(Integer, primary_key=True, index=True)
    page_name = Column(String(50), unique=True, nullable=False, index=True, comment="页面名称")
    page_display_name = Column(String(100), nullable=False, comment="页面显示名称")
    description = Column(Text, nullable=True, comment="页面描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    permissions = relationship("SysPermission", back_populates="page")


class SysPermission(Base):
    __tablename__ = "sys_permission"

    id = Column(Integer, primary_key=True, index=True)
    permission_code = Column(String(100), unique=True, nullable=False, index=True, comment="权限代码")
    permission_name = Column(String(100), nullable=False, comment="权限名称")
    page_id = Column(Integer, ForeignKey('sys_page.id'), nullable=False, comment="页面ID")
    description = Column(Text, nullable=True, comment="权限描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    page = relationship("SysPage", back_populates="permissions")
    roles = relationship("SysRole", secondary="role_permission_association", back_populates="permissions")
