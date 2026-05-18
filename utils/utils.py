# -*- coding = utf-8 -*-
# @Time :2023/7/9 20:53
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :scenic_spots_comment
# @File :  utils.py
import json
import os


def dateToJsonFile(city: list) -> None:
    """
    将答案写入文件保存为json格式
    :param city:
    :return:
    """
    to_dict = {
        "city": city,
    }
    # json.dumps 序列化时对中文默认使用的ascii编码.想输出真正的中文需要指定ensure_ascii=False
    json_data = json.dumps(to_dict, ensure_ascii=False)
    script_path = os.path.abspath(__file__)
    grandparent_dir = os.path.dirname(os.path.dirname(script_path))
    path = os.path.join(grandparent_dir, "city.json")
    with open(path, 'w', encoding="utf-8") as f_:
        f_.write(json_data)


def dateToJsonFileSceneInfo(scene_info: dict, path: str) -> None:
    """
    将答案写入文件保存为json格式
    :param path:
    :param scene_info: 景区信息
    :return:
    """
    # json.dumps 序列化时对中文默认使用的ascii编码.想输出真正的中文需要指定ensure_ascii=False
    json_data = json.dumps(scene_info, ensure_ascii=False)
    path = os.path.join(path, "scene_info.json")
    with open(path, 'w', encoding="utf-8") as f_:
        f_.write(json_data)


def jsonFileToDate(file: str) -> dict:
    with open(file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def create_directories(data: dict, parent_path='') -> None:
    for item in data["city"]:
        name = item['name']
        _path = os.path.join(parent_path, name)
        os.makedirs(_path, exist_ok=True)
        for _item in item["city"]:
            path = os.path.join(_path, _item["name"])
            os.makedirs(path, exist_ok=True)


def create_file() -> None:
    script_path = os.path.abspath(__file__)
    grandparent_dir = os.path.dirname(os.path.dirname(script_path))
    create_directories(jsonFileToDate("city.json"), os.path.join(grandparent_dir, "data"))


def get_is_exist(scene_name: str, city_name: str, province: str) -> bool:
    script_path = os.path.abspath(__file__)
    grandparent_dir = os.path.dirname(os.path.dirname(script_path))

    path = os.path.join(grandparent_dir, "data", province, city_name,scene_name, f"{scene_name}.xlsx")
    return os.path.exists(path)


# ============ Knowledge 目录相关函数 ============

def get_knowledge_base_path() -> str:
    """获取 knowledge 目录的绝对路径"""
    script_path = os.path.abspath(__file__)
    grandparent_dir = os.path.dirname(os.path.dirname(script_path))
    knowledge_path = os.path.join(grandparent_dir, "knowledge")
    os.makedirs(knowledge_path, exist_ok=True)
    return knowledge_path


def create_knowledge_structure(data: dict) -> None:
    """创建 knowledge 目录结构：knowledge/省份/城市/景区"""
    knowledge_path = get_knowledge_base_path()
    create_directories(data, knowledge_path)


def get_scene_data_path(province: str, city: str, scene_name: str, create: bool = True) -> str:
    """获取景区数据保存路径：knowledge/省份/城市/景区"""
    knowledge_path = get_knowledge_base_path()
    path = os.path.join(knowledge_path, province, city, scene_name)
    if create:
        os.makedirs(path, exist_ok=True)
    return path


def get_all_knowledge_provinces() -> list:
    """获取 knowledge 目录中已有的所有省份"""
    knowledge_path = get_knowledge_base_path()
    if not os.path.exists(knowledge_path):
        return []
    return [d for d in os.listdir(knowledge_path) if os.path.isdir(os.path.join(knowledge_path, d))]


def get_all_knowledge_cities(province: str) -> list:
    """获取指定省份下已有的所有城市"""
    province_path = os.path.join(get_knowledge_base_path(), province)
    if not os.path.exists(province_path):
        return []
    return [d for d in os.listdir(province_path) if os.path.isdir(os.path.join(province_path, d))]


def get_all_knowledge_scenes(province: str, city: str) -> list:
    """获取指定城市下已有的所有景区"""
    city_path = os.path.join(get_knowledge_base_path(), province, city)
    if not os.path.exists(city_path):
        return []
    return [d for d in os.listdir(city_path) if os.path.isdir(os.path.join(city_path, d))]
