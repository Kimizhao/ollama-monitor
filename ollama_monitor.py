import requests
import time
import subprocess
import psutil
import logging
import os
from datetime import datetime

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "localhost:11434")
try:
    port = OLLAMA_HOST.split(":")[1]  # 提取端口号
    OLLAMA_API_URL = f"http://localhost:{port}/api/tags"
except IndexError:
    logging.error("OLLAMA_HOST 环境变量格式错误，应为 '主机:端口'")
    port = "11434" #默认端口
    OLLAMA_API_URL = f"http://localhost:{port}/api/tags"

TIMEOUT_SECONDS = 10
RESTART_COMMAND = "ollama ps"

def setup_logging():
    """配置日志记录器，同时输出到文件和控制台。"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = os.path.join(log_dir, f"ollama_monitor_{current_time}.log")

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # 获取根日志记录器并添加处理器
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

def check_ollama_status():
    """检查 Ollama 状态，如果卡住则返回 True，否则返回 False。"""
    try:
        response = requests.get(OLLAMA_API_URL, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Ollama 可能卡住：{e}")
        return True

def restart_ollama():
    """重启 Ollama 服务。"""
    logging.info("重启 Ollama 服务...")
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'ollama.exe':
                p = psutil.Process(proc.info['pid'])
                p.terminate()

        subprocess.Popen(RESTART_COMMAND, shell=True)
        logging.info("Ollama 服务已重启。")
    except Exception as e:
        logging.error(f"重启 Ollama 服务失败：{e}")

if __name__ == "__main__":
    setup_logging()
    while True:
        if check_ollama_status():
            restart_ollama()
        sleep_time = int(os.environ.get("OLLAMA_MONITOR_INTERVAL", 60))
        time.sleep(sleep_time)