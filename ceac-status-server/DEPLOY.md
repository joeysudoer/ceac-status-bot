# Debian 服务器部署指南

本指南介绍如何在 Debian 服务器上使用 uv 和 supervisor 部署 CEAC Status API Server。

## 前置要求

- Debian 服务器（已测试：Debian 11/12）
- root 权限
- Python 3.10+
- uv 包管理器
- supervisor

## 部署步骤

### 1. 安装依赖

```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Python 和 pip
apt install -y python3 python3-pip

# 安装 supervisor
apt install -y supervisor

# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载环境变量
source ~/.bashrc
# 或
source ~/.profile
```

### 2. 创建目录结构

```bash
# 创建应用目录
mkdir -p /root/ceac-status-server

# 创建日志目录
mkdir -p /root/logs/supervisor

# 创建数据目录
mkdir -p /root/ceac-status-server/data
```

### 3. 部署应用文件

将以下文件上传到 `/root/ceac-status-server/`：

- `server.py`
- `pyproject.toml`
- `.gitignore`
- `README.md`

```bash
# 示例：使用 scp 上传
scp -r ceac-status-server/* root@your-server:/root/ceac-status-server/

# 或使用 git clone
cd /root
git clone https://github.com/your-username/ceac-status-bot.git
cp -r ceac-status-bot/ceac-status-server/* /root/ceac-status-server/
```

### 4. 初始化 uv 项目

```bash
cd /root/ceac-status-server

# 使用 uv 同步依赖
uv sync
```

### 5. 配置 Supervisor

```bash
# 复制配置文件到 supervisor 配置目录
cp ceac-status-server.conf /etc/supervisor/conf.d/

# 或者手动创建配置文件
cat > /etc/supervisor/conf.d/ceac-status-server.conf << 'EOF'
[program:ceac-status-server]
command=/root/.local/bin/uv run python server.py
directory=/root/ceac-status-server
autostart=true
autorestart=true
startsecs=10
startretries=3
user=root
redirect_stderr=true
stdout_logfile=/root/logs/supervisor/ceac-status-server.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
stderr_logfile=/root/logs/supervisor/ceac-status-server.error.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=10
environment=HOST="0.0.0.0",PORT="5000"
stopasgroup=true
killasgroup=true
EOF
```

### 6. 重新加载 Supervisor 配置

```bash
# 重新读取配置
supervisorctl reread

# 更新配置
supervisorctl update

# 启动服务
supervisorctl start ceac-status-server

# 查看状态
supervisorctl status ceac-status-server
```

### 7. 验证部署

```bash
# 检查服务状态
supervisorctl status ceac-status-server

# 应该看到类似输出：
# ceac-status-server               RUNNING   pid 12345, uptime 0:00:10

# 测试 API
curl http://localhost:5000/health

# 应该返回：
# {"success":true,"message":"Server is running"}

# 查看日志
tail -f /root/logs/supervisor/ceac-status-server.log
```

## Supervisor 常用命令

```bash
# 查看所有服务状态
supervisorctl status

# 启动服务
supervisorctl start ceac-status-server

# 停止服务
supervisorctl stop ceac-status-server

# 重启服务
supervisorctl restart ceac-status-server

# 查看实时日志
supervisorctl tail -f ceac-status-server

# 重新加载配置
supervisorctl reread
supervisorctl update
```

## 日志管理

### 日志文件位置

- 标准输出日志：`/root/logs/supervisor/ceac-status-server.log`
- 错误日志：`/root/logs/supervisor/ceac-status-server.error.log`

### 查看日志

```bash
# 查看最新日志
tail -f /root/logs/supervisor/ceac-status-server.log

# 查看错误日志
tail -f /root/logs/supervisor/ceac-status-server.error.log

# 查看指定行数
tail -n 100 /root/logs/supervisor/ceac-status-server.log

# 搜索日志
grep "ERROR" /root/logs/supervisor/ceac-status-server.log
```

### 日志轮转

Supervisor 自动管理日志轮转：
- 单个日志文件最大 50MB
- 保留最近 10 个备份文件
- 自动压缩旧日志

## 配置说明

### 环境变量

在 `ceac-status-server.conf` 中配置：

```ini
environment=HOST="0.0.0.0",PORT="5000"
```

可用环境变量：
- `HOST`: 监听地址（默认：0.0.0.0）
- `PORT`: 监听端口（默认：5000）

### 修改配置

1. 编辑配置文件：
```bash
vim /etc/supervisor/conf.d/ceac-status-server.conf
```

2. 重新加载配置：
```bash
supervisorctl reread
supervisorctl update
supervisorctl restart ceac-status-server
```

## 数据管理

### 数据文件位置

`/root/ceac-status-server/data/status_data.json`

### 数据备份

```bash
# 手动备份
cp /root/ceac-status-server/data/status_data.json \
   /root/ceac-status-server/data/status_data.json.backup.$(date +%Y%m%d)

# 设置定时备份（crontab）
crontab -e

# 添加以下行（每天凌晨 2 点备份）
0 2 * * * cp /root/ceac-status-server/data/status_data.json /root/ceac-status-server/data/status_data.json.backup.$(date +\%Y\%m\%d)

# 清理 30 天前的备份
0 3 * * * find /root/ceac-status-server/data/ -name "status_data.json.backup.*" -mtime +30 -delete
```

### 数据恢复

```bash
# 停止服务
supervisorctl stop ceac-status-server

# 恢复备份
cp /root/ceac-status-server/data/status_data.json.backup.20241204 \
   /root/ceac-status-server/data/status_data.json

# 启动服务
supervisorctl start ceac-status-server
```

## 更新应用

```bash
# 停止服务
supervisorctl stop ceac-status-server

# 备份当前版本
cp -r /root/ceac-status-server /root/ceac-status-server.backup.$(date +%Y%m%d)

# 更新代码（使用 git）
cd /root/ceac-status-bot
git pull origin main
cp -r ceac-status-server/* /root/ceac-status-server/

# 或使用 scp
# scp server.py root@your-server:/root/ceac-status-server/

# 同步依赖（如果 pyproject.toml 有变化）
cd /root/ceac-status-server
uv sync

# 启动服务
supervisorctl start ceac-status-server

# 检查状态
supervisorctl status ceac-status-server
tail -f /root/logs/supervisor/ceac-status-server.log
```

## 安全配置

### 1. 防火墙配置

如果只允许本地访问：

```bash
# 使用 iptables
iptables -A INPUT -p tcp --dport 5000 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -j DROP

# 或使用 ufw
ufw allow from 127.0.0.1 to any port 5000
ufw deny 5000
```

如果需要外部访问，建议配置 Nginx 反向代理：

```bash
# 安装 Nginx
apt install -y nginx

# 配置反向代理
cat > /etc/nginx/sites-available/ceac-status-server << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 启用站点
ln -s /etc/nginx/sites-available/ceac-status-server /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 2. HTTPS 配置（使用 Let's Encrypt）

```bash
# 安装 certbot
apt install -y certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

## 监控和告警

### 1. 健康检查脚本

```bash
cat > /root/scripts/health-check.sh << 'EOF'
#!/bin/bash

HEALTH_URL="http://localhost:5000/health"
LOG_FILE="/root/logs/health-check.log"

response=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")

if [ "$response" = "200" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ✅ Server is healthy" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ❌ Server is unhealthy (HTTP $response)" >> "$LOG_FILE"
    # 发送告警（可选）
    # supervisorctl restart ceac-status-server
fi
EOF

chmod +x /root/scripts/health-check.sh

# 添加到 crontab（每 5 分钟检查一次）
crontab -e
# */5 * * * * /root/scripts/health-check.sh
```

### 2. 监控服务状态

```bash
# 检查进程
ps aux | grep server.py

# 检查端口
netstat -tuln | grep 5000

# 检查 supervisor 状态
supervisorctl status ceac-status-server
```

## 故障排查

### 服务无法启动

```bash
# 查看详细日志
tail -n 100 /root/logs/supervisor/ceac-status-server.log
tail -n 100 /root/logs/supervisor/ceac-status-server.error.log

# 检查 supervisor 日志
tail -n 100 /var/log/supervisor/supervisord.log

# 手动测试启动
cd /root/ceac-status-server
/root/.local/bin/uv run python server.py
```

### 端口被占用

```bash
# 查找占用端口的进程
lsof -i :5000

# 或
netstat -tuln | grep 5000

# 结束进程
kill -9 <PID>
```

### uv 命令找不到

```bash
# 检查 uv 是否安装
which uv

# 如果找不到，检查路径
ls -la ~/.local/bin/uv

# 在 supervisor 配置中使用完整路径
command=/root/.local/bin/uv run python server.py
```

### 权限问题

```bash
# 确保目录权限正确
chown -R root:root /root/ceac-status-server
chmod -R 755 /root/ceac-status-server
chmod 755 /root/ceac-status-server/data
```

## 性能优化

### 使用 Gunicorn（生产环境推荐）

```bash
# 添加 gunicorn 依赖到 pyproject.toml
# dependencies = [
#     "flask>=3.0.0",
#     "gunicorn>=21.0.0",
# ]

# 同步依赖
cd /root/ceac-status-server
uv sync

# 修改 supervisor 配置
# command=/root/.local/bin/uv run gunicorn -w 4 -b 0.0.0.0:5000 server:app

# 重启服务
supervisorctl restart ceac-status-server
```

## 卸载

```bash
# 停止并删除服务
supervisorctl stop ceac-status-server
rm /etc/supervisor/conf.d/ceac-status-server.conf
supervisorctl reread
supervisorctl update

# 删除应用文件
rm -rf /root/ceac-status-server

# 删除日志（可选）
rm -rf /root/logs/supervisor/ceac-status-server*
```

## 总结

完成以上步骤后，CEAC Status API Server 将：

- ✅ 自动启动（随系统启动）
- ✅ 自动重启（如果崩溃）
- ✅ 日志自动管理（轮转和备份）
- ✅ 使用 uv 管理依赖
- ✅ 监听在 `0.0.0.0:5000`

API 端点：
- `GET http://localhost:5000/health` - 健康检查
- `GET http://localhost:5000/status` - 获取状态
- `POST http://localhost:5000/status` - 更新状态

需要帮助？查看日志：
```bash
tail -f /root/logs/supervisor/ceac-status-server.log
```

