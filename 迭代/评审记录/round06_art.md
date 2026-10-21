# 美术指导（色彩 / 构图 / 光影 / 材质 / 视觉层级）· 第 6 轮评审

**总分：66 / 100**
**与上轮差：0（66 → 66）——不是白干，是换了一次账。**

> 你把我上轮点名的两件事都做了：**金进了气体**（0.89% → 11.3%，84.3% 在 L<60），**水墨冷了、也退到边上了**（1920《登高》页 mean 18.17 → 15.89，边 +2.75、中 +0.79）。
> 但金是用**抬高整片天幕的曝光**换来的：<code>L</code> 从 <code>pow(dens,1.55)*1.28</code> 改成 <code>pow(dens,1.22)*3.0</code>。天幕 mean 20.9 → 51.1、黑场 27.9% → 3.3%、着色面积 37.2% → 70.8%。
> **金亮了，夜没了。** 五个维度里四个动了，净分不动。

**证据先看**：[天幕 R5/R6 对比](r6/c_sky_r5_vs_r6.png) · [200 列卡](r6/c_card_long.png) · [1440 卡头碰撞](r6/c_card_header_1440.png) · [1600 标题](r6/c_title_1600.png) · [TESTC 反事实](r6/c_sky_testC.png)

---

## 实拍条件与口径

- **版本**：<code>杜诗星海.html</code>，5,993,865 B，sha256 <code>593aa343…</code>，mtime <code>2026-10-20 15:53:09</code>；源码 <code>web/index.html</code> 148,184 B、mtime <code>15:29:16</code>。评审开始时作品在 15:26 / 15:29 各落过一版（加「生涯巡游」）；15:53 又修了 40px / aria-checked / 中性声音键 / placeholder / 1366 hint。我把最后这版钉成 <code>评审/r6/_snap3.html</code>（同 sha），**所有实拍都从它出**。15:53 的 40px、<code>#csound</code> 中性、placeholder 亮度、<code>#hint</code> 1366 显示都是这版才有的，前两版的截图已作废重拍。
- **机器**：Edge <code>--headless=new --use-angle=swiftshader</code>（CDP），DPR=1；相机固定 <code>{yaw:.55, pitch:.10, zoom:1}</code>；等 <code>#load</code> 移除、<code>pts()>1400</code> 后 1.5–1.8 s；隐藏自定义光标。页面 <code>window.__errs</code> 全程为空。
- **实拍 24 张全页（22 张主图 + 2 张反事实样张）**（<code>评审/r6/</code>）：1920×1080（default / 12 列卡 / 200 列长卡 / 提示 hover / 长诗整屏 / 滚动 / 1920《登高》卡与整屏 / ink A/B）、1600×900 与 1440×900（default / 长卡 / 长诗整屏）、1366×768（default / 《登高》卡 / 整屏 / 滚到底）、390×844（default / 卡 / 整屏）、生涯巡游一帧。
- **口径**：
  - 着色 = <code>sat≥16 & max≥26</code>；金 = <code>hue 20–60 & sat≥16</code>；气体带 = <code>L 12–60</code>；彩度 = <code>max−min</code>。R5/R6 都用这一支脚本重测，**不拿本表数字与上轮报告直接相减**。
  - 阅读页 A/B：同帧把 <code>#c-art</code> 的 <code>opacity</code> 置 0，只量水墨贡献。
  - 对比度按 WCAG 相对亮度；左栏实际是 <code>#side .sb</code> 的 <code>opacity .62</code> 叠加，不拿单独色值冒充。
  - 文字行数用 <code>Range</code> 逐字取行首；卡片/页脚几何用 <code>getBoundingClientRect</code>。
- **声音不在美术口径内**：①–⑤ 只做代码核对，没有试听结论；⑥⑦⑧ 有可量 UI。

---

## 一、这轮八条，先核对

| # | 声称 | 实测 | 判定 |
|---|---|---|---|
| ① | 新增统一界面音 audCue（悬停/输入/筛选/面板/缩放） | <code>:1868–1906</code> 五类齐全；悬停星 <code>:1982</code> 走 1568 Hz、0.018×0.55、110 ms 节流；输入 <code>:2414</code>、筛选 <code>:2216</code>、面板 <code>:2218</code>、缩放 <code>:2240</code> | **代码成立**（听感不评） |
| ② | 随机钟改走卷积混响 | <code>:1780–1790</code> 生成 1.8 s 指数衰减 IR；<code>audBell</code> 干 0.65 / 湿 0.42 并接 <code>conv</code> | **成立**（代码） |
| ③ | 真诗按题目哈希取五声音阶 | <code>:2131</code> 题名 <code>h*31</code> 哈希 <code>%10</code> 取 <code>_pent</code> 度数；基频 196×2^(deg/12)，覆盖约 196–659 Hz | **成立**（不再只有 196） |
| ④ | 底噪低通 620 Hz + 330 Hz 分音，呼吸改音量与截止 | <code>:1764</code> lowpass 620、<code>:1768</code> triangle 330；<code>audFollow</code> <code>:1945–1958</code> 按可见伪诗数改 <code>air.gain</code> 与 <code>lp.frequency</code>（420–940 Hz） | **成立**（代码） |
| ⑤ | 记忆恢复前先 <code>ctx.resume()</code> | <code>:1734</code> 在 <code>audToggle(true)</code> 前 resume | **成立** |
| ⑥ | 卡片内声音开关补 aria-checked/aria-label、命中 40px 高 | <code>:1724–1727</code> role/label/tabindex；成品 <code>csound</code> **68×40**（不再是 24）；<code>cs.setAttribute('aria-checked',…)</code> 在成品 <code>:1994</code> 已同步 | **成立**（顶栏 <code>#au .s</code> 仍 52×36，不在本句范围） |
| ⑦ | 12 列起就有「整屏读」提示 | <code>p.L.length>=12</code>，全库 **82 首**；12 列卡实测提示 451×28、<code>#c9a227</code>、下划线、<code>pointer</code>；8 列《登高》无提示；点击进整屏 | **成立**（只是"承认看不全"，见 #2） |
| ⑧ | 12 列门槛、回车清空检索态、单金规则 | 12 列门槛成立；Enter 打开最佳并清空 <code>q</code>（<code>:2415–2428</code>）成立；**单金只做到一半**：阅读页声音已中性、退出是唯一金，但**卡片同屏仍有其中 3–4 个金（hint / 滚动条 / 名篇徽章 / 关系页签）** | **半对** |

---

## 二、分维度

| 维度 | R5 | R6 | 差 | 关键证据（同脚本、同机位） |
|---|---|---|---|---|
| 光影 | 74 | **71** | **−3** | 天幕 mean **20.93 → 51.06**、p50 **14.01 → 41.09**、%L<8 **27.93 → 3.32**、%L>80 **1.89 → 19.54**；阅读 1920《登高》的 mean 与黑场修到目标：mean **18.17 → 15.89**、%L<8 **5.14 → 17.26**；L8–25 仍 **75.39**（目标 45–55） |
| 材质 | 70 | **71** | **+1** | 气体彩度 mean 16.56 → 16.45，p90 **32 → 41**，金进尘埃（L<60 占 84.3%）；阅读页栏间 std **2.78（关水墨）→ 3.16（开）**，水墨只在边（左 +2.75 / 上 +6.32 / 中 +0.79）。代价是绿-橄榄带 130–185° 从 **0.43% → 14.46%**，着色区平均饱和 97.5 → 79.9（更满、更灰） |
| 色彩 | 57 | **63** | **+6** | 金 **0.89% → 11.31%**，中位 L **91.4 → 34.9**，L<60 占比 **30.3% → 84.3%**（终于不是星点）；蓝 p50 **211.8° → 197.2°**，图例「日月」实测 **209.2°**，<code>±10°</code> 覆盖着色像素 **51.7% → 15.4%**。但金仍偏褐、整片偏灰，见下 |
| 构图 | 61 | **60** | **−1** | 200 列卡 <code>scrollWidth 10244 / clientWidth 451</code>，**只见 4.4%**；诗条 128 px 高、上下各空 244/255 px；12 列卡仍藏 31%；1366《登高》整屏第 8 行在屏外；1600/1440/1920 长题三种断法（见 #3） |
| 视觉层级 | 66 | **63** | **−3** | 阅读页单金修好（声音已中性）；但卡片仍有 3–4 个金；单屏 7 档（跨屏 9 个值，含 16px×34–41、10.42px×1）；<code>#c-full</code> 15 px 系统滚动条；1366 左栏压页脚；390 底部 4 组被挤成竖排 |
| **综合** | **66** | **66** | **0** | (71+71+63+60+63)/5 = **65.6 → 66** |

---

## 三、这轮真修好的（别回滚）

1. **金真的进了气体，不再只是星点。** 金面积 **0.89% → 11.31%**，其中 **84.3% 的金属像素 L<60**、中位 L **34.9**（R5 是 91.4）——上轮"金只有 0.6% 在暗部"的问题反过来了。<code>goldL</code> 加性项（<code>:1032</code>）是有效的，方向对。
2. **蓝从图例上挪开了。** 最终色相 p50 **211.8° → 197.2°**；图例「日月」点实测 **209.2°**，<code>±10°</code> 从吃掉 **51.7%** 的着色像素降到 **15.4%**。这是量到像素的改动，不是改声明色。
3. **阅读页真的冷下来，而且水墨退到了边上。** 1920《登高》mean **18.17 → 15.89**、%L<8 **5.14 → 17.26**，正好落进上轮给的 14–16 / 15–20；背景 R−B 中位 **−4 → −6**（更冷）。水墨 A/B：整页 **+2.35**，左 **+2.75**、上 **+6.32**、中 **+0.79**、栏间 **+0.30**——"边缘有画、中间干净"这次成立；栏间 std 2.78 → 3.16 也落在 2.2–3.5。
4. **诗区滚动条终于变金了。** <code>#card #c-poem</code> 的 thumb 计算值 **<code>rgba(201,162,39,.55)</code>**（R5 是 <code>rgb(38,40,46)</code>、3px），特异性已压过旧的 <code>#card .poem</code> 规则（<code>:259–261</code>）。
5. **12 列提示成立，且门槛对。** 全库 82 首 12 列；12 列卡实测提示 451×28，金 <code>#c9a227</code>、下划线、<code>pointer</code>，点进整屏；8 列《登高》不显示。提示的**存在**是进步（见 #2 它还不够）。
6. **阅读页控制键的单金修好了。** 15:53 版 <code>#card.reading #csound</code> 被强制中性（<code>:292</code>），1920/1440/390 的整屏只剩「退出」一个金；声音键 40 px 命中且不再像"已打开"。
7. **1920 的 8 行《登高》整屏刚好放得下。** <code>#c-full</code> <code>sh=ch=1054</code>，不再有第 8 行溢出；这是这一版比上轮强的地方（1366 仍失败，见 #3）。
8. **手机 default 的品牌和图例收了。** 390 下品牌回到一行「杜詩星海」，图例从 5 行收到 2 行（R5 是两行品牌 + 5 行图例）；底部控制行虽然更挤（见六），但上半屏干净了。

---

## 四、还剩三条最伤

### 1. 天幕：金有了，夜没了——整片天空被推到中灰（色彩 / 光影）

**证据**

- 同图同机位重测：天幕 **mean 20.93 → 51.06**、**p50 14.01 → 41.09**、**%L<8 27.93 → 3.32**、**%L>80 1.89 → 19.54**、**着色面积 37.19% → 70.85%**。设计宪法 <code>DESIGN.md §3</code> 写的是"大片天空保持近黑，只让约四成面积有气"；现在是**七成有气、几乎没有黑**。
- 金确实到了 **11.31%**，但**中位 L 只有 34.9**，金周围没有黑可以反衬；视觉上它读作**暗褐色的尘**，不是"会发光的赭金"。同时着色像素平均饱和 **97.5 → 79.9**、绿-橄榄带 **0.43% → 14.46%**——为了让金出现，青蓝和灰白被混成了**奶灰/橄榄**。<code>c_sky_r5_vs_r6.png</code> 上下并排：R5 是"夜里的星云"，R6 是"一张铺满的星云壁纸"。
- 根因能指到两行：
  - <code>:1031</code> <code>var L=Math.pow(dens,1.55)*1.28</code> → <code>Math.pow(dens,1.22)*3.0</code>（**亮度整体抬 2.3 倍，指数更低，暗部被拉起来**）。
  - <code>:1025</code> 的 <code>wG</code> 仍参与混色（<code>226,150,78</code>），金既混色又加性；青蓝被 <code>wG</code> 拉褐，再被 <code>goldL</code> 抬亮，于是呈橄榄灰。
- 左栏的底也跟着变亮：竖排主标签从 **6.69:1 → 5.91:1**（还没死），但 9 px 序号从 **1.87:1 → 1.71:1**，<code>02 生平 / 04 评点</code> 正好落在亮云带上——不是"读不出"，是**整条导航从夜里的字变成了云上的字**。

**改法（我已做反事实样张，见 <code>r6_23_sky_testC_1920.png</code>）**

~~~js
// web/index.html:1025–1032, buildNebulaTex()
var wM=Math.exp(-Math.pow((dens-0.52)/0.20,2))*Math.min(1,fil*2.4);
var wB=Math.max(0,1-wM);                 // 金退出混色
var sum=wB+wM+1e-4;
var cr=(wB*18 + wM*198)/sum;
var cg=(wB*156 + wM*52)/sum;
var cb=(wB*198 + wM*118)/sum;
var L=Math.pow(dens,1.55)*1.28;          // 黑场回到 R5
var goldL=Math.pow(dust,1.8)*0.22;       // 金只做第二光源
~~~

**反事实实测（TESTC，同一支脚本）**：mean **51.06 → 25.02**、p50 **41.09 → 19.17**、%L<8 **3.32 → 12.29**、L8–25 **23.75 → 51.56**、着色 **70.85 → 48.16**、**金 11.31 → 11.37（几乎不动）**、金 L<60 **84.3 → 90.4**、气体彩度 **16.45 → 20.05**、蓝 p50 **197.2 → 204.4**、%L>80 **19.54 → 1.89**。<code>c_sky_testC.png</code> 里夜回来了，金开始像尘埃反射。
> 注意：TESTB（<code>goldL .45</code>）金会冲到 **23.75%**，过冲；别再加 <code>goldL</code>，.22 就够。

**再加一道 UI 底**（否则即使 TESTC，9 px 序号也只有约 1.9:1）：

~~~css
#side{background:linear-gradient(90deg,rgba(4,5,10,.72) 0%,rgba(4,5,10,.30) 64%,rgba(4,5,10,0) 100%);
      padding:18px 24px 18px 0}
#meta-r{text-shadow:0 1px 2px rgba(4,5,10,.9)}
~~~

**验收**：天幕 mean **23–27**、%L<8 **10–16%**、着色 **45–52%**、金 **8–12%** 且金 L<60 ≥60%、蓝 p50 **200–206°**、<code>%L>80 <3%</code>；左栏 9 px 序号对比 **≥3:1**、竖排主标签 **≥6:1**。

---

### 2. 诗卡：451 px 里塞 10244 px；40 px 按钮又压到标题上（构图 / 视觉层级）

**证据**

- 1920 长诗卡：<code>#c-poem</code> **451×627**，<code>scrollWidth 10244</code> → **4.4%** 可见（约 8–9 列）；文字条只占 **128 px**（y 419–547），上下各空 **244 / 255 px**，提示在 **y 802**。<code>c_card_long.png</code> 里就是一根悬在卡片中间的细带。
- 12 列卡：<code>scrollWidth 656 / clientWidth 451</code>，**31% 被藏**；提示写着「共 12 列 · 点这里整屏读 ›」——提示是**把内容的失败写成一句话**，不是构图。
- 1366 卡：诗区 **419×153**，上面空 **344 px**、下面空 **271 px**；8 列《登高》被压成一条 153 px 的横带。
- **15:53 的 40 px 命中又制造了一个新碰撞**：<code>.readtoggle</code> <code>top:26 + min-height:40</code> → 底边 66，而 <code>#c-title</code> 顶边 **48**；1440 长题第一行直接穿到「声音 关」按钮下面（<code>c_card_header_1440.png</code>，<code>郑监</code> 与按钮文字重叠）。1920 的标题块（y 48–115）与按钮（y 26–66、x 1720–1850）也在几何上相交。**按钮变大了，标题的位置没让。**

**改法**

~~~js
// select() 末尾：12 列起直接给整屏，别让用户在 451 px 里读 12 列
if(p.L.length>=12 && !readingOn){ setReading(true); card.dataset.autoReading='1'; }
~~~

~~~css
/* 卡片头：给 40px 控件留一条独立带 */
#card .hd{padding-top:56px}
#card .tt{margin-top:0;padding-right:120px}
/* 8 列短诗：别把 flex 压成一条 */
#card .poem{min-height:46vh;align-items:flex-start}
~~~

- 若不想自动整屏，就**把卡加宽到 2 列**（<code>min(760px,56vw)</code>），并让 <code>#c-poem</code> 顶对齐；但 200 列仍必须自动整屏。
- 12 列以上进整屏后，提示应隐藏（<code>body.reading #c-poemhint</code> 已有规则）；别让"提示"替代"能读"。
- 200 列卡改成"整屏 3 列 + 右侧解析"已经是现成的，直接复用。

**验收**：12 列卡要么 12 列全可见、要么自动整屏；200 列打开即 3 列整屏；1366 卡诗区 **≥200 px**、上下不留 >100 px 的空白；标题第一行与按钮 **不相交**（用 <code>Range</code> 逐字量，不靠肉眼）。

---

### 3. 阅读页：每个宽度断一个专名；1366 第 8 行在屏外（构图 / 视觉层级）

**证据（DOM 逐字取行，不是估）**

- **1920**（左栏 689.6 px，66 px）：<code>['秋日夔府咏怀奉寄郑','监李宾客一百韵']</code> → 断在「**郑 / 监**」。
- **1600**（573.5 px）：<code>['秋日夔府咏怀奉','寄郑监李宾客一','百韵']</code> → **3 行**，末行只有「百韵」；拆「一百韵」。
- **1440**（515.4 px）：<code>['秋日夔府咏怀','奉寄郑监李宾','客一百韵']</code> → **3 行**，拆「**李宾 / 客**」。
- **1366《登高》**：<code>#c-full</code> <code>sh 899 / ch 742</code>；首屏最后一行字底 **887**，视口底 **768**，第 8 行「潦倒新停浊酒杯」整行在屏外；滚到底（<code>scrollTop 157</code>）才到 680。没有进度线，只有右侧 **15 px 的 Windows 系统滚动条**（<code>offsetWidth−clientWidth=15</code>，<code>scrollbar-color:auto</code>，带上下箭头），和全站的 5 px 金滚动条不是一个语言。
- 1920《登高》是唯一过关的：<code>sh=ch=1054</code>。也就是说这不是"内容太多"，是**字号没有跟视口走**。

**改法**

~~~js
// renderFull / fitFull：标题按"两行"算字号，再交给 balance
var tw = document.querySelector('#c-full .fs-left').clientWidth;
var half = Math.ceil(p.t.length/2);
var tfs = Math.min(66, tw/(half*1.14));      // 1920→66, 1600→63, 1440→56
titleEl.style.fontSize = tfs+'px';
titleEl.style.textWrap = 'balance';          // 8/8 断，不再 9/7
~~~

~~~js
// 诗：按可用高度落字号；1366 的 8 行必须全在 742 里
var maxLines = p.L.length;
var pfs = Math.min(34, (full.clientHeight - 190)/(maxLines*2.2));
full.style.setProperty('--fs-poem', pfs+'px');
~~~

~~~css
#c-full .fs-ln{font-size:var(--fs-poem,34px)}
#c-full{scrollbar-width:thin;scrollbar-color:rgba(201,162,39,.55) transparent}
#c-full::-webkit-scrollbar{width:5px}
#c-full::-webkit-scrollbar-thumb{background:rgba(201,162,39,.55);border-radius:3px}
/* 200 列时给一根 1px 金进度线，别再让系统滚动条当唯一提示 */
~~~

**验收**：1366《登高》**8 行全在 742 px 内**；1440/1600/1920 长题 **≤2 行**，断点不落在「郑监」「李宾客」「一百韵」内部；<code>sh>ch</code> 时出现金色进度线；<code>#c-full</code> 滚动条宽 **≤5 px**。

---

## 五、没进三条、但同样要修的

| 位置 | 实测（当前 15:53 版） | 应该 |
|---|---|---|
| 卡片「单金」 | 12 列卡同屏：hint 金 + 滚动条金 + 关系「意象」金（登高再加「名篇」金徽章）；⑧ 只在阅读页成立 | 同屏只留一个金：关系页签保留金；hint 改月白+金下划线；滚动条改 <code>rgba(236,231,219,.22)</code>；名篇徽章改纸色描边 |
| 1366 左栏 × 页脚 | <code>#side</code> 底 **650**；<code>#dims</code> 顶 **628** → **22 px** 压字；「检索」行贴在「04 评点」上。15:53 把 <code>#hint</code> 在 ≤1500 打开（<code>:459</code>），<code>#foot</code> 高 **140**，把页脚顶上来 | 1500 以下重新隐藏 <code>#hint</code>，或 <code>#side{gap:20px}</code> / 上移 30 px；验收 1366 左栏与页脚 **不交叠** |
| 40 px 控件 × 标题 | <code>.readtoggle</code> 底 **66**、<code>#c-title</code> 顶 **48**；1440 长题「郑监」与「声音 关」重叠 | 卡片头 <code>padding-top:56px</code>，或把两个按钮移到标题上方独立一行；用 <code>Range</code> 验每行与按钮矩形不相交 |
| <code>#c-full</code> 滚动条 | 系统 **15 px**、有上下箭头、亮灰；全站诗区是 5 px 金 | 5 px 金 + 1 px 进度线（见 #3 代码） |
| 字号阶梯 | 单屏 **7 档**，跨屏 **9 个值**：9/11/12.5/15/16/17.5/23/34/66，另加 sup 的 **10.42**；16 px 出现 34–41 次；12.5 独占 54–77 次 | tick 归 11 或 15；sup 归 9/11；16 要么写进 DESIGN，要么去掉；12.5 的份额分一档给 15 |
| 390 底部控制 | 15:53 新增「生涯 / 巡游」后一行 **4 组、9 个单位**；「着色 / 诗云 / 生涯 / 声音」竖排，巡游框紧贴声音标签；新 <code>#tourcap</code> 在 <code>#card</code> 里，卡片关闭时随 <code>translateX(101%)</code> 出界（15:29 版量得 x≈2091/1920），现有 <code>#phl</code> 已承担同样信息 | 1500 以下拆两行或横滑；隐藏重复的「生涯」标签；把 <code>#tourcap</code> 移到 <code>body</code> 或删掉，别再写在 <code>#card</code> 里 |

---

## 六、一句总评

这轮最值钱的是**方向对了**：金从"星点"进了气体（11.3%），蓝从图例上让开（±10° 覆盖 51.7% → 15.4%），阅读页冷回去了，水墨也退到边上（中 +0.79 / 边 +2.75）——上轮我点名的两条，你都做了。

但你把它们做在了一张**被抬到中灰的底片**上：<code>L</code> 的 1.55/1.28 变成 1.22/3.0，黑场只剩 3.3%，金没有暗处可反，先灰成了橄榄；卡片还是 451 px 里装 10244 px；阅读页还是 66 px 死标题，1440 拆「李宾 / 客」、1600 只剩「百韵」、1366 把最后一行留在屏外。

**金需要黑才亮，卡需要整屏才读，标题需要跟宽度走才不断。** 净分 0：66。下一轮先做 #1 的三行（反事实样张已给，金 11.37% 不动、黑场 12.3%），再谈卡和标题。

---

### 附：本轮实拍索引

- 天幕：<code>r6_01_default_1920.png</code>、<code>c_sky_r5_vs_r6.png</code>、<code>c_nav_contrast.png</code>
- 卡：<code>r6_02_card_12_col_1920.png</code>、<code>r6_03_card_long_1920.png</code>、<code>c_card_long.png</code>、<code>c_hint12.png</code>、<code>r6_17_card_long_1600/1440.png</code>、<code>c_card_header_1440.png</code>
- 阅读：<code>r6_20_full_denggao_1920.png</code>、<code>r6_09_full_denggao_1366.png</code>、<code>r6_15_full_denggao_1366_bottom.png</code>、<code>r6_18_full_long_1600/1440.png</code>、<code>c_title_1600/1440.png</code>、<code>c_1366_cut.png</code>
- 手机：<code>r6_10_mobile390_default.png</code>、<code>r6_11_mobile390_card.png</code>、<code>r6_12_mobile390_full.png</code>、<code>c_mobile_controls.png</code>
- 反事实：<code>r6_22_sky_testB_1920.png</code>（<code>goldL .45</code>，金 23.75% 过冲）、<code>r6_23_sky_testC_1920.png</code>（推荐，金 11.37%、黑 12.3%）
- A/B：<code>r6_20_full_denggao_1920.png</code> / <code>r6_21_full_denggao_1920_noink.png</code>（水墨 +2.35）