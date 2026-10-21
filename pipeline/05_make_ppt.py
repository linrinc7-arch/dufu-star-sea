# -*- coding: utf-8 -*-
"""05_make_ppt.py — 生成课堂展示 PPT（含逐页讲稿）"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT = os.path.join(BASE, 'web', 'shots')
OUT = os.path.join(BASE, 'docs', '杜诗星海_课堂展示.pptx')

BG   = RGBColor(0x04,0x05,0x0A)
PAPER= RGBColor(0xEC,0xE7,0xDB)
DIM  = RGBColor(0x8A,0x85,0x78)
GOLD = RGBColor(0xC9,0xA2,0x27)
DARK = RGBColor(0x0A,0x0C,0x12)

SW, SH = Inches(13.333), Inches(7.5)
prs = Presentation()
prs.slide_width = SW
prs.slide_height = SH
BLANK = prs.slide_layouts[6]

def slide():
    s = prs.slides.add_slide(BLANK)
    bg = s.shapes.add_shape(1, 0, 0, SW, SH)
    bg.fill.solid(); bg.fill.fore_color.rgb = BG; bg.line.fill.background()
    return s

def txt(s, x, y, w, h, text, size=18, color=PAPER, font='宋体', bold=False,
        spacing=1.0, align=PP_ALIGN.LEFT, italic=False):
    tb = s.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    lines = text.split('\n')
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run(); r.text = ln
        r.font.size = Pt(size); r.font.color.rgb = color
        r.font.name = font; r.font.bold = bold; r.font.italic = italic
        rPr = r._r.get_or_add_rPr()
        ea = etree.SubElement(rPr, qn('a:ea')); ea.set('typeface', font)
    return tb

def hline(s, x, y, w, color=GOLD, h=Emu(6350)):
    ln = s.shapes.add_shape(1, x, y, w, h)
    ln.fill.solid(); ln.fill.fore_color.rgb = color; ln.line.fill.background()

def pic(s, name, x=0, y=0, w=SW, h=SH):
    p = os.path.join(SHOT, name)
    if os.path.exists(p):
        s.shapes.add_picture(p, x, y, width=w, height=h)

def scrim(s, alpha=55, x=0, y=0, w=SW, h=SH):
    sh = s.shapes.add_shape(1, x, y, w, h)
    sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor(3,4,8); sh.line.fill.background()
    srgb = sh.fill.fore_color._xFill.find(qn('a:srgbClr'))
    a = etree.SubElement(srgb, qn('a:alpha')); a.set('val', str(int(alpha*1000)))
    return sh

def notes(s, t):
    s.notes_slide.notes_text_frame.text = t

def kicker(s, num, label):
    txt(s, Inches(0.9), Inches(0.62), Inches(4), Inches(0.3), num + ' / ' + label, 10, GOLD, 'Arial')

# ---------- 1 封面 ----------
s = slide()
pic(s, 'shot_star.png'); scrim(s, 62)
txt(s, Inches(0.9), Inches(2.15), Inches(9), Inches(1.6), '杜诗星海', 66, PAPER, spacing=1.0)
txt(s, Inches(0.95), Inches(3.45), Inches(9), Inches(0.4), 'THE  STAR  SEA  OF  DU  FU', 11, GOLD, 'Arial')
hline(s, Inches(0.95), Inches(3.9), Inches(2.2))
txt(s, Inches(0.95), Inches(4.15), Inches(8.5), Inches(0.5),
    '一千四百六十八首诗，散作一片星海', 17, DIM)
txt(s, Inches(0.95), Inches(6.5), Inches(9), Inches(0.4),
    '《走近大诗人》期末作业 · 题目二 方向C · 诗歌数字化的技术实践', 11, DIM, 'Arial')
notes(s, '各位老师同学好，我做的作品叫《杜诗星海》。一句话说，我把杜甫全部一千四百六十八首诗，放进了一个由用词和意象决定的三维空间里，每一首诗是一颗星。')

# ---------- 2 诗云 ----------
s = slide()
pic(s, 'shot_star.png'); scrim(s, 78)
txt(s, Inches(1.1), Inches(1.5), Inches(1), Inches(0.3), '00 / ORIGIN', 10, GOLD, 'Arial')
txt(s, Inches(1.1), Inches(2.0), Inches(10.5), Inches(2.2),
    '“它拥有全部的诗，\n却判断不出哪一首是好的。”', 34, PAPER, spacing=1.5)
hline(s, Inches(1.15), Inches(4.6), Inches(1.6))
txt(s, Inches(1.1), Inches(4.95), Inches(9.6), Inches(1.6),
    '刘慈欣《诗云》里，神级文明耗尽太阳系的能量，把汉字所有可能的排列组合\n全部写出来，堆成一朵包裹恒星的云。\n\n杜甫的一千四百六十八首是它的反面——不是所有可能的诗，而是一个人写下的那些。',
    14, DIM, spacing=1.9)
notes(s, '作品的起点是刘慈欣的《诗云》。那个神级文明把汉字所有的排列组合都写出来，堆成一片包裹恒星的云——它拥有全部的诗，却判断不出哪一首是好的。我想做的是它的反面：不是所有可能的诗，而是一个具体的人，用五十九年在饥饿、战乱和漂泊里写下的那些。')

# ---------- 3 方法 ----------
s = slide()
kicker(s, '01', 'METHOD')
txt(s, Inches(0.9), Inches(1.15), Inches(11), Inches(0.9), '从一万四千字到一片星海', 34)
txt(s, Inches(0.95), Inches(1.95), Inches(10.5), Inches(0.5),
    '每一首诗变成三维空间里的一个点，距离由用词与意象决定', 14, DIM)
steps = [
    ('01  语料', '《全唐诗》57,607 首\n筛出杜甫 1,489 条'),
    ('02  校勘', '繁简 + 异体字 120 余条\n近重复剔除 → 1,468 首'),
    ('03  意象', '十类词典、约 200 词条\n解决古汉语无法分词'),
    ('04  特征', '字符 n-gram TF-IDF 4,000 维\n+ 意象频率 → SVD 64 维'),
    ('05  星海', 't-SNE 降到三维\nKMeans 分团 + lift 标签'),
]
x = Inches(0.9); w = Inches(2.25); gap = Inches(0.16)
for i,(t,d) in enumerate(steps):
    xx = x + i*(w+gap)
    card = s.shapes.add_shape(1, xx, Inches(2.75), w, Inches(2.35))
    card.fill.solid(); card.fill.fore_color.rgb = DARK
    card.line.color.rgb = RGBColor(0x1E,0x20,0x26); card.line.width = Pt(0.75)
    txt(s, xx+Inches(0.22), Inches(2.98), w-Inches(0.3), Inches(0.35), t, 15, GOLD)
    txt(s, xx+Inches(0.22), Inches(3.45), w-Inches(0.32), Inches(1.4), d, 11, DIM, spacing=1.7)
txt(s, Inches(0.95), Inches(5.55), Inches(11.4), Inches(1.2),
    '关键取舍：不用 jieba（会把“国破山河在”切碎）→ 自建词典匹配；不用 Three.js → 手写 Canvas，\n单文件 0.8 MB，断网双击即开。每条结论都能回溯到具体的词与出处。', 12.5, DIM, spacing=1.8)
notes(s, '技术上分五步：取全唐诗语料筛出杜甫；做繁简和异体字校勘，比如“劒”要还原成“剑”，否则统计里“剑”字会凭空消失；然后自建十类意象词典；再用字符 n-gram 的 TF-IDF 加意象频率做特征，降到三维；最后聚类并打标签。有两个取舍值得说：古汉语不能用现代分词器，所以改用词典匹配；为了教室演示不出意外，我手写了 Canvas 渲染器，不依赖任何库。')

# ---------- 4 星海 ----------
s = slide(); pic(s, 'shot_star.png')
scrim(s, 20, Inches(0), Inches(0), Inches(13.333), Inches(1.5))
kicker(s, '02', 'THE SEA')
txt(s, Inches(0.9), Inches(0.95), Inches(8), Inches(0.6), '可漫游的星海', 26)
txt(s, Inches(0.95), Inches(6.75), Inches(11), Inches(0.5),
    '1,468 个点 · 距离 = 用词与意象的相似度 · 颜色 = 主导意象类别', 11, DIM)
notes(s, '这是主界面。每一颗星是一首诗，它们的距离不是随机的，语义越接近的诗靠得越近，所以你会看到一团一团的星团。颜色代表这首诗的主导意象类别，共十类：日月、江山、草木、鸟兽、器物、病老、愁思、兵戈、亲友、释道。可以拖动巡游、滚轮远近，鼠标移过去会照亮附近的星。')

# ---------- 5 诗卡 ----------
s = slide(); pic(s, 'shot_card.png')
scrim(s, 18, Inches(0), Inches(6.4), Inches(13.333), Inches(1.1))
kicker(s, '03', 'ONE POEM')
txt(s, Inches(0.9), Inches(6.55), Inches(11.5), Inches(0.7),
    '《登高》的区别性意象：浊酒 · 酒杯 · 落木 · 鬓 —— 全部由语料统计得出，不是手写标签', 12, DIM)
notes(s, '点开任意一颗星，就是这首诗的档案卡。这里以《登高》为例。右下角这四个词——浊酒、酒杯、落木、鬓——不是我自己挑的，是算法用 lift 值算出来的：它在《登高》里的频率远高于在全部杜诗里的平均频率，所以它是这首诗的“指纹”。这就是我说的“结论可回溯”。')

# ---------- 6 检索 ----------
s = slide(); pic(s, 'shot_search.png')
scrim(s, 20, Inches(0), Inches(0), Inches(13.333), Inches(1.4))
kicker(s, '04', 'SEARCH')
txt(s, Inches(0.9), Inches(0.92), Inches(11), Inches(0.6), '检索：一条光路', 26)
txt(s, Inches(0.95), Inches(6.8), Inches(11), Inches(0.5),
    '输入“月”——219 首诗同时亮起，其余隐入暗处', 12, DIM)
notes(s, '这是检索。输入“月”，二百一十九首含“月”的诗同时亮起，其余的隐入暗处，像一条光路。这对应方向C原文里说的“按意象检索”那一项。')

# ---------- 7 生平 ----------
s = slide(); pic(s, 'shot_life.png')
scrim(s, 55, Inches(0), Inches(0), Inches(4.6), Inches(7.5))
kicker(s, '05', 'LIFE')
txt(s, Inches(0.9), Inches(1.5), Inches(3.4), Inches(0.8), '一个人的\n星轨', 32, PAPER, spacing=1.3)
hline(s, Inches(0.95), Inches(3.15), Inches(1.2))
txt(s, Inches(0.9), Inches(3.45), Inches(3.3), Inches(2.6),
    '712 — 770\n五期：读书漫游 / 困守长安\n陷贼与为官 / 漂泊西南\n流寓湖湘\n\n36 条大事记 · 29 个行迹点', 11, DIM, spacing=1.8)
notes(s, '除了星海，还有三个模块把“人”补回来。这是生平：五个时期，三十六条大事记，二十九个行迹点。比如“困守长安”十年，是他从裘马清狂到“残杯与冷炙”的转折。')

# ---------- 8 交游 ----------
s = slide(); pic(s, 'shot_friends.png')
scrim(s, 55, Inches(0), Inches(0), Inches(4.6), Inches(7.5))
kicker(s, '06', 'CIRCLE')
txt(s, Inches(0.9), Inches(1.5), Inches(3.4), Inches(0.8), '诗可以群', 32, PAPER)
hline(s, Inches(0.95), Inches(2.55), Inches(1.2))
txt(s, Inches(0.9), Inches(2.85), Inches(3.3), Inches(2.8),
    '十二位同时代诗人\n\n李白 11 首 · 严武 13 首\n高适 10 首 · 郑虔 7 首\n\n线越粗，赠诗越多', 11, DIM, spacing=1.8)
notes(s, '这是交游。杜甫赠李白的诗有十一首，赠严武十三首。线越粗代表赠诗越多。这里也回答了作业里“至少涉及两位课程诗人”的要求：李白、高适、岑参都在里面。')

# ---------- 9 评点 ----------
s = slide(); pic(s, 'shot_crit.png')
scrim(s, 55, Inches(0), Inches(0), Inches(4.6), Inches(7.5))
kicker(s, '07', 'AFTERLIFE')
txt(s, Inches(0.9), Inches(1.5), Inches(3.4), Inches(0.8), '身后之名', 32, PAPER)
hline(s, Inches(0.95), Inches(2.55), Inches(1.2))
txt(s, Inches(0.9), Inches(2.85), Inches(3.3), Inches(2.8),
    '三十条历代评杜\n\n唐 · 元稹、韩愈\n宋 · 苏轼、严羽、张戒\n清 · 仇兆鳌、沈德潜\n近代 · 梁启超、闻一多', 11, DIM, spacing=1.8)
notes(s, '这是评点。从元稹写墓志铭到梁启超叫杜甫“情圣”，三十条。这条时间轴想说明一件事：杜甫不是一开始就是“诗圣”的，每个时代都在重新发现他一次。')

# ---------- 10 结语 ----------
s = slide()
pic(s, 'shot_star.png'); scrim(s, 80)
txt(s, Inches(1.0), Inches(1.7), Inches(11), Inches(1.2),
    '算法能排列出所有的诗\n却排不出哪一首是好的', 32, PAPER, spacing=1.6)
hline(s, Inches(1.05), Inches(4.0), Inches(1.6))
txt(s, Inches(1.0), Inches(4.35), Inches(10.5), Inches(1.8),
    '一千二百年前，杜甫在夔州写下“无边落木萧萧下，不尽长江滚滚来”。\n这句诗不在任何“全组合”里——它只能来自一个在秋天登过高台、\n并且知道自己病了、老了、回不去的人。', 14, DIM, spacing=2.0)
txt(s, Inches(1.0), Inches(6.6), Inches(11), Inches(0.4),
    '谢谢 · 作品可在断网环境双击运行', 11, GOLD, 'Arial')
notes(s, '最后回到开头。算法能排列出所有的诗，却排不出哪一首是好的。《登高》里那句“无边落木萧萧下，不尽长江滚滚来”，它不在任何一个“全组合”里——它只能来自一个在秋天登过高台、并且知道自己病了、老了、回不去的人。这就是我想说的：技术可以让我们更清楚地看见一首诗好在哪，但“好在哪”这件事，最后还是人的事。谢谢。')

prs.save(OUT)
print('saved', OUT, 'slides', len(prs.slides))
