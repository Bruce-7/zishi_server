# 环境配置文件说明

## 配置文件结构

```
configurations/
├── .env                  # Django 实际读取的配置文件（运行时使用）
├── .env.local            # 本地开发环境配置模板
├── .env.development      # 开发环境配置模板（Docker）
├── .env.production       # 生产环境配置模板
└── .env.example          # 配置示例模板
```

## 三套环境说明

### 1. **local（本地开发环境）**

**配置文件：** `.env.local`

**特点：**
- 使用本地 MySQL 数据库
- `DB_HOST=localhost`
- `DEBUG=True`
- 适合本地开发调试

**使用场景：**
- 在 macOS/Windows 本地开发
- 不使用 Docker
- 直接运行 `python manage.py runserver`

**启动方式：**
```bash
# 复制配置文件
cp configurations/.env.local configurations/.env

# 运行开发服务器
python manage.py runserver
```

---

### 2. **development（开发环境）**

**配置文件：** `.env.development`

**特点：**
- 使用 Docker MySQL 容器
- `DB_HOST=mysql`（Docker 服务名）
- `DEBUG=True`
- 适合 Docker 开发环境

**使用场景：**
- 使用 Docker Compose 开发
- 团队协作开发
- 模拟生产环境

**启动方式：**
```bash
# 使用脚本启动（选择 2）
./scripts/docker-start.sh
# 或手动复制
cp configurations/.env.development configurations/.env
docker-compose up -d
```

---

### 3. **production（生产环境）**

**配置文件：** `.env.production`

**特点：**
- 使用 Docker MySQL 容器
- `DB_HOST=mysql`
- `DEBUG=False`
- `CORS_ALLOW_ALL_ORIGINS=False`
- 严格的安全配置

**使用场景：**
- 服务器生产部署
- 正式环境运行

**启动方式：**
```bash
# 使用脚本启动（选择 3）
./scripts/docker-start.sh
# 或手动复制
cp configurations/.env.production configurations/.env
docker-compose up -d
```

---

## 配置对比表

| 配置项 | local | development | production |
|--------|-------|-------------|------------|
| **环境标识** | `DJANGO_ENV=local` | `DJANGO_ENV=development` | `DJANGO_ENV=production` |
| **调试模式** | `DEBUG=True` | `DEBUG=True` | `DEBUG=False` |
| **数据库主机** | `localhost` | `mysql` (Docker) | `mysql` (Docker) |
| **数据库名** | `zishi_server_dev` | `zishi_server_dev` | `zishi_server_prod` |
| **数据库密码** | `root` | `root` | `强密码` |
| **CORS** | 允许所有 | 允许所有 | 仅允许指定域名 |
| **允许主机** | `localhost,127.0.0.1` | `localhost,127.0.0.1` | 实际域名 |

---

## 部署流程

### 方式一：使用脚本（推荐）

```bash
./scripts/docker-start.sh
```

脚本会提示选择环境：
```
请选择部署环境:
  1) local (本地开发环境 - 本地 MySQL)
  2) development (开发环境 - Docker MySQL)
  3) production (生产环境 - Docker MySQL)
```

脚本会自动：
1. 复制对应的 `.env.xxx` 到 `configurations/.env`
2. 启动 Docker 容器
3. 执行数据库迁移

### 方式二：手动部署

```bash
# 1. 复制配置文件
cp configurations/.env.local configurations/.env        # 本地开发
cp configurations/.env.development configurations/.env  # 开发环境
cp configurations/.env.production configurations/.env   # 生产环境

# 2. 启动服务
# 本地开发
python manage.py runserver

# Docker 环境
cd configurations
docker-compose up -d
```

---

## Django 配置读取

Django 只读取 `configurations/.env` 文件：

```python
# django_server/settings.py
env = environ.Env()
environ.Env.read_env(BASE_DIR / 'configurations' / '.env')
```

**重要：** 其他 `.env.xxx` 文件只是模板，必须复制到 `.env` 才会生效。

---

## Git 版本控制

```gitignore
# .gitignore
configurations/.env        # ✅ 忽略（包含敏感信息）
configurations/.env.local  # ✅ 忽略（个人配置）

# ✅ 提交到 Git
configurations/.env.example
configurations/.env.development
configurations/.env.production
```

**注意：** 生产环境配置文件中的敏感信息（如密码）应使用占位符。

---

## 快速切换环境

```bash
# 切换到本地开发
cp configurations/.env.local configurations/.env

# 切换到 Docker 开发
cp configurations/.env.development configurations/.env

# 切换到生产环境
cp configurations/.env.production configurations/.env

# 重启服务使配置生效
```

---

## 常见问题

### Q: 为什么修改 `.env.local` 没有生效？
**A:** Django 只读取 `configurations/.env`，需要复制后才生效。

### Q: 如何知道当前使用的是哪个环境？
**A:** 查看 `configurations/.env` 文件中的 `DJANGO_ENV` 值。

### Q: 本地开发连接不上 MySQL？
**A:** 
- 检查 MySQL 服务是否启动
- 确认使用 `.env.local` 配置（`DB_HOST=localhost`）
- 检查数据库密码是否正确

### Q: Docker 环境连接不上数据库？
**A:**
- 确认使用 `.env.development` 或 `.env.production`
- 确认 `DB_HOST=mysql`（Docker 服务名）
- 等待 MySQL 容器完全启动（约 30 秒）

---

## 最佳实践

1. **本地开发** → 使用 `.env.local`
2. **团队协作** → 使用 `.env.development`
3. **生产部署** → 使用 `.env.production`
4. **切换环境** → 使用 `./scripts/docker-start.sh` 脚本
5. **敏感信息** → 不要提交到 Git
6. **配置修改** → 修改模板文件后重新复制到 `.env`
