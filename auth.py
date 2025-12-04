# 兼容层：将根目录的 auth 导入重定向到新的位置
# 这个文件保留用于向后兼容，新代码应该从 app.modules.auth 导入

from app.modules.auth import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
]
