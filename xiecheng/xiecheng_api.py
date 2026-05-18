import json
import math
import os
import random
import re
import threading
import time

from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from urllib3.exceptions import InsecureRequestWarning, InsecurePlatformWarning

from config import IS_VERIFY, TIME_OUT
from utils.fake_user_agent import get_fake_user_agent
from utils.proxy import my_get_proxy
from utils.utils import create_file, jsonFileToDate, dateToJsonFileSceneInfo, get_scene_data_path

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

# 获取热门城市的id(post)
GET_CITY = "https://vacations.ctrip.com/restapi/gateway/14422/genericDestRecommend"

# 携程景区首页(get)
GET_HOME = "https://you.ctrip.com/"

# 携程景区评论(post)
GET_COMMENT = "https://m.ctrip.com/restapi/soa2/13444/json/getCommentCollapseList"

# 获取景区详细信息(post)
GET_SCENE_INFO = "https://m.ctrip.com/restapi/soa2/18254/json/GetSightOverview"


class XieCheng:
    def __init__(self, console: Console):
        self.scene_list = []
        self.sees = requests.session()
        self.console = console
        self.sees.verify = IS_VERIFY
        self.get_home()

    def get_home(self):
        self.sees.get(
            url=GET_HOME,
            headers={
                "User-Agent": get_fake_user_agent("mobile")
            },
            proxies=my_get_proxy(),
            timeout=TIME_OUT
        )

    def get_areas(self) -> list:
        """获取中国省份和城市列表（硬编码，因为携程页面结构已变化）"""
        # 中国34个省级行政区及其主要城市
        areas_data = [
            {"name": "北京", "city": [{"name": "北京", "url": "https://you.ctrip.com/place/beijing1.html"}]},
            {"name": "上海", "city": [{"name": "上海", "url": "https://you.ctrip.com/place/shanghai2.html"}]},
            {"name": "天津", "city": [{"name": "天津", "url": "https://you.ctrip.com/place/tianjin154.html"}]},
            {"name": "重庆", "city": [{"name": "重庆", "url": "https://you.ctrip.com/place/chongqing158.html"}]},
            {"name": "河北", "city": [
                {"name": "石家庄", "url": "https://you.ctrip.com/place/shijiazhuang199.html"},
                {"name": "秦皇岛", "url": "https://you.ctrip.com/place/qinhuangdao132.html"},
                {"name": "承德", "url": "https://you.ctrip.com/place/chengde135.html"},
                {"name": "张家口", "url": "https://you.ctrip.com/place/zhangjiakou497.html"},
                {"name": "唐山", "url": "https://you.ctrip.com/place/tangshan200.html"},
                {"name": "保定", "url": "https://you.ctrip.com/place/baoding459.html"},
            ]},
            {"name": "山西", "city": [
                {"name": "太原", "url": "https://you.ctrip.com/place/taiyuan161.html"},
                {"name": "大同", "url": "https://you.ctrip.com/place/datong275.html"},
                {"name": "平遥", "url": "https://you.ctrip.com/place/pingyao163.html"},
                {"name": "五台山", "url": "https://you.ctrip.com/place/wutaishan162.html"},
            ]},
            {"name": "内蒙古", "city": [
                {"name": "呼和浩特", "url": "https://you.ctrip.com/place/huhehaote31.html"},
                {"name": "呼伦贝尔", "url": "https://you.ctrip.com/place/hulunbeier33.html"},
                {"name": "鄂尔多斯", "url": "https://you.ctrip.com/place/eerduosi164.html"},
            ]},
            {"name": "辽宁", "city": [
                {"name": "沈阳", "url": "https://you.ctrip.com/place/shenyang159.html"},
                {"name": "大连", "url": "https://you.ctrip.com/place/dalian156.html"},
                {"name": "丹东", "url": "https://you.ctrip.com/place/dandong157.html"},
            ]},
            {"name": "吉林", "city": [
                {"name": "长春", "url": "https://you.ctrip.com/place/changchun160.html"},
                {"name": "吉林", "url": "https://you.ctrip.com/place/jilin165.html"},
                {"name": "长白山", "url": "https://you.ctrip.com/place/changbaishan166.html"},
            ]},
            {"name": "黑龙江", "city": [
                {"name": "哈尔滨", "url": "https://you.ctrip.com/place/haerbin155.html"},
                {"name": "亚布力", "url": "https://you.ctrip.com/place/yabul167.html"},
            ]},
            {"name": "江苏", "city": [
                {"name": "南京", "url": "https://you.ctrip.com/place/nanjing23.html"},
                {"name": "苏州", "url": "https://you.ctrip.com/place/suzhou25.html"},
                {"name": "无锡", "url": "https://you.ctrip.com/place/wuxi24.html"},
                {"name": "扬州", "url": "https://you.ctrip.com/place/yangzhou26.html"},
                {"name": "常州", "url": "https://you.ctrip.com/place/changzhou22.html"},
            ]},
            {"name": "浙江", "city": [
                {"name": "杭州", "url": "https://you.ctrip.com/place/hangzhou29.html"},
                {"name": "宁波", "url": "https://you.ctrip.com/place/ningbo30.html"},
                {"name": "乌镇", "url": "https://you.ctrip.com/place/wuzhen2026903.html"},
                {"name": "西塘", "url": "https://you.ctrip.com/place/xitang2026904.html"},
                {"name": "普陀山", "url": "https://you.ctrip.com/place/putuoshan2026905.html"},
            ]},
            {"name": "安徽", "city": [
                {"name": "合肥", "url": "https://you.ctrip.com/place/hofei21.html"},
                {"name": "黄山", "url": "https://you.ctrip.com/place/huangshan18.html"},
                {"name": "宏村", "url": "https://you.ctrip.com/place/hongcun2026906.html"},
                {"name": "九华山", "url": "https://you.ctrip.com/place/jiuhuashan19.html"},
            ]},
            {"name": "福建", "city": [
                {"name": "福州", "url": "https://you.ctrip.com/place/fuzhou34.html"},
                {"name": "厦门", "url": "https://you.ctrip.com/place/xiamen35.html"},
                {"name": "武夷山", "url": "https://you.ctrip.com/place/wuyishan36.html"},
                {"name": "土楼", "url": "https://you.ctrip.com/place/tulou2026907.html"},
            ]},
            {"name": "江西", "city": [
                {"name": "南昌", "url": "https://you.ctrip.com/place/nanchang37.html"},
                {"name": "庐山", "url": "https://you.ctrip.com/place/lushan38.html"},
                {"name": "婺源", "url": "https://you.ctrip.com/place/wuyuan39.html"},
                {"name": "三清山", "url": "https://you.ctrip.com/place/sanqingshan40.html"},
            ]},
            {"name": "山东", "city": [
                {"name": "济南", "url": "https://you.ctrip.com/place/jinan41.html"},
                {"name": "青岛", "url": "https://you.ctrip.com/place/qingdao42.html"},
                {"name": "泰山", "url": "https://you.ctrip.com/place/taishan43.html"},
                {"name": "曲阜", "url": "https://you.ctrip.com/place/qufu44.html"},
            ]},
            {"name": "河南", "city": [
                {"name": "郑州", "url": "https://you.ctrip.com/place/zhengzhou45.html"},
                {"name": "洛阳", "url": "https://you.ctrip.com/place/luoyang46.html"},
                {"name": "开封", "url": "https://you.ctrip.com/place/kaifeng47.html"},
                {"name": "嵩山", "url": "https://you.ctrip.com/place/songshan48.html"},
            ]},
            {"name": "湖北", "city": [
                {"name": "武汉", "url": "https://you.ctrip.com/place/wuhan51.html"},
                {"name": "宜昌", "url": "https://you.ctrip.com/place/yichang52.html"},
                {"name": "恩施", "url": "https://you.ctrip.com/place/enshi53.html"},
            ]},
            {"name": "湖南", "city": [
                {"name": "长沙", "url": "https://you.ctrip.com/place/changsha54.html"},
                {"name": "张家界", "url": "https://you.ctrip.com/place/zhangjiajie55.html"},
                {"name": "凤凰古城", "url": "https://you.ctrip.com/place/fenghuang56.html"},
                {"name": "岳阳", "url": "https://you.ctrip.com/place/yueyang57.html"},
            ]},
            {"name": "广东", "city": [
                {"name": "广州", "url": "https://you.ctrip.com/place/guangzhou58.html"},
                {"name": "深圳", "url": "https://you.ctrip.com/place/shenzhen59.html"},
                {"name": "珠海", "url": "https://you.ctrip.com/place/zhuhai60.html"},
                {"name": "桂林", "url": "https://you.ctrip.com/place/guilin61.html"},
            ]},
            {"name": "广西", "city": [
                {"name": "桂林", "url": "https://you.ctrip.com/place/guilin61.html"},
                {"name": "阳朔", "url": "https://you.ctrip.com/place/yangshuo62.html"},
                {"name": "柳州", "url": "https://you.ctrip.com/place/liuzhou63.html"},
            ]},
            {"name": "海南", "city": [
                {"name": "三亚", "url": "https://you.ctrip.com/place/sanya61.html"},
                {"name": "海口", "url": "https://you.ctrip.com/place/haikou37.html"},
                {"name": "陵水", "url": "https://you.ctrip.com/place/lingshui1509.html"},
            ]},
            {"name": "四川", "city": [
                {"name": "成都", "url": "https://you.ctrip.com/place/chengdu104.html"},
                {"name": "九寨沟", "url": "https://you.ctrip.com/place/jiuzhaigou105.html"},
                {"name": "峨眉山", "url": "https://you.ctrip.com/place/emeishan106.html"},
                {"name": "乐山", "url": "https://you.ctrip.com/place/leshan107.html"},
                {"name": "都江堰", "url": "https://you.ctrip.com/place/dujiangyan108.html"},
                {"name": "稻城亚丁", "url": "https://you.ctrip.com/place/yaoding109.html"},
                {"name": "康定", "url": "https://you.ctrip.com/place/kangding110.html"},
                {"name": "绵阳", "url": "https://you.ctrip.com/place/mianyang111.html"},
            ]},
            {"name": "贵州", "city": [
                {"name": "贵阳", "url": "https://you.ctrip.com/place/guiyang112.html"},
                {"name": "黄果树", "url": "https://you.ctrip.com/place/huangguoshu113.html"},
                {"name": "荔波", "url": "https://you.ctrip.com/place/libo114.html"},
                {"name": "西江千户苗寨", "url": "https://you.ctrip.com/place/qianhumiaozhai115.html"},
                {"name": "遵义", "url": "https://you.ctrip.com/place/zunyi116.html"},
            ]},
            {"name": "云南", "city": [
                {"name": "昆明", "url": "https://you.ctrip.com/place/kunming29.html"},
                {"name": "大理", "url": "https://you.ctrip.com/place/dali1445616.html"},
                {"name": "丽江", "url": "https://you.ctrip.com/place/lijiang32.html"},
                {"name": "西双版纳", "url": "https://you.ctrip.com/place/xishuangbanna30.html"},
                {"name": "香格里拉", "url": "https://you.ctrip.com/place/shangri-la106.html"},
                {"name": "腾冲", "url": "https://you.ctrip.com/place/tengchong696.html"},
                {"name": "洱海", "url": "https://you.ctrip.com/place/erhai2020651.html"},
                {"name": "普者黑", "url": "https://you.ctrip.com/place/puzhehei117.html"},
            ]},
            {"name": "西藏", "city": [
                {"name": "拉萨", "url": "https://you.ctrip.com/place/lhasa118.html"},
                {"name": "林芝", "url": "https://you.ctrip.com/place/linzhi119.html"},
                {"name": "日喀则", "url": "https://you.ctrip.com/place/rikaze120.html"},
            ]},
            {"name": "陕西", "city": [
                {"name": "西安", "url": "https://you.ctrip.com/place/xian121.html"},
                {"name": "延安", "url": "https://you.ctrip.com/place/yanan122.html"},
                {"name": "华山", "url": "https://you.ctrip.com/place/huashan123.html"},
            ]},
            {"name": "甘肃", "city": [
                {"name": "兰州", "url": "https://you.ctrip.com/place/lanzhou124.html"},
                {"name": "敦煌", "url": "https://you.ctrip.com/place/dunhuang125.html"},
                {"name": "张掖", "url": "https://you.ctrip.com/place/zhangye126.html"},
                {"name": "嘉峪关", "url": "https://you.ctrip.com/place/jiayuguan127.html"},
            ]},
            {"name": "青海", "city": [
                {"name": "西宁", "url": "https://you.ctrip.com/place/xining128.html"},
                {"name": "青海湖", "url": "https://you.ctrip.com/place/qinghaihu129.html"},
                {"name": "茶卡盐湖", "url": "https://you.ctrip.com/place/chakalake130.html"},
            ]},
            {"name": "宁夏", "city": [
                {"name": "银川", "url": "https://you.ctrip.com/place/yinchuan131.html"},
                {"name": "中卫", "url": "https://you.ctrip.com/place/zhongwei132.html"},
            ]},
            {"name": "新疆", "city": [
                {"name": "乌鲁木齐", "url": "https://you.ctrip.com/place/wulumuqi133.html"},
                {"name": "喀什", "url": "https://you.ctrip.com/place/kashgar134.html"},
                {"name": "伊犁", "url": "https://you.ctrip.com/place/yili135.html"},
                {"name": "吐鲁番", "url": "https://you.ctrip.com/place/tulufan136.html"},
                {"name": "哈密", "url": "https://you.ctrip.com/place/hami137.html"},
            ]},
            {"name": "台湾", "city": [
                {"name": "台北", "url": "https://you.ctrip.com/place/taibei360.html"},
                {"name": "高雄", "url": "https://you.ctrip.com/place/kaohsiung756.html"},
                {"name": "垦丁", "url": "https://you.ctrip.com/place/kentingnationalpark1380.html"},
            ]},
        ]

        return areas_data

    def get_city_scene(self, city_name, city_url: str) -> list:
        """
        获取城市热门景区信息
        :param city_name: 城市名称
        :param city_url: 城市对应在携程的主页yrl
        :return: 该城市的热门景区信息
        """
        self.console.rule(f"[green]正在获取[yellow]{city_name}[/yellow]的景区信息[/green]", characters="*")
        scene_list = []
        try:
            res = self.sees.get(
                url=city_url,
                headers={
                    "User-Agent": get_fake_user_agent("mobile")
                },
                proxies=my_get_proxy(),
                timeout=TIME_OUT
            )
        except Exception as e:
            self.console.print(f"[red]获取城市景区信息失败，{e},你可以检查你的网路或者代理。", style="bold red")
            return scene_list
        res_shop = BeautifulSoup(res.text, "lxml")
        city_scene = res_shop.find_all("a", attrs={"class": "guide-main-item"})
        for item in city_scene:
            try:
                city_scene_name = item.find("p", attrs={"class": "title"})
                if city_scene_name is None:
                    continue
                city_scene_name = city_scene_name.string
                city_scene_url = item["href"]
                scene_list.append({
                    "name": city_scene_name,
                    "url": city_scene_url
                })
            except TypeError:
                self.console.print(f"[red]获取景区信息失败[/red]")
            except Exception as e:
                self.console.print(f"[red]获取景区信息失败：{e},你的ip可能被封禁了！[/red]")
        if len(scene_list) == 0:
            self.console.print(
                f"[yellow]获取{city_name}相关景区的信息[red]失败[/red]:[blue]{[item['name'] for item in scene_list]}[/blue]",
                style="bold")
            return scene_list
        self.console.print(
            f"[yellow]获取{city_name}相关景区的信息[green]成功[/green]:[blue]{[item['name'] for item in scene_list]}[/blue]",
            style="bold")
        return scene_list

    def get_city_scene_info(self, city_scene_name, city_scene_url: str, province: str, city: str) -> None:
        """
        获取景区的id
        :param city:城市
        :param province: 省份
        :param city_scene_name: 景点的名称
        :param city_scene_url: 景点对应在携程的主页yrl
        :return:
        """
        pattern_businessId = r'/(\d+)\.html$'
        match = re.search(pattern_businessId, city_scene_url)
        businessId = ""
        districtId = ""
        if match:
            businessId = match.group(1)

        pattern_districtId = r'(\d+)/'
        match = re.search(pattern_districtId, city_scene_url)
        if match:
            districtId = match.group(1)
        _params = self.generate_scene_comments_params()
        _data = {
            "businessId": str(businessId),
            "districtId": int(districtId),
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
        _params = self.generate_scene_comments_params()
        try:
            _res = requests.post(
                url=GET_SCENE_INFO,
                params=_params,
                headers={
                    "User-Agent": get_fake_user_agent("mobile", False),

                },
                data=json.dumps(_data),
                proxies=my_get_proxy(),
                timeout=TIME_OUT

            )
            result = _res.json()
            try:
                scene_info = {
                    "name": city_scene_name,
                    "url": city_scene_url,
                    "resourceId": businessId,
                    "comment_total": result["commentCount"],
                    "comment_score": result["commentScore"],
                    "heat_score": result["heatScore"],
                    "tag_name": result.get("tagName", ""),
                    "poi_Level": result.get("poiLevel", ""),
                    "is_free": result["isFree"],
                }
                self.scene_list.append(scene_info)
                self.console.print(scene_info)
                try:
                    from utils.utils import get_scene_data_path, dateToJsonFileSceneInfo
                    path_file = get_scene_data_path(province, city, city_scene_name)
                    dateToJsonFileSceneInfo(scene_info, path_file)
                except Exception as e:
                    self.console.print(f"[red]保存景点{city_scene_name}信息失败：{e}。[/red]")

            except Exception as e:
                self.console.print(f"[red]解析景点{city_scene_name}信息失败：{e}。[/red]")
        except Exception as e:
            self.console.print(f"[red]获取景点{city_scene_name}信息失败：{e},你可以检查你的网路或者代理。[/red]")

    def get_all_scene_info(self, city_list: list, province: str, city_name: str) -> None:
        """
        获取所有景区的信息
        :param city_name: 城市名称
        :param province: 省份名称
        :param city_list: 城市景区列表
        :return:
        """
        for city in city_list:
            self.get_city_scene_info(city["name"], city["url"], province, city_name)

    def get_scene_comments(self, resourceId: int, page_index: int, page_size) -> list:
        _params = self.generate_scene_comments_params()
        _data = {
            "arg": {
                "channelType": 7,
                "collapseType": 1,
                "commentTagId": 0,
                "pageIndex": page_index,
                "pageSize": page_size,
                "resourceId": int(resourceId),
                "resourceType": 11,
                "sortType": 3,
                "sourceType": 1,
                "starType": 0,
                "videoImageSize": "700_392",
            },
            "contentType": "json",
            "head": {
                "auth": "",
                "cid": _params["_fxpcqlniredt"],
                "ctok": "",
                "cver": "1.0",
                "lang": "01",
                "sid": "8888",
                "extension": [{
                    "name": "tecode",
                    "value": "h5"
                }],
                "syscode": "09",
                "xsid": "",
            }
        }
        try:
            res = self.sees.post(
                url=GET_COMMENT,
                params=_params,
                # 不能直接使用_data，要用json.dumps()转换成json格式
                data=json.dumps(_data),
                headers={
                    "User-Agent": get_fake_user_agent("mobile"),
                    # "Cookie": self.sees.cookies.get_dict(),
                },
                proxies=my_get_proxy(),
                timeout=TIME_OUT
            )
        except Exception as e:
            self.console.print(f"[red]获取景点评论第{page_index}页失败,网络请求异常: {e}[/red]")
            return []

        # 检查HTTP状态码
        if res.status_code != 200:
            self.console.print(f"[red]获取景点评论第{page_index}页失败,HTTP状态码: {res.status_code}[/red]")
            self.console.print(f"[red]返回内容前500字符: {res.text[:500]}[/red]")
            return []

        # 尝试解析JSON
        try:
            return res.json()
        except json.JSONDecodeError as e:
            self.console.print(f"[red]获取景点评论第{page_index}页失败,JSON解析错误: {e}[/red]")
            self.console.print(f"[red]HTTP状态码: {res.status_code}[/red]")
            self.console.print(f"[red]返回内容前500字符: {res.text[:500]}[/red]")
            self.console.print(f"[red]请求头: {dict(res.request.headers)}[/red]")
            return []

    def generate_scene_comments_params(self) -> dict:
        """
        生成请求景区评论的 params参数
        :return:
        """
        random_number = random.randint(100000, 999999)
        return {
            "_fxpcqlniredt": self.sees.cookies.get("GUID"),
            "x-traceID": self.sees.cookies.get("GUID") + "-" + str(int(time.time() * 1000000)) + "-" + str(
                random_number)
        }

    @staticmethod
    def get_province() -> list:
        script_path = os.path.abspath(__file__)
        grandparent_dir = os.path.dirname(os.path.dirname(script_path))
        path = os.path.join(grandparent_dir, "city.json")
        cities_json = jsonFileToDate(path)
        cities_json = cities_json["city"]

        return cities_json

    @staticmethod
    def generate_city_file() -> None:
        create_file()
