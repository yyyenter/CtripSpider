# -*- coding = utf-8 -*-
"""
携程单个景区信息测试脚本
用于测试爬取单个景区的基本信息和评论
"""
import json
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from xiecheng.xiecheng_api import XieCheng
from utils.utils import get_scene_data_path, dateToJsonFileSceneInfo

console = Console(width=150)


def get_scene_info(xc: XieCheng, scene_name: str, scene_url: str, province: str, city: str) -> dict:
    """获取单个景区的详细信息"""
    console.rule(f"[cyan]正在获取景区信息[/cyan]", characters="=")

    # 从 URL 提取 resourceId
    import re
    pattern_businessId = r'/(\d+)\.html$'
    match = re.search(pattern_businessId, scene_url)
    businessId = match.group(1) if match else ""

    pattern_districtId = r'(\d+)/'
    match = re.search(pattern_districtId, scene_url)
    districtId = match.group(1) if match else "0"

    _params = xc.generate_scene_comments_params()
    _data = {
        "businessId": str(businessId),
        "districtId": int(districtId) if districtId else 0,
        "head": {
            "auth": "",
            "cid": _params["_fxpcqlniredt"],
            "ctok": "",
            "cver": "1.0",
            "extension": [],
            "lang": "01",
            "sid": "8888",
            "syscode": "09",
            "xsid": ""
        },
        "scene": "basic",
        "useSightExtend": True
    }

    try:
        from xiecheng.xiecheng_api import GET_SCENE_INFO
        from utils.fake_user_agent import get_fake_user_agent
        import requests

        _res = requests.post(
            url=GET_SCENE_INFO,
            params=_params,
            headers={"User-Agent": get_fake_user_agent("mobile", False)},
            data=json.dumps(_data),
            timeout=10
        )
        result = _res.json()

        scene_info = {
            "name": scene_name,
            "url": scene_url,
            "resourceId": businessId,
            "comment_total": result.get("commentCount", 0),
            "comment_score": result.get("commentScore", 0),
            "heat_score": result.get("heatScore", 0),
            "tag_name": result.get("tagName", []),
            "poi_Level": result.get("poiLevel", ""),
            "is_free": result.get("isFree", False),
        }

        # 显示结果
        table = Table(title="景区信息")
        table.add_column("字段", style="cyan")
        table.add_column("值", style="green")
        table.add_row("名称", scene_info["name"])
        table.add_row("评分", str(scene_info["comment_score"]))
        table.add_row("评论数", str(scene_info["comment_total"]))
        table.add_row("热度", str(scene_info["heat_score"]))
        table.add_row("等级", str(scene_info["poi_Level"]))
        table.add_row("是否免费", "是" if scene_info["is_free"] else "否")
        table.add_row("标签", ", ".join(scene_info["tag_name"]) if scene_info["tag_name"] else "无")

        console.print(table)
        return scene_info

    except Exception as e:
        console.print(f"[red]获取景区信息失败：{e}[/red]")
        return None


def get_comments(xc: XieCheng, scene_name: str, resource_id: str, max_pages: int = 3) -> list:
    """获取少量评论用于测试"""
    console.rule(f"[cyan]正在获取评论数据[/cyan]", characters="=")

    comments = []
    for page in range(1, min(max_pages + 1, 4)):
        console.print(f"[yellow]正在获取第 {page} 页评论...[/yellow]")
        result = xc.get_scene_comments(resource_id, page, 20)

        if result and result.get("result", {}).get("items"):
            items = result["result"]["items"]
            comments.extend(items)
            console.print(f"[green]第 {page} 页获取到 {len(items)} 条评论[/green]")
        else:
            console.print(f"[yellow]第 {page} 页没有更多评论，停止爬取[/yellow]")
            break

    console.print(f"[green]共获取到 {len(comments)} 条评论[/green]")
    return comments


def save_to_knowledge(province: str, city: str, scene_info: dict, comments: list) -> str:
    """保存到 knowledge 目录"""
    scene_name = scene_info["name"]
    path = get_scene_data_path(province, city, scene_name)
    os.makedirs(path, exist_ok=True)

    # 保存景区信息
    info_path = os.path.join(path, "scene_info.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(scene_info, f, ensure_ascii=False, indent=2)
    console.print(f"[green]景区信息已保存到: {info_path}[/green]")

    # 保存评论
    if comments:
        import pandas as pd
        data = []
        for c in comments:
            data.append({
                "评论ID": c.get("commentId", ""),
                "用户昵称": c.get("userInfo", {}).get("nickName", ""),
                "评论内容": c.get("content", ""),
                "评分": c.get("score", ""),
                "评论时间": c.get("publishTypeTag", "").replace(" 发布点评", ""),
                "点赞数": c.get("usefulCount", 0),
                "IP属地": c.get("ipLocatedName", ""),
            })

        df = pd.DataFrame(data)
        excel_path = os.path.join(path, f"{scene_name}_评论.xlsx")
        df.to_excel(excel_path, index=False)
        console.print(f"[green]评论数据已保存到: {excel_path}[/green]")
        return excel_path

    return path


def main():
    console.print("[bold green]=== 携程单个景区信息测试 ===[/bold green]")

    # 配置参数（可修改）
    province = "四川"
    city = "成都"
    scene_name = "九寨沟"
    scene_url = "https://gs.ctrip.com/html5/you/sight/1/10107.html"
    max_pages = 3

    console.print(f"[yellow]省份: {province}[/yellow]")
    console.print(f"[yellow]城市: {city}[/yellow]")
    console.print(f"[yellow]景区: {scene_name}[/yellow]")
    console.print(f"[yellow]URL: {scene_url}[/yellow]")

    # 初始化
    xc = XieCheng(console=console)

    # 获取景区信息
    console.print("[bold yellow]步骤 1: 获取景区基本信息[/bold yellow]")
    scene_info = get_scene_info(xc, scene_name, scene_url, province, city)

    if not scene_info:
        console.print("[red]获取景区信息失败，退出[/red]")
        return

    # 获取评论
    console.print("[bold yellow]步骤 2: 获取评论数据[/bold yellow]")
    comments = get_comments(xc, scene_name, scene_info["resourceId"], max_pages)

    # 保存到 knowledge
    console.print("[bold yellow]步骤 3: 保存到 knowledge 目录[/bold yellow]")
    result_path = save_to_knowledge(province, city, scene_info, comments)

    console.print(f"[bold green]=== 完成！数据已保存到: {result_path} ===[/bold green]")


if __name__ == "__main__":
    main()
