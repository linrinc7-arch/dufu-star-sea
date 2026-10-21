# -*- coding: utf-8 -*-
"""13_errata.py — 名篇正文校勘
按《杜诗详注》通行本改正《全唐诗》库里的形近误字（外部评审列出）。
只在 01_build_corpus.py 之后运行一次；改完重新导出 data.js。
"""
import os, json, sys
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(BASE, 'data', 'build', 'dufu_poems.json')

FIX = [
 ('官因老病休', '官应老病休'),          # 旅夜书怀
 ('野哭几家闻战伐', '野哭千家闻战伐'),    # 阁夜
 ('人事依依漫寂寥', '人事音书漫寂寥'),    # 阁夜
 ('环佩空归月夜魂', '环佩空归夜月魂'),    # 咏怀古迹
 ('歧王宅里寻常见', '岐王宅里寻常见'),    # 江南逢李龟年
 ('寄书长不避', '寄书长不达'),          # 月夜忆舍弟
 ('秋风病欲疏', '秋风病欲苏'),          # 江汉
 ('魂来枫叶青', '魂来枫林青'),          # 梦李白
 ('俱目似愁胡', '侧目似愁胡'),          # 画鹰
 ('茅飞度江洒江郊', '茅飞渡江洒江郊'),    # 茅屋为秋风所破歌
 ('归来倚仗自叹息', '归来倚杖自叹息'),
 ('床床屋漏无干处', '床头屋漏无干处'),
 ('一男附书致', '一男附书至'),          # 石壕吏
 ('出入无完帬', '出入无完裙'),
 ('盘餐市远无兼味', '盘飧市远无兼味'),    # 客至
 ('高标跨苍天', '高标跨苍穹'),          # 同诸公登慈恩寺塔
 ('日宴昆仑丘', '日晏昆仑丘'),
 ('回面北向啼', '回面向北啼'),          # 悲陈陶
 ('汩罗', '汨罗'),                      # 天末忆李白
 ('白手甘契阔', '白首甘契阔'),          # 自京赴奉先县咏怀
 ('贫窭有苍卒', '贫窭有仓卒'),

]

def main():
    d = json.load(open(P, encoding='utf-8'))
    hits = {}
    for p in d:
        body = ''.join(p['lines'])
        newlines = []
        changed = False
        for ln in p['lines']:
            orig = ln
            for a, b in FIX:
                if a in ln: ln = ln.replace(a, b)
            if ln != orig: changed = True
            newlines.append(ln)
        if changed:
            p['lines'] = newlines
            p['body'] = '\n'.join(newlines)
            hits[p['title']] = True
    json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False)
    print('校勘命中 %d 首：%s' % (len(hits), '、'.join(list(hits)[:12])))

if __name__ == '__main__':
    main()
