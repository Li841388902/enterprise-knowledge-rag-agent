import redis
import hashlib
from utils.logger_handler import logger_ag

r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

def save_often_query(query: str,answer: str) -> bool:
    try:
        query_md5 = hashlib.md5(query.encode("utf-8")).hexdigest()
        key = "often_query:"+query_md5
        r.setex(key,259200, answer)
        return True
    except Exception as e:
        logger_ag.error(f"保存often_query失败：{e}")
        return False

def get_often_query(query: str)-> str | None:
    try:
        query_md5 = hashlib.md5(query.encode("utf-8")).hexdigest()
        key = "often_query:"+query_md5
        answer = r.get(key)
        return answer
    except:
        logger_ag.error(f"没有找到该often_query")
        return None