import json
import os
import re
from config import USER_HOTWORDS_FILE

BASE_HOTWORD_MAP = {
    "军不见": "君不见", "军君": "君", "钧": "君", "均": "君", "君君": "君",
    "不建": "君不见", "不不见": "不见", "黄黄河": "黄河", "河之之水": "河之水",
    "之之水": "之水", "水水天上": "水天上", "天上来来": "天上来",
    "天上来海来": "天上来", "上来海来": "上来",
    "奔奔流": "奔流", "流流到": "流到", "道道到海": "到海",
    "还还不复": "还不复", "赴覆": "复", "枯燥回": "复回",
    "尔湖不复葵": "不复回", "不复葵": "不复回",
    "宁静": "明镜", "高堂宁静": "高堂明镜", "高堂明堂明镜": "高堂明镜",
    "高高明镜": "高堂明镜", "高照高堂唐明镜": "高堂明镜", "高唐明镜": "高堂明镜",
    "悲哀T": "悲白发", "悲白白发": "悲白发", "白发际": "白发",
    "悲哀悲白发": "悲白发",
    "照昭": "朝", "如沽": "如青", "桔": "雪", "绮雪": "雪",
    "如今思": "朝如青丝", "朝日朝朝日": "朝如青丝",
    "如清金青的思": "如青丝", "青丝暮沐橙绿血雪": "朝如青丝暮成雪",
    "沐橙绿血雪": "暮成雪", "张朝照朝日朝暮朝日如今艰渐凋渐艰巨之暮景暮橙雪": "朝如青丝暮成雪",
    "艰渐凋渐艰巨": "青丝", "暮景暮橙雪": "暮成雪",
    "人生易需": "人生得意须", "人生得意义易虚近欢安": "人生得意须尽欢",
    "得意义": "得意", "易虚近": "须尽",
    "莫末景莫是": "莫使", "末日是金": "莫使金樽", "莫末日末没时使": "莫使",
    "金墩": "金樽", "空对兑越乐": "空对月",
    "天我才": "天生我材", "天生我财": "天生我材",
    "必避": "必", "必弊避必": "必",
    "千金津金": "千金", "散尽景靳": "散尽",
    "千金灿散尽进净静海富来": "千金散尽还复来",
    "灿散尽": "散尽", "进净静": "尽", "海富来": "还复来",
    "彭杨洋": "烹羊", "仔牛": "宰牛",
    "汇会": "会", "一印尹": "一饮", "一饮三百杯": "一饮三百杯",
    "岑夫子": "岑夫子", "臣岑夫子": "岑夫子", "橙夫敷子": "岑夫子",
    "沾栈丹丘": "丹丘生", "丹丘秋笙": "丹丘生",
    "抢救强将": "将", "枪进劲进": "将进", "枪易昌将静酒": "将进酒",
    "空景空对月": "空对月",
    "中古传撰籍玉": "钟鼓馔玉", "不足桂贵柜": "不足贵",
    "欲遇不足跪": "不足贵",
    "但愿长院长最不负心": "但愿长醉不复醒",
    "凌尹新唻李": "古来圣贤", "鼓来圣晟圣贤接": "古来圣贤皆寂寞",
    "圣贤接寂寞莫": "圣贤皆寂寞", "寂寞莫": "寂寞",
    "名为唯有莹吟邝饮者留刘绮雪丽": "惟有饮者留其名",
    "陈王羲息": "陈王昔时", "使彦雁闫雁平了乐": "宴平乐",
    "斗九十天字还血": "斗酒十千恣欢谑",
    "主人和魏": "主人何为", "延炎绍朔邵琦邵卿浅": "言少钱",
    "静景": "径须", "对君卓拙浊镯浊珠浊爱闫雨景云金卓云卓": "对君酌",
    "滚舞润发际马": "五花马",
    "与君歌裔溢期": "与君歌一曲",
    "前请君未": "请君为我", "我清": "我倾", "耳听天": "耳听",
    "请君未我清耳听天": "请君为我倾耳听",
    "雨津": "与君", "与军津": "与君", "雨津与军津歌以一曲": "与君歌一曲",
    "浅期曲请君": "请君", "侧轻": "倾耳听",
}

_hw_pattern = None
_hw_replacer = None

def load_user_hotwords():
    if os.path.exists(USER_HOTWORDS_FILE):
        try:
            with open(USER_HOTWORDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_hotwords(hotwords):
    with open(USER_HOTWORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(hotwords, f, ensure_ascii=False, indent=4)

def get_full_hotword_map():
    full_map = BASE_HOTWORD_MAP.copy()
    user_map = load_user_hotwords()
    full_map.update(user_map)
    return full_map

def build_hotword_replacer():
    global _hw_pattern, _hw_replacer
    full_map = get_full_hotword_map()
    if not full_map:
        _hw_pattern = None
        _hw_replacer = None
        return
    sorted_keys = sorted(full_map.keys(), key=len, reverse=True)
    escaped = [re.escape(k) for k in sorted_keys]
    _hw_pattern = re.compile('|'.join(escaped))
    def replacer(m):
        return full_map[m.group(0)]
    _hw_replacer = replacer

def apply_hotwords(text):
    if _hw_pattern and _hw_replacer:
        return _hw_pattern.sub(_hw_replacer, text)
    return text