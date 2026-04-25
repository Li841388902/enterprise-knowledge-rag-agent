import time
import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8002"


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
            with st.spinner("正在登录..."):
                time.sleep(2)
                if resp.status_code == 200:
                    result = resp.json()
                    st.session_state.user_nickname = result.get("data")
                    if result.get("status") == "ok":
                        st.session_state.login_user = result.get("data")
                        if "username" not in st.session_state:
                            st.session_state["username"] = username
                        if "password" not in st.session_state:
                            st.session_state["password"] = password
                        st.rerun()
                    else:
                        st.error("登录失败，请检查账号密码或权限")
                else:
                    st.error(f"连接后端失败,{resp.status_code}")
        except Exception as e:
            st.error(f"连接后端失败：{str(e)}")

    st.stop()

st.title("智扫通机器人智能客服")
user_nickname = st.session_state.login_user
st.subheader("用户：" + user_nickname)
st.divider()

if "message" not in st.session_state:
    st.session_state["message"] = []

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 用户输入提示词
prompt = st.chat_input()

if prompt:
    try:
        st.chat_message("user").write(prompt)
        st.session_state["message"].append({"role": "user", "content": prompt})

        response_messages = []
        with st.spinner("智能客服思考中..."):
            def capture(generator, cache_list):     # 捕获

                for chunk in generator:
                    cache_list.append(chunk)
                    for i in chunk:
                        time.sleep(0.01)
                        yield i
            url = "http://127.0.0.1:8002/agent/chat"
            def api_stream():
                json_data = {
                    "query": prompt,
                    "username": st.session_state["username"],
                    "password": st.session_state["password"]

                }
                with requests.post(url, json=json_data,stream=True) as r:
                    for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
                        if chunk:
                            yield chunk


            st.chat_message("assistant").write_stream(capture(api_stream(), response_messages))
            response_messages = "".join(response_messages)
            st.session_state["message"].append({"role": "assistant", "content": response_messages})
            st.rerun()

    except Exception as e:
        st.error(e)