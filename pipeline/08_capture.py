# -*- coding: utf-8 -*-
"""08_capture.py — 生成每轮迭代的证据截图"""
import os, subprocess, sys, shutil, glob
from urllib.parse import quote

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(BASE, 'web')
OUT = os.path.join(BASE, '迭代', '截图')
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
TMP = WEB   # 必须放在 web/ 根目录，否则 data.js 相对路径失效

R = sys.argv[1] if len(sys.argv) > 1 else '00'
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

src = open(os.path.join(WEB, 'index.html'), encoding='utf-8').read()
NOANIM = ('#load{display:none!important}#card{transition:none!important}'
          '#panel{transition:none!important}'
          '.reveal{opacity:1!important;transform:none!important;filter:none!important}'
          '.split-ch{opacity:1!important;transform:none!important;filter:none!important}'
          '.fnet line,.fnet .fnode{opacity:1!important;animation:none!important}')

def page(name, tail='', extra=''):
    html = src.replace('</style>', NOANIM + extra + '</style>', 1)
    if tail:
        html = html.replace('</body>', '<script>%s</script></body>' % tail)
    p = os.path.join(TMP, '_cap_' + name + '.html')
    open(p, 'w', encoding='utf-8').write(html)
    return p

SHOTS = [
 ('star',        '', ''),
 ('period',      "document.querySelectorAll('#mode .m')[1].click();", ''),
 ('card',        'window.__DUFU_DEBUG.selectAndFly("登高");', ''),
 ('search',      'var q=document.getElementById("q");q.value="月";q.dispatchEvent(new Event("input"));', ''),
 ('life',        'window.__DUFU_DEBUG.openPanel("life");', ''),
 ('friends',     'window.__DUFU_DEBUG.openPanel("friends");', ''),
 ('crit',        'window.__DUFU_DEBUG.openPanel("crit");', ''),
 ('about',       'window.__DUFU_DEBUG.openPanel("about");', ''),
]

def shot(name, tail, extra, w=1600, h=900):
    p = page('cap_'+name, tail, extra)
    prof = os.path.join(TMP, '_prof_'+name)
    out = os.path.join(OUT, 'R%s_%s.png' % (R, name))
    cmd = [EDGE, '--headless=new', '--no-sandbox', '--disable-gpu',
           '--user-data-dir='+prof, '--window-size=%d,%d' % (w,h),
           '--screenshot='+out, 'file:///' + quote(p.replace('\\','/'), safe='/:')]
    try:
        subprocess.run(cmd, capture_output=True, timeout=60)
    except Exception as e:
        print('timeout', name)
    if os.path.exists(out):
        print('%-9s %6.1f KB' % (name, os.path.getsize(out)/1024))
    else:
        print('%-9s FAIL' % name)

for n, t, e in SHOTS:
    shot(n, t, e)

for f in glob.glob(os.path.join(WEB, '_cap_*.html')):
    os.remove(f)
for d in glob.glob(os.path.join(WEB, '_prof_*')):
    shutil.rmtree(d, ignore_errors=True)
print('done ->', OUT)
