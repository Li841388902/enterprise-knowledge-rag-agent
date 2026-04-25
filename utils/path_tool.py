"""
为整个工程提供绝对的路径
"""
import os

def get_project_root()->str:
    """
    通过当前文件的绝对路径，获取当前的工程根目录
    :return:工程根目录字符串
    """
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(current_dir)
    return project_root

def get_abs_path(relative_path:str)->str:
    """
    传入相对路径获取绝对路径
    :param relative_path:相对路径字符串
    :return:绝对路径字符串
    """
    project_root = get_project_root()
    return os.path.join(project_root,relative_path)

if __name__ == "__main__":
    print(get_project_root())
    print(get_abs_path("config/config.py"))