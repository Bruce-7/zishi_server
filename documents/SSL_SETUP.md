# SSL 证书目录说明

本目录用于存放不同环境的 SSL 证书文件。

## 目录结构

```
ssl/
├── development/          # 开发环境证书（api.dry-zishi.com）
│   ├── fullchain.pem    # 完整证书链
│   └── privkey.pem      # 私钥
├── production/          # 生产环境证书（dry-zishi.com）
│   ├── fullchain.pem    # 完整证书链
│   └── privkey.pem      # 私钥
└── README.md            # 本说明文件
```

## 腾讯云证书部署

### 1. 下载证书

从腾讯云 SSL 证书管理控制台下载对应域名的证书：
- **开发环境**：下载 `api.dry-zishi.com` 的证书
- **生产环境**：下载 `dry-zishi.com` 的证书

选择 **Nginx** 格式下载，解压后会得到以下文件：
- `域名.key` - 私钥文件 ✅ **需要使用**
- `域名_bundle.crt` 或 `域名_bundle.pem` - 完整证书链 ✅ **需要使用**（两个文件内容相同，任选其一）
- `域名.csr` - 证书签名请求 ❌ **不需要**（申请时用的，部署不需要）

**示例文件名**：
- `api.dry-zishi.com.key`
- `api.dry-zishi.com_bundle.crt`
- `api.dry-zishi.com_bundle.pem`
- `api.dry-zishi.com.csr`

### 2. 上传证书到服务器

#### 开发环境（api.dry-zishi.com）

```bash
# 方式一：使用 scp 上传
scp /path/to/api.dry-zishi.com_bundle.crt root@your-server:/path/to/zishi_server/configurations/ssl/development/fullchain.pem
scp /path/to/api.dry-zishi.com.key root@your-server:/path/to/zishi_server/configurations/ssl/development/privkey.pem

# 方式二：直接在服务器上创建文件并粘贴内容
ssh root@your-server
cd /path/to/zishi_server/configurations/ssl/development
nano fullchain.pem  # 粘贴 api.dry-zishi.com_bundle.crt 或 api.dry-zishi.com_bundle.pem 的内容
nano privkey.pem    # 粘贴 api.dry-zishi.com.key 的内容
chmod 600 privkey.pem  # 设置私钥权限

# 方式三：直接重命名（如果文件已在服务器上）
cp /path/to/api.dry-zishi.com_bundle.crt fullchain.pem
cp /path/to/api.dry-zishi.com.key privkey.pem
chmod 600 privkey.pem
```

#### 生产环境（dry-zishi.com）

```bash
# 方式一：使用 scp 上传
scp /path/to/dry-zishi.com_bundle.crt root@your-server:/path/to/zishi_server/configurations/ssl/production/fullchain.pem
scp /path/to/dry-zishi.com.key root@your-server:/path/to/zishi_server/configurations/ssl/production/privkey.pem

# 方式二：直接在服务器上创建文件并粘贴内容
ssh root@your-server
cd /path/to/zishi_server/configurations/ssl/production
nano fullchain.pem  # 粘贴 dry-zishi.com_bundle.crt 或 dry-zishi.com_bundle.pem 的内容
nano privkey.pem    # 粘贴 dry-zishi.com.key 的内容
chmod 600 privkey.pem  # 设置私钥权限

# 方式三：直接重命名（如果文件已在服务器上）
cp /path/to/dry-zishi.com_bundle.crt fullchain.pem
cp /path/to/dry-zishi.com.key privkey.pem
chmod 600 privkey.pem
```

### 3. 验证证书文件

```bash
# 检查证书文件是否存在
ls -lh configurations/ssl/development/
ls -lh configurations/ssl/production/

# 验证证书有效期
openssl x509 -in configurations/ssl/development/fullchain.pem -noout -dates
openssl x509 -in configurations/ssl/production/fullchain.pem -noout -dates

# 验证证书和私钥是否匹配
openssl x509 -noout -modulus -in configurations/ssl/development/fullchain.pem | openssl md5
openssl rsa -noout -modulus -in configurations/ssl/development/privkey.pem | openssl md5
# 两个 MD5 值应该相同
```

### 4. 重启服务

```bash
cd configurations
docker compose -p zishi_server restart nginx
```

## 证书更新

腾讯云免费证书有效期通常为 1 年，到期前需要重新申请并替换：

1. 在腾讯云重新申请证书
2. 下载新证书
3. 按照上述步骤 2 替换对应环境的证书文件
4. 重启 Nginx 服务

## 注意事项

1. **私钥安全**：`privkey.pem` 文件包含敏感信息，不要提交到 Git 仓库
2. **权限设置**：私钥文件权限应设置为 600（仅所有者可读写）
3. **证书匹配**：确保证书和私钥是配对的，否则 Nginx 无法启动
4. **域名对应**：
   - development 环境使用 `api.dry-zishi.com` 证书
   - production 环境使用 `dry-zishi.com` 证书
5. **文件名固定**：必须命名为 `fullchain.pem` 和 `privkey.pem`，Nginx 配置依赖这些文件名

## 故障排查

### Nginx 启动失败

```bash
# 查看 Nginx 日志
docker compose -p zishi_server logs nginx

# 常见错误：
# - "cannot load certificate": 证书文件不存在或路径错误
# - "key values mismatch": 证书和私钥不匹配
# - "PEM_read_bio": 文件格式错误或内容不完整
```

### 浏览器提示证书错误

1. 检查域名是否正确解析到服务器 IP
2. 确认使用的证书与访问的域名匹配
3. 验证证书未过期
4. 清除浏览器缓存后重试
