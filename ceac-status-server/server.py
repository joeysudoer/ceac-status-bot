#!/usr/bin/env python3
"""
简单的状态管理 API Server
提供两个接口：
- GET /status - 获取上一次的状态
- POST /status - 更新最新的状态
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 数据存储文件路径
DATA_DIR = Path(__file__).parent / "data"
STATUS_FILE = DATA_DIR / "status_data.json"


def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(exist_ok=True)


def load_status_data():
    """加载状态数据"""
    ensure_data_dir()
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.debug(f"成功加载状态数据")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            return None
    logger.info("状态数据文件不存在，返回空数据")
    return None


def save_status_data(data):
    """保存状态数据"""
    ensure_data_dir()
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"成功保存状态数据")


@app.route("/status", methods=["GET"])
def get_status():
    """
    获取上一次的状态
    返回格式：
    {
        "success": true,
        "data": {
            "status": "...",
            "case_last_updated": "...",
            "date": "..."
        }
    }
    如果没有历史记录，返回 null
    """
    try:
        logger.info("收到 GET /status 请求")
        data = load_status_data()
        
        if not data:
            logger.info("没有找到状态记录")
            return jsonify({
                "success": True,
                "data": None,
                "message": "No status record found"
            })
        
        logger.info(f"返回最新状态: {data['status']} (更新于 {data.get('case_last_updated', 'N/A')})")
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        logger.error(f"GET /status 处理失败: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/status", methods=["POST"])
def update_status():
    """
    更新最新的状态
    请求体格式：
    {
        "status": "...",
        "case_last_updated": "..."
    }
    """
    try:
        logger.info("收到 POST /status 请求")
        req_data = request.get_json()
        
        if not req_data:
            logger.warning("请求体为空")
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        status = req_data.get("status")
        case_last_updated = req_data.get("case_last_updated")
        
        if not status:
            logger.warning("缺少必需字段: status")
            return jsonify({
                "success": False,
                "error": "status field is required"
            }), 400
        
        logger.info(f"准备更新状态: {status}, case_last_updated: {case_last_updated}")
        
        # 创建新的状态记录（覆盖旧数据）
        new_record = {
            "status": status,
            "case_last_updated": case_last_updated or "",
            "date": datetime.now().isoformat()
        }
        
        # 保存数据
        save_status_data(new_record)
        
        logger.info(f"状态更新成功: {status} (记录时间: {new_record['date']})")
        
        return jsonify({
            "success": True,
            "data": new_record,
            "message": "Status updated successfully"
        })
    except Exception as e:
        logger.error(f"POST /status 处理失败: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/health", methods=["GET"])
def health():
    """健康检查接口"""
    logger.debug("收到 GET /health 请求")
    return jsonify({
        "success": True,
        "message": "Server is running"
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 19010))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info("=" * 60)
    logger.info("CEAC Status API Server 启动中...")
    logger.info(f"监听地址: {host}:{port}")
    logger.info(f"数据目录: {DATA_DIR}")
    logger.info(f"Python 版本: {sys.version}")
    logger.info("=" * 60)
    
    # 确保数据目录存在
    ensure_data_dir()
    logger.info(f"数据目录已就绪: {DATA_DIR}")
    
    # 加载现有数据并显示统计
    data = load_status_data()
    if data:
        logger.info(f"最新状态: {data['status']} (记录于 {data.get('date', 'N/A')})")
    else:
        logger.info("当前没有状态记录")
    
    logger.info("服务器启动成功，等待请求...")
    
    try:
        app.run(host=host, port=port, debug=False)
    except Exception as e:
        logger.error(f"服务器运行出错: {e}", exc_info=True)
        sys.exit(1)

