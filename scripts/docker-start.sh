#!/usr/bin/env bash

# Docker 启动脚本：自动切换配置、启动/更新容器并执行基础运维命令
# 必须在项目根目录执行，确保 configurations 目录存在

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="${ROOT_DIR}/configurations"
ENV_FILE="${CONFIG_DIR}/.env"
COMPOSE_FILE="${CONFIG_DIR}/docker-compose.yml"
DOCKER_CONFIG_DIR="${CONFIG_DIR}"
ENV_NAME=""

if [[ ! -f "${ROOT_DIR}/configurations/Dockerfile" || ! -f "${COMPOSE_FILE}" ]]; then
  echo "❌ 未找到 configurations/Dockerfile 或 docker-compose.yml，请确认项目结构。" >&2
  exit 1
fi

choose_env() {
  echo "请选择部署环境:"
  echo "  1) local        (本地开发 - DB_HOST=127.0.0.1)"
  echo "  2) development  (Docker 开发 - DB_HOST=mysql)"
  echo "  3) production   (生产环境 - DB_HOST=mysql)"
  read -r -p "请输入序号 [1-3]: " choice

  case "${choice}" in
    1) template=".env.local"; ENV_NAME="local" ;;
    2) template=".env.development"; ENV_NAME="development" ;;
    3) template=".env.production"; ENV_NAME="production" ;;
    *) echo "❌ 无效选项，请重新运行脚本。" >&2; exit 1 ;;
  esac

  if [[ ! -f "${CONFIG_DIR}/${template}" ]]; then
    echo "❌ 模板文件 ${template} 不存在，请先创建。" >&2
    exit 1
  fi

  cp "${CONFIG_DIR}/${template}" "${ENV_FILE}"
  echo "✅ 已切换环境为 ${template} -> .env"
}

export COMPOSE_PROJECT_NAME="zishi_server"
COMPOSE_CMD=(docker compose -f "${COMPOSE_FILE}")
run_compose() {
  "${COMPOSE_CMD[@]}" "$@"
}

choose_env

echo "🚀 构建并启动 Docker 服务..."
run_compose up -d --build --remove-orphans

echo "⏳ 等待数据库准备完毕..."
service_status="$(run_compose ps || true)"

if echo "${service_status}" | grep -q "Up"; then
  echo "========================================="
  echo "✅ 容器启动成功！"
  echo "========================================="
  echo "部署环境: ${ENV_NAME}"
  echo "配置文件: ${ENV_FILE}"
  echo ""
  echo "服务状态:"
  echo "${service_status}"
  echo ""
  if [[ "${ENV_NAME}" == "local" ]]; then
    echo "访问地址: http://localhost:8000"
    echo "API 文档: http://localhost:8000/docs/"
    echo "管理后台: http://localhost:8000/zishi_admin/"
  elif [[ "${ENV_NAME}" == "development" ]]; then
    echo "HTTP 访问: http://43.140.248.182"
    echo "API 文档: http://43.140.248.182/docs/"
    echo "管理后台: http://43.140.248.182/zishi_admin/"
  else
    echo "HTTP 访问: http://api.dry-zishi.com （自动重定向到 HTTPS）"
    echo "HTTPS 访问: https://api.dry-zishi.com"
    echo "API 文档: https://api.dry-zishi.com/docs/"
    echo "管理后台: https://api.dry-zishi.com/zishi_admin/"
  fi
  echo "MySQL 端口: localhost:3306"
  echo ""
  echo "常用命令（需要在 configurations 目录下执行）:"
  echo "  cd ${DOCKER_CONFIG_DIR}"
  echo "  docker compose -p ${COMPOSE_PROJECT_NAME} logs -f              # 查看所有日志"
  echo "  docker compose -p ${COMPOSE_PROJECT_NAME} logs -f web          # 查看 Web 日志"
  echo "  docker compose -p ${COMPOSE_PROJECT_NAME} logs -f mysql        # 查看 MySQL 日志"
  echo "  docker compose -p ${COMPOSE_PROJECT_NAME} down                 # 停止服务"
  echo "  docker compose -p ${COMPOSE_PROJECT_NAME} restart              # 重启服务"
  echo "  docker compose -p ${COMPOSE_PROJECT_NAME} exec web bash        # 进入 Web 容器"
  echo "  docker compose -p ${COMPOSE_PROJECT_NAME} exec mysql bash      # 进入 MySQL 容器"
  echo "========================================="
else
  echo "========================================="
  echo "❌ 容器启动失败，请查看日志"
  echo "========================================="
  run_compose logs
  exit 1
fi
