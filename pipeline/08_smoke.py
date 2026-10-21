# -*- coding: utf-8 -*-
"""08_smoke.py — 交付前的冒烟测试
在 headless Edge 里打开单文件，点一首诗，确认诗卡真的出现。
任何「点星没反应」类的回归都会在这里被拦住。
"""
import os, re, subprocess, sys
from urllib.parse import quote
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
SINGLE = os.path.join(BASE, '杜诗星海.html')
WEB = os.path.join(BASE, 'web')

TAIL = """
setTimeout(function(){
  try{
    var d=window.__DUFU_DEBUG;
    if(!d){ document.title='SMOKE fail: no debug hook'; return; }
    d.selectByTitle('登高');
    setTimeout(function(){
      var on=document.getElementById('card').classList.contains('on');
      var t=document.getElementById('c-title').textContent||'';
      var evd=document.getElementById('c-evd').textContent||'';
      document.title='SMOKE '+((on&&t.indexOf('登高')===0)?'ok':'fail')+' card='+on+' title='+t.slice(0,6)+' evd='+evd.length;
    }, 1200);
  }catch(e){ document.title='SMOKE fail: '+e.message; }
}, 4200);
"""

def run(size='1400,900'):
    src = open(SINGLE, encoding='utf-8').read()
    html = src.replace('</style>', '#load{display:none!important}</style>', 1)
    html = html.replace('</body>', '<script>' + TAIL + '</script></body>')
    p = os.path.join(WEB, '_smoke.html')
    open(p, 'w', encoding='utf-8').write(html)
    cmd = [EDGE, '--headless=new', '--no-sandbox', '--use-angle=swiftshader',
           '--enable-unsafe-swiftshader', '--user-data-dir=' + os.path.join(WEB, '_psmoke'),
           '--window-size=' + size, '--virtual-time-budget=9000', '--dump-dom',
           'file:///' + quote(p.replace('\\', '/'), safe='/:')]
    r = subprocess.run(cmd, capture_output=True, timeout=300, text=True, encoding='utf-8', errors='ignore')
    m = re.search(r'<title>([^<]*)</title>', r.stdout or '')
    return m.group(1) if m else 'no title'

if __name__ == '__main__':
    t = run()
    print('冒烟：', t)
    if not t.startswith('SMOKE ok'):
        sys.exit('冒烟失败：' + t)
