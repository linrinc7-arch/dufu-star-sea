# 交互与产品设计（信息架构 / 可发现性 / 状态反馈 / 适配）· 第 2 轮评审

**总分：65 / 100**（上轮 54，**+11**）

评审对象：`杜诗星海.html` 2026-10-20 13:32 构建（5,976,836 B，md5 `7547a9a4…`），源码 `web/index.html` 13:29 版。
实拍：Edge headless + CDP 固定视口（1920×1080 / 1366×768），关掉虚拟时间、等页面稳定后取帧，共 10 张；截图、探针 JSON、逐帧 `fillText` 记录都在 `评审/_r2/`。
> 评审期间 `web/index.html` 一直在变（13:11 → 13:29 → 13:32 重建）。下列数字全部按 13:32 构建复测；若再重建，按每条的「验收」复验即可。

![默认 1920](<_r2/b_default_1920.png>)

## 与上轮的差（只列实测项）

| 项 | 上轮（54 分那次） | 本轮实测 | 判定 |
| --- | --- | --- | --- |
| 首屏诗题 | 0 个 | 12 个，12.5px / α.62，逐条取样均 ≥4.3:1 | ✅ 修好 |
| 检索回车 | 不打开（`cardAfterEnter:false`） | 回车打开《登高》，卡片 on | ✅ 修好 |
| 阅读态 HUD | 底栏横在诗面上 | `#foot` opacity 0；卡片 1920×1080 盖住 `#top/#side` | ✅ 修好 |
| 卡片 / 底栏层级 | `#foot` z17 压住卡片 | `#card` z16 > `#foot` z12，卡片页脚干净 | ✅ 修好 |
| 1366 卡片诗区 | 52px / scrollHeight 231 | 419×251；《登高》232，7 字列 159px 放得下 | ✅ 修好 |
| 1366 首屏叠压 | 导航压 dims/foot | 105 / 49 px² 的角接触，肉眼不叠 | ✅ 基本修好 |
| 长诗全屏裁头 | 顶部被切 | 200 行首行 y=299，标题完整 | ✅ 修好 |
| 检索入口对比度 | 1.88:1 | 1.95:1；叠上 `#vig` 后 **1.37:1** | ❌ 没修 |
| 层序 | vig 15 / foot 17 | **vig 14 仍在 top/side/foot 12 之上** | ❌ 只修了卡片 |
| 题名可点 | — | 12 个题名 **0/12** 在题名中心点中自己，**10/12 打开别人的诗** | ❌ 新问题 |
| 键盘 | Tab 1 / button 0 | Tab 3（含卡片收起时仍能聚焦的 `#csound`）；全屏/关闭仍不可达，button 0 | ❌ 没修 |
| 200 行全屏 | — | scrollHeight 12,285 / clientHeight 1,054 = **11.7 屏**；右栏 578px | ❌ 未适配 |

## 仍然最伤的三条

### 1. 题名是画上去的，不是入口：点《阁夜》打开《畏人》

- 实现：12 个题名是 canvas 里的 `ctx.fillText(txt, q2.sx+13, q2.sy+1)`，不是 DOM；命中判定仍只有 `pick()` 的 `bd=26`（星点半径 26px）。题名从星点右侧 13px 开始，**只有开头约 13px 落在命中圈里**；《江畔独步寻花七绝句 六》题名宽 163px，可点部分只占 8%。
- 实测（`labels_build.json`，12 个题名逐个算）：在题名文字中心点击，**0/12 打开自己**；**10/12 打开别的诗**；**2/12 没有任何反应**。例子：《阁夜》中心 → 悬停显示「畏人 五言律诗·40字」，点开也是《畏人》；《登高》中心 → 《春日梓州登楼二首 二》；《闻官军收河南河北》中心 → 《潼关吏》。
- 星场太密，靠“离哪个星近”来选中本身就不可靠：一次实测点在《登高》星位的投影点，开的是《登舟将适汉阳》。题名要解决的是“点这个词＝开这首诗”，而不是再赌一次 26px 的近邻。
- 题名本身做得不错：12 个互不重叠、逐条取样最低 4.3:1，用户会相信它。于是“点题名出错诗”比“没有题名”更伤——新做的可发现性直接变成一次误点。

### 2. 检索入口还是隐身的，层序也只修了一半

- 控件：`#search` 187×24，输入框 150×16，唯一可见的是一条 1px 下划线，placeholder「意象 / 诗题」。
- 像素：仅星场时 **1.95:1**；叠上 `#vig` 后 **1.37:1**（取样峰值 rgb(40,38,35)）。同一个暗角把右上「POEMS 1408」从 2.70:1 压到 **1.64:1**。
- 根因：`#vig{z-index:14}` 仍高于 `#top/#side/#foot{z-index:12}`——本轮只把卡片抬到 16，HUD 还在暗角下面。实测隐藏 `#vig` 后同一处 placeholder 立刻回到 1.95:1。
- 命名打架：底栏那个「检索」是 `#dims .lab`，点了出来的是意象/情感/体裁/时期/题材五个**分类筛**；真正的文本检索是右上角那个看不见的框。两个「检索」，能看见的那个不是搜索。
- 回车之后状态不同步：`select()` 把 `query` 置 null，却没有清空 `#q`、没有 `updCount()`。实测回车打开《登高》后：输入框仍是「登高」，`#qc` 仍是「4」，底部还挂着「意象「登高」· 4 首 · 连线＝两首都含此字」。而且查的是诗题，条形却写「意象」。
- 同一套“金色＝选中”的语言在阅读态破功：`#card.reading .readtoggle` 同时命中「退出」和「声音 关」，实测「声音 关」背景 rgb(201,162,39)、文字 rgb(4,5,10)——一个关闭的音效显示成高亮选中。
- 键盘：3 个 Tab 停靠点（`#q`、`#autog`、**卡片收起时仍可聚焦的 `#csound`**），全屏/关闭不可聚焦，结果计数没有 `aria-live`。

![诗卡 1920](<_r2/b_card_denggao.png>)

### 3. 长诗在两种阅读面里都不适配

- 卡片（1366 / 《北征》）：`#c-poem` 419×251，140 列，`scrollWidth 5,821`，一屏只看得到 8 列；唯一的提示「共 140 列 · 点「全屏」整首读」写在了最后一次 `renderRelations()` **之前**，被它重写 `#c-cns.innerHTML` 冲掉——实测 `#c-cns` 结尾是「…看到这两首共享哪个词」，没有「共 140 列」。
- 全屏（200 行《秋日夔府咏怀…》）：`scrollHeight 12,285 / clientHeight 1,054`，要滚 **11.7 屏**；右栏 `.fs-right` 只有 578px，滚到 6,000px 时它的下沿在 -5,331px——后面五屏右边全空。27px/2.2 的行高对 8 行和 200 行是同一个值。
- `fitPoem()` 仍是死代码：算完 `need/avail/needW/availW` 只有注释；而且 ≤1500px 的 `#card .col{font-size:15.5px}` 会压过 `--poem-fs`，就算把缩放写进去也生效不了。
- 没有进度、没有「上一首/下一首」，读长诗是单向滚动 + 退出。

![1366 卡片 北征](<_r2/b_card_beizheng_1366.png>)
![200 行滚到 6000px：右栏已空](<_r2/b_full200_scrolled.png>)

## 三条改法（可直接落地）

### 改法 1：把 12 个题名变成 DOM 命中目标（约 30 分钟）

保留 canvas 的绘制作为无 JS 兜底，另加一层按钮；`pick()` 不再负责题名。

```html
<div id="lablayer"></div>
```

```js
var labNodes = [];
function syncLabels(){
  var on = viewMode==='sky' && cam.zoom<1.6 && !selected && !query;
  var layer = document.getElementById('lablayer');
  layer.style.display = on ? 'block' : 'none';
  if (!on) return;
  var used = [], n = 0;
  for (var li=0; li<_order.length && n<12; li++){
    var p = _order[li]; if (!p.hot || !p._q) continue;
    var q = p._q;
    if (q.sx<70 || q.sx>W-240 || q.sy<60 || q.sy>H-130) continue;
    if (used.some(function(u){ return Math.abs(u[0]-q.sx)<190 && Math.abs(u[1]-q.sy)<26; })) continue;
    used.push([q.sx, q.sy]);
    var b = labNodes[n] || (labNodes[n] = document.createElement('button'));
    b.className = 'plabel';
    b.textContent = '《' + p.t + '》';
    b.style.left = (q.sx + 16) + 'px';
    b.style.top  = (q.sy - 12) + 'px';
    b.setAttribute('aria-label', '读《' + p.t + '》');
    b.onclick = (function(pp){ return function(){ select(pp); }; })(p);
    if (!b.parentNode) layer.appendChild(b);
    n++;
  }
  for (var k=n; k<labNodes.length; k++) if (labNodes[k].parentNode) labNodes[k].parentNode.removeChild(labNodes[k]);
}
```

```css
#lablayer{position:fixed;inset:0;z-index:9;pointer-events:none}
.plabel{position:absolute;pointer-events:auto;height:24px;padding:0 6px;
  background:none;border:0;cursor:none;font:12.5px/24px "Songti SC",SimSun,serif;
  color:#e6e0d2;text-shadow:0 0 6px #04050a,0 0 2px #04050a;opacity:.95;
  transition:color .2s,opacity .2s}
.plabel:hover,.plabel:focus-visible{color:#fff;outline:1px solid rgba(201,162,39,.55);outline-offset:2px}
@media (pointer:coarse){ .plabel{height:44px;line-height:44px} }
```

在 `render()` 末尾调用 `syncLabels()`（12 个节点，20fps 空闲帧只更新 left/top）；canvas 里那段 `fillText` 保留为降级。
**验收**：依次点 12 个题名，卡片标题与题名逐一对上；悬停题名时 tooltip 与题名一致；Tab 能走到题名。

### 改法 2：让检索是控件，让暗角退回星场（约 20 分钟）

```css
#vig{z-index:3}                                  /* 高于星场(0)/诗云(2)，低于 HUD 12 */
#search{min-height:36px;border-bottom-color:rgba(236,231,219,.28);gap:8px}
#search input{width:190px;font-size:12.5px}
#search input::placeholder{color:#8a8578}         /* 5.5:1 */
#search:focus-within{border-bottom-color:var(--gold)}
/* 阅读态只给「退出」上金色：把 #card.reading .readtoggle 改成 #card.reading #readtoggle */
```

```js
/* select() 末尾：检索态跟着卡片走 */
document.getElementById('q').value = '';
if (window.phl) phl.classList.remove('on');
updCount();
/* updCount() 里：条形标签别再写死「意象」 */
document.getElementById('phl-n').textContent = '检索';

/* 键盘可达 */
document.getElementById('readtoggle').tabIndex = 0;
document.getElementById('close').tabIndex = 0;
[document.getElementById('readtoggle'), document.getElementById('close')].forEach(function(b){
  b.addEventListener('keydown', function(e){
    if (e.key==='Enter' || e.key===' '){ e.preventDefault(); this.click(); }
  });
});
/* 卡片收起时不要留下可聚焦的隐藏控件 */
document.getElementById('card').addEventListener('transitionend', function(){
  this.classList.contains('on') ? this.removeAttribute('inert') : this.setAttribute('inert','');
});
```

**验收**：placeholder 实测 ≥4.5:1；`#vig` 的 computed z-index < 12；回车后底部条形消失、输入框清空；阅读态只有「退出」是金色；Tab 从搜索框能走到全屏。

### 改法 3：让版面跟着篇幅走（约 1 小时）

1）把 1366 的横滚收口：`fitPoem()` 用已算好的值，并让 CSS 变量真的生效。
```css
@media (max-width:1500px){ #card .col{font-size:var(--poem-fs,15.5px)} }
```
```js
function fitPoem(p){
  var el = document.getElementById('c-poem');
  if (!el || !p || !p.L || !p.L.length) return;
  var maxLen = 0;
  for (var i=0; i<p.L.length; i++) if (p.L[i].length > maxLen) maxLen = p.L[i].length;
  var fs = FS;
  el.style.setProperty('--poem-fs', fs + 'px');
  var need = maxLen*fs*2.05 + 34, avail = el.clientHeight || 420;
  if (p.L.length >= 40){ if (!readingOn) document.getElementById('readtoggle').click(); return; }
  if (need > avail) el.style.setProperty('--poem-fs', Math.max(13, Math.floor(fs*avail/need)) + 'px');
}
```

2）全屏按行数分档，别让 200 行也用 27px：
```css
#c-full[data-len="mid"]  .fs-ln{font-size:23px;line-height:2}
#c-full[data-len="long"] .fs-ln{font-size:20px;line-height:1.95}
#c-full[data-len="xl"]   .fs-ln{font-size:17px;line-height:1.9}
#c-full .fs-right{position:sticky;top:6vh;align-self:start;max-height:86vh;overflow:auto}
.fsprog{position:fixed;left:0;top:0;width:100%;height:2px;z-index:21}
.fsprog i{display:block;height:100%;width:0;background:var(--gold)}
```
```js
var el = document.getElementById('c-full'), n = p.L.length;
el.dataset.len = n>100 ? 'xl' : n>40 ? 'long' : n>16 ? 'mid' : 'short';
el.scrollTop = 0;
```

3）加进度和翻页；把「共 N 列」挪到最后一次 `renderRelations()` 之后：
```js
renderRelations(p);
if (p.L.length >= 40){
  var cns = document.getElementById('c-cns');
  if (cns) cns.innerHTML += '<br>共 ' + p.L.length + ' 列 · 点「全屏」整首读';
}
el.addEventListener('scroll', function(){
  var r = this.scrollTop / Math.max(1, this.scrollHeight - this.clientHeight);
  document.querySelector('.fsprog i').style.width = (r*100) + '%';
});
```

**验收**：《北征》卡片能看到「共 140 列」；200 行全屏 scrollHeight 降到 5,000px 以内（17px/1.9 约 6,460px，长诗再分两栏约 3,230px）；滚动时右栏始终在视野里；顶部有 1/200 的进度。

## 一句总评

第二轮把「看得见」做到了——12 个题名、干净的阅读态、终于站得住的 1366 卡片；但「点得中、找得到、读得完」还差三口气：题名不是按钮，检索不是控件，长诗不是版面。

---

其余实拍：[全屏 1920](<_r2/b_full_denggao.png>) · [1366 默认](<_r2/b_default_1366.png>) · [200 行全屏顶部](<_r2/b_full_200.png>) · [回车后条形仍在](<_r2/b_search_enter.png>) · [暗角/placeholder 对照](<_r2/b_vig_on.png>)