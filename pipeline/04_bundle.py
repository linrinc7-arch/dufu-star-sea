# -*- coding: utf-8 -*-
"""04_bundle.py — 内联数据与配图，产出可双击运行的单文件"""
import os, base64, glob, json, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(BASE, 'web')
ART = os.path.join(WEB, 'art', 'opt')
OUT = os.path.join(BASE, '杜诗星海.html')

# 构建前先做语法体检：外链数据脚本一旦有语法错误，整块解析会静默失效
for _f in ('analysis.js', 'shiyun.js', 'collation.js', 'gloss.js', 'yiyi.js', 'yiyi2.js'):
    _p = os.path.join(WEB, _f)
    if os.path.exists(_p):
        _r = subprocess.run(['node', '--check', _p], capture_output=True, text=True)
        if _r.returncode != 0:
            sys.exit('语法错误：%s\n%s' % (_f, _r.stderr[:400]))
html = open(os.path.join(WEB, 'index.html'), encoding='utf-8').read()
PRIVATE_USE = [c for c in html if 0xE000 <= ord(c) <= 0xF8FF]
if PRIVATE_USE:
    sys.exit('私用区字符混入正文：%r（会渲染成别的字，等于伪造异文）' % PRIVATE_USE[:5])
data = open(os.path.join(WEB, 'data.js'), encoding='utf-8').read()
shiyun = open(os.path.join(WEB, 'shiyun.js'), encoding='utf-8').read()
skydata = open(os.path.join(WEB, 'sky_data.js'), encoding='utf-8').read()
analysis = open(os.path.join(WEB, 'analysis.js'), encoding='utf-8').read()
collation = open(os.path.join(WEB, 'collation.js'), encoding='utf-8').read()
gloss = open(os.path.join(WEB, 'gloss.js'), encoding='utf-8').read()
yiyi = open(os.path.join(WEB, 'yiyi.js'), encoding='utf-8').read()
yiyi2 = open(os.path.join(WEB, 'yiyi2.js'), encoding='utf-8').read()
sky_js = ''   # 天幕已改为代码程序化生成，不再内联任何图片
sky_js = ''

# 配图 → base64
art = {}
for p in sorted(glob.glob(os.path.join(ART, '*.jpg'))):
    slug = os.path.splitext(os.path.basename(p))[0]
    b64 = base64.b64encode(open(p, 'rb').read()).decode('ascii')
    art[slug] = 'data:image/jpeg;base64,' + b64
art_js = 'window.ART_DATA=' + json.dumps(art) + ';'

guard = """<script>
if(!window.DUFU){document.body.innerHTML='<div style="padding:60px;font:16px/2 serif;color:#e6e0d2">数据未加载，请使用发布版单文件。</div>';}
</script>"""

html = html.replace('<script src="data.js"></script>',
                    '<script>' + sky_js + '</script>' +
                    
                    '<script>' + sky_js + '</script>\n<script>' + data + '</script>\n<script>' + art_js + '</script>\n' + guard)
html = html.replace('<script src="sky_data.js"></script>', '<script>' + skydata + '</script>')
html = html.replace('<script src="shiyun.js"></script>', '<script>' + shiyun + '</script>')
html = html.replace('<script src="analysis.js"></script>', '<script>' + analysis + '</script>')
html = html.replace('<script src="collation.js"></script>', '<script>' + collation + '</script>')
html = html.replace('<script src="gloss.js"></script>', '<script>' + gloss + '</script>')
html = html.replace('<script src="yiyi.js"></script>', '<script>' + yiyi + '</script>')
html = html.replace('<script src="yiyi2.js"></script>', '<script>' + yiyi2 + '</script>')
assert 'window.ANALYSIS' in html
assert 'window.SHIYUN' in html
assert 'window.DUFU=' in html and 'window.ART_DATA=' in html
open(OUT, 'w', encoding='utf-8').write(html)
print('images', len(art), 'size %.2f MB' % (os.path.getsize(OUT)/1048576))
