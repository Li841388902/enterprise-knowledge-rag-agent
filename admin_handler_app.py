import streamlit as st
import requests

# 后端地址
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="RAG 管理员后台",
    layout="wide",
    page_icon="🔐"
)

# ====================== 登录状态保持 ======================
if "login_user" not in st.session_state:
    st.session_state.login_user = None

# ====================== 主界面逻辑 ======================
if not st.session_state.login_user:
    # -------------------- 登录页面 --------------------
    st.title("🔐 管理员登录")

    with st.form("login_form"):
        username = st.text_input("工号 / 用户名")
        password = st.text_input("密码", type="password")
        submit = st.form_submit_button("登录")

    if submit:
        if not username or not password:
            st.warning("请输入用户名和密码")
            st.stop()

        try:
            resp = requests.post(
                f"{API_BASE}/api/login",
                json={
                    "username": username,
                    "password": password
                },
                timeout=8
            )

            if resp.status_code == 200:
                result = resp.json()
                if result.get("status") == "ok":
                    st.session_state.login_user = result.get("data")
                    st.success("登录成功，正在进入管理后台…")
                    st.rerun()
                else:
                    st.error("登录失败，请检查账号密码或权限")
            else:
                st.error("连接后端失败")
        except Exception as e:
            st.error(f"连接后端失败：{str(e)}")

    st.stop()

# ====================== 已登录：后台管理 ======================
user = st.session_state.login_user
st.title(f"🧾 RAG 知识库管理后台")
st.success(f"当前登录：{user.get('nickname', '')} ｜ 角色：{user.get('role', '')}")
st.divider()

# 功能菜单
menu = st.selectbox(
    "请选择操作",
    ["用户列表", "新增用户", "修改用户", "删除用户"]
)


# 用户列表

if menu == "用户列表":
    st.subheader("👥 用户列表")

    try:
        resp = requests.get(f"{API_BASE}/api/users", timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            st.dataframe(data, use_container_width=True)
        else:
            st.error("获取用户列表失败")
    except Exception as e:
        st.error(f"请求异常：{str(e)}")

# ------------------------------------------------------------------------------
# 2. 新增用户
# ------------------------------------------------------------------------------
elif menu == "新增用户":
    st.subheader("➕ 新增用户")

    with st.form("add_user"):
        username = st.text_input("工号/用户名")
        password = st.text_input("密码")
        nickname = st.text_input("昵称")
        role = st.selectbox("角色", ["user", "admin"])
        add_btn = st.form_submit_button("确认添加")

    if add_btn:
        if not all([username, password, nickname]):
            st.warning("请填写完整信息")
            st.stop()

        try:
            resp = requests.post(
                f"{API_BASE}/api/user/add",
                json={
                    "username": username,
                    "password": password,
                    "nickname": nickname,
                    "role": role
                },
                timeout=8
            )
            if resp.status_code == 200:
                st.success("添加成功")
            else:
                st.error(f"添加失败：{resp.text}")
        except Exception as e:
            st.error(f"请求失败：{str(e)}")

# ------------------------------------------------------------------------------
# 3. 修改用户
# ------------------------------------------------------------------------------
elif menu == "修改用户":
    st.subheader("✏️ 修改用户")

    with st.form("update_user"):
        username = st.text_input("要修改的用户名（工号）")
        new_nickname = st.text_input("新昵称")
        new_role = st.selectbox("新角色", ["user", "admin"])
        update_btn = st.form_submit_button("确认修改")

    if update_btn:
        if not username:
            st.warning("请输入要修改的用户名")
            st.stop()

        try:
            resp = requests.post(
                f"{API_BASE}/api/user/update",
                json={
                    "username": username,
                    "nickname": new_nickname,
                    "role": new_role
                },
                timeout=8
            )
            if resp.status_code == 200:
                st.success("修改成功")
            else:
                st.error(f"修改失败：{resp.text}")
        except Exception as e:
            st.error(f"请求失败：{str(e)}")

# ------------------------------------------------------------------------------
# 4. 删除用户
# ------------------------------------------------------------------------------
elif menu == "删除用户":
    st.subheader("🗑️ 删除用户")

    with st.form("delete_user"):
        username = st.text_input("要删除的用户名（工号）")
        delete_btn = st.form_submit_button("确认删除")

    if delete_btn:
        if not username:
            st.warning("请输入要删除的用户名")
            st.stop()

        try:
            resp = requests.post(
                f"{API_BASE}/api/user/delete",
                json={"username": username},
                timeout=8
            )
            if resp.status_code == 200:
                st.success("删除成功")
            else:
                st.error(f"删除失败：{resp.text}")
        except Exception as e:
            st.error(f"请求失败：{str(e)}")