from fastapi import FastAPI
from mysql_handler.user_handler import user_login, user_add, user_delete, user_update, user_list
from pydantic import BaseModel
from utils.logger_handler import logger_ad
import uvicorn
app = FastAPI()

class LoginFrom(BaseModel):
    username: str
    password: str

class AddUserFrom(BaseModel):
    username: str
    password: str
    nickname: str
    role: str

class DeleteUserFrom(BaseModel):
    username: str

class UpdateUserFrom(BaseModel):
    username: str
    nickname: str
    role: str
#创建fastapi后端链接
#登录
@app.post("/api/login")
def api_login(form: LoginFrom)->list|dict:
    try:
        user = user_login(form.username, form.password)
        if not user:
            logger_ad.error(f"{form.username}登录失败，用户名或密码错误")
            return {"status": "error","msg": "用户名或密码错误"}
        else:
            if user.get("role") != "admin":
                logger_ad.error(f"{form.username}登录失败，权限不足")
                return {"status": "error","msg": "权限不足"}
            logger_ad.info(f"{form.username}登录成功")
            return {"status": "ok","msg": "登录成功", "data": user}
    except Exception as e:
        logger_ad.error(f"登录失败{e}")
        return {"status": "error","msg": f"登录失败{e}"}
#查询用户
@app.get("/api/users")
def api_users()->list| dict:
    try:
        users = user_list()
        logger_ad.info("查询用户成功")
        return users
    except Exception as e:
        logger_ad.error(f"查询用户失败{e}")
        return {"status": "error","msg": f"查询用户失败{e}"}
#新增用户
@app.post("/api/user/add")
def api_add_user(form: AddUserFrom)->dict:
    try:
        user = user_add(form.username, form.password, form.nickname, form.role)
        logger_ad.info(f"{form.username}用户添加成功")
        return {"status": "ok","msg": "添加用户成功"}
    except Exception as e:
        logger_ad.error(f"{form.username}用户添加失败，{e}")
        return {"status": "error","msg": f"添加用户失败{e}"}
#删除用户
@app.post("/api/user/delete")
def api_delete_user(form: DeleteUserFrom)->dict:
    try:
        user = user_delete(form.username)
        logger_ad.info(f"{form.username}用户删除成功")
        return {"status": "ok","msg": "删除用户成功"}
    except Exception as e:
        logger_ad.error(f"{form.username}用户删除失败，{e}")
        return {"status": "error","msg": f"删除用户失败{e}"}
#修改用户
@app.post("/api/user/update")
def api_update_user(form: UpdateUserFrom)->dict:
    try:
        user = user_update(form.username, form.nickname, form.role)
        logger_ad.info(f"{form.username}用户修改成功")
        return {"status": "ok","msg": "修改用户成功"}
    except Exception as e:
        logger_ad.error(f"{form.username}用户修改失败，{e}")
        return {"status": "error","msg": f"修改用户失败{e}"}

if __name__ == "__main__":
    res = uvicorn.run(app, host="127.0.0.1", port=8000)
    print(res)





