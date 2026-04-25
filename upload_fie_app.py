import time

import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8001"


if "login_user" not in st.session_state:
    st.session_state.login_user = None

# ====================== 主界面逻辑 ======================
if not st.session_state.login_user:
    # -------------------- 登录页面 --------------------
    st.title("🔐 用户登录")
    st.divider()

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
                f"{API_BASE}/login",
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
                st.error(f"连接后端失败,{resp.status_code}")
        except Exception as e:
            st.error(f"连接后端失败：{str(e)}")

    st.stop()

st.title("📚 企业知识库 - 文件上传")
st.divider()

user = st.session_state.login_user
st.success(f"当前登录：{user.get('nickname', '')} ｜ 角色：{user.get('role', '')}")

uploaded_files = st.file_uploader(
    "选择文件（可多选）",
    type=["txt", "pdf", "docx", "csv", "xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🚀 上传"):
        files_tuple = []
        for f in uploaded_files:
            files_tuple.append(
                ("files", (f.name, f.getvalue()))
            )

        with st.spinner("正在上传..."):
            try:
                resp = requests.post(f"{API_BASE}/vector_store", files=files_tuple)

                if resp.status_code == 200:
                    result = resp.json()
                    st.success(f"共上传{result.get('count')} 个文件")
                    for msg in result.get("msg"):
                        st.success(msg)
                else:
                    st.error(f"❌ 接口异常 {resp.status_code}")
                    st.text(resp.text)

            except Exception as e:
                st.error("无法连接后端服务，请确认 knowledge_base.py 已启动")
                st.exception(e)

st.divider()
st.header("📦 文件列表")
try:
    resp = requests.get(f"{API_BASE}/file_list", timeout=8)
    if resp.status_code == 200:
        data = resp.json()
        st.dataframe(data, use_container_width=True)

    else:
        st.error("获取用户列表失败")
        st.success(resp.status_code)
except Exception as e:
    st.error(f"请求异常：{str(e)}")

st.header("🗑️ 删除文件")
file_id = st.number_input("请输入 file_id", value=0, step=1)
if st.button("删除"):
    try:
        resp = requests.post(
            f"{API_BASE}/delete/{file_id}",
            timeout=8
        )
        if resp.status_code == 200:
            res = resp.json()
            st.success(res["msg"])
            with st.spinner("正在重新获取用户列表..."):
                time.sleep(2)
                st.rerun()
        else:
            st.error(f"删除失败：{resp.status_code}")

    except Exception as e:
        st.error(f"请求异常：{str(e)}")


