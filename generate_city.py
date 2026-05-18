from config import AREAS
from utils.utils import dateToJsonFile, create_file, get_knowledge_base_path
from xiecheng.xiecheng_api import XieCheng
from rich.console import Console

if __name__ == '__main__':
    xc = XieCheng(console=Console())
    _city = xc.get_areas()

    # 如果 AREAS 为 None，则爬取所有省份；否则只爬取指定省份
    if AREAS is None:
        city = _city
        xc.console.print(f"[green]检测到 AREAS=None，将爬取所有 {len(city)} 个省份的数据[/green]", style="bold green")
    else:
        city = [item for item in _city if item["name"] in AREAS]
        xc.console.print(f"[green]检测到 AREAS={AREAS}，将爬取指定 {len(city)} 个省份的数据[/green]", style="bold green")

    dateToJsonFile(city)

    # 创建 knowledge 目录结构
    knowledge_path = get_knowledge_base_path()
    create_file()
    xc.console.print(f"[green]已创建 knowledge 目录结构: {knowledge_path}[/green]", style="bold green")
    xc.console.print(f"你可以根据需要删减city.json中的城市，", style="bold green")

