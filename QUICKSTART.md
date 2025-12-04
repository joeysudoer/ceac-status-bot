# 快速开始指南

本指南将帮助你快速设置并运行更新后的 CEAC Status Bot。

## 架构说明

新架构包含两个组件：

1. **API Server** (`ceac-status-server/server.py`) - 负责状态存储和管理
2. **Bot 客户端** (`trigger.py`) - 负责查询签证状态并发送通知

## 步骤 1: 安装依赖

### Bot 客户端

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### API Server

```bash
cd ceac-status-server
pip install -r requirements.txt
```

## 步骤 2: 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的信息：

```bash
cp .env.example .env
```

**必需的环境变量：**

```bash
# 签证申请信息
LOCATION=your_location
NUMBER=your_case_number
PASSPORT_NUMBER=your_passport_number
SURNAME=your_surname

# API Server 地址（必需）
STATUS_API_BASE_URL=http://localhost:5000
```

**可选的环境变量：**

```bash
# Email 通知
FROM=your_email@example.com
TO=recipient@example.com
PASSWORD=your_email_password
SMTP=smtp.gmail.com

# Telegram 通知
TG_BOT_TOKEN=your_bot_token
TG_CHAT_ID=your_chat_id

# 其他配置
TIMEZONE=America/New_York
ACTIVE_HOURS=09:00-22:00
```

## 步骤 3: 启动 API Server

### 本地运行

```bash
cd ceac-status-server
python server.py
```

默认监听 `http://0.0.0.0:5000`。

### 使用自定义端口

```bash
PORT=8080 python server.py
```

### 后台运行

```bash
nohup python server.py > server.log 2>&1 &
```

## 步骤 4: 运行 Bot

在另一个终端窗口：

```bash
python trigger.py
```

## 步骤 5: 验证运行

### 检查 API Server

```bash
# 健康检查
curl http://localhost:5000/health

# 查看状态
curl http://localhost:5000/status
```

### 查看 Bot 日志

Bot 会输出日志信息，包括：
- 查询结果
- 状态变化
- 通知发送情况

## 部署到生产环境

### 1. 部署 API Server

推荐使用云平台部署 API Server：

#### Railway

1. 创建新项目
2. 连接 GitHub 仓库
3. 选择 `ceac-status-server` 目录
4. 设置启动命令：`python server.py`
5. 获取部署后的 URL

#### Render

1. 创建新的 Web Service
2. 连接仓库
3. Root Directory: `ceac-status-server`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python server.py`

#### Docker 部署

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY ceac-status-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ceac-status-server/server.py .
CMD ["python", "server.py"]
```

构建并运行：

```bash
docker build -t ceac-status-server .
docker run -p 5000:5000 ceac-status-server
```

### 2. 在 GitHub Actions 中运行 Bot

更新你的 `.github/workflows/check-status.yml`：

```yaml
name: Check CEAC Status

on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时运行一次
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run status check
        env:
          LOCATION: ${{ secrets.LOCATION }}
          NUMBER: ${{ secrets.NUMBER }}
          PASSPORT_NUMBER: ${{ secrets.PASSPORT_NUMBER }}
          SURNAME: ${{ secrets.SURNAME }}
          STATUS_API_BASE_URL: ${{ secrets.STATUS_API_BASE_URL }}
          FROM: ${{ secrets.FROM }}
          TO: ${{ secrets.TO }}
          PASSWORD: ${{ secrets.PASSWORD }}
          SMTP: ${{ secrets.SMTP }}
          TG_BOT_TOKEN: ${{ secrets.TG_BOT_TOKEN }}
          TG_CHAT_ID: ${{ secrets.TG_CHAT_ID }}
          TIMEZONE: ${{ secrets.TIMEZONE }}
          ACTIVE_HOURS: ${{ secrets.ACTIVE_HOURS }}
        run: python trigger.py
```

在 GitHub 仓库的 Settings -> Secrets 中添加所有必需的环境变量。

## 常见问题

### Q: API Server 连接失败怎么办？

确保：
1. API Server 正在运行
2. `STATUS_API_BASE_URL` 配置正确
3. 网络连接正常
4. 防火墙没有阻止连接

### Q: 如何查看 API Server 的数据？

数据存储在 `ceac-status-server/data/status_data.json`，可以直接查看：

```bash
cat ceac-status-server/data/status_data.json
```

### Q: 如何迁移旧的状态数据？

如果你有旧的 `status_record.json`，可以将其内容复制到新的数据文件：

```bash
cp status_record.json ceac-status-server/data/status_data.json
```

### Q: 可以多个 Bot 实例使用同一个 API Server 吗？

可以，API Server 支持多个客户端同时使用。

## 测试

### 手动测试 API

```bash
# 添加一个测试状态
curl -X POST http://localhost:5000/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Administrative Processing",
    "case_last_updated": "2024-01-01"
  }'

# 获取状态
curl http://localhost:5000/status
```

### 测试 Bot

```bash
# 运行 bot
python trigger.py

# 查看日志输出
# 应该能看到查询结果和状态比较信息
```

## 监控和维护

### API Server 日志

如果使用 nohup 后台运行：

```bash
tail -f server.log
```

### 数据备份

定期备份状态数据：

```bash
cp ceac-status-server/data/status_data.json \
   ceac-status-server/data/status_data.json.backup.$(date +%Y%m%d)
```

## 下一步

- 设置监控和告警
- 配置 HTTPS（如果公网部署）
- 添加 API 认证（可选）
- 设置自动备份

## 获取帮助

如果遇到问题：
1. 查看日志输出
2. 检查环境变量配置
3. 验证 API Server 可访问性
4. 查看 GitHub Issues

