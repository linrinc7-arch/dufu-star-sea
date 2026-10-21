# 02 · 数据层逆向 —— 诗云（shiyun.cohenjikan.com）

> 负责人：data-layer｜产物：reports/02-data.md
> 对象：work/rea/shiyun/data/ 下全部静态制品（不重新抓取；仅对「桶大小分布」与「Range 行为」做了必要 CDN 探测，见 §9）
> 代码行号指 pretty/index.js（= prettier 格式化后的 site/assets/index-ah4l33vX.js）
> 环境：Python 3.12.10 / Windows。本地文件一律 utf-8 显式读取（系统默认 GBK，直接 open 会 UnicodeDecodeError）

---

## 0. 一页结论

| 问题 | 结论 | 证据 |
|---|---|---|
| 诗人 id 怎么来 | **FNV-1a 32（逐 UTF-16 码元）of name + "\|" + dynasty**，8 位小写 hex；33,458 条**逐条命中** | §2.3、index.js:3284-3289 |
| 数组条数 vs poetCount | 数组 **33,458**，其中 **804** 条带 mergedInto（并入他人），33,458−804 = **32,654** = manifest.poetCount | §2.2 |
| 坐标是否预计算 | **没有**。索引无 x/y/z/seed 字段；星团位置由 qr(poet) 用 id/name 的 FNV 结果实时算 | §2.6、index.js:4749-4798 |
| 分桶规则 | poems = id **前两位**（FNV 高字节）；lines/search = At(key) **& 255**（低字节）；linesf = At(key) **& 4095**（3 位 hex） | §3、index.js:4303 / 4360 / 4494 |
| sidecar 索引 | poems/<b>.idx.json = {诗人id: [offset,len]}，是**JSON 值（数组）的字节区间**；256 桶 32,654 条全部满足「文件字节 = 12n + Σlen + 1」，**零违例** | §4.2 |
| Range 切片 | 本地切片 121/121 与整桶对象全等；Live 抽查 9 位诗人 206+解析，条数与 poemCount **9/9 精确相等** | §4.3 |
| 三套桶 | lines = 行倒排；search = 标题/检索词倒排；linesf = 删一字模糊回退（当前部署抽样 256 桶**全 404**） | §5 |
| gifts.json | 5,051 条有向加权边 [from,to,w]；实测语义 = 诗题以「赠/送/寄…」开头且含对方姓名子串的篇数（本地 9/16 可精确复现） | §6 |
| 缓存 | 7 张**无上限 Map** + 礼物 Promise 单例；无 LRU/TTL，无 ServiceWorker/IndexedDB | §7 |
| 首屏 | ≈ **920 KB（gzip）** 才点亮星图：JS 332 KB + 数据 588 KB（poets.index 一份 465 KB） | §8 |
| 体量 | 全库 raw ≈ **1.18 GiB（1.27 GB）**，gzip ≈ **470 MB**；poems 252.6 MiB + lines 827 MiB + search 129 MiB | §10 |

---

## 1. 制品基线

| 文件 | 字节 | gzip -9 | 说明 |
|---|---:|---:|---|
| data/poets.index.json | 2,908,656 | 465,586 | 诗人索引（首屏必载） |
| data/charset.json | 66,712 | 48,151 | 22,219 字，hash=a9cde1f2 |
| data/lexicon.json | 250,823 | 74,099 | 平仄/韵部（可选，失败也能跑） |
| data/manifest.json | 2,886 | 689 | 构建清单 |
| data/gifts.json | 131,502 | 38,429 | 赠诗边 |
| data/poems/00.json | 1,091,455 | 502,509 | 诗桶：121 位诗人 / 3,670 首 |
| data/poems/00.idx.json | 2,954 | 1,329 | 同桶字节区间 |
| data/lines/00.json | 3,396,679 | 1,243,160 | 行倒排：34,422 键 / 37,435 次 |
| data/search/00.json | 540,678 | 160,263 | 检索：4,421 键 / 6,088 条 |
| data/linesf/00.json | 146 | — | **nginx 404 页**，不是数据 |

manifest 原文（截断）：

    {"version":3,"n":22219,"pullK":13564,"poetCount":32654,"poemCount":871268,
     "buckets":["00",...,"ff"],"lineBuckets":["00",...,"ff"],"giftEdges":5051,
     "poemSidecar":true,"dynCounts":{"song":9495,"qing":8980,"ming":4513,...}}

**与简报的差异**：manifest.lineBuckets 实际是 **256 项**（与 buckets 逐项相同，len=256），不是 224。全文没有 "224" 这个值。
（若 224 是某次观测到的「实际存在的 linesf 桶数」，那是另一个命名空间：linesf 用 3 位 hex，共 4096 个桶位。）

---

## 2. poets.index.json

### 2.1 结构与字段

顶层是**数组**。33,458 条全量字段频次：

| 字段 | 次数 | 含义（实测） |
|---|---:|---|
| id | 33,458 | 8 位 hex，FNV-1a(name+dynasty) |
| name | 33,458 | 姓名；1,584 个重名（"无名氏"×12、"佚名"×7、"王鼎"×5） |
| dynasty | 33,458 | 14 个朝代键之一 |
| poemCount | 33,458 | Σ = **871,268**，与 manifest.poemCount 逐位相等 |
| clusterSize | 33,458 | 星团尺寸标量（**不是坐标**），见 §2.5 |
| mergedInto | 804 | 该记录已并入另一 id（poemCount=0，clusterSize=0） |
| quGap | 97 | 曲/词体标记 |
| lost | 4 | 缺字篇目，如 [{"t":"□□□□ 其一","k":"lacuna"}] |
| collection | 3 | 收录说明（partial / copyright） |
| restrictedOnly | 1 | 仅存目（版权） |

真实片段（≤200 字）：

    {"id":"1ca4256c","name":"陆游","dynasty":"song","poemCount":9612,"clusterSize":60}

    {"id":"4a282690","name":"唐温如","dynasty":"tang","poemCount":0,"clusterSize":0,"mergedInto":"28a217e3"}

    {"id":"67ca2990","name":"叶...","dynasty":"jinxiandai","poemCount":1,"clusterSize":3.4,
     "collection":[{"k":"copyright","note":"作品版权保护至 2074 年，仅建条目"}],"restrictedOnly":1}

804 条 mergedInto 的目标 id 全部存在（all(...) 为 True）。

### 2.2 33,458 vs 32,654

    数组长度           33,458
    带 mergedInto       -804
    ---------------------------
    规范诗人数           32,654   == manifest.poetCount ✅

按朝代分组（剔除 merged）与 manifest.dynCounts **逐项相等**：

    song 9495 | qing 8980 | ming 4513 | dangdai 4332 | tang 2818 | yuan 1188
    nanbeichao 434 | jin 269 | weijin 251 | jinxiandai 191 | sui 84 | qinhan 84
    xianqin 8 | liao 7        （Σ = 32,654）

未剔除时 jinxiandai 是 969、tang 是 2820 —— 对不上；这正好反证「manifest 的 dynCounts 按规范诗人统计」。
另：代码朝代表有 15 条（index.js:3090-3274，id 0..14，含 wudai 五代十国），但**没有任何诗人是 wudai**，该星带恒空；manifest 也只有 14 个键。

### 2.3 id = FNV-1a(name + "|" + dynasty)

浏览器侧同一函数（index.js:3284-3289，混淆名 At）：

    function At(e) {
      let t = 2166136261;
      for (let n = 0; n < e.length; n++)
        (t ^= e.charCodeAt(n)), (t = Math.imul(t, 16777619));
      return t >>> 0;
    }

Python 复算：

    import json
    d = json.load(open("data/poets.index.json", encoding="utf-8"))
    def fnv1a(s):
        h = 2166136261
        for ch in s:                     # 逐字符异或再乘质数（码元级，非 UTF-8 字节级）
            h = ((h ^ ord(ch)) * 16777619) & 0xffffffff
        return h
    bad = [o for o in d if format(fnv1a(o["name"] + "|" + o["dynasty"]), "08x") != o["id"]]
    # len(bad) == 0      → 33,458 / 33,458 命中

| 名字 | dynasty | id（=实算） |
|---|---|---|
| 陆游 | song | 1ca4256c |
| 苏轼 | song | 126fd9ff |
| 白居易 | tang | cf399cf4 |
| 李白 | tang | 82a5851c |
| 王世贞 | ming | e91aca8f |
| 屈大均 | qing | a8d93b82 |
| 纳兰性德 | qing | 38765755 |

旁证：(name,dynasty) 组合**零重复**（33,458 个键全不同），而名字本身有 1,584 个重名 → dynasty 就是为消歧进哈希的。
（试过 crc32 / md5 / sha1 / sha256 / djb2 / sdbm / murmur3 / xxh32 × 9 种拼接模板，仅「码元级 FNV-1a + name|dynasty」命中，且 6/6。）

### 2.4 朝代分布

见 §2.2。补充诗数分布：**中位 2 首**、均值 26.7；poemCount ≤1 占 **40.5%**（13,221 人）、≤5 占 71.3%、≤50 占 93.0%。song 9,495 位是最大头。

### 2.5 clusterSize = min(60, 2 + 1.4·√poemCount)

clusterSize 是 poemCount 的**一元函数**（743 个不同 poemCount，没有一个对应两个 clusterSize）。拟合后的精确形式：

    clusterSize = min(60, round(2 + 1.4 * sqrt(poemCount), 2))

复算 **32,654 / 32,654 全部相等**（误差 < 1e-9）：

| poet | poemCount | clusterSize | 2+1.4√p |
|---|---:|---:|---:|
| 陆游 | 9612 | 60 | 139.3 → 封顶 60 |
| 白居易 | 2942 | 60 | 77.9 → 60 |
| 杜甫 | 1473 | 55.73 | 55.73 |
| 李白 | 1051 | 47.39 | 47.39 |
| 李清照 | 93 | 15.5 | 15.50 |
| 曹操 | 28 | 9.41 | 9.41 |
| 任意 1 首诗人 | 1 | 3.4 | 3.40 |

封顶阈值 p ≥ **1717**（39 位诗人被截到 60；未封顶的最大者 1705 首）。
渲染侧用法（index.js:4833-4835）：

    function ti(e, t) { return e.mergedInto ? 0 : (1.4 + e.clusterSize * 0.32) * (t ? 2.4 : 1); }

即星团视觉半径 = 1.4 + 0.32·clusterSize（选中时再 ×2.4 放大）。

### 2.6 星团坐标：不预计算，靠哈希现算

索引里**没有** x/y/z/seed/xz 任何位置字段（全部键就 §2.1 那 9 个）。位置在客户端生成（index.js:4749-4798，qr）：

    function qr(e) {
      let [t, n] = kt((Et[e.dynasty] ?? wt[Tt - 1]).id),   // 朝代 → y 区间
          r = At(e.id + e.name),                            // FNV(id+name)：轨道半径/分支角/扭转/厚度
          ...
      let y = At(e.name + "#" + e.id), ...                  // 第二组哈希：抖动
      return [Math.cos(p) * o + w(b, x) + D * E, v, Math.sin(p) * o + w(S, C) + O * E];
    }

    function kt(e) { let t = 420 + e * Ot; return [t, t + Ot]; }   // 3280-3283，每朝一条 y 带

结论：星图是**确定性程序化生成**——同一 id 永远同一位置，无需存坐标（32,654 × 3 个 float 若入 JSON 约 1 MB+，现在 0 字节）。

---

## 3. 分桶：三套命名空间，取哈希里不同的字节

| 桶族 | 桶名来源 | 代码 | 验证 |
|---|---|---|---|
| poems/<b>.json | id 前两位 = **FNV 高字节** (h>>24)&255 | _r() 里 e.slice(0,2)（4303） | 33,458 / 33,458 条 id[:2] == format(fnv>>24,"02x") ✅ |
| poems/<b>.idx.json | 同上 | 4308 | 256/256 文件存在 |
| lines/<b>.json | At(行) & 255 → 2 位 hex | xr（4360） | 桶 00 的 34,422 个键**全部** hash&255==0 ✅ |
| search/<b>.json | At(检索词) & 255 | Mr（4494，同式） | 桶 00 的 4,421 个键全部 hash&255==0 ✅ |
| linesf/<b>.json | At(行) & 4095 → 3 位 hex | Sr（4361） | 命名空间 4096；当前部署抽样 256 个**全 404**（§5.2） |

踩坑点：poems 用**高字节**，lines/search 用**低字节**。若以为「都用 hash&255」，会算错 99.6% 的诗人桶（实测只有 118/33,458 恰好相同）。

---

## 4. poems 桶 + sidecar 索引

### 4.1 结构

单层对象：{ "<诗人id>": [ {"t":标题,"f":体裁,"p":[行,...]}, ... ] }

    {"00a6bcb0":[{"t":"忆之纯 其三","f":"wulu","p":["俊气轻天下","高情到古人","衔杯曼卿放",
     "下笔老坡神","时论谁优劣","人材自屈伸","穷愁须理遣","不必泪沾巾"]},...

- 桶 00：**121 键 / 3,670 首**；121/121 键以 00 开头（题目要验证的点）。
- 字段：t 3,670 / f 3,670 / p 3,670 / **d 仅 6**。d 是「补 □ 的展示文本」，p 是「挖掉缺字的分析文本」：

      {"t":"送陈十二仲溱归柯屿幽居","f":"other","p":["怜君复失意","别我向南还","落日渡",...],
       "d":["怜君复失意","别我向南还","落日□□渡",...]}

- f 取值（桶 00）：other 1,228 / qijue 817 / qilu 810 / wulu 658 / wujue 157；代码另有 ziyou 回退（index.js:6845-6853）。
- 平均每首 **11.1 行**（桶 00 实测）→ 871,268 首约 9.5M 行，与行库规模吻合（§5.1）。

### 4.2 idx 的真实语义

    {"00a6bcb0": [12, 8653], "0013eb34": [8677, 1184], "0098c26f": [9873, 366890]}

- offset 指向数组值起始的 **[**，len 是该数组序列化后的字节数。
- 首偏移 12 = 「{"00a6bcb0":」的 12 字节；相邻两条空隙**恒为 12** = 「,"<8hex>":」。实测空隙直方图：{12: 120}，120 个间隙全部 12。
- **全局不变式**：文件字节 = 12·n + Σlen + 1。用 256 个真实桶校验：

      total poets in buckets: 32654      ← 恰等于 manifest.poetCount
      total payload bytes:    264,434,856
      invariant violations:   0 / 256    ← 12*32654 + 264,434,856 + 256 = 264,826,960
                                          = poems 全部 256 个文件的字节之和

这是**整库级证明**：sidecar 不是「大概对」，而是 256/256 精确可逆。

### 4.3 切片 + JSON.parse == 整桶对象

本地（121/121 全等）：

    raw   = open("data/poems/00.json","rb").read()
    whole = json.loads(raw)
    idx   = json.load(open("data/poems/00.idx.json", encoding="utf-8"))
    ok = 0
    for k, (off, ln) in idx.items():
        assert json.loads(raw[off:off+ln].decode("utf-8")) == whole[k]
        ok += 1
    # ok == 121 == len(idx)

Live（真 HTTP Range，206 Partial Content）：

    pid = "1ca4256c"                    # 陆游
    off, ln = idx["1c"]["1ca4256c"]     # [146433, 2215295]
    GET /data/poems/1c.json  Range: bytes=146433-2361727
      → 206, Content-Range: bytes 146433-2361727/2798003
      → len(body) == 2215295，json.loads 长度 9612 == poets.index 里陆游的 poemCount ✅

随机 + 边界抽样 9 位（李白 / 杜甫 / 陆游 / 徐熥 / 孙邦杰 / 冯脩之 / 曾纯 / 席子研 / 陈衍）：

    9/9 status=206，切片字节数与 idx 一致，解析数组长度 == poemCount（含 174 B 的单首诗切片）

→ 跨库一致性（poets.index.poemCount ↔ poems 桶真实数组长度）第三方验证通过。

前端调用（index.js:4300-4350，本文把模板字符串改写为拼接）：

    let i = e.slice(0, 2);                        // 桶名
    if (nr?.poemSidecar && !or) {                 // manifest.poemSidecar 为真才走 sidecar
      let r = ar.get(i);                          // idx 缓存 Map
      if (r === void 0) { ...fetch(idxUrl)... ar.set(i, t) }
      let a = r?.[e];                             // [offset,len]
      if (a) {
        let [r, o] = a;
        let a = await fetch(bucketUrl, { headers: { Range: "bytes=" + r + "-" + (r + o - 1) } });
        if (a.status === 206) { ...JSON.parse(t)... ir.set(e, n); return n }
        else if (a.ok) { or = !0; ... }           // 服务器忽略 Range → 整桶，且此后全局禁用 sidecar
      }
    }
    let a = (await hr(i, t))[e] || [];            // 兜底：整桶 GET
    a.length || console.warn("poet " + e + ": bucket " + i + " loaded but has no entry (data desync?)");

### 4.4 逐诗人切片大小（32,654 条 idx 实测）

| 统计 | 值 |
|---|---|
| 中位数 | **514 B** |
| 均值 | 8,098 B |
| p90 | 11,487 B |
| 最大 | 2,215,295 B（陆游 9,612 首） |
| <5 KB | 桶 00 里 100/121 |

点开一位普通诗人 ≈ 0.5 KB 正文 + 3 KB idx（.idx.json 平均 3,105 B，gzip ~1.3 KB）；点陆游才 2.2 MB。**按需取数做得很彻底。**

---

## 5. lines / linesf / search

### 5.1 lines/<b>.json = 行倒排（行 → 诗坐标）

    {"毁弃无足惜":[{"p":"00a6bcb0","i":4,"t":"白发叹","f":"other"},
                   {"p":"00a6bcb0","i":29,"t":"感秋","f":"other"}],
     "翩翩南雁来回翔":[{"p":"0098c26f","i":13,"t":"临高台","f":"other"}],...

- 键 = **整行诗**；值 = [{p:诗人id, i:该诗人诗集数组下标, t:标题, f:体裁}]。
- 桶 00：34,422 键 / 37,435 次出现（平均 1.09，最多 6）。
- 分桶极其均匀：3 个抽样桶 34,422 / 34,240 / 34,254 键，37,435 / 37,094 / 37,167 次 → 全库约 **8.77M 行 / 9.55M 次**（871,268 首 × 11.1 行 ≈ 9.7M，自洽）。
- 用途：**按整行检索**。Ar()（4409-4492）把输入按非汉字切成若干汉字段 → 每段一个桶（xr）→ Promise.all 并行拉 → 桶内精确查键 → 按「匹配段数 → 是否名家 → 诗人诗数」排序取前 30。

### 5.2 linesf/<b>.json = 删一字模糊回退（当前基本不可用）

- 目的：记错/漏一个字仍能命中。做法 Or()（4392-4402）：把查询句「删掉一个字符」生成变体集；每个变体用 Sr(v) = At(v)&4095（3 位 hex）查 linesf。只有精确行检索零命中且句长 4–10 时触发（4477-4481）。
- 全局熔断（Dr，4376-4391）：

      n.status === 404 && (Tr.set(e, {}), (Er = !0));   // 任一个 linesf 桶 404 → 整条路径永久关闭

- 当前部署的事实：本地 data/linesf/00.json 就是 nginx 404 页（146 B）：

      <html><head><title>404 Not Found</title></head><body><center><h1>404 Not Found</h1></center>

  CDN 实测 /data/linesf/00.json → 404 text/html；另均匀抽样 256 个 3-hex 桶（每 16 个取 1，覆盖 000..ff0）→ **256/256 全 404**。
- 结论：linesf 是**可选的稀疏回退层**，构建/部署时没上传；客户端首次 404 就把 Er 置真、后面不再请求。所谓「有的桶 404」不是分桶规则造成，而是**整层缺失 + 404 即熔断**的设计。

### 5.3 search/<b>.json = 检索倒排

    {"故黎平太守袁公挽歌其三":[{"p":"0098c26f","i":409,"t":"故黎平太守袁公挽歌 其三","f":"wulu"}],...}

- 桶 00：4,421 键 / 6,088 条；**每键最多 12 条**（同名篇共用，如「秋夜闻笛」10 条）。
- 键 = **去掉所有非汉字字符后的检索串**：「故黎平太守袁公挽歌 其三」→ 故黎平太守袁公挽歌其三；「十月的献诗：钟声」→ 十月的献诗钟声。长键（≥4 字，2,488 个）**100% 精确等于某条记录标题**，是明确的标题索引。
- 短键（1–3 字，1,933 个）不是完整标题，是检索词：病(12)、旅(12)、西风(12)、长风(12)、长城(12)。实测多数是「该词出现在正文/标题」的聚合（旅 12/12、西风 12/12、病 11/12 + 标题 1/12），但长城只有 3/12、长风 1/12 能对上 → **短键与当前 poems 文本没严格对齐**，推测索引由另一版诗文生成（版本漂移）。客户端只把 search 结果当「标题 + 坐标」展示，正文永远从 poems 桶按 (p,i) 取，所以不影响正确性，只影响召回。
- 用途 Fr()（4509-4532）：取查询汉字串 q 与前 3 个汉字 q[:3] 两个键，各查一次 search/At(key)&255，合并去重；Ir()（4533-4560）再与行检索 Ar 合并，按 lineMatches → 名家 → 诗数 排序，同一诗人最多 2 条、共 10 条。

---

## 6. gifts.json（5,051 条边）

### 6.1 结构

    {"version":1,"edgeCount":5051,"edges":[
      ["f11cb552","126fd9ff",283],    // 苏辙 → 苏轼 283
      ["126fd9ff","f11cb552",180],    // 苏轼 → 苏辙 180
      ["6cf90ee3","3eb4d52c",106],    // 梅尧臣 → 欧阳修 106
      ["48db3f21","3ead914f",101],    // 皮日休 → 陆龟蒙 101
      ["b442c44f","cf399cf4",85]      // 元稹 → 白居易 85
    ]}

- 边 = [fromId, toId, w] 定长 3；edgeCount 字段与实际长度都是 **5,051**；version 1。
- 无自环、无重复 (from,to) 对；id 全部能在 poets.index 找到（missing=0）。
- 覆盖 2,167 个赠出诗人、2,033 个收到诗人；w ∈ [1,283]，均值 2.13，且**恒 ≤ from.poemCount**（0 例外）。
- 方向：index.js:5745 明确 r(t,n,"out",i) / r(n,t,"in",i)，UI 文案 e.dir === "out" ? "赠出→" : "←收到"（9867）。

### 6.2 语义验证 = 「诗题以赠答动词开头 + 含对方姓名」的篇数

对本地可复核的 16 条边（from 在桶 00），用规则「title[0] ∈ {赠,送,寄,怀,忆,答,酬,和,呈,简,柬,…} 且 name ⊂ title」计数：

    OK       徐熥->陈价夫  w=1 rule=1  ['赠陈价夫荐夫']
    OK       徐熥->道源    w=1 rule=1  ['赠陈道源参军']
    OK       徐熥->江仲鱼  w=1 rule=1  ['赠江仲鱼']     # 另 2 首题含"江仲鱼"但不以赠答动词开头，未计入 ✅
    OK       徐熥->叶进    w=1 rule=1  ['送叶进卿太史还朝']
    OK       徐熥->彭举    w=1 rule=1  ['送胡彭举之衡阳']
    OK       徐熥->王懋    w=1 rule=1  ['送王懋宣先生之泰顺']
    OK       陈尧叟->张无梦 w=1 rule=1 ['送张无梦归天台']
    OK       李观->冯宿    w=1 rule=1  ['赠冯宿']
    MISMATCH 徐熥->袁枚/欧阳修/杜甫、朱朴->王守仁/文徵明、周元晟->晁补之、周燕婷->辛弃疾/杜牧

- 9/16 精确复现；剩 7 条全是「给古人」的边（明人→杜甫、今人→辛弃疾/杜牧），本地诗集找不到对应标题 → 推测构建时还用了**字/号别名**（少陵、稼轩、牧之）或题注/序文，也可能含少量误配。
- 网络结构支持「唱和/致意」语义：**76.6%（3,869/5,051）同朝代**；跨 3 朝以上的 827 条里，大额边清一色「和陶/效古」——李纲→陶潜 63、苏辙→陶潜 50、戴良→陶潜 41、赵秉文→陶潜 35、陈造→陶潜 27；现当代→古代 233 条（汪东→周邦彦 40、程滨→杜甫 16、张伯驹→姜夔 12、乔大壮→周邦彦 9）。
- 出度 hub：苏轼 57、苏辙 39、姚合 28、黄庭坚 27、梅尧臣 26；权重 top：苏辙→苏轼 283、苏轼→苏辙 180、梅尧臣→欧阳修 106。

### 6.3 数据质量：姓名按**子串**匹配会误连

上面 9 条可复现边里，有 4 条收赠人其实另有其人（姓名是对方姓名的真子串）：

| 边 | 命中的诗题 | 真实收赠人 |
|---|---|---|
| 徐熥 → 王懋 | 送**王懋**宣先生之泰顺 | 王懋宣 |
| 徐熥 → 叶进 | 送**叶进**卿太史还朝 | 叶进卿 |
| 徐熥 → 彭举 | 送胡**彭举**之衡阳 | 胡彭举 |
| 徐熥 → 道源 | 赠陈**道源**参军 | 陈道源 |

→ 5,051 条边里存在少量「名字对、人不对」的噪声（本地可核 9 条中 4 条），用图时应作**弱关系**而非考据结论。

---

## 7. 加载与缓存策略

### 7.1 启动 mr()：一次性并发拉 4 个文件

index.js:4251-4271（模板字符串改写为拼接）：

    async function mr(e = Yn) {
      let [t, n, r, i] = await Promise.all([
        fetch(e + "/charset.json").then(r => r.json()),
        fetch(e + "/poets.index.json").then(r => r.json()),
        fetch(e + "/manifest.json").then(r => r.json()),
        fetch(e + "/lexicon.json").then(r => r.ok ? r.json() : null).catch(() => null),  // 可选
      ]);
      (er = n), (tr = new Map(n.map(x => [x.id, x]))), (nr = r),
      (Qn = Kn(t.chars, typeof t.hash == "string" ? t.hash : void 0));   // 字库哈希校验
      Qn.ok || console.error("[诗云] 字库与本版本不匹配:编号链接可能错位。computed=" + ...);
      ...
      return r;
    }

- 4 个请求**并行**；lexicon 失败降级为 null（用内置平仄表 pr(n) 兜底）。
- Promise.all 语义：任一 reject 即整站失败（§7.4）。
- 顺带做 **charset 哈希自检**，不匹配打「编号链接可能错位」（数据版本一致性检查）。

### 7.2 缓存表：7 张 Map + 1 个 Promise 单例，**全部无上限**

| 变量 | 位置 | 内容 | 淘汰 |
|---|---|---|---|
| tr | 4191 | id → 诗人记录（33,458 条） | 无 |
| rr | 4193 | 桶名 → 整桶诗对象 | 无 |
| ir | 4194 | 诗人id → 该诗人诗数组 | 无 |
| ar | 4195 | 桶名 → idx（404 记 null） | 无 |
| Cr | 4362 | 桶名 → lines 桶（**约 3.4 MB/桶**） | 无 |
| Tr | 4376 | 桶名 → linesf 桶 | 无 |
| Nr | 4495 | 桶名 → search 桶 | 无 |
| Lr / Ui | 4561 / 5731 | gifts 数组（Promise 单例） | 无 |

没有 LRU、没有 TTL、没有容量上限。一次行检索就会把 3.4 MB 的 lines 桶永久留在内存（Cr）。

另一组 **localStorage**（与数据加载无关）：shiyun_shiyi_v1（拾遗历史，上限 200 条、预览截 14 字，3299-3350）、shiyun_claims_v1（认领码，上限 500）、shiyun:gesture-fps、shiyun:gesture-backend（手势性能偏好）。

### 7.3 并发 / 预取

- **无预取**：只有 Zo(id)（7101-7114）在「选中 / 键盘跳转 / 赠诗漫游」后按需加载一位诗人的诗；没有邻居桶预取。
- **并发无节流**：mr 4 路；Ar 对查询里每个行段各发一个桶请求并 Promise.all 全并行（4415-4417）；Ir 又让 Fr（标题，最多 2 桶）与 Ar（行，最多 N 桶）并行（4536-4539）。极端情况一次搜索可同时拉 4–6 个 3.4 MB 行桶。
- **无 in-flight 去重**：wr/Pr/_r 都是 await 完再 set，同一桶并发两次会发两次请求。

### 7.4 错误处理矩阵

| 函数 | HTTP 非 2xx | 解析失败 | 结果 |
|---|---|---|---|
| mr | 抛错 → 整站「数据载入失败」 | — | 只能 location.reload() 重载 |
| hr | throw Error("poems bucket <b> → HTTP <status>")（4276） | 抛错 | 诗人面板「作品载入失败，可能是网络波动。」+ 重试按钮（8608-8619 → Zo(id) 重来） |
| _r (Range) | 非 206 但 ok → or = !0 **全局关闭 sidecar**，改整桶；206 解析失败同样 or = !0 | try/catch 吞掉 | 静默降级 |
| wr / Dr / Pr | 404 → 缓存 {}；其它错误吞掉 | 吞掉 | **静默空结果**（「没搜到」与「网络挂了」无法区分） |
| Rr | 404 → [] | 吞掉 | 赠诗层不显示 |

- **没有任何自动重试 / 超时 / AbortController**（全文无 AbortSignal 逻辑），只有 UI 上的手动「重试」按钮。
- **没有 Service Worker / IndexedDB / Cache API**（grep serviceWorker|indexedDB|caches. 无命中）→ **离线不可用**；唯一的「离线」是浏览器 HTTP 缓存（max-age=86400，1 天）。

### 7.5 UI 侧的进度与文案

- 首屏：正在点亮 32,657 位诗人…（13442，硬编码；manifest 实为 **32,654**，差 3 人）。
- 载入诗歌：gr()（4281-4299）用 Content-Length + body.getReader() 流式累计，回调 setPoetPoemsProgress({id, received, total})（7105-7107），进度条组件 qs 消费。
- 启动失败：星图数据载入失败 —— 可能是网络波动。+「重新载入」（13429-13437）。

---

## 8. 首屏 / 交互网络量

### 首屏（点亮星图前）

| 资源 | raw | gzip |
|---|---:|---:|
| index.html | 4,172 | 2,004 |
| index-ah4l33vX.js（应用） | 264,935 | 82,674 |
| three-CjFqNL11.js | 675,551 | 168,786 |
| r3f-yJ-6H-4a.js | 276,945 | 88,089 |
| rolldown-runtime | 694 | 423 |
| CSS | 49,931 | 10,010 |
| charset.json | 66,712 | 48,151 |
| **poets.index.json** | **2,908,656** | **465,586** |
| manifest.json | 2,886 | 689 |
| lexicon.json | 250,823 | 74,099 |
| **合计** | **≈ 4.50 MB** | **≈ 0.92 MB** |

index.html 用 modulepreload 预载三个 JS 分片（23-27 行）→ JS 三条并行；mr() 的 4 个数据请求也并行。**瓶颈是 poets.index.json：465 KB gzip，占数据量 79%。**

### 交互

| 操作 | 请求 | 典型流量（gzip） |
|---|---|---|
| 点一位诗人 | poems/<b>.idx.json + Range 切片 | 1.3 KB + ~0.5 KB（中位）；陆游 2.2 MB |
| 悬浮 / 切换诗人 | 同上（ir 命中则 0） | 0 |
| 按整行搜索 | lines/<b>.json（**整桶**） | **~1.25 MB**（单桶 raw 3.4 MB） |
| 按标题搜索 | search/<b>.json × 1–2 | ~156 KB |
| 打开「赠诗漫游」 | gifts.json 一次 | 38 KB |

行检索是这套设计里**最贵的一步**：为查一行要下整个 3.4 MB 桶（gzip 1.25 MB）。linesf 的稀疏 3-hex 分桶本意就是给模糊匹配降本，但它当前整层 404。

---

## 9. CDN 与缓存头（实测响应头）

| URL | Cache-Control | CF-Cache-Status | 其它 |
|---|---|---|---|
| / | **no-cache** | REVALIDATED | Last-Modified 2026-09-04 |
| /assets/*.js | public, max-age=31536000, immutable | HIT | 强 Etag，hashed 文件名 |
| /data/poets.index.json | public, max-age=86400 | HIT | last-modified 2026-07-23，弱 Etag W/"..."，vary: Accept-Encoding |
| /data/gifts.json | public, max-age=86400 | HIT | 2026-07-23 |
| /data/lines/00.json | public, max-age=86400 | HIT | 2026-07-23，**无 Accept-Ranges** |
| /data/search/00.json | public, max-age=86400 | MISS/HIT | 2026-07-23，无 Accept-Ranges |
| /data/poems/00.json | public, max-age=86400 | HIT | Content-Length 1091455、**Accept-Ranges: bytes**、强 Etag |
| /data/poems/00.idx.json | public, max-age=86400 | HIT | 同上 |
| /data/linesf/00.json | — | MISS | **404 text/html** |

**关键实测：Range 只在 poems 上可靠**

- poems/00.json：Range bytes=0-99 → 206、content-range: bytes 0-99/1091455、Accept-Ranges: bytes，切出来就是原始 JSON 文本 → sidecar 方案成立。
- lines/00.json：Range bytes=0-0 → 206 但 content-range: bytes 0-0/**1263276**。1,263,276 **不是文件大小**（真实 3,396,679 B；全量 GET 的 md5 与本地一致）：
  - 本地 gzip -9 该文件 = 1,243,160 B，与 1,263,276 只差 1.6%（CF 压缩级别不同）；
  - 偏移 1,000,000 取 100 字节，与本地同偏移字节**不一致**（md5 不同）；取 3,000,000 直接 **416 Range Not Satisfiable**；
  - search/00.json 同理：content-range 总量 160,561 ≈ 本地 gzip 160,263（raw 540,678）。
  → lines/、search/ 走的是**压缩表示**，Range 语义被破坏；所幸前端**只对 poems 用 Range**（_r 里唯一的 Range 调用）。
- 「Cache-Control: no-cache」只出现在 **HTML 入口 /**；/data/* 全部 max-age=86400 + 边缘 HIT。

**部署批次**（last-modified）：poems/* = **2026-07-10 06:28:56**；lines/*、search/*、poets.index.json、gifts.json = **2026-07-23**；HTML/JS = **2026-09-04** → 数据与前端**分开部署**，poems 比其它数据旧 13 天（这也是 §5.3 短键对不齐的合理解释）。

---

## 10. 数据体量清单

256 桶全量扫描（Range 取总量 + 抽样全量下载校准）：

| endpoint | 文件数 | 单文件 min / 中位 / max | 合计 raw | 合计 gzip |
|---|---:|---|---:|---:|
| poems/<b>.json | 256 | 270,072 / 1,034,480 / 3,518,863 B | **264,826,960 B（252.6 MiB）** | ≈ 122 MB（按桶 00 的 0.46 比估） |
| poems/<b>.idx.json | 256 | 2,360 / 3,105 / 4,020 B | 794,766 B（0.76 MiB） | ≈ 0.35 MB |
| lines/<b>.json | 256 | ≈3,374,545 / 3,387,653 / 3,396,679 B（3 个抽样） | **≈ 867,239,168 B（827 MiB）** | **323,716,256 B（309 MiB）**（CDN 逐桶实测 gzip 总量） |
| search/<b>.json | 256 | ≈518,074 / 529,108 / 540,678 B（3 个抽样） | **≈ 135,451,648 B（129 MiB）** | **40,008,734 B（38 MiB）** |
| poets.index.json | 1 | — | 2,908,656 B | 465,586 B |
| charset.json | 1 | — | 66,712 B | 48,151 B |
| lexicon.json | 1 | — | 250,823 B | 74,099 B |
| manifest.json | 1 | — | 2,886 B | 689 B |
| gifts.json | 1 | — | 131,502 B | 38,429 B |
| linesf/* | 0（当前部署） | — | — | — |
| **合计** | **1,289** | | **≈ 1.18 GiB（1,271,673,121 B）** | **≈ 470 MB** |

分布特征：

- **按诗人哈希分桶 → 严重不均**：poems 桶最小 270,072 B（6d）、最大 3,518,863 B（e9），**13 倍差**；每桶 97–161 位诗人（均值 127.6）。根因是诗人诗数长尾（中位 2 首、最大 9,612 首）。
- **按行文本哈希分桶 → 极均匀**：lines 桶 3 个样本只差 22 KB（±0.3%），每桶 34,240–34,422 键。
- idx 总共 0.79 MB，却把 252.6 MiB 诗库变成「按诗人随机访问」——**索引只占数据量 0.3%**。

### 为什么不用数据库

1. **数据只读、不可变、按内容哈希静态分片**：文件名就是索引（hash&255 的桶 + 诗人 id 前两位），没有查询语言、事务、写入。这就是一套「预分区 KV / 列族」，只是用文件系统实现。
2. **可变部分只有 feedback / 认领**：全部后端只有 POST /api/claim（+ GET /api/claim/feed?limit=500）和 POST /api/feedback（index.js:3466、10118）。诗词本体一个字节都不经过服务端。
3. **合并查询在客户端**：行倒排、标题倒排、赠诗图都在浏览器里 join（Ir = search ∪ lines），CPU 在客户端，服务端只发字节。
4. **边缘缓存即数据库缓存层**：max-age=86400 + CF HIT，实测 poems 桶二次请求全 HIT；数据库还要自己做缓存、连接池、预热。
5. **成本与可用性**：1.18 GiB 静态文件放 CDN / 对象存储即可，无冷启动、无运维、可整站回滚。871,268 首诗 + 33,458 位诗人用 SQLite/Postgres 当然也扛得住，但要付出服务端进程、连接与查询延迟，换不来任何功能收益。
6. **代价（真实存在）**：
   - 行检索一次要下 3.4 MB 桶（gzip 1.25 MB）——没有服务端就做不到「只回一行」；
   - 按诗人分桶导致 13 倍不均，热门诗人（陆游 2.2 MB 切片、大桶 3.5 MB）拖慢冷缓存；
   - 无法跨桶聚合（如全库字频排序），只能预计算（gifts.json、clusterSize 都是预计算产物）；
   - 版本漂移只能靠 charset.hash 校验 + 控制台警告，缺少服务端 schema 校验（§5.3 短键错位、§6.3 子串误配都是「离线构建、无人校验」的产物）。

---

## 11. 复现脚本

本地（等价于把 §2 / §3 / §4 的断言跑一遍）：

    # -*- coding: utf-8 -*-
    import json, math, os
    os.chdir(r"D:/Desktop/走进大诗人/work/rea/shiyun")

    def fnv1a(s):
        h = 2166136261
        for ch in s:
            h = ((h ^ ord(ch)) * 16777619) & 0xffffffff
        return h

    poets = json.load(open("data/poets.index.json", encoding="utf-8"))
    assert all(format(fnv1a(p["name"] + "|" + p["dynasty"]), "08x") == p["id"] for p in poets)
    canon = [p for p in poets if "mergedInto" not in p]
    assert len(poets) == 33458 and len(canon) == 32654
    assert all(abs(p["clusterSize"] - min(60, round(2 + 1.4*math.sqrt(p["poemCount"]), 2))) < 1e-9
               for p in canon)
    assert all(p["id"][:2] == format(fnv1a(p["name"] + "|" + p["dynasty"]) >> 24, "02x") for p in poets)

    lines = json.load(open("data/lines/00.json", encoding="utf-8"))
    assert all(format(fnv1a(k) & 255, "02x") == "00" for k in lines)

    raw = open("data/poems/00.json", "rb").read()
    whole = json.loads(raw)
    idx = json.load(open("data/poems/00.idx.json", encoding="utf-8"))
    assert all(json.loads(raw[o:o+l].decode("utf-8")) == whole[k] for k, (o, l) in idx.items())
    print("all checks passed")

Live Range（等价于 _r() 的行为）：

    import urllib.request, json
    B = "https://shiyun.cohenjikan.com/data"
    idx = json.loads(urllib.request.urlopen(B + "/poems/1c.idx.json").read())
    off, ln = idx["1ca4256c"]
    req = urllib.request.Request(B + "/poems/1c.json", headers={"Range": "bytes=%d-%d" % (off, off+ln-1)})
    arr = json.loads(urllib.request.urlopen(req).read())
    assert len(arr) == 9612        # == 陆游的 poemCount

---

## 12. 未解 / 存疑

1. **search 短键（1–3 字）的生成规则**：长键 = 去标点标题（2,488 个，100% 精确）已定案；1–3 字键与正文的对应率 5%–100% 不等（旅 / 西风 12/12，长城 3/12、长风 1/12），推测由旧版诗文 / 旧版诗数组生成，无构建脚本可证。
2. **gifts 的 7 条「给古人」边**（徐熥→杜甫 / 欧阳修 / 袁枚 等）无法用本地诗题复现，怀疑构建时用了字 / 号别名表（少陵 / 稼轩 / 牧之）或题序文本。
3. **linesf 是否曾发布**：当前 100% 404；manifest 没有它的清单字段（lineBuckets 256 项 2-hex 属于 lines/），属「代码先上、数据未上」。
4. **32,657 vs 32,654**：品牌文案（OG、加载页）写 32,657，数据是 32,654，差 3；collection 字段恰好 3 条，但无法证明相关。
