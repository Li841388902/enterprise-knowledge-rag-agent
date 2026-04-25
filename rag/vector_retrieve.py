import os
from langchain_community.embeddings import DashScopeEmbeddings
from utils.logger_handler import logger_kn
from langchain_core.documents import Document
import jieba
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.tongyi import Tongyi
from utils.config_loader import rag_config
import dashscope
from mysql_handler.user_stored_parent_chunk import parent_chunk_select
from pymilvus import MilvusClient
from langchain_community.retrievers import BM25Retriever

# Milvus 配置
MILVUS_URI = "http://localhost:19530"
MILVUS_COLLECTION = "my_rag"


class VectorRetrieve:
    def __init__(self):
        self.embedding = DashScopeEmbeddings(model=rag_config["embedding_model"])
        self.client = MilvusClient(uri=MILVUS_URI)

        # 初始化时加载全部文档，用于 BM25 检索
        self.all_docs = self._load_all_docs()

        self.key_prompt = PromptTemplate.from_template(
            "请根据用户的输入提取3到5个关键词，不需要其他内容，只能空格分隔，不要解释。用户输入：{input}"
        )
        self.rewrite_prompt = PromptTemplate.from_template(
            "请将用户输入改写成3个相近的问题，用换行分隔，无多余内容。用户输入：{input}"
        )
        self.key_and_rewrite_llm = Tongyi(
            model=rag_config["key_and_rewrite_llm"],
            api_key=os.getenv("QWEN_API_KEY")
        )

    def _load_all_docs(self)-> list:
        """从 Milvus 加载所有子文档，给 BM25 使用，只加载一次"""
        try:
            res = self.client.query(
                collection_name=MILVUS_COLLECTION,
                filter="",
                output_fields=["text", "file_id", "parent_idx"],
                limit=10000
            )
            docs = []
            for item in res:
                docs.append(Document(
                    page_content=item["text"],
                    metadata={
                        "file_id": item.get("file_id"),
                        "parent_idx": item.get("parent_idx")
                    }
                ))
            return docs
        except Exception as e:
            logger_kn.error(f"加载全量文档失败: {e}")
            return []

    def rewrite(self, query: str)-> list:
        try:
            rewrite_query_list = []
            chain = self.rewrite_prompt | self.key_and_rewrite_llm
            rewrite_query = chain.invoke({"input": query}).strip().split("\n")
            for query_text in rewrite_query:
                rewrite_query_list.append(query_text.strip())
            return rewrite_query_list
        except Exception as e:
            logger_kn.warning(f"查询改写失败，使用原句：{e}")
            return [query]

    def key_extract(self, query_list: list) -> list:
        key_list = []
        for query in query_list:
            chain = self.key_prompt | self.key_and_rewrite_llm
            keywords = [chain.invoke({"input": query}).strip().split()]
            key_list.extend(keywords)
        return key_list



    def vector_retriever(self, query_list: list) -> list:
        try:
            docs_list = []
            if isinstance(query_list, str):
                query_list = [query_list]
            for query in query_list:
                query_vector = self.embedding.embed_query(query)

                res = self.client.search(
                    collection_name=MILVUS_COLLECTION,
                    data=[query_vector],
                    anns_field="vector",
                    limit=rag_config["similarity_search_k"],
                    output_fields=["text", "file_id", "parent_idx"]
                )

                for hit in res[0]:
                    doc = Document(
                        page_content=hit["entity"]["text"],
                        metadata={
                            "file_id": hit["entity"].get("file_id"),
                            "parent_idx": hit["entity"].get("parent_idx")
                        }
                    )
                    docs_list.append(doc)

            logger_kn.info(f"向量检索出 {len(docs_list)} 条结果")
            return docs_list
        except Exception as e:
            logger_kn.error(f"向量检索失败 {e}")
            raise Exception(f"检索失败{e}")

    #关键词检索
    def key_retriever(self, key_list: list) -> list:
        try:
            docs_list = []
            if not self.all_docs:
                return []
            bm25 = BM25Retriever.from_documents(
                self.all_docs,
                preprocess_func=jieba.lcut
            )
            for key in key_list:
                key = " ".join(key)

                bm25.k = rag_config["similarity_search_k"]
                docs = bm25.invoke(key)
                docs_list.extend(docs)

            logger_kn.info(f"BM25 关键词检索出 {len(docs_list)} 条结果")
            return docs_list

        except Exception as e:
            logger_kn.warning(f"BM25 关键词检索失败：{e}", exc_info=True)
            return []



    #重排融合
    def ranked_store(self, query: str, docs_list: list) -> list:
        try:
            distinct_docs_list = []
            seen = set()

            for doc in docs_list:
                if doc.page_content not in seen:
                    seen.add(doc.page_content)
                    distinct_docs_list.append(doc)

            docs_documents = [d.page_content for d in distinct_docs_list]
            if not docs_documents:
                return []

            reranked = dashscope.TextReRank.call(
                model=rag_config["rerank_model"],
                query=query,
                documents=docs_documents,
                top_n=rag_config["rerank_search_k"],
            )

            final_docs = [distinct_docs_list[res.index] for res in reranked.output.results]
            logger_kn.info(f"重排后剩余：{len(final_docs)} 条")
            return final_docs

        except Exception as e:
            logger_kn.warning(f"重排失败：{e}")
            return []

    #MySQL 父文档召回
    def get_parent_chunks(self, child_chunks: list) -> str:
        exist = set()
        full_text = ""
        for chunk in child_chunks:
            file_id = chunk.metadata.get("file_id")
            parent_idx = chunk.metadata.get("parent_idx")

            if file_id is None or parent_idx is None:
                continue

            key = (file_id, parent_idx)
            if key in exist:
                continue
            exist.add(key)

            parent_text = parent_chunk_select(file_id, parent_idx)
            if parent_text:
                full_text += parent_text+"\n\n"
        logger_kn.info(f"父文档数量：{len(exist)}")
        return full_text


