# Docker 脚本使用说明

## 脚本列表

### 1. docker-start.sh - 启动 Docker 服务
启动完整的 Docker 环境（包括 MySQL 和 Web 服务）

```bash
./scripts/docker-start.sh
```

**启动时会提示选择环境：**
- 1) development (开发环境) - 使用 `configurations/.env` 配置
- 2) production (生产环境) - 使用 `configurations/.env.production` 配置

**功能：**
- 选择部署环境（development/production）
- 自动复制对应的环境配置文件到项目根目录
- 自动检测并使用正确的 Docker Compose 命令
- 停止并删除旧容器
- 构建最新的 Docker 镜像
- 启动 MySQL 和 Web 服务
- 等待 MySQL 健康检查通过
- 自动运行数据库迁移
- 显示服务状态和访问地址

### 2. docker-stop.sh - 停止 Docker 服务
停止所有 Docker 容器

```bash
./scripts/docker-stop.sh
```

### 3. docker-db.sh - 数据库管理
管理 Docker 中的 MySQL 数据库，**自动识别当前环境配置**

```bash
# 查看帮助（显示当前环境和数据库名）
./scripts/docker-db.sh help

# 备份数据库（文件名包含数据库名称）
./scripts/docker-db.sh backup

# 恢复数据库
./scripts/docker-db.sh restore backups/zishi_server_prod_20240103_120000.sql

# 进入 MySQL 命令行
./scripts/docker-db.sh shell

# 查看 MySQL 日志
./scripts/docker-db.sh logs

# 重置数据库（危险操作，会显示环境确认）
./scripts/docker-db.sh reset

# 查看数据库状态
./scripts/docker-db.sh status
```

**注意：** `docker-db.sh` 会自动读取项目根目录的 `.env` 文件，使用其中的数据库配置（数据库名、密码等）。

## 环境配置文件说明

### configurations/.env
开发环境配置，数据库名为 `zishi_server_dev`

### configurations/.env.production
生产环境配置，数据库名为 `zishi_server_prod`

### configurations/.env.example
配置文件示例模板

### 环境切换流程

1. 运行 `./scripts/docker-start.sh`
2. 选择环境（1=development, 2=production）
3. 脚本自动将对应配置复制到项目根目录 `.env`
4. 启动 Docker 服务
5. 后续所有数据库操作自动使用当前环境配置

## Docker 服务说明

### MySQL 服务
- **容器名称**: zishi_mysql
- **端口映射**: 3306:3306
- **数据持久化**: Docker volume `mysql_data`
- **字符集**: utf8mb4
- **排序规则**: utf8mb4_unicode_ci
- **开发环境数据库**: zishi_server_dev
- **生产环境数据库**: zishi_server_prod

### Web 服务
- **容器名称**: zishi_web
- **端口映射**: 8000:8000
- **依赖服务**: MySQL（等待健康检查通过）
- **自动执行**: 数据库迁移、静态文件收集

## 常用 Docker Compose 命令

```bash
cd configurations/

# 查看所有日志
docker compose logs -f

# 查看 Web 服务日志
docker compose logs -f web

# 查看 MySQL 日志
docker compose logs -f mysql

# 重启服务
docker compose restart

# 重启单个服务
docker compose restart web

# 进入 Web 容器
docker compose exec web bash

# 进入 MySQL 容器
docker compose exec mysql bash

# 查看服务状态
docker compose ps

# 停止服务（保留数据）
docker compose down

# 停止服务并删除数据卷（危险）
docker compose down -v
```

## 数据持久化

- **MySQL 数据**: 使用 Docker volume `mysql_data` 持久化
- **媒体文件**: 挂载到 `../media` 目录
- **日志文件**: 挂载到 `../logs` 目录
- **数据库备份**: 保存到 `../backups` 目录

## 部署示例

### 开发环境部署

```bash
# 1. 启动服务并选择开发环境
./scripts/docker-start.sh
# 选择: 1 (development)

# 2. 创建超级用户（可选）
cd configurations/
docker compose exec web python manage.py createsuperuser

# 3. 备份数据库
./scripts/docker-db.sh backup
# 生成文件: backups/zishi_server_dev_20240103_120000.sql
```

### 生产环境部署

```bash
# 1. 确保生产环境配置正确
# 编辑 configurations/.env.production
# - 修改 SECRET_KEY
# - 设置 DEBUG=False
# - 配置 ALLOWED_HOSTS
# - 修改数据库密码

# 2. 启动服务并选择生产环境
./scripts/docker-start.sh
# 选择: 2 (production)

# 3. 创建超级用户
cd configurations/
docker compose exec web python manage.py createsuperuser

# 4. 定期备份数据库
./scripts/docker-db.sh backup
# 生成文件: backups/zishi_server_prod_20240103_120000.sql
```

## 注意事项

1. 首次启动会自动创建数据库和运行迁移
2. MySQL 数据存储在 Docker volume 中，删除容器不会丢失数据
3. 如需完全清理数据，使用 `docker compose down -v`
4. 生产环境部署前务必修改 `.env.production` 中的密钥和密码
5. 不同环境使用不同的数据库名称，避免数据混淆
6. 数据库备份文件名包含数据库名称，便于区分环境
