# -*- coding: utf-8 -*-
"""07_package.py — 产出提交目录「交付/」并打包 zip

交付目录按作业《走近大诗人》期末作业·题目二 方向C 的提交要求组织：
  作品（可运行文件） / 技术方法说明（500—800字） / 经典文本关联说明（300—500字）
  数据说明（可复核的表格）

  python pipeline/07_package.py          # 精简版：只出单文件作品（约 12 MB）
  python pipeline/07_package.py --full   # 含完整图库版：附 1,468 幅配图（约 290 MB）
"""
import os, shutil, subprocess, sys, zipfile, glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(BASE, 'web')
DOCS = os.path.join(BASE, 'docs')
PACK = os.path.join(BASE, '交付')
FULL = os.path.join(PACK, '05_全图库版')
PY = sys.executable
WITH_FULL = '--full' in sys.argv

def run(script):
    r = subprocess.run([PY, os.path.join(BASE, 'pipeline', script)],
                       capture_output=True, text=True, cwd=BASE, encoding='utf-8', errors='ignore')
    print(script, '->', (r.stdout or '').strip()[:160])
    if r.returncode:
        print((r.stderr or '')[:600])

# 清空上一版，整目录重出（Word 打开着 docx 时删不掉，退化为就地覆盖）
if os.path.isdir(PACK):
    try:
        shutil.rmtree(PACK)
    except PermissionError as e:
        print('有文件被占用（多半是 Word 开着 docx），改为就地更新：', e)
os.makedirs(PACK, exist_ok=True)

# 1) 单文件版
run('04_bundle.py')
shutil.copy(os.path.join(BASE, '杜诗星海.html'), os.path.join(PACK, '01_作品_杜诗星海.html'))

# 2) 两份说明（docx）
for src, dst in (('技术方法说明.docx', '02_技术方法说明.docx'),
                 ('经典文本关联说明.docx', '03_经典文本关联说明.docx')):
    s = os.path.join(DOCS, src)
    if os.path.exists(s):
        shutil.copy(s, os.path.join(PACK, dst))
    else:
        print('缺文档：', src)

# 3) 数据说明（10_export_data.py 直接写到这里）
run('10_export_data.py')

# 4) 交付清单
lst = os.path.join(DOCS, '交付清单.md')
if os.path.exists(lst):
    shutil.copy(lst, os.path.join(PACK, '00_交付清单.md'))

# 5) 完整图库版（--full）：作品 + 外置图库，保持目录结构
n_all = len(glob.glob(os.path.join(WEB, 'art', 'all', '*.jpg')))
if WITH_FULL:
    print('拷图库 %d 幅（约 280 MB，要等一会儿）…' % n_all)
    os.makedirs(os.path.join(FULL, 'art'), exist_ok=True)
    shutil.copytree(os.path.join(WEB, 'art', 'opt'), os.path.join(FULL, 'art', 'opt'), dirs_exist_ok=True)
    shutil.copytree(os.path.join(WEB, 'art', 'all'), os.path.join(FULL, 'art', 'all'), dirs_exist_ok=True)
    shutil.copy(os.path.join(WEB, 'index.html'), os.path.join(FULL, 'index.html'))
    for f in ('data.js', 'shiyun.js', 'analysis.js', 'collation.js', 'gloss.js', 'gloss2.js',
              'yiyi.js', 'yiyi2.js', 'annot.js', 'imagery.js', 'life.js', 'life_data.js',
              'shiyun_good.js', 'sky_data.js'):
        s = os.path.join(WEB, f)
        if os.path.exists(s):
            shutil.copy(s, os.path.join(FULL, f))
    print('图库版就位：', FULL)

# 6) 使用说明
readme = """《杜诗星海》使用说明
====================

一、双击哪个文件

  01_作品_杜诗星海.html       ← 主件。双击即开，断网可用。
                              内置 31 幅精选配图与全部注释数据，单文件可独立运行，但不含全量配图。
                              只想看作品、不想折腾的话，只打开这一个文件就够。

  %s

二、这是什么

  本项目收录的一千四百六十八首杜甫诗，被放进同一片天球。
  球心是《望岳》——他二十四岁写的、现存最早的作品之一；站在球心向外看，
  每一颗星是一首诗，离你的远近，就是那首诗离这个起点的远近。
  旋臂之间那些暗到几乎看不见的点，是机器用杜甫自己的字拼出来的两万首伪诗：
  真诗是亮的，可能的诗是暗的，但都在天上。

请先完整解压 ZIP；使用 Git 克隆时先执行 git lfs pull，确认配图和文档已下载。

三、怎么操作

  · 拖动：巡游（转头看）        · 滚轮：拉近拉远（换焦距）
  · 点击任意一颗星：镜头转过去，展开诗卡（配图 + 竖排诗 + 注释入口 + 依据 + 意象标签）
  · 检索：按 / 键（或 Ctrl+K）唤出右上角检索框，输入「月」「战」「秋」，
          相关星辰整片亮起；空格分隔可多选（「月 秋」= 含任一词的亮）
          回车直接跳到最匹配的那一首
  · 底部「检索 · 意象 / 情感 / 体裁 / 时期 / 题材」：五个维度筛选，每类下是具体词条
  · 底部「着色」：在意象（主题）与时期（一生）之间切换
  · 左上竖排导航：源起 / 星海 / 生平 / 交游 / 评点 / 诗云
  · 诗卡里点「全屏」或长诗下方的「点这里整屏读」：左栏诗、右栏注，
    宽屏时右侧另挂一张放大的配图（图版）；窄屏时图版改为置顶横幅
  · 快捷键：/ 检索 · F 全屏 · H 静观（收掉所有界面）· Esc 退出

四、数据

  语料：开源《全唐诗》，筛出杜甫 1,489 条，清洗、去重后收录 1,468 首，尚不能视为全部完成学术校勘
  注释：1,468 首全配字注 / 今译 / 逐联串讲 / 赏析 / 写作背景 / 名句
  配图：按诗题与意象生成的水墨风插图，非古画原件；主件内嵌 31 幅，图库版 1,468 幅
  诗云：pipeline/11_shiyun.py 以杜甫用字做二阶马尔可夫链生成的 20,000 首伪诗
  可复核的表格见 04_数据说明/（诗目、坐标、意象频次、星团）
""" % ('  05_全图库版/index.html     ← 含 1,468 幅配图的版本。双击里面的 index.html 即可。\n'
       '                              注意：必须保持文件夹完整（index.html 与 art/ 在同一层），\n'
       '                              单独把 html 拷走会没有图。' if WITH_FULL else
       '  （本次交付未附完整图库版；需要时在项目里跑 python pipeline/07_package.py --full）')
open(os.path.join(PACK, '使用说明.txt'), 'w', encoding='utf-8').write(readme)

# 7) 打包（jpg 直接存储，不再压缩——本来就不压得动）
zpath = os.path.join(BASE, '杜诗星海_交付.zip')
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(PACK):
        for f in files:
            if f.startswith('~$') or f in ('.DS_Store', 'Thumbs.db', 'desktop.ini'):
                continue          # Word 锁文件 / 系统缩略文件不进包
            full = os.path.join(root, f)
            arc = os.path.join('杜诗星海', os.path.relpath(full, PACK))
            ct = zipfile.ZIP_STORED if f.lower().endswith(('.jpg', '.jpeg', '.png')) else zipfile.ZIP_DEFLATED
            z.write(full, arc, compress_type=ct)

print('交付目录 %d 个文件；zip %.1f MB（图库 %d 幅，%s）' % (
    sum(len(f) for _, _, f in os.walk(PACK)),
    os.path.getsize(zpath) / 1048576, n_all, '含图库版' if WITH_FULL else '不含图库版'))
