from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# 用户-角色关联表（多对多）
rel_user_role = Table(
    'rel_user_role',
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
    department_id = Column(Integer, ForeignKey('sys_department.id'), nullable=False, comment="部门ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    roles = relationship("SysRole", secondary=rel_user_role, back_populates="users")
    department = relationship("SysDepartment", backref="users")
