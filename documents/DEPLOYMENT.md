# 服务器部署准备工作

## 一、服务器环境准备

### 1. 系统要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+
- **内存**: 最低 2GB，推荐 4GB+
- **磁盘**: 最低 20GB
- **网络**: 开放 80、443、8000、3306 端口

### 2. 安装必要软件

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | bash -s docker

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version

# 安装 Git
sudo apt install git -y
```

### 3. 配置 Docker 镜像加速（国内服务器必须）

```bash
# 创建 Docker 配置文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF

# 重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证配置
docker info | grep -A 5 "Registry Mirrors"
```

## 二、项目代码准备

### 1. 克隆项目代码

```bash
# 创建项目目录
cd /root  # 或其他目录
git clone <your-git-repository> zishi_server
cd zishi_server
```

### 2. 配置生产环境变量

```bash
# 编辑生产环境配置
vim configurations/.env.production
```

**必须修改的配置项：**

```bash
# 环境类型
DJANGO_ENV=production

# Django 密钥（必须修改为强密钥）
SECRET_KEY=生成一个新的强密钥

# 调试模式（生产环境必须为 False）
DEBUG=False

# 允许访问的主机列表（配置实际域名）
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,服务器IP

# MySQL 数据库配置
DB_ENGINE=django.db.backends.mysql
DB_NAME=zishi_server_prod
DB_USER=root
DB_PASSWORD=修改为强密码
DB_HOST=mysql
DB_PORT=3306

# 数据库连接选项
DB_CONN_MAX_AGE=600

# CORS 配置（配置允许的前端域名）
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com

# JWT Token 有效期
JWT_ACCESS_TOKEN_LIFETIME_DAYS=30
JWT_REFRESH_TOKEN_LIFETIME_DAYS=60
```

### 3. 生成 Django SECRET_KEY

```bash
# 方法一：使用 Python 生成
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 方法二：使用 OpenSSL 生成
openssl rand -base64 50
```

## 三、部署流程

### 1. 启动 Docker 服务

```bash
cd /root/zishi_server

# 给脚本添加执行权限
chmod +x scripts/*.sh

# 启动服务（选择 production 环境）
./scripts/docker-start.sh
# 输入: 2 (选择生产环境)
```

启动过程会自动：
- ✅ 拉取 MySQL 8.0 镜像
- ✅ 构建 Web 应用镜像
- ✅ 创建 MySQL 容器并初始化数据库
- ✅ 等待 MySQL 健康检查通过
- ✅ 启动 Web 容器
- ✅ 自动运行数据库迁移
- ✅ 收集静态文件

### 2. 创建超级管理员

```bash
cd configurations/
docker-compose exec web python manage.py createsuperuser
```

按提示输入：
- 用户名
- 邮箱
- 密码

### 3. 验证部署

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f web
docker-compose logs -f mysql

# 测试访问
curl http://localhost:8000
```

## 四、数据库管理

### 1. 数据库迁移

```bash
# 查看迁移状态
docker-compose exec web python manage.py showmigrations

# 创建新迁移
docker-compose exec web python manage.py makemigrations

# 执行迁移
docker-compose exec web python manage.py migrate

# 回滚迁移（谨慎使用）
docker-compose exec web python manage.py migrate app_name migration_name
```

### 2. 数据库备份

```bash
# 使用管理脚本备份
./scripts/docker-db.sh backup
# 备份文件保存在: backups/zishi_server_prod_YYYYMMDD_HHMMSS.sql

# 手动备份
docker-compose exec -T mysql mysqldump -u root -p'密码' zishi_server_prod > backup.sql
```

### 3. 数据库恢复

```bash
# 使用管理脚本恢复
./scripts/docker-db.sh restore backups/zishi_server_prod_20240103_120000.sql

# 手动恢复
docker-compose exec -T mysql mysql -u root -p'密码' zishi_server_prod < backup.sql
```

### 4. 数据库维护

```bash
# 进入 MySQL 命令行
./scripts/docker-db.sh shell

# 查看数据库状态
./scripts/docker-db.sh status

# 查看 MySQL 日志
./scripts/docker-db.sh logs
```

## 五、Nginx 反向代理配置（可选）

### 1. 安装 Nginx

```bash
sudo apt install nginx -y
```

### 2. 配置 Nginx

```bash
sudo vim /etc/nginx/sites-available/zishi
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /root/zishi_server/static/;
    }

    location /media/ {
        alias /root/zishi_server/media/;
    }
}
```

### 3. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/zishi /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 4. 配置 SSL（推荐）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 自动配置 SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 六、防火墙配置

```bash
# Ubuntu UFW
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 8000/tcp    # Django (如果不用 Nginx)
sudo ufw enable

# CentOS Firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## 七、监控和日志

### 1. 查看实时日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看 Web 服务日志
docker-compose logs -f web

# 查看 MySQL 日志
docker-compose logs -f mysql

# 查看最近 100 行日志
docker-compose logs --tail=100 web
```

### 2. 日志文件位置

- **应用日志**: `/root/zishi_server/logs/`
- **Nginx 日志**: `/var/log/nginx/`
- **Docker 日志**: `docker-compose logs`

### 3. 容器资源监控

```bash
# 查看容器资源使用
docker stats

# 查看容器详情
docker-compose ps
docker inspect zishi_web
docker inspect zishi_mysql
```

## 八、常见运维操作

### 1. 重启服务

```bash
cd /root/zishi_server/configurations

# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart web
docker-compose restart mysql
```

### 2. 更新代码

```bash
cd /root/zishi_server

# 拉取最新代码
git pull origin main

# 重新构建并启动
cd configurations/
docker-compose down
docker-compose build
docker-compose up -d

# 运行迁移
docker-compose exec web python manage.py migrate

# 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput
```

### 3. 清理 Docker 资源

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的卷
docker volume prune

# 清理所有未使用资源
docker system prune -a
```

### 4. 数据库优化

```bash
# 进入 MySQL 容器
docker-compose exec mysql bash

# 优化表
mysql -u root -p
USE zishi_server_prod;
OPTIMIZE TABLE table_name;

# 分析表
ANALYZE TABLE table_name;
```

## 九、安全建议

### 1. 修改默认端口

```yaml
# docker-compose.yml
services:
  web:
    ports:
      - "8001:8000"  # 修改外部端口
```

### 2. 限制数据库访问

```yaml
# docker-compose.yml
services:
  mysql:
    ports:
      - "127.0.0.1:3306:3306"  # 只允许本地访问
```

### 3. 定期备份

```bash
# 添加定时任务
crontab -e

# 每天凌晨 2 点备份数据库
0 2 * * * cd /root/zishi_server && ./scripts/docker-db.sh backup

# 删除 7 天前的备份
0 3 * * * find /root/zishi_server/backups -name "*.sql" -mtime +7 -delete
```

### 4. 更新依赖

```bash
# 定期更新 Python 依赖
docker-compose exec web pip list --outdated

# 更新 Docker 镜像
docker-compose pull
docker-compose up -d
```

## 十、故障排查

### 1. 容器无法启动

```bash
# 查看详细日志
docker-compose logs web
docker-compose logs mysql

# 检查配置文件
cat .env

# 检查端口占用
netstat -tulpn | grep 8000
netstat -tulpn | grep 3306
```

### 2. 数据库连接失败

```bash
# 检查 MySQL 容器状态
docker-compose ps mysql

# 测试数据库连接
docker-compose exec web python manage.py dbshell

# 查看 MySQL 日志
docker-compose logs mysql
```

### 3. 静态文件无法访问

```bash
# 重新收集静态文件
docker-compose exec web python manage.py collectstatic --noinput

# 检查文件权限
ls -la /root/zishi_server/static/
```

## 十一、部署检查清单

- [ ] 服务器环境准备完成
- [ ] Docker 和 Docker Compose 安装完成
- [ ] Docker 镜像加速配置完成
- [ ] 项目代码克隆完成
- [ ] 生产环境配置文件修改完成
- [ ] SECRET_KEY 已修改为强密钥
- [ ] DEBUG 设置为 False
- [ ] ALLOWED_HOSTS 配置正确
- [ ] 数据库密码已修改
- [ ] CORS 配置正确
- [ ] Docker 服务启动成功
- [ ] 数据库迁移执行成功
- [ ] 超级管理员创建完成
- [ ] 静态文件收集完成
- [ ] 服务访问测试通过
- [ ] 防火墙配置完成
- [ ] Nginx 反向代理配置完成（可选）
- [ ] SSL 证书配置完成（可选）
- [ ] 数据库备份策略设置完成
- [ ] 日志监控配置完成

## 十二、快速命令参考

```bash
# 启动服务
./scripts/docker-start.sh

# 停止服务
./scripts/docker-stop.sh

# 查看日志
docker-compose logs -f

# 进入容器
docker-compose exec web bash

# 数据库备份
./scripts/docker-db.sh backup

# 数据库恢复
./scripts/docker-db.sh restore backup.sql

# 运行迁移
docker-compose exec web python manage.py migrate

# 创建超级用户
docker-compose exec web python manage.py createsuperuser

# 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput

# 重启服务
docker-compose restart

# 查看容器状态
docker-compose ps
```
