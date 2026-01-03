#!/bin/bash
# Docker 快速启动脚本

set -e

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKER_CONFIG_DIR="$PROJECT_ROOT/configurations"

# 选择环境
echo "========================================="
echo "启动 ZiShi Docker 容器"
echo "========================================="
echo "请选择部署环境:"
echo "  1) local (本地开发环境 - 本地 MySQL)"
echo "  2) development (开发环境 - Docker MySQL)"
echo "  3) production (生产环境 - Docker MySQL)"
echo ""
read -p "请输入选项 [1/2/3] (默认: 2): " ENV_CHOICE

# 根据选择设置环境配置文件
case "${ENV_CHOICE:-2}" in
    1)
        ENV_FILE=".env.local"
        ENV_NAME="local"
        ;;
    2)
        ENV_FILE=".env.development"
        ENV_NAME="development"
        ;;
    3)
        ENV_FILE=".env.production"
        ENV_NAME="production"
        ;;
    *)
        echo "无效选项，使用默认环境: development"
        ENV_FILE=".env.development"
        ENV_NAME="development"
        ;;
esac

# 检查环境配置文件是否存在
if [ ! -f "$DOCKER_CONFIG_DIR/$ENV_FILE" ]; then
    echo "错误: 环境配置文件不存在: $DOCKER_CONFIG_DIR/$ENV_FILE"
    exit 1
fi

echo ""
echo "========================================="
echo "部署环境: $ENV_NAME"
echo "配置文件: $ENV_FILE"
echo "项目目录: $PROJECT_ROOT"
echo "Docker配置: $DOCKER_CONFIG_DIR"
echo "========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装并确定使用哪个命令
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo "错误: Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "使用 Docker Compose 命令: $DOCKER_COMPOSE"
echo ""

# 进入项目根目录
cd "$PROJECT_ROOT"

# 创建必要的目录
mkdir -p logs media

# 复制环境配置文件到 configurations/.env
echo "复制环境配置文件..."
cp "$DOCKER_CONFIG_DIR/$ENV_FILE" "$DOCKER_CONFIG_DIR/.env"
echo "✅ 已复制 $ENV_FILE 到 .env"
echo ""

# 停止并删除旧容器
echo "停止旧容器..."
cd "$DOCKER_CONFIG_DIR"
$DOCKER_COMPOSE down 2>/dev/null || true

# 构建镜像
echo "构建 Docker 镜像..."
$DOCKER_COMPOSE build

# 启动容器
echo "启动容器..."
$DOCKER_COMPOSE up -d

# 等待 MySQL 服务健康检查通过
echo "等待 MySQL 服务启动..."
for i in {1..30}; do
    if $DOCKER_COMPOSE ps mysql | grep -q "healthy"; then
        echo "✅ MySQL 服务已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ MySQL 服务启动超时"
        $DOCKER_COMPOSE logs mysql
        exit 1
    fi
    sleep 2
done

# 等待 Web 服务启动
echo "等待 Web 服务启动..."
sleep 5

# 检查容器状态
if $DOCKER_COMPOSE ps | grep -q "Up"; then
    echo "========================================="
    echo "✅ 容器启动成功！"
    echo "========================================="
    echo "部署环境: $ENV_NAME"
    echo "配置文件: $ENV_FILE"
    echo ""
    echo "服务状态:"
    $DOCKER_COMPOSE ps
    echo ""
    echo "访问地址: http://localhost:8000"
    echo "API 文档: http://localhost:8000/docs/"
    echo "管理后台: http://localhost:8000/zishi_admin/"
    echo "MySQL 端口: localhost:3306"
    echo ""
    echo "常用命令（需要在 configurations 目录下执行）:"
    echo "  cd $DOCKER_CONFIG_DIR"
    echo "  $DOCKER_COMPOSE logs -f              # 查看所有日志"
    echo "  $DOCKER_COMPOSE logs -f web          # 查看 Web 日志"
    echo "  $DOCKER_COMPOSE logs -f mysql        # 查看 MySQL 日志"
    echo "  $DOCKER_COMPOSE down                 # 停止服务"
    echo "  $DOCKER_COMPOSE restart              # 重启服务"
    echo "  $DOCKER_COMPOSE exec web bash        # 进入 Web 容器"
    echo "  $DOCKER_COMPOSE exec mysql bash      # 进入 MySQL 容器"
    echo "========================================="
else
    echo "========================================="
    echo "❌ 容器启动失败，请查看日志"
    echo "========================================="
    $DOCKER_COMPOSE logs
    exit 1
fi
