# -*- coding: utf-8 -*-
"""14_periods_align.py — 用人工解析的系年回写时期标签，消除「pd 与解析年冲突」

解析（analysis.js）里的年份是人工核过的；时期标签（pd）是模型推的。
两者冲突时，以人工为准。
"""
import os, re, json, sys
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(BASE, 'web', 'analysis.js')
P = os.path.join(BASE, 'data', 'build', 'dufu_poems.json')

BOUNDS = [(731, 745, 0), (746, 755, 1), (756, 759, 2), (760, 765, 3), (766, 770, 4)]

def year_of(text):
    m = re.search(r'(\d{3})\s*年', text or '')
    if not m: return None
    y = int(m.group(1))
    return y if 700 <= y <= 780 else None

def period_of(y):
    for lo, hi, i in BOUNDS:
        if lo <= y <= hi: return i
    return None

def main():
    src = open(A, encoding='utf-8').read()
    entries = re.findall(r'\"([^\"]+)\":\s*\{([^{}]*)\}', src)
    want = {}
    for title, body in entries:
        my = re.search(r'y:\s*\"([^\"]*)\"', body)
        mi = re.search(r'id:\s*(\d+)', body)
        y = year_of(my.group(1)) if my else None
        if y is None: continue
        want[title] = (y, int(mi.group(1)) if mi else None)
    poems = json.load(open(P, encoding='utf-8'))
    by_id = {p['id']: p for p in poems}
    fixed, conflicts = 0, []
    for title, (y, pid) in want.items():
        pi = period_of(y)
        if pi is None: continue
        cands = [p for p in poems if p['title'] == title]
        if pid is not None:
            cands = [p for p in cands if p['id'] == pid]
        for p in cands:
            if p.get('pd') != pi:
                conflicts.append((title, p.get('pd'), pi, y))
                p['pd'] = pi
                fixed += 1
    json.dump(poems, open(P, 'w', encoding='utf-8'), ensure_ascii=False)
    print('解析条数 %d，改写时期 %d 处' % (len(want), fixed))
    for t, old, new, y in conflicts[:8]:
        print('  %s: %s → %s（%d）' % (t, old, new, y))

if __name__ == '__main__':
    main()
