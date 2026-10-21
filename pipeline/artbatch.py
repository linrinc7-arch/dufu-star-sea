# -*- coding: utf-8 -*-
"""artbatch.py — 用 wb_image.py CLI 批量出图（比 MCP 快 15 倍：约 20-30 秒/张）

用法: python pipeline/artbatch.py <worker> [轮数]
每轮领 4 张，逐张生成并入库，直到队列领完或达到轮数上限。
"""
import os, sys, json, subprocess, time
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = r'D:\Desktop\开放空间\wb_image.py'
AQ = os.path.join(BASE, 'pipeline', 'artqueue.py')
PY = sys.executable

# wb_image.py 的 stdout 是 GBK（Windows 控制台默认），必须强制子进程输出 UTF-8，
# 否则中文路径会被解坏、finish 会报 src missing。
ENV = dict(os.environ)
ENV['PYTHONIOENCODING'] = 'utf-8'
ENV['PYTHONUTF8'] = '1'

def run(args, timeout=420, **kw):
    kw.setdefault('env', ENV)
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                          encoding='utf-8', errors='replace', **kw)

def main():
    worker = sys.argv[1] if len(sys.argv) > 1 else 'w-b1'
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    out = os.path.join(BASE, 'web', 'art', 'tmp', worker)
    os.makedirs(out, exist_ok=True)
    claim_path = os.path.join(BASE, 'data', 'claims', worker + '.json')
    total = 0
    for r in range(rounds):
        run([PY, AQ, 'next', '4', worker])
        try:
            items = json.load(open(claim_path, encoding='utf-8'))
        except Exception:
            time.sleep(5); continue
        if not items:
            print('queue empty', flush=True); break
        for it in items:
            pid = it['id']; prompt = it.get('prompt') or it.get('title') or ''
            try:
                p = run([PY, CLI, '--prompt', prompt, '--size', '1024x1536',
                         '--out', out, '--json'], timeout=420)
            except subprocess.TimeoutExpired:
                run([PY, AQ, 'fail', str(pid), 'cli-timeout']); continue
            j = None
            for line in (p.stdout or '').strip().split('\n')[::-1]:
                line = line.strip()
                if line.startswith('{'):
                    try: j = json.loads(line); break
                    except Exception: pass
            files = (j or {}).get('files') or []
            if not files:
                run([PY, AQ, 'fail', str(pid), 'cli-nofile']); continue
            run([PY, AQ, 'finish', str(pid), files[0]])
            total += 1
            print('%s %d ok total=%d' % (worker, pid, total), flush=True)
    print('done', worker, total, flush=True)

if __name__ == '__main__':
    main()
