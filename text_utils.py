import re

RE_CLEAN_TAGS = re.compile(r'<[^>]*>|FIL|ILE|SPK|UNK|UT|[A-Za-z]+', re.IGNORECASE)
RE_DEDUPE_CHAR = re.compile(r'([\u4e00-\u9fff])\1+')
RE_DEDUPE_PHRASE = re.compile(r'([\u4e00-\u9fff]{2,8})\1+')

def common_prefix_len(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

def dedupe_text(text):
    if not text: return ""
    old = None
    while old != text:
        old = text
        text = RE_DEDUPE_PHRASE.sub(r'\1', text)
        text = RE_DEDUPE_CHAR.sub(r'\1', text)
    return text

def light_clean(text):
    """预览阶段极简清洗（仅去标签）"""
    if not text: return ""
    return RE_CLEAN_TAGS.sub('', text)

def full_clean(text):
    """确认阶段深度清洗（去标签 + 去重 + 热词 + 诗句校正）"""
    from hotwords import apply_hotwords
    from poem_corrector import correct_by_poem
    if not text: return ""
    text = RE_CLEAN_TAGS.sub('', text)
    text = dedupe_text(text)
    text = apply_hotwords(text)
    text = dedupe_text(text)
    text = correct_by_poem(text)
    return text.strip()