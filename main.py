from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.auth import router as auth_router
from app.modules.user.routes import router as user_router
from app.modules.role.routes import router as role_router
from app.modules.department.routes import router as department_router
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

app = FastAPI(
    title="用户管理系统",
    description="基于FastAPI的用户登录系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

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
