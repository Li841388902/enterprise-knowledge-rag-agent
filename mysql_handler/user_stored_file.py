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
def execute_sql(sql: str, params: tuple = None)-> list:
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


# ====================
# 你要的 增删查
# ====================

# 1. 新增文件 → 返回刚生成的 file_id
def file_add(filename: str,md5: str) -> None:
    sql = """
    INSERT INTO user_file (filename,md5)
    VALUES (%s,%s)
    """
    execute_sql(sql, (filename,md5))




# 2. 查询所有文件（列表）
def file_list() -> list:
    sql = "SELECT file_id, filename FROM user_file"
    return execute_sql(sql)


# 3. 按 file_id 删除（最安全，不会删错）
def file_id_delete(file_id: int) -> None:
    sql = "DELETE FROM user_file WHERE file_id = %s"
    execute_sql(sql, (file_id,))

# 根据文件名获取最新的 file_id
def file_get_id(filename: str) -> int | None:
    sql = "SELECT file_id FROM user_file WHERE filename = %s ORDER BY file_id DESC LIMIT 1"
    res = execute_sql(sql, (filename,))
    return res[0]["file_id"] if res else None

def file_get_md5(file_id: int) -> str | None:
    sql = "SELECT md5 FROM user_file WHERE file_id = %s LIMIT 1"
    res = execute_sql(sql, (file_id,))
    return res[0]["md5"] if res else None










