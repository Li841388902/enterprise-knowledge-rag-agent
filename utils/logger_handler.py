import logging
import os
from utils.path_tool import get_abs_path
from datetime import datetime
#获取日志存放目录绝对路径
LOG_ROOT_ADMIN = get_abs_path("logs/admin_logs")
LOG_ROOT_KNOWLEDGE_BASE = get_abs_path("logs/knowledge_base_logs")
LOG_ROOT_AGENT = get_abs_path("logs/agent_logs")

os.makedirs(LOG_ROOT_ADMIN, exist_ok=True)
os.makedirs(LOG_ROOT_KNOWLEDGE_BASE, exist_ok=True)
os.makedirs(LOG_ROOT_AGENT, exist_ok=True)
#配置日志格式
DEFAULT_LOG_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

def get_admin_logger(
        name:str = "admin",
        console_level:int = logging.INFO,
        file_level:int = logging.DEBUG,
        log_file = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    #避免日志重复输出
    if logger.handlers:
        return logger
    #控制台日志配置
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)
    #文件日志配置
    if not log_file:
        log_file = os.path.join(LOG_ROOT_ADMIN, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)
    return logger

def get_knowledge_base_logger(
        name:str = "knowledge_base",
        console_level:int = logging.INFO,
        file_level:int = logging.DEBUG,
        log_file = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    #避免日志重复输出
    if logger.handlers:
        return logger
    #控制台日志配置
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)
    #文件日志配置
    if not log_file:
        log_file = os.path.join(LOG_ROOT_KNOWLEDGE_BASE, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)
    return logger

def get_agent_logger(
        name:str = "agent",
        console_level:int = logging.INFO,
        file_level:int = logging.DEBUG,
        log_file = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    #避免日志重复输出
    if logger.handlers:
        return logger
    #控制台日志配置
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)
    #文件日志配置
    if not log_file:
        log_file = os.path.join(LOG_ROOT_AGENT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)
    return logger

logger_ad = get_admin_logger()
logger_kn = get_knowledge_base_logger()
logger_ag = get_agent_logger()

# if __name__ == "__main__":
#     logger_ad.info("admin log")
#     logger_kn.info("knowledge_base log")
#     logger_ag.info("agent log")



