# 用户管理系统 - FastAPI

基于FastAPI框架的用户登录系统，支持多角色管理。

## 项目结构

```
.
├── main.py              # FastAPI应用入口
├── database.py          # 数据库连接配置
├── models.py            # SQLAlchemy数据模型
├── schemas.py           # Pydantic请求/响应模型
├── auth.py              # 认证和密码处理
├── routes.py            # API路由
├── init_db.sql          # 数据库初始化脚本
├── requirements.txt     # 项目依赖
└── README.md            # 本文件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 数据库配置

### 1. 创建数据库

使用MySQL客户端执行以下命令：

```bash
mysql -u root -p < init_db.sql
```

或者在MySQL中直接执行 `init_db.sql` 文件中的SQL语句。

### 2. 数据库连接

编辑 `database.py` 中的 `DATABASE_URL`：

```python
DATABASE_URL = "mysql+pymysql://root:password@localhost/gangganghao"
```

- `root`: MySQL用户名
- `password`: MySQL密码
- `localhost`: 数据库主机
- `gangganghao`: 数据库名称

## 运行应用

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API文档

启动应用后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API端点

### 1. 用户登录

**请求：**
```
POST /api/login
Content-Type: application/json

{
  "username": "superadmin",
  "password": "ls231007"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "id": 1,
    "username": "superadmin",
    "real_name": "超级管理员",
    "phone": "13800000001",
    "department": "系统管理部",
    "roles": [
      {
        "id": 1,
        "role_name": "superadmin",
        "description": "超级管理员"
      }
    ],
    "created_at": "2024-01-01T00:00:00"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. 获取用户信息

**请求：**
```
GET /api/user/{user_id}
```

**响应：**
```json
{
  "id": 1,
  "username": "superadmin",
  "real_name": "超级管理员",
  "phone": "13800000001",
  "department": "系统管理部",
  "roles": [...],
  "created_at": "2024-01-01T00:00:00"
}
```

## 数据库表结构

### sys_user（用户表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 用户ID（主键） |
| username | VARCHAR(50) | 账号（唯一） |
| password | VARCHAR(255) | 密码（加密存储） |
| real_name | VARCHAR(50) | 真实姓名 |
| id_card | VARCHAR(18) | 身份证号（唯一） |
| phone | VARCHAR(20) | 手机号 |
| department | VARCHAR(100) | 部门 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### sys_role（角色表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 角色ID（主键） |
| role_name | VARCHAR(50) | 角色名称（唯一） |
| description | TEXT | 角色描述 |
| created_at | DATETIME | 创建时间 |

### user_role_association（用户-角色关联表）

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | INT | 用户ID（外键） |
| role_id | INT | 角色ID（外键） |

## 默认账号

- **账号：** superadmin
- **密码：** ls231007
- **角色：** 超级管理员

## 安全说明

1. **密码加密**：使用bcrypt算法加密存储，原始密码不会被存储
2. **JWT令牌**：登录成功后返回JWT令牌，用于后续请求认证
3. **CORS**：已配置CORS中间件，允许跨域请求

## 生产环境建议

1. 修改 `auth.py` 中的 `SECRET_KEY`
2. 修改数据库连接密码
3. 设置 `database.py` 中的 `echo=False`
4. 配置环境变量管理敏感信息
5. 添加请求日志和错误处理
6. 配置HTTPS
7. 实现速率限制和请求验证
