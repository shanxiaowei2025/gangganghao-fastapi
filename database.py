import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量读取数据库连接字符串
# 优先使用 DATABASE_URL，如果没有则使用单独的配置参数
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@127.0.0.1:3306/gangganghao"
)

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
