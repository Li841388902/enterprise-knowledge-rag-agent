from utils.path_tool import get_abs_path
import yaml

def load_rag_config(config_file=get_abs_path("config/rag.yaml")) -> dict:
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        return config
def load_agent_config(config_file=get_abs_path("config/agent.yaml")) -> dict:
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        return config

rag_config = load_rag_config()
agent_config = load_agent_config()