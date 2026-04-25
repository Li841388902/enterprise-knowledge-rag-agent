from langchain_core.tools import tool
from rag.vector_retrieve import VectorRetrieve
from rag.rag import Rag
from utils.logger_handler import logger_ag
from ai_search_online.search_online import web_search_online
import requests
import os
from datetime import datetime



vec = VectorRetrieve()
rag = Rag()

@tool(description="用于知识库文档检索，输入为用户问题，返回为优化后的知识库内容。")
def rag_search(query: str) -> str:
    docs_list = None
    try:
        rewrite_query = vec.rewrite(query)
        key_extract_query = vec.key_extract(rewrite_query)
        key_docs = vec.key_retriever(key_extract_query)
        vector_docs = vec.vector_retriever(rewrite_query)
        docs_list = vector_docs + key_docs
        logger_ag.info("文档召回成功。")
    except Exception as e:
        logger_ag.warning(f"文档召回失败：{e}")
    try:
        if docs_list == []:
            logger_ag.warning("文档为空")
            return ""
        logger_ag.info(f"文档优化开始")
        rank_docs = vec.ranked_store(query, docs_list)
        parent_chunks = vec.get_parent_chunks(rank_docs)
        sum_up = rag.rag_chain(query, parent_chunks)
        logger_ag.info(f"文档优化成功，返回总结。")
        return sum_up
    except Exception as e:
        logger_ag.warning(f"文档优化失败,无法返回总结：{e}")
        return ""

@tool(description="用于当内部知识库为空或者与问题偏离较大时，进行联网搜索，传入问题，返回结果")
def web_search(query: str) -> str:
    try:
        result = web_search_online(query)
        logger_ag.info(f"网络搜索成功，返回结果。")
        return result
    except Exception as e:
        logger_ag.warning(f"网络搜索失败：{e}")
        return ""

@tool(description="获取指定城市的天气，以消息字符串的形式返回，传入城市名，以及对应的日期，返回城市该日期的天气信息")
def get_weather(city: str, date: str) -> str:
    try:
        key = os.getenv("GAODE_MAP_API_KEY")
        url = "https://restapi.amap.com/v3/weather/weatherInfo?parameters"
        params = {
            "city": city,
            "key": key,
            "extensions": "all",
            "output": "json"
        }
        res = requests.get(url,params=params)
        res = res.json()
        res = res["forecasts"][0]["casts"]
        if res:
            for i in res:
                if i["date"] == date:
                    logger_ag.info(f"请求天气成功，返回结果。")
                    return i
    except Exception as e:
        logger_ag.warning(f"请求失败：{e}")
        return f"请求失败。{e}"

@tool(description="获取当前的日期，不需要传任何参数，返回为年，月，日的字符串")
def get_datetime() -> str:
    logger_ag.info(f"获取当前时间成功，返回结果。")
    return datetime.now().strftime("%Y-%m-%d")







