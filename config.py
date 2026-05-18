# 爬取指定省份内的所有地区景点的评论数据
# AREAS = ['云南', '四川', '贵州']  # 指定省份，None 表示爬取所有省份
import os
AREAS = os.getenv("CSPIDER_AREAS")
if AREAS:
    try:
        AREAS = eval(AREAS)  # 支持 None 或列表
    except:
        pass

# 爬取评论时每页的数据
PAGESIZE = int(os.getenv("CSPIDER_PAGESIZE", "20"))

# 爬取评论的页数
MAX_PAGE = int(os.getenv("CSPIDER_MAX_PAGE", "300"))

# 是否启动代理
IS_PROXY = os.getenv("CSPIDER_IS_PROXY", "False").lower() == "true"

# 是否启动随机UA
IS_FAKE_USER_AGENT = os.getenv("CSPIDER_IS_FAKE_USER_AGENT", "True").lower() == "true"

# 是否启动验证ssl
IS_VERIFY = os.getenv("CSPIDER_IS_VERIFY", "False").lower() == "true"

# 是否要覆盖已经保存的excel文件
IS_OVER = os.getenv("CSPIDER_IS_OVER", "False").lower() == "true"

# 延时时间（城市）
CITY_SLEEP_TIME = int(os.getenv("CSPIDER_CITY_SLEEP_TIME", "10"))

# 景区之间的休眠时间
SCENE_SLEEP_TIME = int(os.getenv("CSPIDER_SCENE_SLEEP_TIME", "10"))

# 线程池数量
POOL_NUMBER = int(os.getenv("CSPIDER_POOL_NUMBER", "1"))

# 请求超时时间
TIME_OUT = int(os.getenv("CSPIDER_TIMEOUT", "5"))
