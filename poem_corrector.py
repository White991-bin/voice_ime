import re
from difflib import SequenceMatcher

try:
    from pypinyin import lazy_pinyin, Style
    PINYIN_AVAILABLE = True
except ImportError:
    PINYIN_AVAILABLE = False

JIANGJINJIU = [
    "君不见黄河之水天上来",
    "奔流到海不复回",
    "君不见高堂明镜悲白发",
    "朝如青丝暮成雪",
    "人生得意须尽欢",
    "莫使金樽空对月",
    "天生我材必有用",
    "千金散尽还复来",
    "烹羊宰牛且为乐",
    "会须一饮三百杯",
    "岑夫子",
    "丹丘生",
    "将进酒",
    "杯莫停",
    "与君歌一曲",
    "请君为我倾耳听",
    "钟鼓馔玉不足贵",
    "但愿长醉不复醒",
    "古来圣贤皆寂寞",
    "惟有饮者留其名",
    "陈王昔时宴平乐",
    "斗酒十千恣欢谑",
    "主人何为言少钱",
    "径须沽取对君酌",
    "五花马",
    "千金裘",
    "呼儿将出换美酒",
    "与尔同销万古愁"
]

# 预计算双字集合
POEM_BIGRAMS = set()
for poem in JIANGJINJIU:
    for i in range(len(poem)-1):
        POEM_BIGRAMS.add(poem[i:i+2])

def pinyin_similarity(a, b):
    if not PINYIN_AVAILABLE:
        return 0.0
    try:
        pa = ''.join(lazy_pinyin(a, style=Style.TONE3, errors='ignore'))
        pb = ''.join(lazy_pinyin(b, style=Style.TONE3, errors='ignore'))
        return SequenceMatcher(None, pa, pb).ratio()
    except:
        return 0.0

def correct_by_poem(text, threshold=0.72):
    if not text or len(text) < 3:
        return text

    # 移除标点，快速预检
    text_clean = re.sub(r'[，。？！；、]', '', text)
    if len(text_clean) < 3:
        return text

    text_bigrams = {text_clean[i:i+2] for i in range(len(text_clean)-1)}
    if not text_bigrams.intersection(POEM_BIGRAMS):
        return text

    # 构建映射
    clean_to_raw = []
    raw_idx = 0
    for ch in text:
        if ch not in '，。？！；、':
            clean_to_raw.append(raw_idx)
            raw_idx += 1
        else:
            raw_idx += 1

    matches = []
    sorted_poems = sorted(JIANGJINJIU, key=len, reverse=True)

    for poem in sorted_poems:
        plen = len(poem)
        min_win = max(2, plen - 4)
        max_win = plen + 4
        best_score = 0.0
        best_start_clean = -1
        best_end_clean = -1

        for start_clean in range(len(text_clean)):
            for win_len in range(min_win, max_win + 1):
                end_clean = start_clean + win_len
                if end_clean > len(text_clean):
                    break
                window = text_clean[start_clean:end_clean]
                char_score = SequenceMatcher(None, window, poem).ratio()
                final_score = char_score
                if PINYIN_AVAILABLE and char_score < threshold:
                    py_score = pinyin_similarity(window, poem)
                    final_score = max(char_score, py_score * 0.95)
                if final_score > best_score:
                    best_score = final_score
                    best_start_clean = start_clean
                    best_end_clean = end_clean

        if best_score >= threshold and best_start_clean != -1:
            start_raw = clean_to_raw[best_start_clean]
            end_raw = clean_to_raw[best_end_clean - 1] + 1 if best_end_clean > 0 else start_raw
            while end_raw < len(text) and text[end_raw] not in '，。？！；、':
                end_raw += 1
            matches.append((start_raw, end_raw, best_score, poem))

    if not matches:
        return text

    matches.sort(key=lambda x: x[2], reverse=True)
    occupied = [False] * len(text)
    selected = []
    for start, end, score, poem in matches:
        if not any(occupied[start:end]):
            selected.append((start, end, poem))
            for i in range(start, end):
                occupied[i] = True

    selected.sort(key=lambda x: x[0], reverse=True)
    result = list(text)
    for start, end, poem in selected:
        result[start:end] = list(poem)

    return ''.join(result)