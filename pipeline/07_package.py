# -*- coding: utf-8 -*-
"""07_package.py — 产出两种交付：单文件版 + 作品/外置图库版，并压缩"""
import os, shutil, subprocess, sys, zipfile, glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(BASE, 'web')
PACK = os.path.join(BASE, '交付')
PY = sys.executable

def run(script):
    r = subprocess.run([PY, os.path.join(BASE, 'pipeline', script)],
                       capture_output=True, text=True, cwd=BASE)
    print(script, '->', (r.stdout or '').strip()[:160])
    if r.returncode: print(r.stderr[:400])

if os.path.isdir(PACK):
    shutil.rmtree(PACK)
os.makedirs(PACK)

run('04_bundle.py')

# A. 单文件版（精选 30 幅内联，展览用）
shutil.copy(os.path.join(BASE, '杜诗星海.html'), os.path.join(PACK, '杜诗星海.html'))

# B. 作品 + 外部图库版（全量按需加载）
FULL = os.path.join(PACK, '杜诗星海_全图版')
os.makedirs(os.path.join(FULL, 'art', 'opt'), exist_ok=True)
os.makedirs(os.path.join(FULL, 'art', 'all'), exist_ok=True)
shutil.copy(os.path.join(WEB, 'index.html'), os.path.join(FULL, 'index.html'))
shutil.copy(os.path.join(WEB, 'data.js'), os.path.join(FULL, 'data.js'))
shutil.copy(os.path.join(WEB, 'shiyun.js'), os.path.join(FULL, 'shiyun.js'))
shutil.copy(os.path.join(WEB, 'analysis.js'), os.path.join(FULL, 'analysis.js'))
shutil.copy(os.path.join(WEB, 'collation.js'), os.path.join(FULL, 'collation.js'))
shutil.copy(os.path.join(WEB, 'gloss.js'), os.path.join(FULL, 'gloss.js'))
shutil.copy(os.path.join(WEB, 'yiyi.js'), os.path.join(FULL, 'yiyi.js'))
shutil.copy(os.path.join(WEB, 'yiyi2.js'), os.path.join(FULL, 'yiyi2.js'))
if os.path.exists(os.path.join(WEB, 'sky.jpg')):
    shutil.copy(os.path.join(WEB, 'sky.jpg'), os.path.join(FULL, 'sky.jpg'))
for p in glob.glob(os.path.join(WEB, 'art', 'opt', '*.jpg')):
    shutil.copy(p, os.path.join(FULL, 'art', 'opt'))
n_all = 0
for p in glob.glob(os.path.join(WEB, 'art', 'all', '*.jpg')):
    shutil.copy(p, os.path.join(FULL, 'art', 'all')); n_all += 1

for f in ['技术方法说明.docx', '经典文本关联说明.docx']:
    src = os.path.join(BASE, 'docs', f)
    if os.path.exists(src): shutil.copy(src, PACK)

readme = """《杜诗星海》交付说明
====================

一、两个版本，按需选择

1) 杜诗星海.html
   单文件，双击即开。内含精选 30 幅配图，断网可用，适合课堂直接演示。

2) 杜诗星海_全图版/
   作品 + 外部图库两件套。双击里面的 index.html 即可。
   配图按需加载：点开哪首诗，才取那一张。目前图库 %d 幅，仍在持续增长。
   注意：这个版本必须保持目录结构完整（index.html 与 art/ 在同一层）。

二、这是什么

杜甫现存一千四百六十八首诗，被放进了同一片天球。
天球的球心是《望岳》——他二十四岁写下的、现存最早的作品之一。
你站在球心向外看：每一颗星是一首诗，离你的远近，就是那首诗离这个起点的远近。

三、怎么操作

  · 拖动：转头看      · 滚轮：拉近拉远（相当于换焦距）
  · 点击任意一颗星：镜头转过去看它，展开诗卡（画 + 竖排诗 + 依据 + 意象标签）
  · 星座连线：只连视野内相邻、且共享意象的星
        把指针停在线上 → 立刻显示这两首是什么、共享哪几个词
  · 卡片里「关系」四个标签：问一次不同的问题
        意象（默认）＝共享区别性意象
        时期        ＝推定同期
        题材        ＝同属一类
        体裁        ＝同一种诗体
  · 左上竖排导航：源起 / 星海 / 生平 / 交游 / 评点
  · 右上检索：输入意象或诗题（如「月」「战」），相关星辰亮起
  · 底部「着色」：在意象（主题）与时期（一生）之间切换
  · 底部「视角」：天球（站在球心）/ 星云（在球外看整团）

四、文件清单
  杜诗星海.html              单文件版（主件）
  杜诗星海_全图版/           作品 + 外部图库
  技术方法说明.docx          500—800 字
  经典文本关联说明.docx      300—500 字

五、数据
  语料：开源《全唐诗》库，杜甫 1,468 首
  配图：宋画风格生成，精选 %d 幅 + 全量 %d 幅
  天幕照片：ESO / S. Brunier 全天银河全景（eso0932a），CC BY 4.0
           已重投影到《望岳》的球心视角并调色
  诗云：pipeline/11_shiyun.py 生成的 20,000 首机器伪诗（只用杜甫自己的字）
""" % (n_all, 30, n_all)
open(os.path.join(PACK, '使用说明.txt'), 'w', encoding='utf-8').write(readme)

zpath = os.path.join(BASE, '杜诗星海_交付.zip')
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(PACK):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, PACK)
            z.write(full, os.path.join('杜诗星海', rel))

run('10_export_data.py')

print('package done. 全量图库 %d 幅' % n_all)
print('zip %.2f MB' % (os.path.getsize(zpath)/1048576))

# 交付前的冒烟：点首诗，确认诗卡真的出现（防「点星没反应」类回归）
import subprocess as _sp, sys as _sys
_r = _sp.run([_sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), '08_smoke.py')],
             capture_output=True, text=True, encoding='utf-8', errors='ignore')
print('冒烟：', (_r.stdout or '').strip()[-80:])
if _r.returncode != 0:
    _sys.exit('冒烟未通过，交付中止')

# 交付一致性：关键代码段必须与源码逐字节一致（防止「源码改了、交付没重打」）
import hashlib as _h
def _block(path, a, b):
    _s = open(path, encoding='utf-8').read()
    return _s[_s.index(a):_s.index(b)]
_src = os.path.join(WEB, 'index.html')
_dst = os.path.join(BASE, '杜诗星海.html')
try:
    _a = _block(_src, 'function audInit(', 'function audCue(')
    _b = _block(_dst, 'function audInit(', 'function audCue(')
    if _h.sha1(_a.encode()).hexdigest() != _h.sha1(_b.encode()).hexdigest():
        _sys.exit('交付与源码不一致：声音段（源码改了但没重打）')
    print('一致性：交付与源码一致（声音段 %d 字符）' % len(_a))
except ValueError:
    _sys.exit('交付与源码不一致：找不到声音段')
