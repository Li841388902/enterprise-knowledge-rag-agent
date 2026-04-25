import uvicorn
from langchain.agents import create_agent
from pydantic import BaseModel

from mysql_handler.user_login import user_login
from langchain_openai import ChatOpenAI
from utils.config_loader import agent_config
from tool import rag_search,web_search,get_weather,get_datetime
from middleware import before_agent,before_model,after_agent,after_model,monitor_tool
from utils.load_prompt import agent_prompt
from fastapi import FastAPI
from utils.logger_handler import logger_ag
from fastapi.responses import StreamingResponse
from mysql_handler.user_chat_history import insert_chat_history
from redis_handler.user_cache_history import get_chat_history,save_chat_history
from redis_handler.user_often_query import save_often_query
import os

app = FastAPI()

class Agent:
    def __init__(self):
        self.model = ChatOpenAI(
            model=agent_config["agent_model"],
            api_key=os.getenv("QWEN_API_KEY"),
            base_url=agent_config["agent_url"],
            streaming=True
        )
        self.agent = create_agent(
            model=self.model,
            system_prompt=agent_prompt,
            tools=[
                rag_search,
                web_search,
                get_weather,
                get_datetime
            ],
            middleware=[before_model,before_agent,after_agent,after_model,monitor_tool]
        )

    def get_user_nickname(self, username: str, password: str) -> str:
        return user_login(username, password).get("nickname", "")

    def execute_stream(self, user_query: str, username: str, password: str):
        user_nickname = agent.get_user_nickname(username, password)

        messages = []
        for text in get_chat_history(user_nickname):
            messages.extend(text)
        user_query_text = {"role": "user", "content": user_query}
        input_dict = {
            "messages": messages + [user_query_text]
        }
        logger_ag.info(f"历史记录为：{input_dict}")
        agent_answer_text = ""
        for chunk in self.agent.stream(input_dict, stream_mode="values"):
            last_messages = chunk["messages"][-1]
            if last_messages.type == "ai" and last_messages.content:
                yield last_messages.content
                agent_answer_text += last_messages.content
        if save_often_query(user_query, agent_answer_text):
            logger_ag.info(f"用户{user_nickname}问题和答案存储redis成功。")
        if save_chat_history(user_nickname, user_query, agent_answer_text):
            logger_ag.info(f"用户{user_nickname}聊天记录存储redis成功。")
        if insert_chat_history(user_nickname, user_query, agent_answer_text):
            logger_ag.info(f"用户{user_nickname}聊天记录存储mysql成功。")




agent = Agent()
class LoginFrom(BaseModel):
    username: str
    password: str

class QueryFrom(BaseModel):
    query: str
    username: str
    password: str
@app.post("/login")
async def login(form: LoginFrom):
    res = user_login(form.username,form.password)
    if res:
        logger_ag.info(f"用户{res.get('nickname', '')}登录成功")
        return {"status": "ok","msg": "登录成功","data": res.get("nickname", '')}
    else:
        logger_ag.warning(f"用户{form.username}登录失败")
        return {"status": "error","msg": "用户名或密码错误"}

@app.post("/agent/chat")
async def agent_chat(input_str: QueryFrom):
    return StreamingResponse(
        agent.execute_stream(input_str.query, input_str.username, input_str.password),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)








