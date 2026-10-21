# -*- coding: utf-8 -*-
"""artqueue.py — 全量配图生成队列（供多个子代理并行领任务）

用法：
  python pipeline/artqueue.py init
  python pipeline/artqueue.py stats
  python pipeline/artqueue.py next 10 <worker>
  python pipeline/artqueue.py finish <id> <生成文件路径>
  python pipeline/artqueue.py fail <id> <原因>
"""
import os, sys, json, time, random

# 强制 UTF-8 输出：Windows 控制台默认 GBK，会把中文提示词打成乱码
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(BASE, 'data', 'build')
Q = os.path.join(BASE, 'data', 'art_queue.json')
LOCK = Q + '.lock'
ALL = os.path.join(BASE, 'web', 'art', 'all')

STYLE = ('中国宋代水墨山水画，竖幅构图。墨色为主，焦墨与淡墨层次分明，赭石与极淡的金色点缀，'
         '宣纸肌理与飞白笔触，大面积留白，人物为远景小像不画面部，画面中不出现任何文字、印章、签名。')
PERIODS = ['读书漫游（少年裘马）','困守长安（残杯冷炙）','陷贼与为官（国破山河在）',
           '漂泊西南（万里悲秋）','夔州·湖湘（老病孤舟）']


# —— 构图差异化：同一套风格下，按 id 稳定地注入不同的画面元素，
#    否则战乱类题材会反复出现"将军骑马+火城+军旗"这类近似构图。
VARIANTS = [
 '江边孤舟，一人在船头望北', '雪后空山，只余一行脚印', '驿道黄昏，瘦马与断旗',
 '残破的城楼上升起一柱轻烟', '月下的沙洲与成排的芦苇', '雨中茅屋，屋漏处有人仰面',
 '山寺半隐于云，钟不见而声', '石壕村口的野草与半扇门', '渡口无人，只有一根系船的桩',
 '秋江枫叶落在水面', '孤雁掠过山脊', '荒祠里的一盏长明灯',
 '田埂上两个模糊的小人', '兵车辙痕里的一只鞋', '城墙下的野花开在箭孔边',
 '茅屋顶上蹲着一只鸟', '寒夜里的一堆余烬', '远山如黛，近处一株枯树',
 '栈道贴着绝壁，云雾在脚下', '暮色里的炊烟', '一只船停在中流',
 '溪水绕过一块大石', '藤蔓垂在断崖上', '半塌的桥与涉水的人',
]
def variant_for(pid):
    import random as _r
    _r.seed(int(pid) * 7919 + 13)
    return _r.choice(VARIANTS)

def load():
    return json.load(open(Q, encoding='utf-8'))

def save(d):
    tmp = Q + '.tmp'
    json.dump(d, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
    os.replace(tmp, Q)

def locked(fn, timeout=30):
    t0 = time.time()
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd); break
        except FileExistsError:
            if time.time() - t0 > timeout:
                try: os.remove(LOCK)
                except Exception: pass
            time.sleep(0.15)
    try:
        return fn()
    finally:
        try: os.remove(LOCK)
        except Exception: pass

def cmd_init():
    poems = json.load(open(os.path.join(B, 'dufu_poems.json'), encoding='utf-8'))
    sf = json.load(open(os.path.join(B, 'starfield.json'), encoding='utf-8'))
    per = json.load(open(os.path.join(B, 'periods.json'), encoding='utf-8'))['periods']
    items = []
    for p, s in zip(poems, sf['poems']):
        pid = p['id']
        imgs = [w for w in (s.get('top') or []) if len(w) >= 1][:3]
        first = (p['lines'][0] if p['lines'] else '')[:14]
        per_name = PERIODS[per[pid]] if 0 <= per[pid] < 5 else ''
        prompt = '《%s》诗意：画面以%s为主，气象取「%s」之意。%s。%s' % (
            p['title'], '、'.join(imgs) if imgs else '山川', first, per_name, STYLE)
        items.append({'id': pid, 'title': p['title'], 'prompt': prompt,
                      'status': 'pending', 'worker': '', 'ts': 0})
    save({'items': items, 'created': time.strftime('%Y-%m-%d %H:%M:%S')})
    os.makedirs(ALL, exist_ok=True)
    print('queue built:', len(items))

def cmd_stats():
    d = load(); c = {}
    for it in d['items']: c[it['status']] = c.get(it['status'], 0) + 1
    have = len([f for f in os.listdir(ALL)]) if os.path.isdir(ALL) else 0
    print(json.dumps({'counts': c, 'total': len(d['items']), 'files': have}, ensure_ascii=False))

def cmd_next(n, worker):
    """领任务。同时把结果写到 data/claims/<worker>.json，
    避免 Windows 控制台编码把中文提示词打成乱码。
    若该 worker 还有未完成的认领，先把它们交回去（不重复领新的）。
    """
    n = int(n)
    claims_dir = os.path.join(BASE, 'data', 'claims')
    os.makedirs(claims_dir, exist_ok=True)

    def go():
        d = load()
        now = time.time()
        # 回收超时未完成的认领（>20 分钟）
        for it in d['items']:
            if it['status'] == 'claimed' and now - it['ts'] > 1200:
                it['status'] = 'pending'; it['worker'] = ''
        # 该 worker 自己的未完成认领，优先返还
        mine = [it for it in d['items'] if it['status'] == 'claimed' and it['worker'] == worker]
        if mine:
            return mine[:n]
        picked = [it for it in d['items'] if it['status'] == 'pending'][:n]
        for it in picked:
            it['status'] = 'claimed'; it['worker'] = worker; it['ts'] = now
        save(d)
        return picked

    picked = locked(go)
    payload = [{'id': x['id'], 'title': x['title'],
                'prompt': x['prompt'] + ' 构图元素：' + variant_for(x['id']) +
                '。严禁出现：人头特写、骷髅、鬼面、巨幅人像、文字与印章。'
                '建筑一律为中国古代形制（木构、夯土、城楼、飞檐、石阶），不得出现欧洲城堡、哥特建筑。'} for x in picked]
    out = os.path.join(claims_dir, '%s.json' % worker)
    json.dump(payload, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.stdout.write(json.dumps({'ok': True, 'count': len(picked), 'file': out}, ensure_ascii=False) + '\n')
    sys.stdout.flush()

def cmd_finish(pid, src):
    from PIL import Image
    pid = int(pid)
    os.makedirs(ALL, exist_ok=True)
    if not os.path.exists(src):
        print(json.dumps({'ok': False, 'err': 'src missing'})); return
    im = Image.open(src).convert('RGB')
    w, h = im.size
    tw = 768
    if w > tw: im = im.resize((tw, int(h * tw / w)), Image.LANCZOS)
    out = os.path.join(ALL, '%04d.jpg' % pid)
    im.save(out, 'JPEG', quality=80, optimize=True, progressive=True)
    try: os.remove(src)
    except Exception: pass
    def go():
        d = load()
        for it in d['items']:
            if it['id'] == pid:
                it['status'] = 'done'; it['ts'] = time.time()
        save(d)
    locked(go)
    print(json.dumps({'ok': True, 'out': out, 'kb': os.path.getsize(out)//1024}))

def cmd_fail(pid, reason=''):
    pid = int(pid)
    def go():
        d = load()
        for it in d['items']:
            if it['id'] == pid:
                it['status'] = 'failed'; it['worker'] = reason[:60]; it['ts'] = time.time()
        save(d)
    locked(go)
    print(json.dumps({'ok': True}))

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(0)
    if a[0] == 'init': cmd_init()
    elif a[0] in ('stats', 'status'): cmd_stats()
    elif a[0] == 'next': cmd_next(a[1], a[2] if len(a) > 2 else 'worker')
    elif a[0] == 'finish': cmd_finish(a[1], a[2])
    elif a[0] == 'fail': cmd_fail(a[1], a[2] if len(a) > 2 else '')
