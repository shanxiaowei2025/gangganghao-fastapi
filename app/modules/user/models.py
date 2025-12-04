from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# 用户-角色关联表（多对多）
user_role_association = Table(
    'user_role_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('sys_user.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('sys_role.id'), primary_key=True)
)


class SysUser(Base):
    __tablename__ = "sys_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="账号")
    password = Column(String(255), nullable=False, comment="密码")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    id_card = Column(String(18), unique=True, nullable=False, comment="身份证号")
    phone = Column(String(20), nullable=False, comment="手机号")
    department = Column(String(100), nullable=False, comment="部门")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    roles = relationship("SysRole", secondary=user_role_association, back_populates="users")


class SysRole(Base):
    __tablename__ = "sys_role"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    description = Column(Text, nullable=True, comment="角色描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关系
    users = relationship("SysUser", secondary=user_role_association, back_populates="roles")
