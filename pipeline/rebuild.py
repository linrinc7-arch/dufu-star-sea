# -*- coding: utf-8 -*-
"""rebuild.py — 一键重建：从原始语料到完整交付包"""
import os, subprocess, sys, time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

STEPS = [
    ('01_build_corpus.py', '语料清洗：筛杜甫 / 去重 / 繁简与异体字 / 体裁判定'),
    ('02_features.py',     '特征：意象词典 + TF-IDF + SVD + t-SNE + 聚类'),
    ('02b_periods.py',     '时期推定：地理意象直判 + 语义近邻补全'),
    ('03_export_web.py',   '导出网页数据 data.js'),
    ('04_bundle.py',       '打包单文件（内联数据与精选配图）'),
    ('06_make_docs.py',    '生成两份说明的 DOCX'),
    ('07_package.py',      '产出交付目录与压缩包'),
    ('10_export_data.py',  '导出可复核的数据表'),
]

def main():
    t0 = time.time()
    for i, (script, desc) in enumerate(STEPS, 1):
        path = os.path.join(BASE, 'pipeline', script)
        if not os.path.exists(path):
            print('[%d/%d] 跳过（不存在） %s' % (i, len(STEPS), script)); continue
        print('[%d/%d] %s — %s' % (i, len(STEPS), desc, script))
        r = subprocess.run([PY, path], cwd=BASE, capture_output=True, text=True)
        if r.returncode != 0:
            print('  失败：', (r.stderr or r.stdout)[-500:])
            sys.exit(1)
        out = (r.stdout or '').strip().split('\n')[-1][:100]
        if out: print('  ', out)
    print('完成，用时 %.1f 秒' % (time.time() - t0))

if __name__ == '__main__':
    main()
