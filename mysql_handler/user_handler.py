import pymysql
from pymysql.cursors import DictCursor  #导入字典游标，返回为字典，不是元组

#配置mysql数据库的链接配置
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
def get_connection():
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

        if sql.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')): #判断是否是增删改
            conn.commit()                                                  #提交"增”，"改"，"删"操作
        return cursor.fetchall()                                           #查询则返回结果
    except Exception as e:
        if conn:
            conn.rollback()                                                #如果报错，回滚"增”，"改"，"删"操作
        raise e
    finally:
        if cursor:
            cursor.close()                                                 #关闭游标
        if conn:
            conn.close()                                                   #关闭数据库连接

#增加用户
def user_add(username: str, password: str,nickname: str=None,role: str='user')-> list:
    sql = """
    INSERT INTO user(username,password,nickname,role)
    VALUES (%s,%s,%s,%s)
    """
    return execute_sql(sql, (username, password, nickname, role))
#删除用户
def user_delete(username: str)-> list:
    sql = """
    DELETE FROM user WHERE username=%s
    """
    return execute_sql(sql, (username,))
#修改用户
def user_update(username: str,nickname: str=None,role: str='user')-> list:
    sql = """
    UPDATE user SET nickname=%s,role=%s WHERE username=%s
    """
    return execute_sql(sql, (nickname,role,username))
#查询用户
def user_list()-> list:
    sql = """
    SELECT * FROM user 
    """
    return execute_sql(sql)
#登录
def user_login(username: str,password: str)-> list:
    sql="""
    SELECT * FROM user WHERE username=%s AND password=%s
    """
    res = execute_sql(sql, (username, password))
    return res[0] if res else None




if __name__ == '__main__':
    # res = user_add("000002", "123456", "黑总", "admin")
    # print(res)
    res = user_update('000001', '李总', 'admin')
    print(res)
    print(user_list())



