# -*- coding = utf-8 -*-
# @Time :2023/7/15 23:14
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :scenic_spots_comment
# @File :  get_all_excel_file_data.py
import os

import openpyxl
from rich.console import Console

from utils.utils import jsonFileToDate, get_knowledge_base_path
import pandas as pd

# 设置控制台的宽度
console = Console(width=150)


def get_city_scene_knowledge(province_name: str, city_name: str) -> list:
    """从 knowledge 目录获取景区列表"""
    path = get_knowledge_base_path()
    path = os.path.join(path, province_name, city_name)
    if not os.path.exists(path):
        return []
    files = os.listdir(path)
    scene_list = []
    for file_name in files:
        scene_path = os.path.join(path, file_name)
        if os.path.isdir(scene_path):
            scene_list.append({
                "name": file_name,
                "path": scene_path
            })
    return scene_list


def read_excel_to_data(path: str, scene_name: str) -> list:
    # 尝试多种可能的文件名格式
    possible_files = [
        f"{scene_name}.xlsx",
        f"{scene_name}_评论.xlsx",
        f"{scene_name}_comments.xlsx",
    ]
    for filename in possible_files:
        _path = os.path.join(path, filename)
        if os.path.exists(_path):
            data = pd.read_excel(_path).to_dict(orient='records')
            return data
    return []


def get_all_excel_file_data():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "city.json")
    all_province_city = jsonFileToDate(path)
    comment_total = 0

    scene_total = 0
    scene_fail_total = 0
    knowledge_path = get_knowledge_base_path()

    console.print(f"[green]Knowledge 目录路径: {knowledge_path}[/green]", style="bold green")

    for province in all_province_city["city"]:
        console.rule(f"[blue]统计{province['name']}的数据")
        province_comment_total = 0
        for city in province["city"]:
            console.rule(f"[green]开始统计{city['name']}的景区信息", characters="+")
            all_scene = get_city_scene_knowledge(province['name'], city['name'])
            for scene in all_scene:
                console.print(f"[yellow]开始获取{scene['name']}的景区评论信息")
                comment_scene = read_excel_to_data(scene['path'], scene['name'])
                if not comment_scene:
                    scene_fail_total += 1
                    console.log(f"[red]该景区{scene['name']}没有发现excel文件")
                scene_total += 1
                comment_total += len(comment_scene)
                console.print(f"[green]{scene['name']}发现{len(comment_scene)}条评论")
            province_comment_total = province_comment_total + comment_total

        console.print(f"[blue]{province['name']}共爬取了{province_comment_total}条评论")
    console.print(f"总计爬取了:{scene_total}个景区,实际结果为{scene_total - scene_fail_total},共计评论{comment_total}条")


if __name__ == "__main__":
    get_all_excel_file_data()
