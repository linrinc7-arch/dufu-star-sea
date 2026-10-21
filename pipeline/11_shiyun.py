# -*- coding: utf-8 -*-
"""11_shiyun.py — 诗云 · 白噪音

用杜甫自己的用字，生成 2 万首"读得通、想不通"的伪诗。

做法（全部可复现）：
  1. 从 1,468 首杜诗的正文里切出五言/七言句，分别统计：
     单字频率、双字（bigram）、三字上下文（二阶马尔可夫）、句尾用字。
  2. 生成时按句长固定 5 或 7 字；每一字由前两字决定，但给罕见上下文留退路
     （上下文 / 双字 / 单字频率按权重插值），因此不会成句抄回原诗。
  3. 每句以真实的句首双字起、真实的句尾双字收。五言、七言的句尾分别统计，
     所以它"像"押韵；但机器从不检查两句是否同韵——它只是在复读统计。
  4. 四句一首，句与句之间没有任何连贯性：这正是作品要的东西——
     组合可以穷尽，意义为零。

用法：
    python pipeline/11_shiyun.py                  # 全量 20,000 首 + 预览页
    python pipeline/11_shiyun.py --n 240 --show 12  # 快速看样本
"""

import argparse
import bisect
import json
import math
import os
import random
import sys
import time
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "data", "build", "dufu_poems.json")
DST = os.path.join(BASE, "data", "build", "shiyun.json")
DEMO = os.path.join(BASE, "web", "_shiyun_demo.html")

SEED = 20261020
N_POEMS = 20000
LINES_PER_POEM = 4
WU_SHARE = 0.80   # 五言/七言的首数比例，与语料中两种句子的比例一致

# ---- 采样参数：决定"像诗"与"不成诗"之间的那条线 -------------------------
K3 = 0.7          # 二阶上下文的可信度折扣：出现 1 次也给 59% 的权重
W2 = 0.72         # 上下文让位后，双字统计占剩下的比例（其余给单字）
TRIES = 12        # 同字约束下的重抽次数


def is_han(ch):
    return "\u4e00" <= ch <= "\u9fff"


def make_pack(counter):
    """把 Counter 压成 (字数组, 累积权重, 总权重)，用 bisect 采样。"""
    chars, cums, acc = [], [], 0
    for ch, n in counter.items():
        acc += n
        chars.append(ch)
        cums.append(acc)
    return chars, cums, acc


def pick(pack):
    chars, cums, total = pack
    return chars[bisect.bisect_right(cums, random.random() * total)]


class FormModel:
    """一种句长（5 或 7）的统计模型。"""

    def __init__(self, lines):
        self.uni = Counter()
        self.end = Counter()
        self.start2 = Counter()   # 句首双字：让一句诗起得像诗
        self.end2 = Counter()     # 句尾双字：让一句诗收得像诗（但它不懂韵）
        self.bi = {}    # a -> [Counter(b), total]
        self.tri = {}   # (a,b) -> [Counter(c), total]
        self._bi_pack = {}
        self._tri_pack = {}

        for ln in lines:
            self.uni.update(ln)
            self.end[ln[-1]] += 1
            self.start2[ln[:2]] += 1
            self.end2[ln[-2:]] += 1
            for i in range(len(ln) - 1):
                e = self.bi.get(ln[i])
                if e is None:
                    e = self.bi[ln[i]] = [Counter(), 0]
                e[0][ln[i + 1]] += 1
                e[1] += 1
            for i in range(len(ln) - 2):
                k = ln[i:i + 2]
                e = self.tri.get(k)
                if e is None:
                    e = self.tri[k] = [Counter(), 0]
                e[0][ln[i + 2]] += 1
                e[1] += 1

        self.uni_pack = make_pack(self.uni)
        self.end_pack = make_pack(self.end)
        self.start2_pack = make_pack(self.start2)
        self.end2_pack = make_pack(self.end2)

    # -- 三种退路 --------------------------------------------------------
    def _bi(self, a):
        p = self._bi_pack.get(a)
        if p is None:
            e = self.bi.get(a)
            p = make_pack(e[0]) if e else self.uni_pack
            self._bi_pack[a] = p
        return p

    def _tri(self, key):
        p = self._tri_pack.get(key)
        if p is None:
            p = make_pack(self.tri[key][0])
            self._tri_pack[key] = p
        return p

    def _step(self, a, b):
        """二阶马尔可夫：P(c | a,b) 与双字、单字频率插值。"""
        if b is None:
            return pick(self.uni_pack)
        key = a + b
        e = self.tri.get(key)
        w3 = 0.0
        if e is not None:
            w3 = e[1] / (e[1] + K3)
        r = random.random()
        if r < w3:
            return pick(self._tri(key))
        if r < w3 + (1.0 - w3) * W2:
            return pick(self._bi(b))
        return pick(self.uni_pack)

    # -- 一整句 ----------------------------------------------------------
    def _pair(self, pack, out, seen):
        """成对追加两个字，返回是否成功。同字最多两次、不出现三连。"""
        for _ in range(TRIES):
            p = pick(pack)
            a, b = p[0], p[1]
            if seen[a] + 1 > 2 or seen[b] + 1 + (1 if a == b else 0) > 2:
                continue
            if len(out) >= 2 and out[-1] == a and out[-2] == a:
                continue
            out.append(a); seen[a] += 1
            out.append(b); seen[b] += 1
            return True
        return False

    def make_line(self, L):
        out = []
        seen = Counter()

        def guard(ch):
            if seen[ch] >= 2:
                return False                      # 同一句里同一个字最多两次
            if len(out) >= 2 and out[-1] == ch and out[-2] == ch:
                return False                      # 不出现三连字
            return True

        def draw(fn):
            ch = None
            for _ in range(TRIES):
                ch = fn()
                if guard(ch):
                    return ch
            return ch

        # 起句两字：取自真实的句首双字（"江上""三月""远山"）
        if not self._pair(self.start2_pack, out, seen):
            while len(out) < 2:
                ch = draw(lambda: pick(self.uni_pack))
                out.append(ch); seen[ch] += 1

        # 中间字：二阶马尔可夫 P(c | a,b)，向双字、单字退让
        while len(out) < L - 2:
            ch = draw(lambda: self._step(out[-2], out[-1]))
            out.append(ch); seen[ch] += 1

        # 收句两字：取自真实的句尾双字。它因此"像"押韵，
        # 但机器从不检查两句是否同韵——它只是在复读句尾统计。
        if not self._pair(self.end2_pack, out, seen):
            while len(out) < L:
                ch = draw(lambda: pick(self.end_pack))
                out.append(ch); seen[ch] += 1

        while len(out) < L:                       # 极端情况兜底
            ch = draw(lambda: self._step(out[-2], out[-1]))
            out.append(ch); seen[ch] += 1

        return "".join(out)


def load_corpus():
    poems = json.load(open(SRC, encoding="utf-8"))
    lines = {5: [], 7: []}
    dropped = 0
    for p in poems:
        for ln in p["lines"]:
            if len(ln) in (5, 7):
                if all(is_han(c) for c in ln):
                    lines[len(ln)].append(ln)
                else:
                    dropped += 1
    return poems, lines, dropped


def build_demo(meta, items):
    raw = "\n".join("|".join(it["lines"]) for it in items)
    html = DEMO_TEMPLATE
    html = html.replace("__DATA__", json.dumps(raw, ensure_ascii=False))
    html = html.replace("__META__", json.dumps(meta, ensure_ascii=False))
    open(DEMO, "w", encoding="utf-8", newline="\n").write(html)
    return len(html.encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=N_POEMS)
    ap.add_argument("--show", type=int, default=0, help="打印几首样本")
    ap.add_argument("--no-demo", action="store_true")
    args = ap.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    t0 = time.time()
    poems, lines, dropped = load_corpus()
    m5 = FormModel(lines[5])
    m7 = FormModel(lines[7])
    models = {5: m5, 7: m7}
    src_vocab = set(m5.uni) | set(m7.uni)

    real_lines = set(lines[5]) | set(lines[7])
    real4 = set()                 # 真实诗里的所有四字片段，用来量"半句重合"
    for ln in real_lines:
        for j in range(len(ln) - 3):
            real4.add(ln[j:j + 4])
    random.seed(SEED)

    items = []
    dup_lines = 0
    near_lines = 0
    same_end = 0          # 四句里第 2、4 句末字相同的首数（机器"押韵"的假象）
    used = set()
    n5 = n7 = 0

    for i in range(args.n):
        L = 5 if random.random() < WU_SHARE else 7
        model = models[L]
        ls = []
        for _ in range(LINES_PER_POEM):
            ln = model.make_line(L)
            for _try in range(3):
                if ln not in ls:
                    break
                ln = model.make_line(L)
            ls.append(ln)
        for ln in ls:
            if ln in real_lines:
                dup_lines += 1
            if any(ln[j:j + 4] in real4 for j in range(len(ln) - 3)):
                near_lines += 1
            used.update(ln)
        if ls[1][-1] == ls[3][-1]:
            same_end += 1
        if L == 5:
            n5 += 1
        else:
            n7 += 1
        items.append({"id": i, "lines": ls, "n_chars": L * LINES_PER_POEM})

    n_lines = args.n * LINES_PER_POEM
    n_chars = sum(it["n_chars"] for it in items)
    v = len(src_vocab)
    combos_log10 = LINES_PER_POEM * 5 * math.log10(v)   # 四句五言的组合数下限
    meta = {
        "n": len(items),
        "seed": SEED,
        "source_poems": len(poems),
        "vocab": len(used),
        "vocab_source": v,
        "n_lines": n_lines,
        "n_chars": n_chars,
        "dup_lines": dup_lines,
        "dup_ratio": round(dup_lines / max(n_lines, 1), 6),
        "near_dup_lines": near_lines,
        "forms": {"5": n5, "7": n7},
        "combos_log10": round(combos_log10, 2),
        "method": "二阶马尔可夫（向双字、单字退让）+ 句首/句尾双字采样",
    }

    payload = {"meta": meta, "items": items}
    with open(DST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    size_kb = os.path.getsize(DST) / 1024

    demo_kb = 0
    if not args.no_demo:
        demo_kb = build_demo(meta, items) / 1024

    dt = time.time() - t0
    print("诗云 · 白噪音")
    print("  源诗 %s 首 / 五言 %s 行 / 七言 %s 行%s" % (
        format(len(poems), ","), format(len(lines[5]), ","),
        format(len(lines[7]), ","), "（剔除 %d 行含异体字）" % dropped if dropped else ""))
    print("  生成 %s 首（五言 %s / 七言 %s），%s 行，%s 字" % (
        format(len(items), ","), format(n5, ","), format(n7, ","),
        format(n_lines, ","), format(n_chars, ",")))
    print("  用字 %s 个（源诗 %s 个）" % (format(len(used), ","), format(v, ",")))
    print("  与真诗完全相同的行 %d 行（%.4f%%）；含四字连续重合的 %s 行（%.2f%%）" % (
        dup_lines, 100.0 * dup_lines / max(n_lines, 1),
        format(near_lines, ","), 100.0 * near_lines / max(n_lines, 1)))
    print("  第 2、4 句末字偶然相同的首数 %s（%.2f%%）——机器不懂韵，只是复读" % (
        format(same_end, ","), 100.0 * same_end / max(len(items), 1)))
    print("  组合空间下限 %d^20 ≈ 10^%.2f" % (v, combos_log10))
    print("  用时 %.1fs  ->  %s (%.0f KB)" % (dt, DST, size_kb))
    if demo_kb:
        print("                ->  %s (%.0f KB)" % (DEMO, demo_kb))
    if args.show:
        print()
        for it in items[:args.show]:
            print("  #%d" % it["id"])
            for ln in it["lines"]:
                print("    " + ln)
            print()


DEMO_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>诗云 · 白噪音</title>
<style>
  :root{
    --bg:#04050A; --paper:#ECE7DB; --dim:#7E7A6E; --mute:#4A4740; --gold:#C9A227;
    --line:rgba(236,231,219,.10); --line2:rgba(236,231,219,.055);
    --t1:9px; --t2:11px; --t3:12.5px; --t4:15px; --t6:34px;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{height:100%;overflow:hidden;background:var(--bg);color:var(--paper);
    font-family:"Songti SC","STSong","SimSun","Source Han Serif SC","Noto Serif SC",serif;
    -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
  #wall{position:fixed;inset:0;display:flex;justify-content:center;align-items:stretch;
    gap:clamp(14px,2.6vw,46px);padding:0 clamp(14px,4vw,70px)}
  .col{position:relative;flex:1 1 0;min-width:0;max-width:196px;overflow:hidden;
    -webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 9%,#000 91%,transparent 100%);
    mask-image:linear-gradient(to bottom,transparent 0,#000 9%,#000 91%,transparent 100%)}
  .strip{position:absolute;left:0;right:0;top:0;will-change:transform}
  .poem{padding:0 0 1.7em;font-size:var(--t3);line-height:2.02;letter-spacing:.18em;
    color:rgba(236,231,219,.62);white-space:pre-line}
  #vignette{position:fixed;inset:0;pointer-events:none;
    background:radial-gradient(ellipse at 50% 46%,transparent 34%,rgba(4,5,10,.55) 78%,rgba(4,5,10,.9) 100%)}
  #scrim{position:fixed;inset:0;pointer-events:none;z-index:2;
    background:
      linear-gradient(180deg,rgba(4,5,10,.995) 0,rgba(4,5,10,.93) 86px,rgba(4,5,10,.55) 150px,rgba(4,5,10,0) 236px),
      linear-gradient(0deg,rgba(4,5,10,.99) 0,rgba(4,5,10,.88) 46px,rgba(4,5,10,0) 150px)}
  #hd{position:fixed;top:clamp(24px,4vh,48px);left:clamp(18px,4vw,58px);z-index:3}
  #hd h1{font-size:var(--t6);font-weight:400;letter-spacing:.34em;line-height:1}
  #hd .en{margin-top:12px;font-family:"Helvetica Neue",Arial,sans-serif;font-size:var(--t1);
    letter-spacing:.34em;color:var(--dim);text-transform:uppercase}
  #note{position:fixed;top:clamp(26px,4vh,48px);right:clamp(18px,4vw,58px);z-index:3;
    font-size:var(--t2);line-height:2.1;color:var(--dim);letter-spacing:.12em;text-align:right}
  #ft{position:fixed;bottom:clamp(22px,3.4vh,40px);left:clamp(18px,4vw,58px);z-index:3;
    right:clamp(18px,4vw,58px);display:flex;align-items:center;gap:13px;overflow:hidden;white-space:nowrap}
  #ft .rule{width:26px;height:1px;background:linear-gradient(90deg,var(--gold),rgba(201,162,39,0))}
  #ft .st{font-size:var(--t2);letter-spacing:.14em;color:var(--dim)}
  #ft .st b{font-weight:400;color:rgba(236,231,219,.82)}
  #tag{position:fixed;bottom:clamp(22px,3.4vh,40px);right:clamp(18px,4vw,58px);z-index:3;
    font-family:"Helvetica Neue",Arial,sans-serif;font-size:var(--t1);letter-spacing:.3em;
    color:var(--mute)}
  @media (max-width:620px){
    #note{display:none}
    #tag{display:none}
    #hd h1{font-size:23px}
    #ft .rule{width:16px}
  }
  @media (prefers-reduced-motion:reduce){.strip{will-change:auto}}
</style>
</head>
<body>
<div id="wall"></div>
<div id="vignette"></div>
<div id="scrim"></div>
<header id="hd">
  <h1>诗云</h1>
  <div class="en">Shi Yun · White Noise</div>
</header>
<div id="note">机器可以穷尽所有诗，<br>却认不出其中哪一首好。</div>
<footer id="ft">
  <span class="rule"></span>
  <span class="st" id="stats"></span>
</footer>
<div id="tag">组合穷尽 · 意义为零</div>
<script>
const RAW = __DATA__;
const META = __META__;
const POEMS = RAW.split("\n").map(function(s){return s.split("|")});
const N = POEMS.length;
function stats(){
  const f = function(n){ return n.toLocaleString("en-US") };
  const el = document.getElementById("stats");
  if (innerWidth < 620){
    el.innerHTML = "用字 <b>" + f(META.vocab) + "</b> · <b>" + f(N) +
      "</b> 首伪诗 · 与真诗重复 <b>" + META.dup_lines + "</b> 行";
  } else {
    el.innerHTML = "用字 <b>" + f(META.vocab) + "</b> · 源诗 <b>" +
      f(META.source_poems) + "</b> 首 · 与真诗重复 <b>" + META.dup_lines +
      "</b> 行 · <b>" + f(N) + "</b> 首伪诗";
  }
}
stats();

const wall = document.getElementById("wall");
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
let cols = [];
let rafId = 0;

function ncols(){
  const w = innerWidth;
  return w < 560 ? 3 : w < 820 ? 4 : w < 1120 ? 5 : w < 1560 ? 6 : 7;
}

function makePoem(idx){
  const d = document.createElement("div");
  d.className = "poem";
  d.textContent = POEMS[idx % N].join("\n");
  return d;
}

function build(){
  wall.innerHTML = "";
  cols = [];
  stats();
  const n = ncols();
  const mid = (n - 1) / 2;
  for (let i = 0; i < n; i++){
    const col = document.createElement("div");
    col.className = "col";
    col.style.opacity = (0.30 + 0.70 * (1 - Math.abs(i - mid) / (mid + 0.6))).toFixed(3);
    const strip = document.createElement("div");
    strip.className = "strip";
    col.appendChild(strip);
    wall.appendChild(col);

    const c = {
      strip: strip,
      col: col,
      y: -(i * 53) % 120,
      h: 0,
      speed: 5.2 + ((i * 37) % 9) * 0.5,
      cursor: (i * 2797 + 11) % N,
      step: n
    };
    cols.push(c);
  }
  for (const c of cols) fill(c);
  for (const c of cols) c.strip.style.transform = "translate3d(0," + c.y.toFixed(1) + "px,0)";
  if (reduce) return;
  if (rafId) cancelAnimationFrame(rafId);
  last = 0;
  rafId = requestAnimationFrame(tick);
}

function appendPoem(c){
  const node = makePoem(c.cursor % N);
  c.cursor += c.step;
  c.strip.appendChild(node);
  const h = node.offsetHeight || 110;
  c.h += h;
}

function fill(c){
  const H = innerHeight;
  let guard = 0;
  while (c.y + c.h < H + 200 && guard++ < 80){
    appendPoem(c);
  }
}

let last = 0;
function tick(t){
  if (!last) last = t;
  const dt = Math.min((t - last) / 1000, 0.1);
  last = t;
  for (const c of cols){
    c.y -= c.speed * dt;
    let first = c.strip.firstElementChild;
    while (first && c.y + first.offsetHeight < 0){
      const h = first.offsetHeight;
      c.y += h;
      c.h -= h;
      c.strip.removeChild(first);
      first = c.strip.firstElementChild;
    }
    fill(c);
    c.strip.style.transform = "translate3d(0," + c.y.toFixed(1) + "px,0)";
  }
  rafId = requestAnimationFrame(tick);
}

let rt = 0;
addEventListener("resize", function(){
  clearTimeout(rt);
  rt = setTimeout(build, 220);
});
build();
</script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
