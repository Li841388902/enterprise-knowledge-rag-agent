import pymysql
from pymysql.cursors import DictCursor

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


# ====================
# 你要的 增删查
# ====================

# 1. 新增文件 → 返回刚生成的 file_id
def parent_chunk_add(file_id: int,parent_idx: int,parent_content: str) -> None:
    sql = """
    INSERT INTO file_parent_chunks (file_id,parent_idx,parent_content)
    VALUES (%s,%s,%s)
    """
    execute_sql(sql, (file_id,parent_idx,parent_content))


def parent_chunk_delete(file_id: int) -> None:
    sql = "DELETE FROM file_parent_chunks WHERE file_id = %s"
    execute_sql(sql, (file_id,))

def parent_chunk_select(file_id: int,parent_idx: int) -> str:
    sql = "SELECT parent_content FROM file_parent_chunks WHERE file_id = %s AND parent_idx = %s"
    result = execute_sql(sql, (file_id,parent_idx))
    return result[0]["parent_content"] if result else None











