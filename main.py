from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.modules.auth import router as auth_router
from app.modules.user.routes import router as user_router
from app.modules.role.routes import router as role_router
from app.modules.department.routes import router as department_router
from app.modules.permission.routes import router as permission_router
from app.modules.order.order_list import router as order_item_router
from dotenv import load_dotenv
from database import Base, engine

# 导入所有模型以确保它们被注册到 Base.metadata
from app.modules.user.models import SysUser
from app.modules.role.models import SysRole
from app.modules.department.models import SysDepartment
from app.modules.permission.models import SysPermission
from app.modules.order.order_list.models import OrderItem

# 加载 .env 文件
load_dotenv()

# 创建所有表（已禁用，需要手动创建数据表）
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="用户管理系统",
    description="基于FastAPI的用户登录系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 禁用 Swagger 文档缓存的中间件
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # 为 Swagger 相关路径添加禁用缓存头
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheMiddleware)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(department_router)
app.include_router(permission_router)
app.include_router(order_item_router)


@app.get("/")
def read_root():
    return {
        "message": "欢迎使用用户管理系统",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import os
    import uvicorn
    
    # 根据环境变量决定是否启用热重载
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=reload)
