#!/bin/bash
# 部署前环境检查脚本

set -e

echo "========================================="
echo "部署环境检查"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查结果统计
PASSED=0
FAILED=0
WARNINGS=0

# 检查函数
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2 已安装"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $2 未安装"
        ((FAILED++))
        return 1
    fi
}

check_port() {
    if netstat -tuln 2>/dev/null | grep -q ":$1 "; then
        echo -e "${YELLOW}⚠${NC} 端口 $1 已被占用"
        ((WARNINGS++))
        return 1
    else
        echo -e "${GREEN}✓${NC} 端口 $1 可用"
        ((PASSED++))
        return 0
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} 文件存在: $1"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} 文件不存在: $1"
        ((FAILED++))
        return 1
    fi
}

# 1. 检查必要命令
echo "1. 检查必要软件"
echo "-----------------------------------"
check_command docker "Docker"
check_command docker-compose "Docker Compose" || check_command "docker compose" "Docker Compose"
check_command git "Git"
echo ""

# 2. 检查 Docker 服务
echo "2. 检查 Docker 服务"
echo "-----------------------------------"
if systemctl is-active --quiet docker 2>/dev/null || docker info &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker 服务运行中"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Docker 服务未运行"
    ((FAILED++))
fi
echo ""

# 3. 检查 Docker 镜像加速
echo "3. 检查 Docker 镜像加速配置"
echo "-----------------------------------"
if [ -f "/etc/docker/daemon.json" ]; then
    if grep -q "registry-mirrors" /etc/docker/daemon.json; then
        echo -e "${GREEN}✓${NC} Docker 镜像加速已配置"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} Docker 镜像加速未配置（国内服务器建议配置）"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠${NC} Docker 配置文件不存在（国内服务器建议配置镜像加速）"
    ((WARNINGS++))
fi
echo ""

# 4. 检查端口占用
echo "4. 检查端口占用"
echo "-----------------------------------"
check_port 8000
check_port 3306
echo ""

# 5. 检查项目文件
echo "5. 检查项目文件"
echo "-----------------------------------"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

check_file "$PROJECT_ROOT/manage.py"
check_file "$PROJECT_ROOT/configurations/Dockerfile"
check_file "$PROJECT_ROOT/configurations/docker-compose.yml"
check_file "$PROJECT_ROOT/configurations/requirements.txt"
echo ""

# 6. 检查环境配置文件
echo "6. 检查环境配置文件"
echo "-----------------------------------"
check_file "$PROJECT_ROOT/configurations/.env"
check_file "$PROJECT_ROOT/configurations/.env.production"
check_file "$PROJECT_ROOT/configurations/.env.example"
echo ""

# 7. 检查生产环境配置
echo "7. 检查生产环境配置"
echo "-----------------------------------"
if [ -f "$PROJECT_ROOT/configurations/.env.production" ]; then
    # 检查 DEBUG 设置
    if grep -q "^DEBUG=False" "$PROJECT_ROOT/configurations/.env.production"; then
        echo -e "${GREEN}✓${NC} DEBUG 已设置为 False"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} DEBUG 未设置为 False（生产环境必须为 False）"
        ((FAILED++))
    fi
    
    # 检查 SECRET_KEY
    if grep -q "^SECRET_KEY=django-insecure-" "$PROJECT_ROOT/configurations/.env.production"; then
        echo -e "${RED}✗${NC} SECRET_KEY 使用默认值（生产环境必须修改）"
        ((FAILED++))
    else
        echo -e "${GREEN}✓${NC} SECRET_KEY 已修改"
        ((PASSED++))
    fi
    
    # 检查 ALLOWED_HOSTS
    if grep -q "^ALLOWED_HOSTS=.*localhost.*" "$PROJECT_ROOT/configurations/.env.production"; then
        echo -e "${YELLOW}⚠${NC} ALLOWED_HOSTS 包含 localhost（建议配置实际域名）"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✓${NC} ALLOWED_HOSTS 已配置"
        ((PASSED++))
    fi
    
    # 检查 DB_HOST
    if grep -q "^DB_HOST=mysql" "$PROJECT_ROOT/configurations/.env.production"; then
        echo -e "${GREEN}✓${NC} DB_HOST 配置正确（mysql）"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} DB_HOST 不是 mysql（Docker 环境应该使用 mysql）"
        ((WARNINGS++))
    fi
fi
echo ""

# 8. 检查磁盘空间
echo "8. 检查磁盘空间"
echo "-----------------------------------"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✓${NC} 磁盘空间充足 (已使用 ${DISK_USAGE}%)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} 磁盘空间不足 (已使用 ${DISK_USAGE}%)"
    ((WARNINGS++))
fi
echo ""

# 9. 检查内存
echo "9. 检查内存"
echo "-----------------------------------"
if command -v free &> /dev/null; then
    TOTAL_MEM=$(free -m | awk 'NR==2 {print $2}')
    if [ "$TOTAL_MEM" -ge 2048 ]; then
        echo -e "${GREEN}✓${NC} 内存充足 (${TOTAL_MEM}MB)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} 内存较少 (${TOTAL_MEM}MB)，建议至少 2GB"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠${NC} 无法检查内存"
    ((WARNINGS++))
fi
echo ""

# 10. 检查脚本执行权限
echo "10. 检查脚本执行权限"
echo "-----------------------------------"
if [ -x "$PROJECT_ROOT/scripts/docker-start.sh" ]; then
    echo -e "${GREEN}✓${NC} docker-start.sh 有执行权限"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} docker-start.sh 无执行权限"
    echo "    运行: chmod +x $PROJECT_ROOT/scripts/docker-start.sh"
    ((FAILED++))
fi

if [ -x "$PROJECT_ROOT/scripts/docker-stop.sh" ]; then
    echo -e "${GREEN}✓${NC} docker-stop.sh 有执行权限"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} docker-stop.sh 无执行权限"
    echo "    运行: chmod +x $PROJECT_ROOT/scripts/docker-stop.sh"
    ((FAILED++))
fi

if [ -x "$PROJECT_ROOT/scripts/docker-db.sh" ]; then
    echo -e "${GREEN}✓${NC} docker-db.sh 有执行权限"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} docker-db.sh 无执行权限"
    echo "    运行: chmod +x $PROJECT_ROOT/scripts/docker-db.sh"
    ((FAILED++))
fi
echo ""

# 总结
echo "========================================="
echo "检查结果汇总"
echo "========================================="
echo -e "${GREEN}通过: $PASSED${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo -e "${YELLOW}警告: $WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 环境检查通过，可以开始部署！${NC}"
    echo ""
    echo "下一步操作："
    echo "  1. 修改生产环境配置: vim configurations/.env.production"
    echo "  2. 启动服务: ./scripts/docker-start.sh"
    echo "  3. 创建超级用户: docker-compose exec web python manage.py createsuperuser"
    exit 0
else
    echo -e "${RED}✗ 环境检查未通过，请解决上述问题后再部署${NC}"
    exit 1
fi
