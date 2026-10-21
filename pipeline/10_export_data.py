# -*- coding: utf-8 -*-
"""10_export_data.py — 导出可独立复核的数据（不依赖网页）"""
import os, json, csv

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(BASE, 'data', 'build')
OUT = os.path.join(BASE, '交付', '数据')
os.makedirs(OUT, exist_ok=True)

poems = json.load(open(os.path.join(B, 'dufu_poems.json'), encoding='utf-8'))
sf = json.load(open(os.path.join(B, 'starfield.json'), encoding='utf-8'))
per = json.load(open(os.path.join(B, 'periods.json'), encoding='utf-8'))['periods']
feat = json.load(open(os.path.join(B, 'features.json'), encoding='utf-8'))

PN = ['读书漫游', '困守长安', '陷贼与为官', '漂泊西南', '夔州·湖湘']

# 1) 诗目总表
with open(os.path.join(OUT, 'dufu_poems.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'title', 'form', 'chars', 'lines',
                'period_id', 'period_name', 'dominant_category', 'top_imagery', 'body'])
    for p, s in zip(poems, sf['poems']):
        pid = p['id']
        w.writerow([pid, p['title'], p['form'], p['n_chars'], p['n_lines'],
                    per[pid], PN[per[pid]] if 0 <= per[pid] < 5 else '',
                    s.get('dom', ''), ' '.join(s.get('top', [])[:4]), p['body']])

# 2) 星海坐标
with open(os.path.join(OUT, 'starfield_coords.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'title', 'x', 'y', 'z', 'cluster'])
    for p, s in zip(poems, sf['poems']):
        w.writerow([p['id'], p['title'], s['x'], s['y'], s['z'], s['c']])

# 3) 意象频次（长表）
with open(os.path.join(OUT, 'imagery_counts.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'title', 'word', 'count'])
    for p, c in zip(poems, feat['counts']):
        for word, n in sorted(c.items(), key=lambda x: -x[1]):
            w.writerow([p['id'], p['title'], word, n])

# 4) 星团
with open(os.path.join(OUT, 'clusters.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['cluster_id', 'size', 'label', 'top_words'])
    for c in sf['clusters']:
        w.writerow([c['id'], c['size'], c['label'], ' '.join(c['top_words'])])

readme = '''# 数据说明

本目录是把《杜诗星海》的全部结论导出成可独立复核的表格，不依赖网页也能验证。

## 文件

| 文件 | 行数 | 说明 |
|---|---|---|
| dufu_poems.csv | 1,468 | 诗目总表：体裁、字数、句数、推定时期、主导意象、全文 |
| starfield_coords.csv | 1,468 | 每首诗在三维语义空间中的坐标（t-SNE 结果）与所属星团 |
| imagery_counts.csv | 约 3 万 | 十类意象词典在一首诗中的命中次数（长表，一行一个词） |
| clusters.csv | 8 | 星团汇总：大小、标签、代表意象 |

## 怎么复核

1. **统计类结论**：直接在 dufu_poems.csv 上筛选。例如「五律+七律 = 830 首」：
   筛 form 列等于 五言律诗 / 七言律诗，共 830 行。
2. **意象类结论**：在 imagery_counts.csv 里按 word 聚合。
   例如「月出现 236 次」，sum(count) where word='月'。
3. **空间类结论**：starfield_coords.csv 的 x/y/z 就是网页里星点的坐标。
   任意两点欧氏距离 = 它们在网页上的远近。
4. **时期是推定值**：period_id 由「地理意象直判 + 语义近邻补全」得到，
   不是学界编年。dufu_poems.csv 里 period_name 只是参考。

## 生成方式

全部由 pipeline/ 下的脚本从开源《全唐诗》语料重新算出，可完整复现：

    python pipeline/01_build_corpus.py    # 语料清洗
    python pipeline/02_features.py        # 特征、降维、聚类
    python pipeline/02b_periods.py        # 时期推定
    python pipeline/03_export_web.py      # 导出网页数据
    python pipeline/10_export_data.py     # 导出本目录
'''
open(os.path.join(OUT, 'README.md'), 'w', encoding='utf-8').write(readme)
print('exported ->', OUT)
for fn in sorted(os.listdir(OUT)):
    print('  ', fn, round(os.path.getsize(os.path.join(OUT, fn))/1024, 1), 'KB')
