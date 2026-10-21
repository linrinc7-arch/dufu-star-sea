# 美术指导（色彩 / 构图 / 光影 / 材质 / 视觉层级）· 第 8 轮评审

**总分：71 / 100**
**与上轮差：+5（66 → 71）——六条全部落地，而且多修了一条没写进清单的：天幕 <code>wG</code>。**

> 三个数字先摆着：<code>#c-full</code> 从 **y=524.4** 回到 **y=22.0**（1920 整屏 51.5% → **98.0%**）；长诗卡正文从 **9958px** 降到 **4200px**（16.7 屏 → **7.1 屏**，比自称的 12 屏还好）；天幕赭橙 **29.0% → 15.6%**、青 **27.2% → 54.1%**、蓝占着色 **37.5% → 64.0%**——testC 是 12.3 / 59.8 / 69.5，**这轮追上了**。
> 但三笔债还在：12–40 行的诗（**387 首，26.4%**）在卡里**只看得到 21.6%**，两轮没动；整屏内容贴在上三分之一，下方 **31–38% 是空场**；导航塌成 5 个 **1.41:1** 的编号，390 长题仍压在按钮下（**760 / 1081.6 px²，与 R7 一个数都不差**）。

**证据先看**：[天幕 R7/R8](r08/c_sky_r7_vs_r8.png) · [整屏 R7/R8](r08/c_full_r7_vs_r8.png) · [导航 R7/R8](r08/c_nav_r7_vs_r8.png) · [页脚 R7/R8](r08/c_foot_r7_vs_r8.png) · [12–40 行的卡](r08/r08_04_card_midcol_1920.png) · [390 长题压按钮](r08/c_m_head.png)

---

## 实拍条件与口径

- **版本**：<code>杜诗星海.html</code>，**5,996,576 B**，sha256 <code>3fcf200d4b3bcce6…</code>，mtime <code>2026-10-20 17:12:46</code>；源码 <code>web/index.html</code> **151,367 B**、mtime <code>17:09:14</code>。钉成 <code>评审/r08/_snap.html</code>（同 sha），**所有实拍从它出**。
- **机器**：Edge <code>--headless=new --use-angle=swiftshader</code>（CDP），DPR=1；相机固定 <code>{yaw:.55, pitch:.10, zoom:1}</code>；等 <code>#load</code> 移除、<code>pts()&gt;1400</code> 后 1.0–1.8 s；隐藏自定义光标。页面 <code>window.__errs</code> 全程为空。
  - 注：首跑时机器上还挂着**上一轮残留的 29 个 headless Edge**，渲染被拖死（<code>127.0.0.1:9401</code> 无响应）。清干净后同一支脚本 4.6 s 起页、全部复现。**所有数字来自清理后的第二轮。**
- **实拍 22 张**（<code>评审/r08/</code>）：1920×1080（默认 / 图例展开 / 《登高》卡 / 40 列卡 / 200 句长卡 / 长卡滚到 50% / 长诗整屏 / 《登高》整屏 / 检索态 / 导航悬停）、1440×900（长诗整屏 /《登高》卡）、1366×768（默认 /《登高》卡 /《登高》整屏 / 整屏滚到底 / 长诗整屏）、1600×900（长诗整屏）、390×844（默认 / 长卡 /《登高》整屏 / 图例展开）。
- **口径**：与 R7 **同一支脚本**（<code>_stats8.py</code> 复用 <code>_stats7.py</code> 的 HSV/亮度定义，<code>_con8.py</code> 复用 WCAG 相对亮度），所以两轮数字可直接相减，不与上轮报告里的数比。
  - 着色 = <code>sat≥16 &amp; max≥26</code>；金 = <code>hue 20–60 &amp; sat≥16</code>；赭橙 <code>20–35</code>、真金 <code>35–50</code>、青 <code>185–215</code>、洋红 <code>280–330</code>（占**着色像素**份额）；气体彩度 = <code>max−min</code>。
  - **天幕是确定性的**：<code>buildNebulaTex()</code> 的 <code>seed=17.3</code>、噪声全为 nFbm，无 <code>Math.random</code>。所以两轮天幕像素差**可以归因到代码**，不是随机。
- **声音不在美术口径内**：⑥ 只做代码核对，没有试听。

---

## 一、六条核对：这一轮**六条全中**，外加一条没写在清单里的

| # | 声称 | 实测 | 判定 |
|---|---|---|---|
| ① | 左侧导航只显示当前章节标题，其余只留编号，悬停展开 | <code>.sb span{max-height:0;opacity:0}</code>（<code>:85–88</code>）；实测 <code>['00' 0/0, '01' 42.5/1, '02' 0/0, '03' 0/0, '04' 0/0]</code>；真实鼠标悬停 02：只有 02 的 <code>span</code> 长到 42.5、opacity 1 | **成立**（代价见四.3） |
| ② | 图例默认收起，底部一枚「图例」按钮 | <code>#legend.collapsed{display:none}</code>（<code>:305</code>）；<code>renderLegend()</code> 首行 <code>lg.classList.add('collapsed')</code>（<code>:2331</code>）；实测 <code>display:none、rect 0×0</code>，按钮 <code>54.5×30 @ (46,1020)</code>，点开后 <code>flex</code>、10 类、940×34 | **成立** |
| ③ | 长诗卡两句一行（200 句 25.6 屏 → 12 屏） | <code>:2167–2179</code> 每两行一个 <code>.row</code>；实测 200 句 → **100 个 row**、<code>sw 441 = cw 441</code>、<code>sh 4200 / ch 595</code> = **7.06 屏**（R7 是 9958 = 16.7 屏）；最宽一行 381 ≤ 441，**无横向裁切** | **成立，且好于声称** |
| ④ | 长诗全屏窄屏两栏 | <code>.fs-left.long{column-count:2}</code>（<code>:278</code>）、<code>≥1700px → 3</code>（<code>:279</code>）；实测 1366/1440/1600 = <code>cols 2</code>、1920 = <code>cols 3</code> | **成立** |
| ⑤ | 正文 <code>clamp(15,min(1.9vw,3vh),23)</code>、标题 <code>clamp(23,min(3.2vw,4.2vh),34)</code> | <code>:282 / :286</code>；计算值 1920/1440 **34px**、1366 **32.256px**；正文 1920/1366 **23px**、390 **15px** | **成立** |
| ⑥ | 空气层 1400Hz、随机钟进卷积、真诗按题目取五声音阶、<code>var base</code> 已修 | <code>:1799</code> <code>bandpass 1400</code> ✓；<code>:1833–1835</code> <code>outB→conv + dry</code> ✓；<code>:1868–1870</code> <code>_pent=[0,2,4,7,9,12,14,16,19,21]</code>、<code>base=196*2^(_pent[deg%10]/12)</code>、<code>deg</code> 来自题名哈希（<code>:2153</code>）✓ | **代码成立**（不试听） |
| ★ | （未声称）天幕金退出混色 | <code>:1046–1051</code> **<code>wG</code> 整行已删**，<code>wB=1-wM</code>；实测见二.色彩 | **成立**——这是 R7 的 #2 |

---

## 二、分维度

| 维度 | R7 | R8 | 差 | 关键证据（同脚本、同机位、同机） |
|---|---|---|---|---|
| 光影 | 77 | **79** | **+2** | meanL **26.85 → 25.87**、p50 **20.97 → 20.26**、%L&lt;8 **10.32 → 10.98**、L8–25 **49.34 → 50.51**、%L&gt;80 **2.11 → 1.81**、着色 **47.27 → 50.01**——R7 的七条验收**落六条**，只有金面积 **13.89%** 还高 0.9pp（带 8–12）。扣：金仍不发光（金中位亮度 **26.3**、L≥60 只占 **8.3%**，最亮的仍是洋红脊线 L 51.4） |
| 材质 | 72 | **75** | **+3** | 气体彩度 mean **15.13 → 19.32**、p90 **29 → 34**（testC 21.12 / 37）；着色面积 +2.7pp，丝状脊在黑底上的层次回来了。扣：金 chroma 仍 **10**，没有金属反光；尘埃是弥散雾，不是颗粒 |
| 色彩 | 64 | **72** | **+8** | 全帧：赭橙 **29.0% → 15.6%**、青 **27.2% → 54.1%**、蓝占着色 **37.5% → 64.0%**、金 **22.72% → 13.89%**；裁切区（260,100–1500,820）：赭橙 **26.5 → 14.3**、青 **30.8 → 57.4**、蓝 **42.7 → 66.7**、金 **22.26 → 13.61**、彩度 **15.36 → 20.47**。**testC = 12.3 / 59.8 / 69.5 / 11.38 / 21.12**——四条齐了。扣：ochre 15.6 仍高 1.6pp、金 13.9 高 0.9pp、彩度 14.0（裁切区）差 2 |
| 构图 | 57 | **67** | **+10** | + 整屏 <code>y 524.4 → 22.0</code>、<code>h 555.6 → 1058</code>（**98.0%** 视口）；+ 1366《登高》第 8 行底 **837 → 523.6**（全在 742 内）；+ 长题 **66px 三行 → 34px 一/两行**，1440/1600/1366 都断在「奉寄 / 郑监」；+ 长卡 9958 → **4200**、<code>sw=cw</code>。− 12–40 行 **387 首**仍 <code>2084/451</code>；− 整屏内容贴顶、下方空场；− 长诗 2/3 栏读序断裂 |
| 视觉层级 | 61 | **64** | **+3** | + 页脚 **208 → 162px**（收起 10 类图例）；+ 整屏字号落到 **34 / 23 / 17.5 / 12.5** 四档；+ hint 改「共 200 行」（R7 是「200 列」）。− 导航编号 **1.41:1**；− 页脚第 3 行只剩一枚「图例」；− 同屏仍 ≥7 处金；− 390 长题压按钮 760/1081.6 px² 不变 |
| **综合** | **66** | **71** | **+5** | (79+75+72+67+64)/5 = **71.4 → 71** |

---

## 三、这轮真修好的（别回滚）

1. **「整屏读」回来了，而且回得比 R6 更彻底。** <code>#c-full</code> 1920 <code>{y:22.0, h:1058}</code>（98.0%）、1440 <code>{y:22, h:878}</code>（97.6%）、1366 <code>{y:26, h:742}</code>（96.6%）。对比图 <code>c_full_r7_vs_r8.png</code>：R7 上半屏是卡里 9 行「马来皆汗血…」的重复 + 66px 两行大标题，第一屏只看得见一行诗；R8 标题在顶、三栏正文从 y=194 开始，一屏读 22 行。R7 的 #1 是**一行 CSS** 的事（<code>#card.reading #c-poem.horiz{display:none!important}</code>，<code>:307</code>），你写了。
2. **长题不再跟字符总数走。** 34px + <code>text-wrap:balance</code> 之后：1920 一行、1440/1600/1366 两行，**三种宽度断点都是「奉寄 / 郑监」**——正是 R7 点名的那个语义断点。R7 的三行「秋日夔府咏怀奉 / 寄郑监李宾客一 / 百韵」没有了。
3. **1366 的八行整整齐齐在屏内。**《登高》<code>.fs-ln</code> 23px/42.55px，第 8 行底 **523.6 &lt; 768**（R7 是 837）；滚到底也不需要了（R7 要滚 157px）。
4. **天幕的金退出混色，颜色终于像 testC。** <code>wG</code> 那一行没了，蓝占着色 37.5 → **64.0**、青 27.2 → **54.1**、赭橙 29.0 → **15.6**。左边 R7、右边 R8 的 <code>c_sky_r7_vs_r8.png</code>：R7 整个画面蒙一层暖褐，R8 的褐收回到尘埃区，青蓝回到星空本体。
5. **长诗卡两句一行是对的。** 200 句 100 行、<code>sw = cw = 441</code>、最宽行 381，**没有把一句裁成两截**；竖排时代那根「悬在卡片中间的细带」和 4.4% 可见率都成了历史。
6. **页脚轻了 46px，导航让出了右半边。** 图例收起后 <code>#foot</code> 162px（R7 208），默认态左栏只剩「01 星海」一条标题，画面的第一读数不再是五条竖排汉字。
7. **声音按题名落五声音阶**（<code>_pent</code> + 题名哈希），不再是每首同一个 196Hz——这是把「同一首诗每次进来是同一记磬」变成了可辨认的身份，方向是对的。

---

## 四、还剩三条最伤

### 1. 12–40 行的诗（387 首，26.4%）在卡里只看得到 21.6%——两轮没动，而长诗那 57 首修了两轮

**证据**

- 40 句《奉同郭给事汤东灵湫作》：<code>#c-poem</code> <code>sw **2084** / cw **451**</code> → **21.6%** 可见（本轮实测，与 R7 一字不差）；40 列里只露 **8 列**。
- 同一帧里 <code>#c-poem</code> <code>sh 618 / ch 618</code>——盒子是满高的，可 8 列 5 言只占 **~150px**，上下各空 **210 / 250px**：一块 452×618 的黑，中间一小撮字（<code>r08_04_card_midcol_1920.png</code>）。
- 提示语把「看不全」写成一句话：<code>共 40 列 · 点这里整屏读 ›</code>（金、12.5px、<code>y=801.8</code>）。
- 数量级：全库 1468 首里 **12–40 行 = 387 首（26.4%）**，是 &gt;40 行那 **57 首**的 **6.8 倍**。你两轮把 3.9% 做到接近满分，把 26.4% 留在原地。
- 门槛就一行：<code>:2165</code> <code>var _long = p.L.length &gt; 40;</code>

**改法**（二选一，优先 A）

~~~js
// A. 门槛从 40 降到 12——直接复用已经跑通的「两句一行 + 纵向滚」
var _long = p.L.length > 12;                    // web/index.html:2165
// 配套：hint 的文案单位别再写死「列」
var _unit = _long ? ' 句' : ' 列';               // :2203
~~~

~~~css
/* B. 不改门槛也能救一半：让 12 行以上的竖排先落 15px、列宽收到 30px，多露 60% 的列 */
#card #c-poem .col{font-size:15px}
#card .poem{padding:26px 18px;gap:10px}
~~~

**验收**：40 句卡 <code>sw/cw ≥ 0.95</code>（或「两句一行」后 <code>sh ≤ 1200</code>、纵向可滚）；hint 不再出现「共 40 列」；387 首里抽 5 首，<code>sw/cw</code> 全部 ≥0.9。

---

### 2. 整屏的竖向构图：内容贴在上三分之一，下方 31–38% 是空场；长诗 2/3 栏的读序是断的

**证据**

- 1920《登高》整屏：<code>#c-full {y:22, h:1058}</code>，标题 <code>y=149.8</code>、正文 <code>278.7 → 619.0</code>、<code>.fs-note</code> 到 **668**。**块心 409px，视口中心 540px**——整块高悬 131px，下方 **412px（38%）无物**；右栏写到 880 也停，右下再空 200px。
- 成因不是「内容少」，是 <code>#c-full{align-content:safe center; align-items:start}</code>：被居中的是**行**（行高由右栏 800px 决定），左栏在行内**顶对齐**。
- 长诗：1440 <code>.fs-left.long</code> 2 栏 <code>w 515.4 / h 4587</code>、视口 878 → 每栏 **235.7×2293（2.6 屏）**；1920 3 栏 <code>h 3062</code>、每栏 ~1020px。多栏 + 单滚动轴 = 读完第 1 栏要**滚回顶部**才能接第 2 栏；而且 5 言行宽只有 133.4px，在 235.7px 栏里居中后每侧留 **51px**，栏间视觉空隙实得 **146px**——三条互不相干的竖带。
- 附带一个状态 bug：进出全屏**不重置 <code>#c-full.scrollTop</code>**。1366 实测进整屏后 <code>st=123</code>，标题被推出屏外（<code>.fs-t</code> <code>y=-70.3</code>），顶上只剩一行「唐 · 杜甫」飘着（<code>r08_17_full_long_1366.png</code>）。

**改法**

~~~css
/* ① 短诗在右栏内垂直居中；长诗因溢出自动回到顶（safe） */
#c-full{align-items:safe center}

/* ② 长诗别用报纸栏：1 栏 + 两句一行，行数减半、读序连续 */
#c-full .fs-left.long{column-count:1}
#c-full .fs-left.long .fs-ln{font-size:clamp(17px,min(1.5vw,2.2vh),21px)}
~~~

~~~js
// ③ 进全屏 / 换诗，滚动位置归零
function setReading(on){ /* 现有实现末尾 */ document.getElementById('c-full').scrollTop=0; }
// renderFull(p) 末尾同理
~~~

**验收**：1920/1366《登高》整屏块心与视口中心差 **≤60px**；底部空场 **≤20%**；长诗整屏滚到底时**同栏接续**（无跳栏）；进整屏与换诗后 <code>scrollTop = 0</code>。

---

### 3. 导航塌成 5 个 1.41:1 的编号（唯一入口），且 390 长题仍压在按钮下

**证据**

- 导航：<code>.sb i</code> 9px <code>#5f5c53</code>、父级 <code>opacity .42</code>；实测对比度 **1.41:1**（00、03 两次取样），比 R7 的 1.82 还低。而它现在是 4/5 章节的**唯一可点入口**。
- 间距不齐：<code>.sb</code> 顶边 <code>387.7 / 441.7 / 560.3 / 614.3 / 668.3</code> → 步长 **54 / 118.6 / 54 / 54**（当前章的 42.5px 标题 + 22px 金线把 02 推下去 64px）。
- 悬停还会**整列重排**：悬停 02 时 <code>#side</code> 高 **304.5 → 347.1**（<code>translateY(-50%)</code> 居中），03 从 614.3 掉到 **635.5**——点一个，另外三个跳。
- 390：《秋日夔府咏怀奉寄郑监李宾客一百韵》标题盒 <code>(38.6, 40, 327.4)</code> 与「全屏」(272.5,16,47.5,40) 交 **760 px²**、与「声音」(190.4,16,67.6,40) 交 **1081.6 px²**——**与 R7 完全相同**，截图 <code>c_m_head.png</code> 里「寄」被按钮描边压住。⑤ 的 clamp 只管 <code>#c-full .fs-t</code>，卡内的 <code>.tt</code> 没动。

**改法**

~~~css
/* 编号是唯一线索了，就得读得见，并且等距 */
.sb{min-height:54px;justify-content:center}
.sb i{font-size:11px;color:#8d887c}
.sb{opacity:.72}
.sb:hover,.sb.on{opacity:1}
/* 展开时不要再挤别人：用绝对定位的浮层 */
.sb span{position:absolute;left:100%;margin-left:10px}

/* 390：给按钮留出 56px，标题不再往右上跑 */
@media (max-width:700px){
  #card .hd{padding-top:56px;padding-right:24px}
  #c-title{max-width:100%}
}
~~~

**验收**：导航编号对比度 **≥4.5:1**；5 个编号顶边等距（±2px）；悬停时其它项位移 **0**；390 长题与「全屏」「声音」交集 **0 px²**。

---

## 五、没进三条、但同样要修

| 位置 | 实测（本版） | 应该 |
|---|---|---|
| <code>#c-full</code> 滚动条 | 仍是 **15px 系统灰**（<code>cw 1905/1920、1351/1366、1425/1440</code>），<code>::-webkit-scrollbar-thumb</code> 计算值 <code>rgba(0,0,0,0)</code>，带箭头、亮灰，是全站唯一的原生控件 | 5px、<code>rgba(236,231,219,.18)</code> 或金 <code>.45</code>；<code>scrollbar-width:thin</code> |
| 长诗卡的 flex gap | 100 行 × (25.8 + **16**) = 4180；**1584px（38%）是空滚**（R7 建议的 <code>#card #c-poem.horiz{gap:0}</code> 没加） | <code>gap:0</code> + <code>line-height:1.95</code> → <code>sh ≈ 2616</code> |
| 两句一行的右半 | <code>:2175</code> <code>b.style.marginLeft='2.2em'</code> 是**行内偏移**，右半起点跟着左半字数跑：**18/57 首**长诗行内混长（5/6/7/8/10 字），**8 首**错位 ≥1 字，最多 **5 字 / 79px**（《赠蜀僧闾丘师兄》5+10 字） | <code>.row{display:grid;grid-template-columns:1fr 1fr}</code>，两半各占一列 |
| 卡内竖排诗 | 1366 <code>sh 167 / ch 153</code>、1440 <code>sh 197 / ch 188</code> → 末字被切 **9–14px**（<code>fitPoem</code> 的 1.34 系数偏小） | 系数改 **1.42**，或 <code>#card .poem</code> 竖向内边距 26 → 14 |
| 单金 | 同屏仍 **≥7 处**金：名篇徽章、<code>#c-bar</code>、hint、<code>#c-poem</code> 滚动条 <code>.55</code>、关系页签、正文 <code>em</code>、页脚两枚选中 chip、左栏当前章 | 只留关系页签；hint 改月白 + 金下划线；滚动条 <code>rgba(236,231,219,.22)</code> |
| 页脚第 2 行 | 「生涯」标签**没有专属规则**：计算值 **16px**（同排其它 label 12.5）、<code>margin-right:0</code>，右缘 **352.5** 与「巡游」左缘 **352.5** **零间隙**；「巡游」右缘 **419** 又与「声音」左缘 **419** 零间隙 | 补 <code>#sy2 .lab{font-size:12.5px;letter-spacing:.3em;color:#8a8578;margin-right:12px}</code>；组间距 8px |
| 「图例」按钮 | 独占第 3 行、左对齐、<code>54.5×30 @ (46,1020)</code>，右侧 940px 空着；页脚三行宽 355 / 480 / 54.5，右缘全不齐 | 并到 <code>.ctrlrow</code> 末尾（<code>margin-left:auto</code>）或做成页脚右下角图标 |
| 「伪诗」chip | <code>#sytog</code> 默认带 <code>.on</code>，填充 <code>rgba(236,231,219,.62)</code>——**全屏最亮的实心块**，比选中的金 chip 还抢 | 同一排里「选中」只留一种语言（金），伪诗改金描边态 |
| 390 品牌副标 | <code>.brand .en</code> 仍折成两行「THE STAR SEA OF DU / FU」、**1.55:1** | <code>white-space:nowrap</code> 或 ≤700 隐藏 |
| 字号阶梯 | 单屏仍 6 档：9 / 11 / 12.5 / 15 / 17.5 / 23（整屏 4 档已好转） | 9 并入 11；12.5 的份额分一档给 15 |

---

## 六、一句总评

这轮是**七轮里第一次六条声称全部落地**，而且落得准：整屏从 51.5% 回到 98.0%（R7 的 #1，一行 CSS 的事你写了）、长题在四种宽度上断在同一个语义点上、1366 的第八行终于进了屏、长诗卡 9958 → 4200 且不裁字。**更值钱的是你没写在清单里的那一条**：<code>wG</code> 归零之后，赭橙 29.0 → 15.6、青 27.2 → 54.1、蓝占着色 37.5 → 64.0，**testC 的三个数全追上了**——「金」第一次不是褐雾，是落在青蓝夜上的尘。

所以 +5，71 分。但这 5 分几乎全在「把该开的那扇门打开了」，而不是「屋子布置好了」：**门开了以后，屋里还是空的**——1920《登高》整屏的块心在 409px，下方 412px 什么也没有；**而那扇一直没开的门是 387 首（26.4%）的 12–40 行卡**，它们两轮都在 21.6% 的可见率上原地不动，hint 还替你把「看不全」写成了文案。下一轮先做两件事：<code>_long</code> 的 40 改 12，和 <code>#c-full{align-items:safe center}</code>——又是两行。

**净分 +5：71。** 这轮的天幕和整屏，已经是这份作品的最高点；剩下的分数全在「26.4% 的那批诗」和「空着的下半屏」里。

---

### 附：本轮实拍索引（<code>评审/r08/</code>）

- **默认态**：<code>r08_01_default_1920.png</code>、<code>r08_02_default_legend_1920.png</code>（图例展开）、<code>r08_09_search_1920.png</code>、<code>r08_10_nav_hover_1920.png</code>、<code>r08_13_default_1366.png</code>、<code>r08_19_mobile_default_390.png</code>、<code>r08_22_mobile_legend_390.png</code>
- **诗卡**：<code>r08_03_card_denggao_1920.png</code>、<code>r08_04_card_midcol_1920.png</code>（40 句，21.6%）、<code>r08_05_card_long_1920.png</code>（200 句）、<code>r08_06_card_long_scrolled_1920.png</code>、<code>r08_12_card_denggao_1440.png</code>、<code>r08_14_card_denggao_1366.png</code>、<code>r08_20_mobile_card_long_390.png</code>；细节 <code>c_m_head.png</code>、<code>c_1366_card.png</code>、<code>c_longcard_body.png</code>
- **整屏**：<code>r08_07_full_long_1920.png</code>、<code>r08_08_full_denggao_1920.png</code>、<code>r08_11_full_long_1440.png</code>、<code>r08_15_full_denggao_1366.png</code>、<code>r08_16_full_denggao_1366_bottom.png</code>、<code>r08_17_full_long_1366.png</code>、<code>r08_18_full_long_1600.png</code>、<code>r08_21_mobile_full_390.png</code>；细节 <code>c_full_dg_left.png</code>
- **对照**：<code>c_sky_r7_vs_r8.png</code>、<code>c_full_r7_vs_r8.png</code>、<code>c_nav_r7_vs_r8.png</code>、<code>c_nav.png</code>、<code>c_foot.png</code>、<code>c_foot_open.png</code>、<code>c_r07_foot.png</code>
- **数据**：<code>probe8.json</code>（22 个状态的几何/计算样式）、<code>_stats8.py</code> / <code>_stats8b.py</code> / <code>_con8.py</code>（像素与对比度口径）、<code>_cap8.py</code>（实拍脚本）、<code>_foot8.py</code>（页脚控制几何）
