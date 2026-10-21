# -*- coding: utf-8 -*-
"""01_build_corpus.py — 全唐诗 JSON → 杜甫诗结构化语料（繁简 + 异体字 + 体裁）"""
import json, glob, os, re, collections, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'data', 'raw', 'tang')
OUT = os.path.join(BASE, 'data', 'build')

# ---------- 1. 繁简字典 ----------
def load_opencc(path):
    m = {}
    for line in open(path, encoding='utf-8'):
        if line.startswith('#') or '\t' not in line:
            continue
        k, v = line.rstrip('\n').split('\t', 1)
        m[k] = v.split()[0]
    return m

OPENCC = load_opencc(os.path.join(BASE, '_tools', 'TSCharacters.txt'))

# 词级保护：转换前替换成占位符，转换后还原（避免 OpenCC 的语境误伤）
PROTECT = {
    '乾坤': '\ue000', '乾元': '\ue001',
}
# 异体字补充表（OpenCC 未收，或唐诗习惯写法）
VARIANT = {
    # —— 人物 / 常见异体 ——
    '猨': '猿', '桮': '杯', '盃': '杯', '盌': '碗', '沈': '沉',
    '歎': '叹', '敎': '教', '峯': '峰', '羣': '群', '裏': '里',
    '麤': '粗', '鬭': '斗', '鷰': '燕', '迺': '乃', '蹔': '暂',
    '暫': '暂', '廻': '回', '逈': '迥', '閒': '闲', '閑': '闲',
    '牀': '床', '窓': '窗', '牎': '窗', '栢': '柏', '煖': '暖',
    '喫': '吃', '徧': '遍', '絃': '弦', '舩': '船', '艸': '草',
    '菓': '果', '邨': '村', '隣': '邻', '颿': '帆',
    # —— 兵器 / 高频实字 ——
    '劒': '剑', '劍': '剑', '劔': '剑', '劎': '剑',
    # —— 其余异体 ——
    '疎': '疏', '媿': '愧', '飜': '翻', '嬾': '懒', '蘂': '蕊',
    '慙': '惭', '竝': '并', '褭': '袅', '荅': '答', '姪': '侄',
    '鴈': '雁', '緜': '绵', '櫂': '棹', '檝': '楫', '顦': '憔',
    '顇': '悴', '臯': '皋', '隄': '堤', '棃': '梨', '羇': '羁',
    '簷': '檐', '秪': '只', '缾': '瓶', '覩': '睹', '柟': '楠',
    '牓': '榜', '跼': '局', '椶': '棕', '斾': '旆', '穉': '稚',
    '偪': '逼', '賸': '剩', '髣': '仿', '髴': '佛', '蔕': '蒂',
    '輭': '软', '鉏': '锄', '胷': '胸', '搆': '构', '鏁': '锁',
    '稉': '粳', '怱': '匆', '悤': '匆', '牋': '笺', '鼇': '鳌',
    '歘': '欻', '鹢': '鹢', '鵞': '鹅', '麪': '面', '鷄': '鸡',
}
# 词组级异体
VARIANT_PHRASE = {'衮衮': '滚滚', '滚滚': '滚滚'}

def to_simplified(s):
    for k, v in PROTECT.items():
        s = s.replace(k, v)
    for k, v in VARIANT_PHRASE.items():
        s = s.replace(k, v)
    s = ''.join(VARIANT.get(c, OPENCC.get(c, c)) for c in s)
    for k, v in PROTECT.items():
        s = s.replace(v, k)
    return s

# ---------- 2. 载入语料 ----------
files = sorted(glob.glob(os.path.join(RAW, '*.json')), key=lambda p: int(os.path.basename(p).split('.')[0]))
raw_all, dufu = [], []
for f in files:
    d = json.load(open(f, encoding='utf-8'))
    raw_all.extend(d)
    dufu.extend([x for x in d if x['author'] == '杜甫'])

# 去重：按正文前 20 字
seen, poems = set(), []
for x in dufu:
    body = ''.join(x['paragraphs'])
    key = body[:20]
    if key in seen:
        continue
    seen.add(key)
    poems.append(x)

# ---------- 2b. 近重复去除（同归一化标题 + 正文相似度 > 0.85） ----------
import difflib
LEFU = ['横吹曲辞','相和歌辞','杂曲歌辞','杂歌谣辞','舞曲歌辞','琴曲歌辞','近代曲辞','郊庙歌辞','燕射歌辞','清商曲辞']
def norm_title(t):
    t = t.strip()
    for pfx in LEFU:
        if t.startswith(pfx):
            t = t[len(pfx):].strip()
    return t
def norm_body(b):
    return re.sub(r'[^\u4e00-\u9fff]', '', b)

groups = collections.defaultdict(list)
for i, x in enumerate(poems):
    groups[norm_title(to_simplified(x['title']))].append(i)
drop = set()
for t, idxs in groups.items():
    if len(idxs) < 2:
        continue
    for a in range(len(idxs)):
        for b in range(a + 1, len(idxs)):
            ia, ib = idxs[a], idxs[b]
            ba, bb = norm_body(''.join(poems[ia]['paragraphs'])), norm_body(''.join(poems[ib]['paragraphs']))
            if not ba or not bb:
                continue
            if difflib.SequenceMatcher(None, ba, bb).ratio() > 0.85:
                ta, tb = to_simplified(poems[ia]['title']), to_simplified(poems[ib]['title'])
                a_lefu = any(ta.startswith(x) for x in LEFU)
                b_lefu = any(tb.startswith(x) for x in LEFU)
                victim = ia if (a_lefu and not b_lefu) else ib
                drop.add(victim)
poems = [p for i, p in enumerate(poems) if i not in drop]

# ---------- 3. 结构化 ----------
PUNCT = '，。？！；：、'
def split_lines(paras):
    out = []
    for p in paras:
        for seg in re.split(r'[，。？！；：]', p):
            seg = seg.strip()
            if seg:
                out.append(seg)
    return out

def classify(lines, paras):
    lens = [len(l) for l in lines]
    if not lens:
        return '未知', 0
    n = len(lines)
    uniq = set(lens)
    if uniq == {5}: w = '五言'
    elif uniq == {7}: w = '七言'
    elif uniq <= {5, 7}: w = '五七言'
    else: w = '杂言'
    uniform = uniq in ({5}, {7})
    if n == 4 and uniform: f = '绝句'
    elif n == 8 and uniform: f = '律诗'
    elif n > 8 and uniform and n % 2 == 0: f = '长诗'   # 古体与排律难以启发式判别，统称长诗
    else: f = '古体'
    return w + f, n

records = []
for i, x in enumerate(poems):
    paras = [to_simplified(p) for p in x['paragraphs']]
    title = to_simplified(x['title'])
    lines = split_lines(paras)
    form, n = classify(lines, paras)
    body = ''.join(lines)
    records.append({
        'id': i,
        'seq': i,                       # 语料顺序（全唐诗编次，近似编年）
        'title': title,
        'paragraphs': paras,
        'lines': lines,
        'n_lines': n,
        'n_chars': len(body),
        'form': form,
        'body': body,
    })

# ---------- 4. 残留繁体检测 ----------
trad_keys = {k for k, v in OPENCC.items() if k != v}
resid = collections.Counter()
for r in records:
    for ch in r['body'] + r['title']:
        if ch in trad_keys:
            resid[ch] += 1

os.makedirs(OUT, exist_ok=True)
json.dump(records, open(os.path.join(OUT, 'dufu_poems.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

report = []
report.append('全库诗数: %d' % len(raw_all))
report.append('杜甫原始条数: %d' % len(dufu))
report.append('精确去重后: %d' % len(records))
report.append('乐府近重复去除: %d 首' % len(drop))
report.append('体裁分布: ' + str(collections.Counter(r['form'] for r in records).most_common()))
report.append('残留繁体字数: %d 种' % len(resid))
report.append('残留 top30: ' + ' '.join('%s×%d' % (c, n) for c, n in resid.most_common(30)))
open(os.path.join(OUT, 'build_report.txt'), 'w', encoding='utf-8').write('\n'.join(report))
print('done', len(records))
