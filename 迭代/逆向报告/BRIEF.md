# 诗云 · shiyun.cohenjikan.com 逆向工程 — 团队简报

## 目标
用 REA（rea-agents 6.7.0 + Ghidra 12.1.4，JS 路线不需要引擎）分析
https://shiyun.cohenjikan.com 的真实制品（打包后的 ES2022 bundle + 静态数据），
产出一份可复用的技术拆解报告：它是怎么把"一切可能的诗"做成可漫游的三维星图的。

## 已采集的制品（全部在 work/rea/shiyun/ 下，勿删）
- site/index.html   4,172 B   —— 入口 + 能力门（BigInt / WebGL 检测）
- site/assets/index-ah4l33vX.js      264,935 B  —— 应用主体（Vite/Rolldown 打包，压缩）
- site/assets/three-CjFqNL11.js       675,551 B  —— three.js vendor
- site/assets/r3f-yJ-6H-4a.js         276,945 B  —— @react-three/fiber + drei vendor
- site/assets/rolldown-runtime-QTnfLwEv.js   694 B
- site/assets/index-DZz16_0d.css       49,931 B  —— 全站样式
- site/announce-202607.js              16,233 B  —— 公告横幅
- data/charset.json     66,712 B  —— version2, n=22219 个字，hash=a9cde1f2
- data/lexicon.json    250,823 B  —— 平/仄表、韵部表（rhymeMembers 30 部）
- data/manifest.json     2,886 B  —— version3, n=22219, pullK=13564, poetCount=32654,
                                     poemCount=871268, buckets 00..ff(256), lineBuckets 224,
                                     giftEdges=5051, poemSidecar=true, dynCounts(14 朝)
- data/poets.index.json 2,908,656 B —— 诗人索引
- data/gifts.json       131,502 B  —— 5000+ 条"赠诗"边
- data/poems/00.json    1,091,455 B —— 分桶的诗人诗集，key=诗人 id(8 hex)
- data/poems/00.idx.json    2,954 B —— 同桶的字节区间索引 [offset,len]，配合 Range 请求
- data/lines/00.json    3,396,679 B —— 行库分桶
- data/linesf/00.json —— 404（该桶无文件，按需 404 即空）
- data/search/00.json     540,678 B —— 检索分桶
- 数据基址：代码里 `Yn="/data"`；API：POST /api/feedback

## 已知的代码线索（压缩后的原文片段）
- `var Q=e=>BigInt(e)` 与 `function Wa(e,t){let n=Q(e+1),r=0n;for(...)}` —— 编号→字的进制转换
- `function ho(){return BigInt(Bn().lexicon.N)}` —— 编号空间基数 N
- `async function mr(e=Yn)` 一次性并发拉 charset/poets.index/manifest/lexicon
- `hr(e,t)` 按桶读诗（有 sidecar 时用 `poems/<b>.idx.json` + Range 只取所需切片）
- `wr`→`lines/<b>.json`、`?f`→`linesf/<b>.json`、`Pr`→`search/<b>.json`、`Rr`→`gifts.json`
- `Kn(t.chars, t.hash)` 校验字库哈希，不匹配会提示"编号链接可能错位"

## 反编译/阅读方法
1. 压缩代码先美化：
   `npx prettier@3.3.3 --parser babel work/rea/shiyun/site/assets/index-ah4l33vX.js > work/rea/shiyun/pretty/index.js`
   （vendor 文件 three/r3f 基本是原样库，只在需要时读）
2. REA 结构化视图：
   `bash ~/.dsh/skills/rea-reverse/scripts/rea.sh analyze-javascript-application work/rea/shiyun/site --format json > work/rea/shiyun/rea-js.jsonl`
3. 结论必须挂在证据上：给出**文件 + 函数名/字符串片段/行号**，不要凭名字猜。
4. 数据格式的结论要用真实文件验证（python/json 读一遍，贴出真实样例）。

## 分工与写入范围（互不重叠）
| 负责人 | 范围 | 产物 |
|---|---|---|
| lead | 编号引擎（charset/lexicon/BigInt 编解码）、总报告、可运行 PoC | reports/04-numbering.md, reports/REPORT.md, poc/ |
| architecture | 构建体系、模块图、状态管理、i18n、CSS、REA Evidence | reports/01-architecture.md |
| data-layer | 数据格式与加载策略（桶/区间/缓存/预取/CDN） | reports/02-data.md |
| render-ui | three.js 星图渲染、诗人星团、拾取、交互、UI 流程 | reports/03-render-ui.md |

只写自己的产物文件；不要修改 site/ 与 data/ 下的原始制品。
报告用中文，重证据、重细节，给得出可复现的结论。每条结论后面附证据位置。
