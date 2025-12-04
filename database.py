import os
from urllib.parse import quote
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 从环境变量读取数据库配置
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = os.getenv("DB_PORT", "3306")
db_username = os.getenv("DB_USERNAME", "root")
db_password = os.getenv("DB_PASSWORD", "zhongyue123")
db_database = os.getenv("DB_DATABASE", "gangganghao")

# 对密码进行URL编码（处理特殊字符如@）
db_password_encoded = quote(db_password, safe='')

# 数据库连接字符串
DATABASE_URL = f"mysql+pymysql://{db_username}:{db_password_encoded}@{db_host}:{db_port}/{db_database}"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # 打印SQL语句，生产环境建议设为False
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    connect_args={
        "connect_timeout": 30,  # 连接超时时间（秒）
        "read_timeout": 30,  # 读超时时间（秒）
        "write_timeout": 30,  # 写超时时间（秒）
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
