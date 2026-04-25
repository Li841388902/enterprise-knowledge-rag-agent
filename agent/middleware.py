from typing import Callable
from langchain.agents.middleware import before_agent, before_model, after_agent, after_model, wrap_tool_call
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger_ag
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from redis_handler.user_often_query import get_often_query


@before_agent
def before_agent(state: AgentState, runtime: Runtime):
    logger_ag.info(f"[Agent] 开始执行任务 | 消息条数：{len(state['messages'])}")


@before_model
def before_model(state: AgentState, runtime: Runtime):
    logger_ag.info(f"[Model] 开始调用 | 消息条数：{len(state['messages'])}")


@after_model
def after_model(state: AgentState, runtime: Runtime):
    logger_ag.info(f"[Model] 调用完成 | 消息条数：{len(state['messages'])}")


@after_agent
def after_agent(state: AgentState, runtime: Runtime):
    logger_ag.info(f"[Agent] 任务执行完成 | 消息条数：{len(state['messages'])}")


@wrap_tool_call
def monitor_tool(
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command]
) -> ToolMessage | Command :
    tool_name = request.tool_call["name"]
    args = request.tool_call["args"]
    try:
        if tool_name == "rag_search":
            answer = get_often_query(args["query"])
            if answer is not None:
                logger_ag.info(f"[Tool] 命中高频用户常用问题，返回结果。")
                return ToolMessage(content=answer, tool_call_id=request.tool_call["id"])
        logger_ag.info(f"[Tool] 开始执行：{tool_name} | 参数：{args}")
        result = handler(request)
        logger_ag.info(f"[Tool] {tool_name} 执行成功")
        return result
    except Exception as e:
        logger_ag.error(f"[Tool] {tool_name} 执行失败：{str(e)}", exc_info=True)
        raise e