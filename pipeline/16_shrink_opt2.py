# -*- coding: utf-8 -*-
import os, glob
from PIL import Image
BASE = r'D:\Desktop\走进大诗人'
SRC = os.path.join(BASE, 'web', 'art', 'opt')
t0 = t1 = 0
for p in sorted(glob.glob(os.path.join(SRC, '*.jpg'))):
    t0 += os.path.getsize(p)
    im = Image.open(p).convert('RGB')
    w, h = im.size
    if w > 460:
        im = im.resize((460, int(h * 460 / w)), Image.LANCZOS)
    tmp = p + '.tmp'
    im.save(tmp, 'JPEG', quality=56, optimize=True, progressive=True)
    os.replace(tmp, p)
    t1 += os.path.getsize(p)
print('%.2f MB → %.2f MB' % (t0/1048576, t1/1048576))
