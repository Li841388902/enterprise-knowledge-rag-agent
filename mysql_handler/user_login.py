import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'db': 'my_rag_db',
    'charset': 'utf8mb4',    #设置编码
    'cursorclass': DictCursor  #使用字典游标
}
#获取数据库连接
def get_connection()-> pymysql.Connection:
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        raise f"数据库连接失败：{e}"

#执行sql
def execute_sql(sql: str, params: tuple=None)-> list:
    conn = None
    cursor = None
    try:
        conn = get_connection()             #获取数据库连接
        cursor = conn.cursor()              #获取游标
        cursor.execute(sql, params or ())   #执行sql
        return cursor.fetchall()
    except Exception as e:                                              #如果报错，回滚"增”，"改"，"删"操作
        raise e
    finally:
        if cursor:
            cursor.close()                                                 #关闭游标
        if conn:
            conn.close()

def user_login(username: str,password: str)-> list:
    sql="""
    SELECT * FROM user WHERE username=%s AND password=%s
    """
    res = execute_sql(sql, (username, password))
    return res[0] if res else None