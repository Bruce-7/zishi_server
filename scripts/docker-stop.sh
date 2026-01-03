#!/bin/bash
# Docker 停止脚本

set -e

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKER_CONFIG_DIR="$PROJECT_ROOT/configurations"

echo "========================================="
echo "停止 ZiShi Docker 容器"
echo "========================================="

# 检查 Docker Compose 是否安装并确定使用哪个命令
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo "错误: Docker Compose 未安装"
    exit 1
fi

echo "使用 Docker Compose 命令: $DOCKER_COMPOSE"
echo ""

# 进入配置目录
cd "$DOCKER_CONFIG_DIR"

# 停止并删除容器
echo "停止容器..."
$DOCKER_COMPOSE down

echo "========================================="
echo "✅ 容器已停止"
echo "========================================="
