import redis
import json
from utils.config_loader import agent_config

r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)
MAX_HISTORY = agent_config["MAX_HISTORY"]

def save_chat_history(nickname: str, query: str, agent_answer: str) -> True:
    one_round = [
        {"role": "user", "content": query},
        {"role": "assistant", "content": agent_answer}
    ]
    r.rpush(nickname,json.dumps(one_round))
    r.ltrim(nickname, -MAX_HISTORY, -1)
    return True

def get_chat_history(nickname: str) -> list:
    history = r.lrange(nickname, 0, -1)
    return [json.loads(item) for item in history]