import json

import pymysql
from pymysql.cursors import DictCursor
import redis
from utils.config_loader import agent_config

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'db': 'my_rag_db',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

# 获取连接
def get_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        raise Exception(f"数据库连接失败：{e}")  # 这里修复了


# 执行 SQL（通用，支持增删改查）
def execute_sql(sql: str, params: tuple = None) -> list:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params or ())

        # 增删改需要提交
        if sql.strip().upper().startswith(('INSERT', 'DELETE', 'UPDATE')):
            conn.commit()

        # 查询返回全部
        return cursor.fetchall()

    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def insert_chat_history(nickname: str, query: str, agent_answer: str) -> True:
    sql = """
    INSERT INTO user_chat_history (nickname, query, agent_answer)
    VALUES (%s, %s, %s)
    """
    execute_sql(sql, (nickname, query, agent_answer))
    return True





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

