# -*- coding: utf-8 -*-
"""压缩内联用的 30 幅精选图：单文件里 79% 的体积是它们"""
import os, glob
from PIL import Image
BASE = r'D:\Desktop\走进大诗人'
SRC = os.path.join(BASE, 'web', 'art', 'opt')
tot0 = tot1 = 0
for p in sorted(glob.glob(os.path.join(SRC, '*.jpg'))):
    tot0 += os.path.getsize(p)
    im = Image.open(p).convert('RGB')
    w, h = im.size
    if w > 520:
        im = im.resize((520, int(h * 520 / w)), Image.LANCZOS)
    tmp = p + '.tmp'
    im.save(tmp, 'JPEG', quality=62, optimize=True, progressive=True)
    os.replace(tmp, p)
    tot1 += os.path.getsize(p)
print('精选图 %d 张：%.2f MB → %.2f MB' % (len(glob.glob(os.path.join(SRC, '*.jpg'))), tot0/1048576, tot1/1048576))
