# -*- coding: utf-8 -*-
"""02b_periods.py — 给 1,468 首诗推定创作时期（地理意象 + 语义近邻）"""
import json, os, collections
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(BASE, 'data', 'build')

poems = json.load(open(os.path.join(B, 'dufu_poems.json'), encoding='utf-8'))
N = len(poems)

# 五期的地理/事象标志词（权重：专名 1.0，泛称 0.35）
KW = {
 0: {  # 读书漫游 731—745
   '吴越':1.0,'姑苏':1.0,'苏台':1.0,'剡溪':1.0,'金陵':0.8,'齐赵':1.0,'兖州':1.0,
   '泰山':0.8,'岱宗':1.0,'齐鲁':0.8,'邯郸':0.8,'燕赵':0.6,'梁宋':1.0,'宋州':0.6,
   # 注意：不要把「望岳」这类题名当分期证据——杜甫三首《望岳》分咏泰山/华山/衡山，
   # 题名一进关键词，三首就都被判成早年（见 work/_why.py 复算）。
   '吹台':1.0,'单父':1.0,'梁园':1.0,'天姥':0.9,'吴门':0.9,'燕':0.25,
   '赵':0.25,'齐':0.25,'鲁':0.25,'少年':0.3,'裘马':0.9,
 },
 1: {  # 困守长安 746—755
   '长安':0.35,'奉先':1.0,'骊山':1.0,'曲江':0.8,'慈恩':0.9,'渼陂':1.0,'鄠县':1.0,
   '杜陵':0.8,'少陵':0.5,'韦曲':1.0,'天宝':0.4,'丽人':0.8,'京华':0.8,'凤翔':0.0,
   '华清':1.0,'昆明池':1.0,'乐游':1.0,'兵车':0.9,'京':0.25,'省':0.2,'丹陛':0.6,'献赋':0.9,
   '集贤':0.8,'率府':0.9,'奉先':1.0,'寒士':0.5,
 },
 2: {  # 陷贼与为官 756—759
   '鄜州':1.0,'羌村':1.0,'凤翔':0.9,'华州':0.9,'秦州':1.0,'同谷':1.0,
   '潼关':0.8,'陈陶':1.0,'新安':0.8,'石壕':1.0,'胡骑':0.8,'贼':0.6,'北征':0.6,
   '左拾遗':1.0,'贼中':0.8,'陷贼':0.9,'行在':0.9,'收复':0.7,'九庙':0.8,'胡尘':0.7,
 },
 3: {  # 漂泊西南 760—765
   '成都':1.0,'草堂':1.0,'浣花':1.0,'锦官':0.9,'梓州':1.0,'阆州':1.0,
   '武侯':0.9,'蜀相':0.9,'青城':0.8,'严武':0.8,'西蜀':0.9,'蜀':0.3,'巴':0.2,
 },
 4: {  # 夔州·湖湘 766—770
   '夔州':1.0,'白帝':0.9,'瞿塘':1.0,'滟滪':1.0,'江陵':1.0,'公安':0.9,
   '岳阳':1.0,'洞庭':0.9,'潭州':1.0,'衡州':0.9,'耒阳':1.0,'湘':0.6,'荆':0.4,'湖湘':1.0,
 },
}

label = np.full(N, -1, dtype=np.int32)
score_detail = []
for i, p in enumerate(poems):
    text = p['body'] + p['title']
    sc = {k: 0.0 for k in KW}
    for k, ws in KW.items():
        for w, wt in ws.items():
            c = text.count(w)
            if c: sc[k] += c * wt
    best = max(sc, key=sc.get)
    if sc[best] >= 0.6:
        label[i] = best
    score_detail.append(sc)

# 语义近邻补全
Z = np.load(os.path.join(B, 'space.npz'))['Z']
known = np.where(label >= 0)[0]
unk = np.where(label < 0)[0]
Zk = Z[known]
# 反向频次加权，避免样本多的时期把周围全吸过去
class_n = collections.Counter(label[known].tolist())
inv = {k: 1.0 / (class_n[k] ** 0.5) for k in class_n}
for i in unk:
    d = ((Zk - Z[i]) ** 2).sum(axis=1)
    idx = np.argsort(d)[:21]
    votes = collections.Counter()
    for j in idx:
        c = int(label[known[j]])
        votes[c] += inv[c] / (1.0 + d[j] * 3.0)
    label[i] = votes.most_common(1)[0][0]

# 人工定年覆盖：题名同题、地名同形（华山「白帝」≠ 夔州白帝城）等靠字面判不出来的，
# 在这里逐条钉死。键是诗序号，值见 PERIODS：0读书漫游 1困守长安 2陷贼与为官 3漂泊西南 4夔州·湖湘
OVERRIDE = {
  24: 0,   # 望岳 其一「岱宗夫如何」，约 736—740 齐赵
  393: 4,  # 望岳 其三「南岳配朱鸟」，大历四年（769）衡山
  539: 2,  # 望岳 其二「西岳崚嶒」，乾元元年（758）贬华州途中
}
for i, k in OVERRIDE.items():
    label[i] = k

cnt = collections.Counter(label.tolist())
out = {'periods': [int(x) for x in label.tolist()]}
json.dump(out, open(os.path.join(B, 'periods.json'), 'w', encoding='utf-8'))
print('地理直判 %d 首，语义补全 %d 首' % (len(known), len(unk)))
print('分期分布（0—4）:', [cnt.get(i,0) for i in range(5)])
