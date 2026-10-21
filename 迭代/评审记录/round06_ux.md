# 交互与产品设计（信息架构 / 可发现性 / 状态反馈 / 适配）· 第 6 轮评审

**总分：69 / 100**（上轮 75，**−6**）

评审对象：`杜诗星海.html` 2026-10-20 **15:29:39** 构建（5,993,393 B，md5 `64d42454…`；评审到 15:47 复核 mtime 未再变）＋源码 `web/index.html`（148,184 B / 3,157 行）。
口径：Edge headless 1920×1080 / 1366×768 / 390×844（DPR 1，swiftshader，触摸仿真），等 `#load` 移除后取帧；**每次导航都核对 `location.pathname` 为交付文件**（上一轮同一目录里有并行进程抢过调试端口，这轮全部改成独立 profile + 端口，杜绝串页）。声音不靠耳朵判：把 `AudioContext.prototype.createOscillator` 包一层，记录调用栈里最近一帧的函数名，用来区分 `audCue` / `audBell` / `audSelect`——这是「界面音有没有响、在哪响」的直接证据，不改页面行为。对比度按截图取样算 sRGB 相对亮度。实拍与探针在 `评审/r6/ux/`。

![1920 首屏：全站 fillText = 0，天幕上仍然没有一个诗题；唯一的入口是右上角那条 1.66:1 的虚线](r6/ux/ux01_default_1920.png)

## 一句话

这轮把「声音」从一个播放器做成了一个系统——界面音、卷积钟、题目哈希的五声音阶、底噪随视角呼吸、记忆恢复；但第 ③ 条改动里的一行赋值丢了 `var`，在 `'use strict'` 的 IIFE 里直接抛 `ReferenceError`，而它发生在写卡片之前：**同一个动作，关掉声音能开卡，开着声音只飞镜头、不开卡**。首屏那件五轮没动的事（0 个诗题、1.66:1 的输入框、1366 与手机没有提示）也还站在原地。

## 与上轮的差（只列实测）

| 项 | 上轮 75 分那次 | 本轮 15:29 | 判定 |
| --- | --- | --- | --- |
| **开声音后点真诗** | 可开卡（`var base=196`） | **不开卡**：`audSelect` 抛 `base is not defined`，`select()` 在写 `c-title`/`card.on` 之前中断 | ❌ **P0 回归** |
| 首屏诗题 | 0（fillText=0） | **0**（fillText 仍 0） | ❌ 第五轮未动 |
| 检索 placeholder | 1.83:1（`#3F3D37`） | **1.66:1**（同色，实测底 `rgb(20,23,24)`） | ❌ |
| POEMS 计数 | 2.55:1 | **2.49:1**（9px `#55524A`） | ❌ |
| 1366 / 手机操作提示 | `display:none` | **仍 none**（`@media(max-width:1500px){#hint{display:none}}`） | ❌ |
| 手机 HUD | 379px = 44.9% 屏高 | **268px = 31.8%**（顶 76 + 底 192） | ✅ |
| 手机 `#side` | 16×552，插进底栏 120px | **`display:none`** | ✅ |
| 手机 检索维度 | 「情感/体裁」两字一行 | dims 修好（55×36 单行）；**第二排（着色·诗云·生涯·声音）变成两字一行，「生涯」与「巡游」还叠在一起** | ⚠ 修好一排、坏了一排 |
| 触屏 A→关→B | 正常 | **仍正常**：登高 → 点 ✕ → 春望，`tip` 已散、0 异常 | ✅ |
| 12 列卡提示 | `null`（82 首漏掉） | **有**：1920 656/451、1366 563/419、390 578/373，三档都真的溢出 | ✅ 但 28px 高 |
| 诗区金色滚动条 | 声明金、像素是系统灰 | **实拍是金色**（1366 3× 可见金轨 + 两端箭头） | ✅ |
| 阅读态「单金」 | 双金 | **仍双金**：`#readtoggle` 与 `#csound` 同为 `rgb(201,162,39)` / `#04050a` | ❌ 声称已修 |
| 卡片声音 aria | 无 | `role=switch`/`tabindex`/`aria-label` 都有；**点击后 `aria-checked` 仍是 false**，而文字已写「声音 开」、页脚已变 true | ⚠ 一半 |
| 按钮命中高度 | 24px | **仍 24px**（`#csound` 68×24、`#readtoggle` 48×24、`#close` 26×26） | ❌ 声称 40px |
| 回车后检索态 | 输入框/计数/金条都还写着「明月·7 首」 | **全清**：输入框空、`qc` 空、金条 off、`query=null`，卡片正常打开 | ✅ |
| Esc 两步 | 一次只退阅读 | **仍是**：第一次 `reading=false`/`on=true`，第二次才关 | ✅ |
| 200 列全屏（390） | 11.87 屏、解析在第 11 屏 | **11.87 屏**（9,758/822）、解析 `rightTop=9,023`、无进度线 | ❌ 未动 |
| 首次点星的「真假」 | 24,000 点 vs 1,468 首，判断「多半点到假诗」 | **30 次随机悬停：26 次吸到真诗、4 次空、0 次机器诗**；`NPT` 已从 24,000 降到 **9,000** | ⚠ **我更正上轮的判断** |

> 更正：上轮我按「点的数量」推「第一次多半点到假诗」。这版把伪诗点降到 9,000，且 `pick()` 对真诗有 26px 吸附，实测悬停 30 次没有一次落到机器诗上。交互侧这条我撤回——**星空的视觉仍是机器为主，但可点的面积已经是真诗为主**。

## 这轮八条，逐条对账

| # | 说法 | 实测 | 判定 |
| --- | --- | --- | --- |
| ① | 统一界面音 `audCue`，五类（悬停/输入/筛选/面板/缩放），悬停换星极轻一声 | 五类都在；悬停 8 颗真星 → `audCue` 8 次（1:1），1,568Hz / 0.09s。**但它不认遮罩**：指针在**卡片正文**上移 8 次 → 响 4 次；在**底栏**上移 8 次 → 响 3 次 | ⚠ 响了，但在错的地方 |
| ② | 随机钟改走卷积混响 | `audBell` 的 3 个振荡器归因在 9–22s 的钟窗口内，同时接 `conv` 与 `dry`；交互侧无异议 | ✅ |
| ③ | 真诗按题名哈希取五声音阶 | `base = 196 * Math.pow(2,…)`（第 1848 行）**没有 `var`**，而全文件包在 `(function(){'use strict';…})()` 里 → 开声音选真诗必抛错；`select()` 的卡片渲染全在这行之后 | ❌ **P0** |
| ④ | 底噪低通 620Hz + 330Hz 分音，呼吸同改音量与截止 | 代码在（`lp.frequency=620`、`o3=330`、`audFollow` 里 `air.gain` 与 `lp.frequency` 同改） | ✅（声音视角另判） |
| ⑤ | 记忆恢复前先 `ctx.resume()` | 代码在；`dsh_sound=1` 重载后：页脚写「开」、`aria-checked=true`、`AudioContext` 1 个。**但「开」是 `audToggle` 里写死的，不读 `ctx.state`**——本机没能造出 `suspended`，所以只记风险，不算实证 | ⚠ 可复现一半 |
| ⑥ | 卡片声音开关补 `aria-checked`/`aria-label`、命中 40px 高 | `role`/`tabindex`/`aria-label` 有；**`aria-checked` 只在初始化写一次**，点击后 卡片=false、页脚=true；高度 **24px**，不是 40px，也低于 44px 触摸下限 | ❌ 一半且未达标 |
| ⑦ | 12 列起就有「整屏读」提示 | `_need = p.L.length>=12`；12 列三档都真溢出、提示都在；**但判定按列数不按溢出**，390 下 11 列（全库 1 首）478/373 真溢出却无提示；提示只有 **28px** 高 | ✅ 主体成立 |
| ⑧ | 12 列门槛、回车清空检索态、单金规则 | 门槛 ✅；回车 ✅（见上表）；**单金 ❌**：`#card.reading .readtoggle{background:var(--gold)}` 仍一把抓两个按钮 | ⚠ 两件半 |

![同一坐标、同一次点击（1920 右侧 1:1）：声音关（左）卡片照常打开《春望》；声音开（右）卡片没有出现，只有镜头照着飞过去](r6/ux/compare_sound_off_on.png)

![声音开着点星之后：HUD 写「声音 开」，天幕上什么都没有发生——控制台里是 audSelect 抛的 ReferenceError](r6/ux/crop_hud_after_click.png)

## 仍然最伤的三条

### 1. 声音一开，产品的主干就断了：点真诗不开卡（P0，六字符回归）

- 证据链完整：同一坐标、同一次点击——**关声音 → `card.on=true`、标题《春望》**；开声音 → `card.on=false`、标题还是上一首、`window.onerror` 记到 `base is not defined`。调用栈：`audSelect`（杜诗星海.html:1900）← `select`。
- 根因是第 ③ 条：上版是 `var base=196;`，这版改成 `base = 196 * …`。整个应用包在 `'use strict'` 的 IIFE 里，给未声明变量赋值 = 抛错。
- 为什么比「一个音效没响」严重：`audSelect()` 在 `select()` 的第 2128 行，而 `c-title`/`c-meta`/`c-poem`/`card.classList.add('on')` 都在它之后。声音是装饰，却把内容渲染整段带走了——**而且镜头照飞**，用户看到的是「星飞过去了，卡片没出来」，不是「报错了」。
- 触发面不是小众：默认关声音，但 `dsh_sound=1` 会在重载 2.6s 后自动 `audToggle(true)`（实测页脚确实变「开」）。**只要用户曾经开过一次声音，之后每次回来，点诗都没反应**——而他不会想到去关声音。
- 假诗不受影响：`audNoiseVoice` 里是 `var base=146.83`，所以开声音时机器诗照开，真诗全死——入口本来就少，这下正好只剩假的那一半。

**改法（10 分钟，一行 + 一层护栏）**

```js
// web/index.html:1848
var base = 196 * Math.pow(2, _pent[_deg % _pent.length] / 12);   // 少的就是这个 var
```

```js
// select()：声音在卡片之后、且包住——装饰永远不许阻断产品
document.getElementById('c-no').textContent = 'NO. ' + String(p.i + 1).padStart(4, '0');
/* …标题/正文/卡片都在这里… */
try { audSelect(pan, pent); audPaper(); } catch (e) { /* 静默，最多 console.warn */ }
```

**验收**：开声音依次点《登高》《春望》《月夜》→ 三张卡都开、标题正确、0 未捕获异常；关声音同样三张；重载（带 `dsh_sound=1`）后再点三首仍全对。

![阅读态 3×：左边「声音 关」、右边「退出」，仍是两个金块——`#card.reading .readtoggle` 没有区分](r6/ux/crop_double_gold_3x.png)

### 2. 找到：首屏 0 个诗题、唯一入口 1.66:1、1366 与手机连一句提示都没有（连续第五轮）

- 全站 `fillText` 仍为 **0**；1920 首屏上所有可见文字都是导航、图例、计数，**没有一个诗题**。
- 输入框 `150×16`、外框 `187×24`；placeholder `#3F3D37` 在实测底 `rgb(20,23,24)` 上 **1.66:1**（上轮 1.83，这版更暗）；`POEMS 1468` **2.49:1**。全站唯一入口，是全屏最看不清的东西（见下图 2×）。
- `#hint`（「拖动 巡游 / 点击星辰 读诗」）只在 >1500px 出现：1366 `display:none`、390 `display:none`。**笔记本和手机第一次打开，没有任何一句操作说明。**
- 这轮把「点开之后」修得更顺（12 列提示、回车清空、手机 HUD 收短），但「点开之前」一步没动。产品不是「能打开一次」，是「第一次就知道点哪儿」——这句上轮说过，这轮还是同一句。

**改法（40 分钟，照抄上轮）**

```css
#search input::placeholder,#search input:focus::placeholder{ color:#8a8578 }  /* 4.9:1，聚焦不要变暗 */
#meta-r .num{ color:#8a8578 }                                                  /* 4.9:1 */
#search{ min-height:34px; border-bottom-color:rgba(236,231,219,.24) }
#search input{ width:190px; font-size:12.5px }
@media (max-width:1500px){ #hint{ display:block; font-size:11px; line-height:1.9; color:#8f8a7e } }
```

```html
<!-- 首屏 6 个名篇；桌面手机同一份，不再靠 26px 星距去猜 -->
<div id="starts"><b>从这儿进</b>
  <span data-t="登高">登高</span><span data-t="春望">春望</span><span data-t="月夜">月夜</span>
  <span data-t="秋兴八首 一">秋兴</span><span data-t="望岳">望岳</span><span data-t="茅屋为秋风所破歌">茅屋</span>
</div>
```

**验收**：placeholder / POEMS ≥4.5:1；1366 与 390 首屏都能看见并点开 6 个诗题；1366 有一行操作提示。

![右上角 2×：全站唯一入口——「意象 / 诗题」几乎融进背景（1.66:1），上面那行 POEMS 2.49:1](r6/ux/crop_topright_2x.png)

### 3. 界面在说错话，也在错的地方出声

这轮有四处「你以为修好了」：

- **阅读态双金**：`#card.reading .readtoggle{color:#04050a;background:var(--gold)}` 仍然同时命中「声音 关」和「退出」；DOM 计算值两枚都是 `rgb(201,162,39)`，实拍就是两个金块（上图）。念作「声音 关」的按钮长得像激活，是这页最容易被误读的一处。
- **卡片声音的 `aria-checked` 不跟手**：点击后文字变「声音 开」、页脚 `autog` 变 `true`，卡片自己的 `aria-checked` 还是 `false`。读屏会听到「开关，未选中」+ 名字里却是「声音 开」。`audToggle` 里只给 `#autog` 写了 `setAttribute`，`#csound` 只改了 `textContent`/`classList`。
- **「40px 命中」没落地**：实测 `#csound` 68×24、`#readtoggle` 48×24、`#close` 26×26（`.readtoggle` 只有 `padding:3px 8px`，没有 `min-height`）。手机上 24px 的触摸高度，比 44px 下限小一半。
- **界面音越界**：`audCue('hover')` 由 `pick()` 的命中变化触发，而 `pick()` 只看屏幕坐标、不看上面盖着什么。于是**读着卡片、手在卡片上移 8 次，会响 4 声**；在底栏上移 8 次，响 3 声。一个以「静」为气质的产品，在阅读时自己敲自己。

**改法（35 分钟）**

```css
#card.reading #readtoggle{ background:var(--gold); color:#04050a; border-color:var(--gold) }
#card.reading #csound{ background:transparent; color:#6a675e; border-color:rgba(236,231,219,.12) }
.readtoggle{ min-height:40px; display:inline-flex; align-items:center; justify-content:center }
#c-poemhint{ min-height:44px; display:flex; align-items:center; padding-left:34px; padding-right:34px }
#close{ width:40px; height:40px }
```

```js
// audToggle：两个开关同一份状态，含 aria
var cs = document.getElementById('csound');
if (cs) { cs.textContent = '声音 ' + (AUD.on ? '开' : '关');
          cs.classList.toggle('on', AUD.on);
          cs.setAttribute('aria-checked', AUD.on ? 'true' : 'false'); }
```

```js
// pointermove：指针在界面上时，不算「悬停一颗星」
document.addEventListener('pointermove', function(e){
  var ui = e.target.closest && e.target.closest('#card,#top,#foot,#panel,#legend,#hint');
  if (ui || drag) { hover = null; return; }
  /* …原来的 pick / pcHover / audCue… */
});
```

顺带一条产品判断：**环境声和界面音现在是同一个开关**。喜欢底噪的人不一定想听 1,568Hz 的悬停 tick；在意安静的人可能想要底噪但不要按键声。要么拆成两个开关，要么把悬停音降到「读卡片时绝不响」。

**验收**：阅读态只有「退出」金；点卡片声音后 `aria-checked` 与文字一致；`#csound`/`#readtoggle`/`#close` 均 ≥40px；指针在卡片/底栏上移动 0 次 `audCue`。

![1366：12 列卡真的溢出（563/419），金色「共 12 列 · 点这里整屏读 ›」在诗区下方——这条是这轮最干净的一笔，只是 28px 高](r6/ux/ux21_card12_1366.png)

![手机 390：HUD 从 44.9% 降到 31.8%，导航收掉；但第二排「着色/诗云/生涯/声音」被压成两字一行，「生涯」和「巡游」叠在一起](r6/ux/crop_mobile_foot_2x.png)

## 另外四条（次伤，但不该再留一轮）

**A. 手机第二排控件塌了。** `#foot` 收到 192px 后，`#mode/#sy/#sy2/#au` 这一行没有 `nowrap` 也没有滚动：实测 `#mode .m` 40×44、`#tourbtn` 65×55，截图里「生涯」两个字压在「巡游」按钮左缘上。改：`@media(max-width:700px){ #foot .ctrlrow{flex-wrap:nowrap;overflow-x:auto} .lab{display:none} #mode .m,#sy .s,#sy2 .s,#au .s{flex:0 0 auto;white-space:nowrap;min-height:44px} }`。

**B. 长诗仍然不告诉你在哪。** 390 上 200 列全屏 **11.87 屏**（9,758/822），解析块 `rightTop=9,023`（第 11 屏），`#fsprog` 不存在；1366 是 4.55 屏、同样无进度。改：`<div id=fsprog><i></i></div>` + `scroll` 里写宽度；≤700 给「写作时间 · 诗中之意 ↘」锚点。

**C. 键盘与读屏仍是零。** 卡片关闭时 Tab 第一站是隐藏的 `#c-poem`，第五站进关闭卡片的 `#csound`（前四站是隐藏诗区、BODY、输入框、页脚声音）；`outline:0`、全站 0 条 `:focus-visible`、0 个 `aria-live`、0 条 `prefers-reduced-motion`。最低限度：卡片关闭时 `#card{inert}`、`#qc{aria-live=polite}`、reduce 下关自动旋转与逐字入场。

**D. 「刷屏」的判定仍是列数。** `p.L.length>=12` 在 390 差一点就错（实测 11 列 478/373 已溢出但无提示；10 列按同列宽只剩十几像素余量）。改成渲染后 `po.scrollWidth > po.clientWidth + 8`、并在 `resize` 后重算，一行就够。

## 评分拆解

| 维度 | 上轮 | 本轮 | 说明 |
| --- | ---: | ---: | --- |
| 可发现性 / 信息架构（25） | 15 | **15** | 入口三件（0 诗题、1.66:1、1366/手机无提示）一件没动；可点面积变健康（30 次悬停 26 真诗）抵不了入口本身看不见 |
| 核心交互可靠性（25） | 21 | **13** | 开声音点真诗 100% 不开卡（P0）；触屏 A→B、Esc 两步、回车开卡仍好 |
| 状态反馈（20） | 15 | **15** | 回车清空 +1；「单金」再落空、`aria-checked` 不同步 −1；12 列提示算进长文本 |
| 长文本阅读（20） | 17 | **18** | 12 列 444 首有提示、金滚动条实拍可见；仍 28px、无进度、200 列 11.87 屏 |
| 适配与性能（10） | 7 | **8** | HUD 44.9%→31.8%、`#side` 收起、dims 单行；第二排 chip 两字一行并重叠、无 reduce |
| **合计** | **75** | **69** | **−6** |

**为什么是 −6，而不是 +3 或 −12**：这轮确实挣到了三笔——12 列提示（444 首）、回车清空检索态、手机 HUD 收短 11 个百分点；界面音的思路也对（悬停 8/8 一次一声）。但「开声音点诗不开卡」是**主干回归**：它不挑人（只要开过一次声音）、不报错、不解释，而且正好把真诗挡在外面、把假诗放进来。交互评审的分主要给「能不能走到诗」，这一条不能不通还记账。所以核心交互 −8，其余加减相抵，净 −6。

## 一句总评

这版最像作品的一屏仍是天幕，最像产品的一步是手机 HUD 终于收进去了；但**声音这一层这轮是加法做过头**：界面音、卷积钟、五声音阶、呼吸耦合一起进来，其中一条在 strict 模式下抛错，把「点诗」这条唯一的门带走了——而门外那块牌子，第五轮说好的六个诗题，还空着。**下一轮先把 `var base` 和六个诗题补上，再谈声音。**

---

其余实拍：[1920 默认](r6/ux/ux01_default_1920.png) · [诗卡（声音关）](r6/ux/ux02_card_denggao_1920.png) · [点星后无卡（声音开）](r6/ux/ux03_after_click_sound_on_1920.png) · [阅读态 1920](r6/ux/ux05_reading_1920.png) · [1366 默认（无提示）](r6/ux/ux20_default_1366.png) · [1366 长诗全屏](r6/ux/ux24_readinglong_1366.png) · [手机默认](r6/ux/ux30_mobile_default_390.png) · [手机诗卡](r6/ux/ux31_mobile_card_390.png) · [手机 12 列提示 2×](r6/ux/crop_mobile_hint_2x.png) · [手机长诗全屏](r6/ux/ux34_mobile_readinglong_390.png) · [回车后（已清空）](r6/ux/ux43_after_enter_1920.png)。

> 原始数：`r6/ux/probe5.json`（1920 默认/卡/阅读/aria/Esc/Tab）、`probe6.json`（1366、12 列三档、记忆恢复、手机）、`probe7.json`（随机点击、严格自动播放策略）、`probe8.json`（回车、30 次悬停采样、手机芯片尺寸、A→B）；对比度 `contrast.json`；脚本 `r6_probe5/6/7/8.py`、`contrast6.py`。像素与计算样式在 swiftshader 下取得，颜色/对比度可复现；加载 4.3–4.8s，性能只作相对参考。
