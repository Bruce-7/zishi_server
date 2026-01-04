#!/usr/bin/env bash

# Docker 停止脚本：安全停止并移除容器

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="${ROOT_DIR}/configurations"
COMPOSE_FILE="${CONFIG_DIR}/docker-compose.yml"

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "❌ 未找到 configurations/docker-compose.yml，请确认项目结构。" >&2
  exit 1
fi

export COMPOSE_PROJECT_NAME="zishi_server"

# 设置环境变量避免警告
cd "${CONFIG_DIR}"

echo "🛑 正在停止 Docker 服务..."
docker compose -p zishi_server down --remove-orphans "$@"

echo "✅ Docker 服务已停止。"
