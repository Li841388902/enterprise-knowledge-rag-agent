from langchain_community.llms.tongyi import Tongyi
from utils.config_loader import rag_config
from langchain_core.prompts import PromptTemplate
import os


class Rag:
    def __init__(self):
        self.llm = Tongyi(
            model=rag_config["rag_model"],
            api_key=os.getenv("QWEN_API_KEY")
        )
        self.prompt = PromptTemplate.from_template(
            """
            首先，你要自主的去总结参考资料，并且找到与用户问题接近的内容，严格按照参考资料的内容去回答用户问题。
            如果没有参考资料或者没有在参考资料中找到合适的内容，回复用户“抱歉，在知识库中没有找到对应的资料。”，不做任何其他的回复。
            严格遵守上述内容。
            这是参考资料：{content}
            这是用户问题：{input}
            """
        )

    def rag_chain(self, query: str, content: str) -> str:
        chain = self.prompt | self.llm
        return chain.invoke({
            "input": query,
            "content": content
        })


if __name__ == "__main__":
    rag = Rag()
    answer = rag.rag_chain("有关自动喷漆系统设计的设计思路是什么", "")
    print(answer)