# 使用官方 Python 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 配置腾讯云 apt 源并安装系统依赖
RUN echo "deb http://mirrors.cloud.tencent.com/debian bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
    echo "deb http://mirrors.cloud.tencent.com/debian bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 先复制 requirements.txt（这样可以利用 Docker 缓存）
COPY requirements.txt .

# 升级 pip 并安装 Python 依赖（使用腾讯云镜像源）
RUN pip install --upgrade pip -i https://mirrors.cloud.tencent.com/pypi/simple && \
    pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple

# 复制项目文件（放在最后，避免频繁重建）
COPY . .

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["python", "main.py"]
