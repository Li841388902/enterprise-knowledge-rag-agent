from utils.config_loader import agent_config
from utils.path_tool import get_abs_path
from utils.logger_handler import logger_ag

def load_agent_prompt(path=agent_config["prompt_path"]):
    try:
        return open(get_abs_path(path), "r", encoding="utf-8").read()
    except Exception as e:
        logger_ag.error(f"加载提示文件失败：{e}")
        raise f"加载提示文件失败：{e}"

agent_prompt = load_agent_prompt()
