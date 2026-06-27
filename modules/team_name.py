from core.logger import log

TEAM_NAME_ZH = {
    # AFC亞洲區
    "Australia": "澳洲",
    "Iran": "伊朗",
    "Iraq": "伊拉克",
    "Japan": "日本",
    "Jordan": "約旦",
    "Qatar": "卡達",
    "Saudi Arabia": "沙烏地",
    "South Korea": "南韓",
    "Uzbekistan": "烏茲別克",

    # CAF非洲區
    "Algeria": "阿爾及利亞",
    "Cape Verde": "維德角",
    "Cape Verde Islands": "維德角",   # 保留相容
    "DR Congo": "剛果民主共和國",
    "Congo DR": "剛果民主共和國",     # 保留相容
    "Egypt": "埃及",
    "Ghana": "迦納",
    "Ivory Coast": "象牙海岸",
    "Morocco": "摩洛哥",
    "Senegal": "塞內加爾",
    "South Africa": "南非",
    "Tunisia": "突尼西亞",

    # CONCACAF中北美洲及加勒比海區
    "Canada": "加拿大",
    "Mexico": "墨西哥",
    "United States": "美國",
    "Curaçao": "古拉索",
    "Curacao": "古拉索",              # 避免 API 沒有 ç
    "Haiti": "海地",
    "Panama": "巴拿馬",

    # CONMEBOL南美洲區
    "Argentina": "阿根廷",
    "Brazil": "巴西",
    "Colombia": "哥倫比亞",
    "Ecuador": "厄瓜多",
    "Paraguay": "巴拉圭",
    "Uruguay": "烏拉圭",

    # OFC大洋洲區
    "New Zealand": "紐西蘭",

    # UEFA歐洲區
    "Austria": "奧地利",
    "Belgium": "比利時",
    "Bosnia and Herzegovina": "波赫",
    "Bosnia-Herzegovina": "波赫",     # 保留相容
    "Croatia": "克羅埃西亞",
    "Czech Republic": "捷克",
    "England": "英格蘭",
    "France": "法國",
    "Germany": "德國",
    "Netherlands": "荷蘭",
    "Norway": "挪威",
    "Portugal": "葡萄牙",
    "Scotland": "蘇格蘭",
    "Spain": "西班牙",
    "Switzerland": "瑞士",
    "Sweden": "瑞典",
    "Turkey": "土耳其",
}

def team_zh(name: str) -> str:
    if name not in TEAM_NAME_ZH:
        log(f"[WARNING] 未翻譯隊名：{name}")
      
    return TEAM_NAME_ZH.get(name, name)
