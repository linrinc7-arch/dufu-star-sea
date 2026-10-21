# 交互与产品设计（信息架构/可发现性/状态反馈/适配） · 第 1 轮评审

总分：54/100

评审对象：`杜诗星海.html` 2026-10-20 13:01 构建（md5 `dad39106f92ebce9cbf6dc6b81f0a29b`），1920×1080 与 1366×768 实拍（Edge headless + SwiftShader）。截图在 `web/rev3_ux_*.png`。

| 维度 | 分 | 依据 |
| --- | --- | --- |
| 信息架构 | 58 | 五章导航（源起/星海/生平/交游/评点）+ 五维检索 + 十类图例，骨架清楚；但顶部检索框与底部「检索/意象」是两套入口，讲方法的「源起」藏在最左侧 00；同一首《登高》卡片写「≈夔州·湖湘 推定」，全屏解析写「767 年秋 / 夔州」，两处各说一套。 |
| 可发现性 | 36 | 默认 1920 画面里没有任何诗题标签；检索 placeholder 对比度 1.88:1；搜「登高」只亮 4 颗无标签星，回车不打开；最亮、最像入口的中心是白噪音伪诗，首点即机器诗。 |
| 状态反馈 | 44 | 悬停 tooltip、结果计数、图例 dimming 是加分项；但底栏 z-index 压住卡片/全屏；0 结果仍写「连线＝两首都含此字」；统计兜底只在页脚 10.5px/2.66:1 的说明里交代，标题区没有「非人工解析」标记（本轮 analysis 曾整段静默失败）；白噪音默认开却用纸白填充，与其他金色选中态不是一套语言。 |
| 阅读版面 | 62 | 全屏 42/27/15.5px 的层级、竖排诗卡、左诗右析是强项；但全屏底部被 HUD 盖住，1366×768 卡片里的诗被页脚切掉（探针 clientHeight 52 / scrollHeight 231），全屏诗注 10.5px/2.66:1。 |
| 适配/无障碍 | 27 | 全站 `@media` 数量 0；1366×768 实测 nav 与 dims/foot 相交；可点击元素 0 个 `<button>`、Tab 可聚焦的只有搜索框 1 个、无 `aria-pressed`；「全屏」44×22、关闭 26×26；无 pinch；`body{cursor:none}` 全局。 |
| 一致性/完成度 | 56 | 金色选中态基本统一，但「白噪音」用纸白填充且默认开；「机器」灰标 vs「名篇」金标；「全屏」实为阅读模式；卡片与全屏的系年/地点不一致。 |

**版本说明（必须知道）**：本轮评审从 12:46 构建开始。期间发现 `web/analysis.js:36` 的 `"江南逢李龟年"` 条目末尾少一个逗号，整个 `window.ANALYSIS` 脚本 SyntaxError，**全部人工解析静默未加载**；《登高》全屏落到兜底「推定：流寓湖湘 · 766—770 / 行迹不详」。13:01 构建已补逗号，`node --check` 通过，全屏现为「767 年秋 / 夔州」。故障态与修复后对比：[故障态](<../web/rev2_ux_read.png>) / [修复后](<../web/rev2_ux_read_fixed.png>)。这条已从「最伤」中移除，但请把 `node --check web/analysis.js` 加进构建门禁：它降级时页面完全不报错。

## 最伤的三个问题（每条带证据）

### 1. 层级错了：底栏压住卡片，全屏阅读并不全屏
- **卡片**：打开《登高》后，右下角的「拖动 巡游 · 滚轮 远近 / 点击星辰 读诗」直接画在卡片页脚上，压住「浊酒/酒杯/落木/夔」关键词和星座说明，见 [rev3_ux_card.png](<../web/rev3_ux_card.png>) 与局部 [crop3_cardhint.png](<../web/crop3_cardhint.png>)。
- **全屏**：点「全屏」后，底部的「检索 / 着色 / 诗云 / 白噪音 / 声音 / 图例 / 操作提示」仍横在诗面上，阅读模式不是全屏，见 [rev3_ux_read.png](<../web/rev3_ux_read.png>) 与 [crop3_readfooter.png](<../web/crop3_readfooter.png>)。
- **根因**：本轮把 `#foot` 提到 `z-index:17`、`#vig` 提到 15，而 `#card` 仍是 16。结果 HUD 高于卡片，暗角也盖在顶栏/导航之上，边缘文字更暗（底栏因 17 反而在暗角之上）。
- 1366 下同一问题叠加：提示压住卡片页脚，见 [rev3_ux_narrow_card.png](<../web/rev3_ux_narrow_card.png>)。

### 2. 首屏找不到一首真诗；最亮的地方是假诗
- **默认**：1468 颗星没有一个诗题；唯一的入口提示是右下角 11px/3.83:1 的「点击星辰 读诗」；顶部检索 placeholder 对比度仅 1.88:1，几乎看不见。见 [rev3_ux_default.png](<../web/rev3_ux_default.png>)。
- **检索不导航**：输入「登高」后只亮 4 颗无标签星、拉出两条横贯全屏的金线；没有结果列表，回车不打开（探针：`selAfterEnter:null`、`cardAfterEnter:false`），用户仍要逐颗悬停。见 [rev3_ux_search.png](<../web/rev3_ux_search.png>)。
- **空结果**：输入不存在的词，计数为 0，但底部仍写「0 首 · 连线＝两首都含此字」，画面也不给「没找到」的解释，见 [rev3_ux_zero.png](<../web/rev3_ux_zero.png>)。
- **假诗抢入口**：白噪音默认开（`var syOn=true`），中心是最亮、最诱人点的地方；在中心附近模拟首点，打开的是「白噪音 11229 / 机器」的伪诗《鹍楚威俳吉马行》，只有 9px 灰标「机器」，与真名篇的金色「名篇」标只差颜色。见 [rev3_ux_centerclick.png](<../web/rev3_ux_centerclick.png>)。

### 3. 1366×768 一压就崩，键盘/触屏几乎不可用
- **导航压检索**：1366×768 下左侧竖排「04 评点」与底部「检索」、维度药丸叠在一起；图例折成两行，「释道 94」孤零零掉到下一行。见 [rev3_ux_narrow.png](<../web/rev3_ux_narrow.png>)；布局探针返回 `nav_x_dims:true`、`nav_x_foot:true`，图例高度 64px（1920 下 30px）。
- **卡片截诗**：1366×768 打开《登高》，最后一列「杯/鬓」被卡片页脚切掉；探针（内容区 626px 高）`#c-poem` 的 `clientHeight 52`、`scrollHeight 231`。`fitPoem()` 里算了 `need/avail/needW/availW`，但函数体最后只有注释，没有真正缩放或触发全屏——这是死代码。
- **键盘/触屏**：全站 0 个 `<button>`，Tab 只能到搜索框（1 个），无 `aria-pressed`，无方向键翻诗；无 `@media`、无 pinch、无 `pointer:coarse` 分支。9px 的 `NO.` 对比度 2.34:1，8.5px 的导航编号 3.05:1。

## 三条改法（每条具体到怎么改）

### 改法 1：先把层级排成一套（约 10 分钟）
把暗角降到内容之下、底栏降到卡片之下；全屏时直接隐藏 HUD，别让用户靠颜色猜。
```css
#vig{z-index:2}                 /* 暗角只压星场，不压 UI */
#top,#side{z-index:12}
#foot{z-index:13}               /* 低于卡片，别压诗卡 */
#card{z-index:20}
#panel{z-index:30}
#sweep{z-index:31}
```
再给阅读态一个 body class（`setReading` 里 `document.body.classList.toggle('reading', on)`）：
```css
body.reading #top,body.reading #side,body.reading #foot{opacity:0;pointer-events:none;transition:opacity .25s}
```
验收：1920/1366 各截「卡片」与「全屏」两张，确认 `#foot` 的矩形不与 `#card` 相交，且全屏底部无按钮。

### 改法 2：给首屏一个真入口，把检索做成能落地的结果
1. **默认就给出 8–12 首名篇的题名**：现在 canvas 里没有任何 `fillText`，只有悬停后的 HTML tooltip；新增一层 `drawLabels()`，在星点绘制后只给 `p.hot` 画 10.5px 题名，用「40px 内不重复」去重。首屏必须能读到「登高 / 春望 / 月夜 / 石壕吏 / 秋兴八首 一」中的至少 4 个。
```js
function drawLabels(){
  var placed=[];
  pts.filter(function(p){return p.hot&&p._q;}).forEach(function(p){
    var q=p._q;
    if(q.sx<0||q.sx>W||q.sy<0||q.sy>H) return;
    if(placed.some(function(s){return Math.hypot(s.x-q.sx,s.y-q.sy)<40;})) return;
    placed.push({x:q.sx,y:q.sy});
    ctx.font='10.5px "Songti SC","SimSun",serif';
    ctx.textAlign='center'; ctx.lineWidth=3;
    ctx.strokeStyle='rgba(4,5,10,.85)';
    ctx.strokeText(p.t,q.sx,q.sy-14);
    ctx.fillStyle='rgba(236,231,219,.82)';
    ctx.fillText(p.t,q.sx,q.sy-14);
  });
}
```
在 `render()` 画完星点后调用 `drawLabels()`；hover / selected 可复用同一层。
2. **加一条「从这里开始」**：底部图例上方放 5 个 44px 高的胶囊，点击直接 `selectAndFly('登高')`；文案就是诗题，不要写「探索」。
3. **把检索变成命令面板**：输入即出 `#results`（右侧 360px，最多 8 行，每行 44px：诗题 13px + 首句/年代 11px）；↑↓ 选择、Enter 打开选中项、Esc 清空；空态文案「没有找到「X」。试试：月 / 秋 / 登高」；结果按「诗题精确命中 → 诗题包含 → 全文包含」排序。现在回车是空操作，这一条能立刻把检索从「高亮过滤器」变成「导航」。
4. **别让中心装成杜甫**：在星璇中心常驻 10px 标签「白噪音 · 非杜甫」；`selectNoise` 的卡片标题改成「机器拟诗 · 非杜甫」，并给整张卡一条不同的顶边/底色；或者在首次点开前加一句「这是机器用杜甫的字拼的，不是他的诗」。概念可以保留，但不能让首点误解。

### 改法 3：补 1366/短屏规则，补键盘与触屏
```css
@media (max-height:820px){
  #side{top:auto;bottom:210px;transform:none;gap:14px}
  #foot{padding-bottom:18px}
  #legend{gap:10px 14px;max-width:calc(100vw - 500px)}
}
@media (max-width:1500px){
  #card{width:min(420px,42vw)}
  #legend{max-width:calc(100vw - 470px)}
}
@media (pointer:coarse){
  body{cursor:auto} #cur{display:none}
  #view .v,#mode .m,#sy .s,#au .s{min-height:44px;display:inline-flex;align-items:center}
}
```
- **字**：`.no,.lg .c,.fs-note{color:#8a8578;font-size:11px}`；`#hint{font-size:12px;color:#a9a496}`；`#search input::placeholder{color:#8a8578}`；所有正文元信息不低于 11px、对比度不低于 4.5:1。
- **控件**：把 `.sb/.dm/.m/.s/.readtoggle/.lg` 改成 `<button>`，加 `aria-pressed`；`button:focus-visible{outline:1px solid var(--gold);outline-offset:3px}`；点击区不小于 44×44。
- **诗卡**：把 `fitPoem` 里已经算好的 `need/avail` 用起来：`if(need>avail){ setReading(true); }`，或按 `avail/need` 缩 `--poem-fs` 到最小 13px；1366×768 打开长诗应自动进全屏，而不是切掉最后一行。
- **阅读**：加「←/→ 上一首/下一首」「返回星海」可见入口；现在的阅读是死路，只能退出或 Esc。

## 一句总评

它先是一件会呼吸的视觉作品，还不是一件能让人找到诗的产品：层级、入口、小屏这三件事修好，1468 颗星才真正可读。