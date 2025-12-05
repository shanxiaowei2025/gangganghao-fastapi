from sqlalchemy import Column, Integer, String, DateTime, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# 角色-权限关联表（多对多）
role_permission_association = Table(
    'role_permission_association',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('sys_role.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('sys_permission.id'), primary_key=True)
)


class SysRole(Base):
    __tablename__ = "sys_role"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    description = Column(Text, nullable=True, comment="角色描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    users = relationship("SysUser", secondary="user_role_association", back_populates="roles")
    permissions = relationship("SysPermission", secondary=role_permission_association, back_populates="roles")
