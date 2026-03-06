import logging
import threading
import time
from typing import List

import requests

# 基础日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 保活目标地址（后端 + Streamlit）
TARGET_URLS: List[str] = [
    # Render 后端：命中应用根路径即可触发唤醒
    "https://ai-career-helper-backend-u1s0.onrender.com",
    # Streamlit 应用
    "https://ai-career-apper-resume-doctor-69etycfa4ohbkxdweoawk.streamlit.app",
]

# 间隔与超时配置
INTERVAL = 600  # 10 分钟请求一次（低于 Render 15 分钟休眠阈值）
TIMEOUT = 60  # 适配 Streamlit 冷启动

# 模拟浏览器请求头（绕过部分平台对“爬虫”的限制）
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def ping_url(url: str) -> bool:
    """发送模拟浏览器的请求，唤醒目标服务。"""
    try:
        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True,  # 允许重定向（Streamlit 可能跳转）
        )
        # 即便是 404/403，只要有响应就说明服务已被唤醒
        if resp.status_code in (200, 301, 302, 303, 307, 308, 404, 403):
            logging.info("保活成功 | URL: %s | 状态码: %s", url, resp.status_code)
            return True

        logging.warning("保活响应异常 | URL: %s | 状态码: %s", url, resp.status_code)
        return False
    except requests.exceptions.Timeout:
        # 冷启动阶段可能超时，但已经触发平台唤醒
        logging.warning("保活超时 | URL: %s（可能处于冷启动中）", url)
        return True
    except Exception as exc:  # noqa: BLE001
        logging.error("保活异常 | URL: %s | 错误: %s", url, exc)
        return False


def keep_alive_loop() -> None:
    """循环保活所有目标地址。"""
    logging.info(
        "保活服务启动 | 间隔: %s 秒 | 超时: %s 秒 | 监控地址: %s",
        INTERVAL,
        TIMEOUT,
        TARGET_URLS,
    )
    while True:
        for url in TARGET_URLS:
            ping_url(url)
            # 单次之间稍微间隔一下，避免瞬时并发
            time.sleep(5)
        time.sleep(INTERVAL)


def start_keep_alive() -> None:
    """启动后台保活线程（不阻塞主服务）。"""
    t = threading.Thread(target=keep_alive_loop, daemon=True)
    t.start()
    logging.info("保活线程已启动（后台运行）")


if __name__ == "__main__":
    # 单独运行脚本时启动保活
    start_keep_alive()
    # 保持脚本常驻
    while True:
        time.sleep(3600)

