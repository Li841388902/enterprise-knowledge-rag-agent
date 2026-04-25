
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymilvus import MilvusClient, DataType
from utils.path_tool import get_abs_path
from utils.config_loader import rag_config
from langchain_community.embeddings import DashScopeEmbeddings
from file_handler import chunk_md5, save_md5, get_md5, file_check, file_load, docs_wash
from utils.logger_handler import logger_kn
from fastapi import FastAPI
from fastapi import File, UploadFile
from mysql_handler.user_login import user_login
from pydantic import BaseModel
from mysql_handler.user_stored_file import file_add, file_id_delete, file_list, file_get_id, file_get_md5
from mysql_handler.user_stored_parent_chunk import parent_chunk_add, parent_chunk_delete


app = FastAPI()

MILVUS_URI = "http://localhost:19530"
MILVUS_COLLECTION = "my_rag"


class VectorStore:
    def __init__(self):
        self.embedding = DashScopeEmbeddings(model=rag_config["embedding_model"])
        self.client = MilvusClient(uri=MILVUS_URI)
        if not self.client.has_collection(MILVUS_COLLECTION):
            schema = self.client.create_schema(auto_id=True, enable_dynamic_field=True)
            # 修正：原生 Milvus 字段是 dtype 不是 datatype
            schema.add_field(field_name="id", dtype=DataType.INT64, is_primary=True)
            schema.add_field(field_name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024)
            schema.add_field(field_name="text", dtype=DataType.VARCHAR, max_length=65535)

            index_params = self.client.prepare_index_params()
            index_params.add_index(
                field_name="vector",
                index_type="IVF_FLAT",
                metric_type="COSINE",
                params={"nlist": 1024}
            )
            self.client.create_collection(
                collection_name=MILVUS_COLLECTION,
                schema=schema,
                index_params=index_params
            )

        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=rag_config["child_chunk_size"],
            chunk_overlap=rag_config["child_chunk_overlap"],
            separators=rag_config["separators"],
            length_function=len
        )
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=rag_config["parent_chunk_size"],
            chunk_overlap=rag_config["parent_chunk_overlap"],
            separators=rag_config["separators"],
            length_function=len
        )

        try:
            self.client.create_index(
                collection_name=MILVUS_COLLECTION,
                field_name="file_id",
                index_type="STL_SORT"
            )
        except Exception:
            pass

    def file_handler(self, file_bytes: bytes, file_name: str) -> dict:
        try:
            file_md5 = get_md5(file_bytes)
            if chunk_md5(file_md5):
                logger_kn.warning(f"{file_name}文件已处理过")
                return {"status": "warning", "msg": f"{file_name}文件已处理过"}
            else:
                file_checking = file_check(file_bytes)
                if not file_checking:
                    logger_kn.error(f"{file_name}文件格式错误")
                    return {"status": "error", "msg": f"{file_name}文件格式错误"}
        except Exception as e:
            logger_kn.error(f"{file_name}文件处理失败{e}")
            return {"status": "error", "msg": f"{file_name}文件处理失败{e}"}

        try:
            docs_loaded = file_load(file_bytes, file_name)
            docs_last = docs_wash(docs_loaded, file_name)
            logger_kn.info(f"{file_name}文件加载文本成功，并以成功清洗")

        except Exception as e:
            logger_kn.error(f"{file_name}文件加载文本失败{e}")
            return {"status": "error", "msg": f"{file_name}文件加载文本失败{e}"}

        file_id = None
        try:
            child_full_documents = []
            file_add(file_name, file_md5)
            file_id = file_get_id(file_name)

            for doc in docs_last:
                doc.metadata["file_id"] = file_id

            parent_docs = self.parent_splitter.split_documents(docs_last)
            for parent_idx, parent_doc in enumerate(parent_docs):
                child_docs = self.child_splitter.split_documents([parent_doc])
                parent_chunk_add(file_id, parent_idx, parent_doc.page_content)
                for child_doc in child_docs:
                    child_doc.metadata["parent_idx"] = parent_idx
                    child_full_documents.append(child_doc)
                    logger_kn.info("切分成功")


            texts = [doc.page_content for doc in child_full_documents]
            metadatas = [doc.metadata for doc in child_full_documents]

            vectors = self.embedding.embed_documents(texts)

            insert_data = []
            for txt, vec, meta in zip(texts, vectors, metadatas):
                insert_data.append({
                    "text": txt,
                    "vector": vec,
                    **meta
                })

            self.client.insert(
                collection_name=MILVUS_COLLECTION,
                data=insert_data
            )

            save_md5(file_md5)
            logger_kn.info(f"{file_name}文件向量化成功,并成功保存md5")
            return {"status": "success", "msg": f"{file_name}上传成功"}
        except Exception as e:
            try:
                file_id_delete(file_id)
                parent_chunk_delete(file_id)
            except:
                pass
            logger_kn.error(f"{file_name}文件向量化失败{e}")
            return {"status": "error", "msg": f"{file_name}文件向量化失败{e}"}

    def file_delete(self, file_id: int) -> dict:
        try:
            self.client.delete(
                collection_name=MILVUS_COLLECTION,
                filter=f"file_id == {file_id}"
            )
            file_md5 = file_get_md5(file_id)
            md5_list = []
            with open(get_abs_path(rag_config["md5_text_path"]), "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip() != file_md5:
                        md5_list.append(line)
            with open(get_abs_path(rag_config["md5_text_path"]), "w", encoding="utf-8") as f:
                f.writelines(md5_list)

            file_id_delete(file_id)
            parent_chunk_delete(file_id)
            logger_kn.info(f"file_id={file_id} 删除成功")

            return {
                "status": "success",
                "msg": "删除成功"
            }

        except Exception as e:
            logger_kn.exception(f"file_id={file_id} 删除失败{e}")
            return {"status": "error", "msg": str(e)}




class LoginFrom(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(form: LoginFrom):
    res = user_login(form.username,form.password)
    if res:
        logger_kn.info(f"用户{res.get('nickname', '')}登录成功")
        return {"status": "ok","msg": "登录成功","data": res}
    else:
        logger_kn.warning(f"用户{form.username}登录失败")
        return {"status": "error","msg": "用户名或密码错误"}

kn = VectorStore()
@app.post("/vector_store")
async def vector_store(files: list[UploadFile] = File(...)):
    result = []
    try:
        for file in files:
            res = kn.file_handler(file_bytes=file.file.read(),file_name=file.filename)
            result.append(res.get("msg"))
    except Exception as e:
        logger_kn.error(f"文件处理失败{e}")
        return {"status": "error","msg": f"文件处理失败{e}"}
    return {"status": "success","count": len(result), "msg":result}
@app.get("/file_list")
async def get_file_list():
    return file_list()

@app.post("/delete/{file_id}")
async def delete(file_id: int):
    res = kn.file_delete(file_id)
    return {"status": res.get("status"),"msg": res.get("msg")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)