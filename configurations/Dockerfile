# Django Web 服务基础镜像构建
# 只负责安装依赖与准备运行环境，所有敏感配置通过 configurations/.env 提供

FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# 安装系统依赖（如需可在此添加构建依赖）
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential default-libmysqlclient-dev wget curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY configurations/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# 拷贝项目代码
COPY . /app

# 默认命令交由 docker-compose 指定
