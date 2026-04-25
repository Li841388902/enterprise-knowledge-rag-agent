import hashlib
from utils.config_loader import rag_config
import os
from utils.path_tool import get_abs_path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader,Docx2txtLoader,CSVLoader,TextLoader,UnstructuredFileLoader
import pandas as pd


def chunk_md5(file_md5: str) -> bool:
    if not os.path.exists(get_abs_path(rag_config["md5_text_path"])):
        open(get_abs_path(rag_config["md5_text_path"]), "w").close()
        return False
    with open(get_abs_path(rag_config["md5_text_path"]), "r") as f:
        for line in f:
            if line.strip() == file_md5:
                return True
        return False

def save_md5(file_md5: str) -> None:
    if os.path.exists(get_abs_path(rag_config["md5_text_path"])):
        with open(get_abs_path(rag_config["md5_text_path"]), "a") as f:
            f.write(file_md5+"\n")

def get_md5(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()

def file_check(file_bytes: bytes) -> bool:
    if not file_bytes:
        return False
    try:
        header = file_bytes[:3]
        if header:
            return True
    except:
        return False

def file_load(file_bytes: bytes, file_name: str) -> list[Document]:
    scratch_path = f"./{file_name}"
    try:
        with open(scratch_path, "wb") as f:
            f.write(file_bytes)

        if file_name.endswith("txt"):
            try:
                docs = TextLoader(file_path=scratch_path, encoding="utf-8").load()
            except:
                docs = TextLoader(file_path=scratch_path, encoding="gbk").load()

        elif file_name.endswith("pdf"):
            docs = PyPDFLoader(file_path=scratch_path).load()

        elif file_name.endswith("csv"):
            try:
                docs = CSVLoader(file_path=scratch_path, encoding="utf-8").load()
            except:
                docs = CSVLoader(file_path=scratch_path, encoding="gbk").load()

        elif file_name.endswith("docx"):
            docs = Docx2txtLoader(file_path=scratch_path).load()

        elif file_name.endswith((".xlsx", ".xls")):
            excel_data = pd.read_excel(scratch_path)
            text = excel_data.to_string(index=False)
            docs = [Document(page_content=text,metadata={"source":file_name})]

        else:
            docs = UnstructuredFileLoader(file_path=scratch_path).load()

    finally:
        if os.path.exists(scratch_path):
            os.remove(scratch_path)
    return docs

def docs_wash(docs: list[Document],filename: str) -> list[Document]:
    text = "\n".join([d.page_content for d in docs])
    text = text.strip()
    lines =[line.strip() for line in text.splitlines() if line.strip()]
    text = "\n".join(lines)
    text = " ".join(text.split())
    return [Document(page_content=text,metadata={"source":filename})]





















