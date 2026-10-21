# -*- coding: utf-8 -*-
"""02_features.py — 意象词典 + 文本特征 + 语义空间降维（星海坐标）"""
import json, os, re, collections, math
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(BASE, 'data', 'build')

# ============ 1. 意象词典 ============
LEX = {
 '天象时序': ['月','日','云','雨','雪','风','霜','露','星','天','秋','春','夏','冬','暮','夜','晓','昏','寒','暖','晴','阴','日暮','落日','明月','新月','残月','秋风','春风','风雪','霜雪','白日','青春'],
 '地理空间': ['江','河','山','川','原','野','关','塞','城','郭','楼','台','舟','船','岸','洲','浦','峡','谷','岭','峰','泉','溪','湖','海','江湖','关山','边塞','长安','中原','故园','故乡','天涯','万里','千里'],
 '动物': ['雁','鸿','鸟','马','虎','鹰','猿','鸥','燕','莺','鱼','龙','鹤','鸡','犬','豺','狼','白鸥','沙鸥','孤雁','归雁','战马','胡马'],
 '植物': ['松','柏','竹','菊','梅','柳','花','草','枫','桑','麻','禾','黍','稻','蓬','蒿','落木','黄叶','秋草','春草','桃花','梅花'],
 '器物': ['剑','酒','杯','琴','书','灯','衣','衾','杖','策','帆','橹','戈','戟','弓','箭','衣裳','征衣','浊酒','酒杯','孤舟','扁舟','书剑'],
 '身体生命': ['病','老','白','发','泪','血','骨','身','心','眼','头','鬓','颜','魂','梦','白发','白头','老病','衰','病身','泪痕','血泪','白骨'],
 '情感心理': ['愁','悲','喜','哀','怨','叹','哭','笑','恨','思','忆','忧','苦','乐','惊','恐','寂寞','凄凉','萧瑟','伤心','断肠','慷慨','悲哀'],
 '社会战争': ['兵','戈','战','征','戍','烽','鼓','角','军','贼','盗','乱','国','家','民','黎','元','吏','税','干戈','兵戈','战乱','盗贼','黎元','苍生','朝廷','天子','将军','征戍','烽火'],
 '人伦交往': ['君','臣','友','亲','妻','子','儿','弟','兄','故人','客','宾','主','邻','乡','朋友','故交','知己','骨肉','兄弟','妻子','儿童'],
 '宗教哲理': ['道','佛','禅','仙','神','鬼','命','理','乾坤','天地','万物','浮生','虚空'],
}
WORD2CAT = {}
for cat, words in LEX.items():
    for w in words:
        WORD2CAT.setdefault(w, cat)

STOP1 = set('之其而以于不无有是也矣焉哉乎者所为与且则乃何如若如我吾汝尔彼此斯夫盖故虽然既已未莫勿可能得见使令将又更还却只但共相自各每诸凡皆悉尽')

# ============ 2. 载入语料 ============
poems = json.load(open(os.path.join(BUILD, 'dufu_poems.json'), encoding='utf-8'))
N = len(poems)
bodies = [p['body'] for p in poems]

# ============ 3. 意象计数 ============
imagery = np.zeros((N, len(WORD2CAT)), dtype=np.float32)
words = list(WORD2CAT.keys())
counts = []
for i, b in enumerate(bodies):
    c = collections.Counter()
    for w in words:
        k = b.count(w)
        if k:
            c[w] = k
            imagery[i, list(WORD2CAT).index(w)] += k
    counts.append(c)

# 全库词频 → 每首诗的"区别性意象"（lift 而非词频，避免 风/月/日 这类全库高频字占位）
_gw = collections.Counter()
for c in counts: _gw.update(c)
_total_len = float(sum(len(b) for b in bodies))
def distinctive(i, topk=6):
    c = counts[i]; L = max(1, len(bodies[i]))
    scored = []
    for w, k in c.items():
        lift = (k / L) / (_gw[w] / _total_len)
        scored.append((lift * math.log(1 + _gw[w]), w))
    scored.sort(reverse=True)
    return [w for _, w in scored[:topk]]
distinct_cache = [distinctive(i) for i in range(N)]

cat_names = list(LEX.keys())
cat_counts = np.zeros((N, len(cat_names)), dtype=np.float32)
for i, c in enumerate(counts):
    for w, k in c.items():
        cat_counts[i, cat_names.index(WORD2CAT[w])] += k

# 归一化（按诗长）
lens = np.array([max(1, len(b)) for b in bodies], dtype=np.float32)
imagery_n = imagery / lens[:, None] * 100
cat_n = cat_counts / lens[:, None] * 100

# 类别 lift：相对全集平均的"过表达"倍数（解决"天象"占 55% 无法配色的问题）
global_rate = cat_counts.sum(0) / lens.sum()
# 平滑 lift：α=2，避免"宗教哲理"这种稀有类别被 1 次命中放大
ALPHA = 2.0
cat_lift = (cat_counts + ALPHA) / (global_rate[None, :] * lens[:, None] + ALPHA)

# ============ 4. TF-IDF 字符 n-gram ============
def ngrams(s):
    toks = []
    for n in (1, 2):
        for i in range(len(s) - n + 1):
            g = s[i:i+n]
            if n == 1 and g in STOP1:
                continue
            if n == 1 and not ('\u4e00' <= g <= '\u9fff'):
                continue
            toks.append(g)
    return ' '.join(toks)

docs = [ngrams(b) for b in bodies]
tfidf = TfidfVectorizer(token_pattern=r'\S+', min_df=3, max_features=4000, sublinear_tf=True)
X_tfidf = tfidf.fit_transform(docs)

# ============ 5. 拼接 + SVD ============
from scipy.sparse import hstack, csr_matrix
X = hstack([X_tfidf * 0.6, csr_matrix(imagery_n * 1.4)]).tocsr()
svd = TruncatedSVD(n_components=64, random_state=42)
Z = svd.fit_transform(X)
Z = normalize(Z)

# ============ 6. t-SNE 降维到 3D ============
tsne = TSNE(n_components=3, perplexity=35, random_state=42, init='pca',
            learning_rate='auto', max_iter=1200, metric='cosine')
P = tsne.fit_transform(Z)
# 按 95 分位半径缩放：保留 t-SNE 的密度结构（不打到球面上）
_rad = np.linalg.norm(P, axis=1)
_scale = np.percentile(_rad, 95) or 1.0
P = P / _scale


# ============ 7. 聚类（K 选择 + lift 标签） ============
from sklearn.metrics import silhouette_score

np.savez(os.path.join(BUILD, 'space.npz'), Z=Z, P=P, lab_placeholder=np.zeros(N))

def cluster_label(idx, counts, N, k):
    """用 lift 找出这个簇最有区分度的词"""
    allfreq = collections.Counter()
    for c in counts: allfreq.update(c)
    agg = collections.Counter()
    for i in idx: agg.update(counts[i])
    scored = []
    for w, k2 in agg.items():
        if k2 < max(3, len(idx) * 0.05): continue
        lift = (k2 / len(idx)) / (allfreq[w] / N)
        if lift < 1.4: continue
        scored.append((lift * math.log(1 + k2), w, k2, round(lift, 2)))
    scored.sort(reverse=True)
    if not scored:
        return [(0, w, k2, 0.0) for w, k2 in agg.most_common(6)]
    return scored[:6]

best = None
for k in range(6, 13):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    lb = km.fit_predict(Z)
    s = silhouette_score(Z[::5], lb[::5])
    if best is None or s > best[1]: best = (k, s, lb, km)
    print('K=%d silhouette=%.3f' % (k, s))

K, sil, lab, km = best
print('chosen K =', K, 'silhouette = %.3f' % sil)

clusters = []
for k in range(K):
    idx = np.where(lab == k)[0]
    top = cluster_label(idx, counts, N, k)
    titles = [poems[i]['title'] for i in idx[:4]]
    clusters.append({
        'id': int(k), 'size': int(len(idx)),
        'top_words': [t[1] for t in top],
        'lift': [t[3] for t in top],
        'label': '·'.join(t[1] for t in top[:3]),
        'samples': titles,
        'form': collections.Counter(poems[i]['form'] for i in idx).most_common(2),
    })

# ============ 8. 输出 ============
out = {
  'poems': [],
  'clusters': clusters,
  'lexicon': LEX,
  'cat_names': cat_names,
}
for i, p in enumerate(poems):
    top = [w for w, _ in counts[i].most_common(4)]
    out['poems'].append({
        'id': i, 'title': p['title'], 'form': p['form'], 'n': p['n_chars'],
        'x': round(float(P[i, 0]), 4), 'y': round(float(P[i, 1]), 4), 'z': round(float(P[i, 2]), 4),
        'c': int(lab[i]),
        'top': distinct_cache[i],
        'dom': cat_names[int(np.argmax(cat_lift[i]))],
        'dom_lift': round(float(np.max(cat_lift[i])), 2),
        'cat': {cat_names[j]: round(float(cat_n[i, j]), 2) for j in range(len(cat_names)) if cat_n[i, j] > 0},
    })
json.dump(out, open(os.path.join(BUILD, 'starfield.json'), 'w', encoding='utf-8'), ensure_ascii=False)

# 特征单独存一份给检索系统
feat = {'ids': list(range(N)), 'words': words, 'counts': [dict(c) for c in counts],
        'cat': cat_names, 'cat_counts': cat_n.round(3).tolist(),
        'cat_lift': cat_lift.round(2).tolist(), 'dom': [cat_names[int(np.argmax(cat_lift[i]))] for i in range(N)]}
json.dump(feat, open(os.path.join(BUILD, 'features.json'), 'w', encoding='utf-8'), ensure_ascii=False)

rep = []
rep.append('诗数 %d' % N)
rep.append('TF-IDF 特征 %d 维, SVD 64 维, t-SNE 3D' % X_tfidf.shape[1])
rep.append('explained variance (SVD): %.3f' % svd.explained_variance_ratio_.sum())
for c in clusters:
    rep.append('簇%d size=%d  %s  %s' % (c['id'], c['size'], c['label'], c['form']))
open(os.path.join(BUILD, 'feature_report.txt'), 'w', encoding='utf-8').write('\n'.join(rep))
print('ok')