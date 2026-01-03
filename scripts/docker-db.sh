#!/bin/bash
# Docker MySQL 数据库管理脚本

set -e

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKER_CONFIG_DIR="$PROJECT_ROOT/configurations"

# 检查 Docker Compose 是否安装并确定使用哪个命令
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo "错误: Docker Compose 未安装"
    exit 1
fi

# 进入配置目录
cd "$DOCKER_CONFIG_DIR"

# 读取当前环境配置（从 configurations/.env）
if [ -f "$DOCKER_CONFIG_DIR/.env" ]; then
    DB_NAME=$(grep "^DB_NAME=" "$DOCKER_CONFIG_DIR/.env" | cut -d '=' -f2)
    DB_PASSWORD=$(grep "^DB_PASSWORD=" "$DOCKER_CONFIG_DIR/.env" | cut -d '=' -f2)
    DJANGO_ENV=$(grep "^DJANGO_ENV=" "$DOCKER_CONFIG_DIR/.env" | cut -d '=' -f2)
else
    echo "警告: 未找到 configurations/.env 文件，使用默认配置"
    DB_NAME="zishi_server_dev"
    DB_PASSWORD="root"
    DJANGO_ENV="development"
fi

# 显示帮助信息
show_help() {
    echo "========================================="
    echo "MySQL 数据库管理脚本"
    echo "========================================="
    echo "当前环境: $DJANGO_ENV"
    echo "数据库名: $DB_NAME"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo "  backup              备份数据库"
    echo "  restore <file>      从备份文件恢复数据库"
    echo "  shell               进入 MySQL 命令行"
    echo "  logs                查看 MySQL 日志"
    echo "  reset               重置数据库（删除所有数据）"
    echo "  status              查看数据库状态"
    echo "  help                显示此帮助信息"
    echo "========================================="
}

# 备份数据库
backup_db() {
    echo "开始备份数据库..."
    echo "环境: $DJANGO_ENV"
    echo "数据库: $DB_NAME"
    BACKUP_DIR="$PROJECT_ROOT/backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql"
    
    $DOCKER_COMPOSE exec -T mysql mysqldump -u root -p"$DB_PASSWORD" "$DB_NAME" > "$BACKUP_FILE"
    
    echo "✅ 数据库备份完成: $BACKUP_FILE"
}

# 恢复数据库
restore_db() {
    if [ -z "$1" ]; then
        echo "错误: 请指定备份文件路径"
        echo "用法: $0 restore <backup_file>"
        exit 1
    fi
    
    if [ ! -f "$1" ]; then
        echo "错误: 备份文件不存在: $1"
        exit 1
    fi
    
    echo "开始恢复数据库..."
    echo "环境: $DJANGO_ENV"
    echo "数据库: $DB_NAME"
    $DOCKER_COMPOSE exec -T mysql mysql -u root -p"$DB_PASSWORD" "$DB_NAME" < "$1"
    echo "✅ 数据库恢复完成"
}

# 进入 MySQL 命令行
mysql_shell() {
    echo "进入 MySQL 命令行..."
    echo "数据库: $DB_NAME"
    $DOCKER_COMPOSE exec mysql mysql -u root -p"$DB_PASSWORD" "$DB_NAME"
}

# 查看 MySQL 日志
mysql_logs() {
    echo "查看 MySQL 日志..."
    $DOCKER_COMPOSE logs -f mysql
}

# 重置数据库
reset_db() {
    echo "⚠️  警告: 此操作将删除所有数据库数据！"
    echo "环境: $DJANGO_ENV"
    echo "数据库: $DB_NAME"
    read -p "确认重置数据库？(yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "操作已取消"
        exit 0
    fi
    
    echo "重置数据库..."
    $DOCKER_COMPOSE exec mysql mysql -u root -p"$DB_PASSWORD" -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo "运行数据库迁移..."
    $DOCKER_COMPOSE exec web python manage.py migrate
    echo "✅ 数据库重置完成"
}

# 查看数据库状态
db_status() {
    echo "数据库状态:"
    echo "环境: $DJANGO_ENV"
    echo "数据库: $DB_NAME"
    $DOCKER_COMPOSE exec mysql mysql -u root -p"$DB_PASSWORD" -e "SHOW DATABASES; SELECT VERSION();"
}

# 主逻辑
case "${1:-help}" in
    backup)
        backup_db
        ;;
    restore)
        restore_db "$2"
        ;;
    shell)
        mysql_shell
        ;;
    logs)
        mysql_logs
        ;;
    reset)
        reset_db
        ;;
    status)
        db_status
        ;;
    help|*)
        show_help
        ;;
esac
