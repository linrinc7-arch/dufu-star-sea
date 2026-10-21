# 交互与产品设计（信息架构 / 可发现性 / 状态反馈 / 适配）· 第 4 轮评审

**总分：68 / 100**（上轮 64，**+4**）

评审对象：`杜诗星海.html` 2026-10-20 **14:17** 构建（5,982,528 B，md5 `3960c50e…`），源码 `web/index.html` 14:17 版（137,319 B / 2,940 行）。
实拍：Edge headless + CDP，1920×1080 / 1366×768 / 390×844（`Emulation.setTouchEmulationEnabled`），关虚拟时间，等 `#load` 移除后再取帧。性能数字在 swiftshader 下取得，只作相对参考。截图与探针在 `评审/r4_ux/`（`评审/r4/` 被并行的字体评审占用，未动）。

![默认 1920](r4_ux/ux_01_default_1920.png)

## 一句话

触屏终于能点开第一首诗了，长诗卡也终于有了一句「共 200 列」——但两处都只修到一半：关掉卡片后，手机点哪儿都重开同一首；点「整屏读」进去，390 宽上 34px 的诗句直接压到右栏分析文字上，66px 的标题一个字一行。首屏仍然没有任何一个诗题，唯一可见的入口是一个 1.88:1 的输入框。

## 与上轮的差（只列实测）

| 项 | 上轮 64 分那次 | 本轮 14:17 构建 | 判定 |
| --- | --- | --- | --- |
| 触屏首点 | 点《赠李白》→ `ReferenceError`，卡片不出现 | 390 宽 tap《陪郑广文…》→ 卡片打开、`sel` 一致、0 异常 | ✅ 修好 |
| 触屏第二点 | —（首点已死，测不到） | 关掉卡后点 90px 外的《木皮岭》→ 重开《陪郑广文…》 | ❌ 新暴露 |
| 点白噪音星 | 抛 `ReferenceError: p` | 仍抛 `ReferenceError: p is not defined`（卡片能开，异常在 `.on` 之后） | ❌ 没修 |
| 长诗卡提示 | 无；8,308px 横滚 | 9,070px；有「共 200 列 · 点这里整屏读 ›」，但只在 ≥24 列出现 | ⚠️ 半修 |
| 诗区滚动条 | 3px `#26282E` | 3px `#26282E`（计算值 `rgb(38,40,46)`） | ❌ 宣称的金色没有 |
| 200 行全屏 | 3.1 屏 @1920 / 4.35 @1366 | **3.26 / 4.77 屏**；右栏 sticky 仍成立 | ⚠️ 略长 |
| 短诗全屏（桌面） | 未单测 | 《登高》单栏 34px，1.02 屏 | ✅ 好 |
| 短诗全屏（390） | 上轮判「单栏、不叠字」 | 诗句行盒 141px、文字宽 276px，**压过右栏 103px** | ❌ 上轮误判，实际叠字 |
| 长诗全屏（390） | 未测 | 66px 标题 **16 行 / 1,584px**；全屏 4,756 / 796 = **5.98 屏** | ❌ 不可读 |
| 字号 | 20 多个值 | 7 个 token（9/11/12.5/15/23/34/66）+ 竖排 17.5；默认屏可见 4 档；检索框仍 13.3333px | ⚠️ 基本收口 |
| 检索 placeholder | 1.88:1 | **1.88:1**（仍 `#3F3D37`） | ❌ |
| POEMS 计数 | 2.60:1 | **2.60:1**（9px `#55524A`） | ❌ |
| 回车后状态 | 不同步 | 仍不同步：真输入「明月」时计数 7、天幕已筛；Enter 打开首条后，输入框仍写「明月」、计数仍停在 **7**、`state().q=null`、维度仍「意象」——界面说还在筛，实际已清空 | ❌ |
| 阅读态双金 | 声音 / 退出都金 | 仍双金：`#csound` 与 `#readtoggle` 同挂 `.readtoggle`，reading 下同被刷金 | ❌ |
| 键盘 | Tab 3 站 | Tab 4 站；卡片关闭时 `#csound`（x=2177，屏外）仍可聚焦；`readtoggle`/`close` 仍不可达 | ❌ |
| 手机底栏 | 256px | **266px = 31.5% 屏高**；品牌两行、左导航压进底栏 | ❌ |
| 1366 卡内长标题 | 未测 | 标题首行 `[967,41,248,26]` 与「声音 关」`[1166,30,68,24]` **相交** | ❌ |
| 顶 / 底局部压暗 | — | 两条渐变都在（top `.85→0`、foot `.90→0`），底栏可读性确有改善 | ✅ 有，但救不了 1.88:1 |

## 这轮五项改动，逐条对账

| # | 说法 | 实测 | 判定 |
| --- | --- | --- | --- |
| ① | 字号收口到 8 档 | `--t1…--t7` 已建（9/11/12.5/15/23/34/66），加竖排诗的 17.5 共 8 档；默认屏实际显示 9/11/12.5/17.5，全屏加 34/66。**但 `#search input` 是 13.3333px**（`font:12px/1 inherit` 是非法简写，整条被丢弃，落到浏览器默认），卡片里的「≈推定」是 10.4167px，`.phead`/`#load .ttl` 仍是 `clamp()`。15px 这一档在首屏没有用武之地。 | ⚠️ 约九成，入口控件恰是例外 |
| ② | 长诗卡提示改成可点的金色链接；诗区加金色滚动条 | `#c-poemhint` 的 `onclick` 真的接上了（桌面真点击、手机 tap 都能进全屏），文字也是「共 200 列 · 点这里整屏读 ›」。**但颜色是 `rgb(138,133,122)`，`cursor:none`，无下划线、无 hover 变化**；滚动条计算值仍是 `rgb(38,40,46)` / 3px。且判定写死 `p.L.length>=24`：12/15/18/20 列的卡片照样横滚，却一个字提示都没有。 | ⚠️ 可点，但不金；只在极端长诗出现 |
| ③ | 触屏点星崩溃已修（click 先 pick） | 真诗路径修好了：首点开卡、拖拽只转天幕不开卡、关闭 X 正常。**但 `closeCard()` 不清 `hover`，`click()` 又只在 `!hover` 时重算** → 关掉后点任意位置都重开上一首；灰色 tooltip 留在天幕上。白噪音路径也没修：`selectNoise()` 第 1980 行仍写 `p.L.length`，而 `typeof p === "undefined"`。 | ⚠️ 只修好第一下 |
| ④ | 全屏短诗单栏、长诗三栏、右栏 sticky | 桌面成立：8 行单栏 1.02 屏；200 行三栏 3.26 屏；右栏滚到 1,300px 仍 sticky。**但 390 宽没有分支**：短诗行盒 141px 装 276px 的字，压到右栏；长诗 66px 标题 16 行；三栏挤在 141px 里。另外 40 行单栏 3.37 屏、61 行三栏 1.31 屏——长度翻倍，阅读反而短一半。 | ⚠️ 桌面成立，窄屏崩 |
| ⑤ | 底栏 / 顶栏加局部压暗 | 两条渐变确实加了；底栏图例、按钮的可读性比上轮好。顶部压暗只压了背景，没有改字色：placeholder 仍 1.88:1，`POEMS` 仍 2.60:1。 | ✅ 有，但只解决一半 |

## 仍然最伤的三条

按「找到 → 点开 → 读完」这条主线排，不是按字数。

### 1. 找到：首屏仍然没有一个诗题，唯一入口是 1.88:1 的输入框

- 整个文件 `fillText` = **0**，天幕上没有任何诗题；触屏没有 hover，所以「点星读诗」在手机上等于「盲点」。
- 检索框 `#search` 187×24，`input` 只有 **150×16**；placeholder `#3F3D37`，实测 **1.88:1**（局部背景采样 `(3,5,8)`，压暗后并没有变好）。
- 唯一的命题数字 `POEMS 1468 · 712—770` 是 9px、`#55524A`、**2.60:1**。
- 这轮新加的「共 N 列」提示在卡片里，解决的是「读不完」，不是「找不到」。上轮给入口开的两条方子（placeholder 换色、首屏给 6–12 个名篇入口）一条没落地。

![1366 首屏：检索框几乎不存在](r4_ux/crop_search_1366_4x.png)

**改法（约 30 分钟）**

```css
#search input::placeholder{color:#8a8578}     /* 5.7:1 */
#meta-r .num{color:#8a8578}
#search{min-height:34px;border-bottom-color:rgba(236,231,219,.24)}
#search input{font:inherit;font-size:12.5px;width:190px}
```

```html
<!-- 首屏底栏上方常驻 6 个名篇入口；触屏也显示 -->
<div id="starts"><b>从这儿进</b>
  <span data-t="登高">登高</span><span data-t="春望">春望</span>
  <span data-t="月夜">月夜</span><span data-t="秋兴八首 一">秋兴</span>
  <span data-t="茅屋为秋风所破歌">茅屋</span><span data-t="望岳">望岳</span>
</div>
```

```js
// 绑定用现成的 selectByTitle，别再靠 26px 星距去猜
[].forEach.call(document.querySelectorAll('#starts span'),function(el){
  el.onclick=function(){ __DUFU_DEBUG.selectByTitle(el.dataset.t); };
});
```

**验收**：placeholder / 计数 ≥4.5:1；390 首屏能看见并点开至少 6 个诗题；检索框高度 ≥34px。

### 2. 点开：触屏只修好了第一下，第二下永远回到同一首

- 实测 A→关→B：tap《陪郑广文…》(194,359) 开卡；点 X 关闭；再点 90px 外的《木皮岭》(255,292)——**开的还是《陪郑广文…》**，`sel` 也一样，0 异常。
- 原因在状态：`hover` 只在 `pointermove` 里更新；触摸点按不产生 `pointermove`；`click()` 第 1931 行是 `if(!hover) pick(...)`，于是一直用旧值；`closeCard()` 也没有清 `hover` / `tip`。关闭后那块「陪郑广文游何将军山林十首 十 / 五言律诗 · 40字」的 tooltip 还悬在天幕上。
- 白噪音路径仍会抛错：点 (783,274) 打开「白噪音 23455」，`#c-no` 正确、卡片也开了，但控制台 `Uncaught ReferenceError: p is not defined`——`selectNoise()` 第 1980 行还在写 `p.L.length`（该函数里没有 `p`；全站 `typeof p` 为 `undefined`）。全站有 **24,000** 个白噪音点，这条路不是边角。

![手机：关掉卡片后 tooltip 留在天上](r4_ux/ux_13_mobile_after_close_390.png)

**改法（约 15 分钟）**

```js
function click(mx,my){
  pick(mx,my);                       // 无条件按当前点重算，别信上一次的快照
  if(hover){ select(hover); return; }
  var po=pcPick(mx,my,18);
  if(po) selectNoise(po);
}
function closeCard(){
  card.classList.remove('on'); selected=null; query=null; constellation=null;
  hover=null; tip.classList.remove('on');   // 新增：清悬停与 tooltip
  document.getElementById('q').value=''; updCount();
}
```

```js
// selectNoise 第 1978-1982 行整段删掉（四句白噪音不需要「共 N 列」），
// 如果一定要保留，把 p 改成 po，并判 po.L.length。
```

**验收**：关掉卡后点任意一颗星 → 开的是那颗星；天幕上不留 tooltip；点白噪音星 → 卡片出现、控制台 0 异常；拖拽仍不开卡。

### 3. 读完：全屏在窄屏是坏的，在桌面也没有「读到哪」的状态

**3a. 390 宽全屏直接叠字 / 崩版**

- 短诗《登高》：`.fs-ln` 行盒 141px，文字实宽 **276px**，右栏从 x=200 开始——诗句压过去 **103px**，和「诗中之意」逐字重叠（见下）。
- 长诗《秋日夔府咏怀…》：66px 标题在 141px 栏里 **16 行 / 1,584px**，标题自己占两屏；全屏 `scrollHeight 4,756 / 796` = **5.98 屏**；三栏挤在 141px 里；顶部「共 200 列 · 点这里整屏读 ›」还被「声音 关 / 全屏」两个金按钮压住。
- 根因不是诗句字号，是 `#c-full` 的 `grid-template-columns` 在 390 下仍是 `1fr / 1.15fr`，而这个视图现在被卡片上的提示主动推销给手机用户。

![手机全屏短诗：诗句压到右栏上](r4_ux/ux_19_mobile_full_short_390.png)
![手机全屏长诗：66px 标题一个字一行](r4_ux/ux_17_mobile_long_full_390.png)

**3b. 桌面：入口在，状态不在**

- 提示只在 ≥24 列出现。12 列卡 `scrollWidth 563 / clientWidth 419`、15 列 699/419、18 列 835/419、20 列 925/419——都横滚 1.3–2.2 屏，**全都没有提示**，滚动条还是 3px `#26282E`。
- 从提示点进全屏后：提示条**不消失**（1920 下还是一条 1,920 宽的灰字横在 y=22），「全屏」按钮**仍写「全屏」**（只有点按钮进入的路径才会改成「退出」），「声音 关」和「全屏」**双金**（`#csound` 和 `#readtoggle` 共用 `.readtoggle`）。
- 按 Esc 退出全屏：卡片关了，但 `reading` 类留在 `#card` 和 `body` 上；下一首诗（《登高》）**直接以全屏打开**。全屏也**没有进度条**（`.fsprog` 仍不存在），而 1366 下 200 行是 4.77 屏。
- 1366 下 66px 标题换 3 行（297px），第一句诗在 y=474——768 高的屏，**62% 已经没了**，读者先看标题，再翻 4.77 屏。
- 中长诗是最差的一段：40 行单栏 **3.37 屏**，61 行三栏 **1.31 屏**——加 21 行反而少读两屏。阈值 `>60` 是一刀切，不是为了「读得下」。

| 行数（1920 全屏） | 布局 | scrollHeight / clientHeight | 屏数 |
| --- | --- | --- | --- |
| 8 | 单栏 34px | 1,081 / 1,058 | 1.02 |
| 20 | 单栏 34px | 1,879 / 1,058 | 1.78 |
| 40 | 单栏 34px | 3,474 / 1,032 | **3.37** |
| 61 | 三栏 23px | 1,350 / 1,032 | **1.31** |
| 200 | 三栏 23px | 3,366 / 1,032 | 3.26 |

**改法（约 1 小时，五段）**

```css
/* ① 窄屏：全屏回到单栏，右栏落到诗后 */
@media (max-width:900px){
  #c-full{grid-template-columns:minmax(0,1fr);gap:36px;padding:5vh 7vw 10vh}
  #c-full .fs-left.long{column-count:1}
  #c-full .fs-t{font-size:34px;line-height:1.5}
  #c-full .fs-right{position:static;border-left:0;padding:0;margin-top:8px}
}
/* ② 1366 的标题别用 66px */
@media (max-width:1500px){ #c-full .fs-t{font-size:34px} }
/* ③ 滚动条用金 */
#card .poem::-webkit-scrollbar{height:4px}
#card .poem::-webkit-scrollbar-thumb{background:rgba(201,162,39,.55);border-radius:2px}
#card .poem::-webkit-scrollbar-thumb:hover{background:rgba(201,162,39,.9)}
```

```js
// ④ 提示按「真的滚不滚」判定，并在关/开全屏时同步状态
var po=document.getElementById('c-poem');
var need = po.scrollWidth > po.clientWidth + 8;
_hint.dataset.need = need ? '1':'0';
_hint.textContent = need ? ('共 '+p.L.length+' 列 · 点这里整屏读 ›') : '';
_hint.style.display = need ? 'block':'none';

function setReading(on){
  /* …原有逻辑… */
  var h=document.getElementById('c-poemhint');
  if(h) h.style.display = (on||h.dataset.need!=='1') ? 'none':'block';
  var rt=document.getElementById('readtoggle');
  if(rt) rt.textContent = on ? '退出' : '全屏';
  var prog=document.querySelector('.fsprog');
  if(prog) prog.style.display = on ? 'block':'none';
}
function closeCard(){ if(readingOn) setReading(false); /* …原有逻辑… */ }
```

```js
// ⑤ 栏数按「装不装得下」算，而不是 60 行一刀切
var avail = innerHeight - 240;          // 去掉标题/说明后的可用高
var lineH = 34*2.2;
var cols = Math.max(1, Math.min(3, Math.ceil(p.L.length*lineH/avail)));
h='<div class="fs-left'+(cols>1?' long':'')+'" style="column-count:'+cols+'">';
```

**验收**：390 全屏短诗 0 重叠、长诗标题 ≤2 行且全文可读；提示按实际 `scrollWidth` 出现；进/出全屏后提示与按钮文案一致；Esc 退出后下一首不再全屏；40 行诗 ≤2 屏；全屏顶部有随位置走的 2px 金线。

## 另外三条（次伤，但都不该留到下一轮）

**A. 手机 HUD 还是桌面版压扁的。** 390×844 下：顶栏 113px、底栏 **266px**（31.5%），中间只剩 465px 给天幕；`#side` 从 y=146 一直到 698，**已经压进底栏的 578–844 区间**；「检索 / 着色」两个标签被挤成竖排两字；品牌「杜詩星海」换行成「杜詩星 / 海」，英文也换两行；检索输入只有 150×16。这轮加的压暗让字看得清了，但没有让版面站住。改法：≤700px 隐藏左侧竖排导航（改成底部一个「目录」按钮）；底栏拆成两行、chips 横向滚动、标签 `white-space:nowrap`、命中区 ≥44px；图例默认收起。

![手机首屏：底栏占 31.5%](r4_ux/ux_09_mobile_default_390.png)

**B. 键盘与读屏还是零。** 卡片关闭时 Tab 仍会落到屏外的 `#csound`（x=2177）；`readtoggle` / `close` 是 `tabIndex −1` 的 div，Tab 永远到不了；`<button>` 0 个、`aria-live` 0 个、`h1` 0 个；没有 `prefers-reduced-motion`，自动旋转、星点呼吸、逐字入场、伪诗下落全在跑。最低限度：把两个 toggle 换成 `<button>`、卡片关闭时 `inert`、计数加 `aria-live="polite"`、`reduce` 下关 `autoSpin` 与逐字入场。

**C. 字号的尾巴在入口上。** `#search input{font:12px/1 inherit}` 是非法简写，整条被丢，输入文字实际 **13.3333px**（浏览器默认），而且不是全站任何一档。改成 `font:inherit;font-size:12.5px` 即可。另外 `sup` 的 10.4167px 和两处 `clamp()` 与「只有 8 档」的宪法不符——前者建议并入 9px，后者若确实需要流式，应在 DESIGN.md 里登记为第二例外。加载计数仍是 `buildNebulaTex()` 之后才起步（6× 下 FCP 584ms、DOMContentLoaded 5.9s，计数器前置冻在 0000），上轮提过，这轮代码路径未动。

## 评分拆解

| 维度 | 分 | 说明 |
| --- | --- | --- |
| 可发现性 / 信息架构 | 15 / 25 | 天幕 0 个诗题；检索 1.88:1、150×16；命题数字 2.60:1。本轮没有动入口。 |
| 核心交互可靠性 | 18 / 25 | 桌面点星/拖拽/关闭都成立；触屏首点修好是这轮最大的真实进步。但第二点永远回到同一首、tooltip 不散、白噪音仍抛 `ReferenceError`、24,000 个噪声点与真诗不可分辨。 |
| 状态反馈 | 13 / 20 | 长诗提示、零结果文案、关闭 X 都在。但提示不金、不消失、按钮文案不同步、Esc 泄漏 reading、双金、回车后查询态清空、无进度、无 aria-live。 |
| 长文本阅读 | 16 / 20 | 桌面短诗单栏 1.02 屏、长诗三栏 + sticky 成立，是本轮实打实的改善；但 390 全屏叠字/一字一行，40 行单栏 3.37 屏 vs 61 行 1.31 屏，1366 标题占 62% 首屏，且无进度。 |
| 适配与性能 | 6 / 10 | 触屏从「打不开」到「能开一首」；但窄屏全屏、手机 HUD（266px 底栏、导航压底栏）、1366 卡内标题压按钮都还在；无 reduced-motion。 |
| **合计** | **68** | 上轮 64 |

**为什么是 +4 而不是更多**：触屏首点、长诗卡提示、短诗单栏、压暗都是真的，但它们各自都只覆盖了「第一次 / 极端长诗 / 桌面」这一半；同时这轮把「全屏读」的入口做得更显眼了，而 390 宽的全屏恰恰是坏的——入口越显眼，越容易把手机用户送进那一屏。分数给到 68，是因为核心链路已经能走通一次；不给更高，是因为「第二次」和「小屏」都还走不通，「找到」更是连续三轮没动。

## 一句总评

这版最像作品的一屏仍然是天幕，最像产品的一步是触屏终于能点开诗；但产品不是「能打开一次」，是「关掉之后还能再打开另一首」。**先把 `hover` 清掉、把 390 的全屏改成单栏，再谈金色和进度条**——这两件都是十几行的事，却决定手机用户能不能读完第二首。

---

其余实拍：[诗卡 1920](r4_ux/ux_02_card_denggao_1920.png) · [全屏 1920](r4_ux/ux_03_full_denggao_1920.png) · [1366 默认](r4_ux/ux_04_default_1366.png) · [长诗卡 1366](r4_ux/ux_05_card_long_1366.png) · [长诗全屏 1366](r4_ux/ux_06_full_long_1366.png) · [手机诗卡](r4_ux/ux_10_mobile_tap_390.png) · [提示与滚动条 3×](r4_ux/crop_hint_scroll_3x.png) · [双金与「全屏」文案 3×](r4_ux/crop_full_btns_3x.png)

> 口径：headless Edge / CDP，DPR 1，swiftshader；触屏用 `Input.dispatchTouchEvent`，`mobile:true`。截图取自 14:17 单文件构建；`r4_ux/probe*.json` 存了本文所有原始数（含 12/15/18/20/200 列、8/20/40/61/200 行、390 全屏、Tab 序列、Enter 状态）。
