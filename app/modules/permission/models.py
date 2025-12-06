from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class SysPage(Base):
    """系统页面表"""
    __tablename__ = "sys_page"

    id = Column(Integer, primary_key=True, index=True)
    page_name = Column(String(50), unique=True, nullable=False, comment="页面名称（英文）")
    page_display_name = Column(String(100), nullable=False, comment="页面显示名称（中文）")
    parent_id = Column(Integer, ForeignKey("sys_page.id", ondelete="SET NULL"), nullable=True, comment="父页面ID")
    description = Column(Text, nullable=True, comment="描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    permissions = relationship("SysPermission", back_populates="page", cascade="all, delete-orphan")
    parent = relationship("SysPage", remote_side=[id], backref="children")  # 自关联：父页面和子页面


class SysPermission(Base):
    """系统权限表"""
    __tablename__ = "sys_permission"

    id = Column(Integer, primary_key=True, index=True)
    permission_code = Column(String(100), unique=True, nullable=False, comment="权限代码 如: users:create")
    permission_name = Column(String(100), nullable=False, comment="权限名称")
    page_id = Column(Integer, ForeignKey("sys_page.id", ondelete="CASCADE"), nullable=False, comment="所属页面ID")
    description = Column(Text, nullable=True, comment="描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    page = relationship("SysPage", back_populates="permissions")
    roles = relationship("SysRole", secondary="rel_role_permission", back_populates="permissions")


# 角色权限关联表
rel_role_permission = Table(
    'rel_role_permission',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('sys_role.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('sys_permission.id', ondelete='CASCADE'), primary_key=True)
)
