# CEAC Status Server

简单的状态管理 API Server，用于存储和获取美签状态检查结果。

## 功能

提供两个 API 接口：
- `GET /status` - 获取上一次的状态
- `POST /status` - 更新最新的状态
- `GET /health` - 健康检查

## 安装

### 开发环境

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install flask
```

## 运行

### 开发环境

```bash
# 使用 uv
uv run python server.py

# 或直接运行
python server.py
```

默认监听 `0.0.0.0:5000`，可以通过环境变量配置：
- `HOST` - 监听地址（默认：0.0.0.0）
- `PORT` - 监听端口（默认：5000）

### 生产环境（Debian + Supervisor）

详细部署指南请参考 [DEPLOY.md](DEPLOY.md)

快速部署：

```bash
# 1. 上传文件到服务器
scp -r ceac-status-server/* root@your-server:/root/ceac-status-server/

# 2. SSH 登录服务器
ssh root@your-server

# 3. 安装依赖
cd /root/ceac-status-server
uv sync

# 4. 配置 supervisor
cp ceac-status-server.conf /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update
supervisorctl start ceac-status-server

# 5. 查看状态
supervisorctl status ceac-status-server
tail -f /root/logs/supervisor/ceac-status-server.log
```

## API 接口

### 获取状态

```bash
GET /status
```

返回示例：
```json
{
  "success": true,
  "data": {
    "status": "Issued",
    "case_last_updated": "2024-01-01",
    "date": "2024-01-01T12:00:00"
  }
}
```

### 更新状态

```bash
POST /status
Content-Type: application/json

{
  "status": "Issued",
  "case_last_updated": "2024-01-01"
}
```

返回示例：
```json
{
  "success": true,
  "data": {
    "status": "Issued",
    "case_last_updated": "2024-01-01",
    "date": "2024-01-01T12:00:00"
  },
  "message": "Status updated successfully"
}
```

## 数据存储

数据存储在 `data/status_data.json` 文件中。

## 日志

服务运行时会输出详细的日志信息：

- 启动信息（监听地址、数据目录等）
- API 请求日志（GET/POST /status）
- 状态更新日志
- 错误日志（带堆栈跟踪）

开发环境日志输出到控制台，生产环境（supervisor）日志输出到：
- `/root/logs/supervisor/ceac-status-server.log` - 标准输出
- `/root/logs/supervisor/ceac-status-server.error.log` - 错误输出

## 文件说明

- `server.py` - API Server 主程序
- `pyproject.toml` - 项目配置和依赖（uv 管理）
- `ceac-status-server.conf` - Supervisor 配置文件
- `DEPLOY.md` - 详细部署指南
- `README.md` - 本文件
- `.gitignore` - Git 忽略配置

