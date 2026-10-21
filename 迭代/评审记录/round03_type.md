# 字体与编辑设计（字号阶梯 / 竖排 / 行距 / 阅读版式）· 第 3 轮评审

**总分：65 / 100**
**与上轮差：−1（66 → 65）**

实拍口径：Edge headless（`--use-angle=swiftshader`）经 CDP 实控，先 `Emulation.setDeviceMetricsOverride` 锁 1920×1080 / 1366×768，再等程序化星云算完；所有 px、行数、滚动量、对比度取自 `getComputedStyle` / `getBoundingClientRect` / 截图逐像素亮度，不是目测。实拍 19 张（12 张整屏 + 7 张局部），主图 4 张（默认 / 诗卡 / 全屏 / 1366），另加背景空板、200 行长诗、滚动后、2× 局部。文件在 `评审/r3_type/`。

> 结论先说：**这一轮修好了两个"读不到"，却新添了三个"读不对"。** 字本身一个没动——`--t1…--t7`、`.fs-t 42 / .fs-ln 27 / 2.2 / .fs-k 10.5 / .fs-note 10.5`、`#card` 452px 与上轮逐字相同；变的是装字的容器和字底下的天幕。

---

## 一、与上轮的差：+5 / −6 = −1

| 变化 | 分 | 证据（本轮实测 vs 上轮） |
|---|---|---|
| 1366×768 的七律终于读全了 | **+3** | 《登高》诗区 `clientH=232`、列高 `158.5`、`scrollW=419 = clientW`；上轮是 `152 / 179 / 432 > 409`，末字被切、最左列出界。这一轮 56 字全在框内 |
| 200 行长诗改成双栏，滚动减半 | **+2** | `scrollH 6,257`，`clientH 1,058` → **5.9 屏**；上轮单栏 `12,265` → 13.4 屏。少滚约 6,000px，是这轮最实在的阅读改善 |
| 《登高》被 2 栏拆成 3+5，标题从居中变左挂 | **−3** | `#c-full .fs-left{column-count:2}`（[`web/index.html:254`](../web/index.html#L254)）。DOM 顺序 1–8 行，实际落成左栏 3 行（风急/渚清/无边）、右栏 5 行（不尽/万里/百年/艰难/潦倒）——**颔联被拆到两栏**。上轮同一首是单栏居中（`assets_type2/03_full_denggao_1920.png`） |
| 星云把 9–10px 灰字的"最坏情况"打穿 | **−2** | 天空中心平均亮度 `0.0098 → 0.0411`（**4.2×**），p95 `0.0255 → 0.1300`（**5.1×**），>0.10 的像素 `1.88% → 9.25%`；底栏 p95 `0.0068 → 0.0921`（**13.5×**）。图例计数 10px 中位对比度 3.0–3.9，亮云处 **1.81:1**；右下提示 11px 中位 3.43、p99 **2.07:1** |
| 首屏 12 个诗题整层消失 | **−1** | 上轮 canvas `11.5px / α.55` 的《望岳》《登高》《秋兴八首 一》等 12 个题名，本轮源码里已无任何 `fillText`；首屏 DOM 文字只剩 9–12.5px 的操作界面（实测 56 个文字节点，0 个诗题）。天幕更美，但**第一屏不再有一个可读的诗名** |

字阶本身零改动，所以分数几乎全部由"容器"和"底"决定：

- 「推定」实测 **9.16667px / `#6a665c` / 3.52:1**，与上轮 9.17px / 3.52 逐位相同；
- `#c-full .fs-note` 仍 **10.5px / `#57544c` / 2.66:1**；
- 1366 的"读全"是拿高度换的：艺术图 150 + 卡头 159 + 卡脚 227 = 536px，诗区只剩 **232px（30% 屏高）**；
- 诗卡仍 **452px 宽**，长诗诗墨仍 **127.8px 高**，`scrollWidth` 仍 **10,244px**；
- 「共 N 列」提示仍是死代码：`#c-cns` 对 200 行长诗 `hasLie=false、hasFull=false`，文字仍是"星座 · 共享…"——1984 行追加的提示在 2038/2059 行又被 `renderRelations()` 的 `el.innerHTML=txt` 盖掉（[`web/index.html:1983`](../web/index.html#L1983)、[`:2477`](../web/index.html#L2477)）。

![默认 1920：星云是第一眼的主角，界面文字退成了噪点](r3_type/01_default_1920.png)

![诗卡 1920：452px 的侧栏，诗、图、考据各占一段](r3_type/02_card_denggao_1920.png)

![全屏 1920：《登高》八句被拆成 3+5](r3_type/03_full_denggao_1920.png)

![1366×768 默认：底栏图例正压在亮云上](r3_type/07_default_1366.png)

---

## 二、还剩的三条最伤

### 1. 全屏长诗：右栏只活一屏；短诗又被 2 栏拆联

**长诗（200 行《秋日夔府咏怀…》）**

- `#c-full` `scrollH=6,257 / clientH=1,058` = **5.9 屏**；左栏高 **6,106px**，右栏只有 **578px**。
- 滚到 `scrollTop=1,400`：右栏 `y = −1,313`，**整块消失**；再往下 5,400px，右半屏永久空白（[`06_full_long_scrolled_1920.png`](r3_type/06_full_long_scrolled_1920.png)）。
- `.fs-left.long{column-count:3}` 写在 255 行，但没有任何 JS 加 `long` 类：200 行实测 `cols="2"`、`class="fs-left"`。三栏样式是死的。
- 标题与作者在同一个滚动容器里，滚过一屏连"这是哪首"都没有；行距 **59.4px = 2.2×**，200 行仍要滚近 6 屏。

**短诗（《登高》）**

- 2 栏把 8 句切成 3+5，颔联"无边落木萧萧下 / 不尽长江滚滚来"跨栏；标题被挤到左栏顶端，上轮的居中单栏仪式感没了。
- 左栏 690px 里诗墨只占 **356px**；右栏 793px 里正文按 `max-width:62ch` 也只吃到约 **480px**——两侧合计约 **650px（34% 屏宽）没有字**。
- 说明行 10.5px / 2.66:1，是整屏最该被读到的"名篇 · 七言律诗 · 56 字"，却最看不见。

![《登高》2×：左栏 3 行、右栏 5 行，颔联被栏切断](r3_type/13_denggao_split_2x.png)

**改法（可直接落）**

```js
// renderFull() 末尾：按诗型分栏，短诗回单栏，长诗才三栏
var left = document.querySelector('#c-full .fs-left');
left.classList.toggle('short', p.L.length <= 16);
left.classList.toggle('long',  p.L.length > 60);
```

```css
#c-full .fs-left.short{column-count:1;max-width:24em;margin:0 auto}
#c-full .fs-left.long {column-count:3;column-gap:44px}
#c-full .fs-right{position:sticky;top:6vh;align-self:start;max-height:86vh;overflow:auto}
#c-full .fs-ln{font-size:clamp(21px,1.45vw,27px);line-height:1.9;break-inside:avoid}
/* 七律的联不能被栏切开：两行一包 */
#c-full .cu{break-inside:avoid;page-break-inside:avoid}
```

```js
// 行循环改成"两句一联"的块，再交给 column 分配
for (var i = 0; i < p.L.length; i += 2) {
  var g = document.createElement('div'); g.className = 'cu';
  g.appendChild(mkLine(p.L[i]));
  if (p.L[i+1]) g.appendChild(mkLine(p.L[i+1]));
  left.appendChild(g);
}
```

预期：200 行三栏约 **4,200px（3.4 屏）**；右栏常驻；《登高》回到单栏 8 行、标题居中，颔联不再跨栏。

### 2. 诗卡里"诗"仍然只是右上角一条：200 列只看见 4.4%

- 200 行：`scrollW=10,244 / clientW=451` = **22.7 倍**；一屏 8 列，**可见 4.4%**。
- 诗墨高 **127.8px**：占 675px 诗区的 **18.9%**、占 1080px 卡片的 **11.8%**；卡头 171 + 卡脚 233，诗被夹在中间。
- 8 列挤在卡片最右，往左拖 192 列没有计数、没有箭头、没有"共 200 列"；滚动条 3px `#26282e`，在 `#06070c` 上等于隐形。
- `fitPoem()` 名字叫 fit，实际只写死 `--poem-fs:17.5px`（[`web/index.html:2365`](../web/index.html#L2365)）；1366 的字号又由媒体查询直写 `#card .col{font-size:15.5px}`（[`:445`](../web/index.html#L445)），两边互不知情。
- 评语 `#c-note` 仍在诗**之前**（诗卡头部 y=395，诗 y=431），11.5px 的结论压在诗上。

**改法**

```html
<!-- #c-poem 之后，独立节点，不再和 #c-cns 抢 -->
<div id="c-poemhint" class="poemhint"></div>
```

```js
function fitPoem(p){
  var el = document.getElementById('c-poem');
  var maxLen = Math.max.apply(null, p.L.map(function(s){return s.length;}));
  var fs = Math.max(14, Math.min(21, Math.floor((el.clientHeight - 28) / (maxLen * 1.22))));
  el.style.setProperty('--poem-fs', fs + 'px');           // 真的把字号落下去
  var per = Math.max(1, Math.floor((el.clientWidth - 32) / (fs * 1.16 + 16)));
  var hint = document.getElementById('c-poemhint');
  hint.textContent = p.L.length > per
    ? '第 1–' + per + ' 列 / 共 ' + p.L.length + ' 列 · 横向拖动或按 →'
    : '';
  hint.style.display = p.L.length > per ? '' : 'none';
}
```

```css
#card .poem{--poem-fs:17.5px;scroll-snap-type:x mandatory;
  scrollbar-width:thin;scrollbar-color:#8a8578 transparent}
#card .col{font-size:var(--poem-fs)}          /* 媒体查询也改走变量 */
#card .poem::-webkit-scrollbar{height:6px}
#card .poem::-webkit-scrollbar-thumb{background:#8a8578}
#card .poemhint{font-size:12px;letter-spacing:.08em;color:#8f8a7c;padding:0 30px 12px}
```

再把评语移到诗后，并在 `p.L.length > 24` 时直接进全屏：

```js
document.getElementById('c-poem').after(document.getElementById('c-note'));
if (p.L.length > 24) setReading(true);
```

### 3. 字号阶梯与底噪：11 个字号里 7 个不在阶，9–10px 灰字没有"均匀的黑"可站

**阶梯名存实亡。** 注释写"8 个层级"，实际只有 7 个变量（9 / 11 / 12.5 / 15 / 23 / 34 / 66，[`web/index.html:12`](../web/index.html#L12)）。三态实测：

| 场景 | 实测字号（出现次数） | 在 7 档上 |
|---|---|---|
| 默认 1920 | 8.5×5、9×3、10×10、11×13、12×9、12.5×15、16×1 | **3 / 7**（8.5、10、12、16 全在阶外） |
| 诗卡（开《登高》） | 8.5、9、10、10.5、11、11.5、12、12.5、16、17.5、23 | **4 / 11** |
| 全屏（同首） | 8.5、9、10、10.5、11、12、12.5、15.5、16、27、42 | **3 / 11** |

- 第一个字就不在阶上：`杜詩星海` 16px，七档里没有 16；全屏正文 15.5px，阶梯里是 15px；全屏 42 / 27 也都不在阶上。
- 同一"级"两套比例：卡片 `23 : 17.5 = 1.31`，全屏 `42 : 27 = 1.56`。

**对比度：小字本来就不达标，星云把最坏情况又拉低一半。**

| 元素 | 字号 | 色 | 底 | 对比度 |
|---|---|---|---|---|
| 英文品牌 | 9px | `#4e4b44` | 黑 | **2.29:1** |
| 右上 `POEMS 1468` | 9px | `#55524a` | 黑 | **2.63:1** |
| 左栏编号 00–04 | 8.5px | `#5f5c53` | 黑 | **2.95:1** |
| 图例计数 | 10px | `#6f6b61` | 星云 | 3.0–3.9，亮云 **1.81** |
| 右下操作提示 | 11px | `#6f6b61` | 星云 | 3.43，p99 **2.07** |
| 「推定」 | **9.17px** | `#6a665c` | 卡面 | **3.52:1** |
| 全屏说明 | 10.5px | `#57544c` | 卡面 | **2.66:1** |
| 关系标签 | 10.5px | `#6a675e` | 卡面 | **3.56:1** |
| 关系前置词 | 9px | `#3f3d37` | 卡面 | **1.85:1** |

公平地说，星云没有把中位对比度拉垮多少——顶栏和左栏底下仍是黑的（`bgmed 0.001–0.006`），真正变糟的是**最坏情况**：底栏 p95 亮度 13.5×，图例计数从黑底的约 4.0 掉到中位 3.0–3.9、最亮处 1.81，提示中位 3.43、p99 2.07。9–10px 的字原本靠"均匀的黑"撑着，现在黑没了，字又没有变大。**读的地方反而是干净的**：卡面最安静 64×64 区块 σ=9e−5，全屏 σ=2.2e−4——脏的只有天幕四角。

![右上 9px：在黑底上也只有 2.6:1](r3_type/11_topright_2x.png)

![底栏 2×：12.5px 的意象名可读，10px 的计数已经开始化进云里](r3_type/12_bottom_2x.png)

**改法：一条 8 档阶梯 + 一层局部压暗，别全局调暗星云。**

```css
:root{
  --t1:12px; --t2:15px; --t3:17.5px; --t4:23px;
  --t5:27px; --t6:34px; --t7:42px; --t8:66px;
  --ink-1:#ece7db; --ink-2:#c9c3b4; --ink-3:#a9a496; --ink-4:#8f8a7c;
}
.brand .cn{font-size:var(--t2)}                       /* 16 → 15 */
.brand .en,#meta-r .num,#side .sb i{font-size:var(--t1);color:var(--ink-4)}
#c-meta,#c-meta sup,#c-full .fs-k,#c-full .fs-note{font-size:var(--t1)}
#c-meta sup{color:var(--ink-3);vertical-align:baseline;margin-left:4px}  /* 9.17 → 12，3.52 → 5.9 */
#c-note{font-size:var(--t1);color:#b5b0a2}            /* 11.5 → 12，7.4 → 8.9 */
.rel i,.rel .rl{font-size:var(--t1);color:var(--ink-3)}
#c-full .fs-ln{font-size:clamp(21px,1.45vw,27px);line-height:1.9}
```

```css
/* 只压 UI 两条边，不动天幕主体 */
#scrim-t,#scrim-b{position:fixed;left:0;right:0;z-index:10;pointer-events:none}
#scrim-t{top:0;height:170px;
  background:linear-gradient(180deg,rgba(4,5,10,.78),rgba(4,5,10,.45) 45%,transparent)}
#scrim-b{bottom:0;height:150px;
  background:linear-gradient(0deg,rgba(4,5,10,.82),rgba(4,5,10,.40) 50%,transparent)}
```

按最亮云 0.092 估算：底栏 0.092 × (1−0.82) ≈ 0.017，配 `#a9a496` 可得 **约 6.5:1**；顶栏 0.03 × 0.22 ≈ 0.007，配 `#8f8a7c` 约 **5.3:1**。星云主体一像素不动，四角的字先活下来。

---

## 三、竖排与行距：竖排没坏，行距还太松

- 诗卡竖排的执行是对的：`row-reverse` 保证首列在右，`text-orientation:upright`，17.5px 字配 `line-height:2`、列距 51px（35+16）、字距 2.8px；1366 是 15.5px / 29.45 / 列距 41.5。**读起来是舒服的**，坏的是装它的容器只有 451px 宽、长诗只露 8 列。
- 全屏行距 2.2×（27px → 59.4px）对八句律诗是海报，不是书；200 行则纯属浪费。收到 **1.9×** 正好：短诗仍舒展，长诗三栏后约 4.2k px。
- 诗卡 452px 是"侧栏"宽度，不是"阅读页"宽度；竖排每列 35px，一屏 8 列，先天只能当索引。要它承担"读整首"，就得在宽度或全屏之间二选一。

![长诗诗卡：8 列、200 行，诗墨 127.8px，下面 500px 空场](r3_type/15_longcard.png)

![长诗全屏：2 栏各 16 行，右栏在这一屏之后就不存在了](r3_type/05_full_long_top_1920.png)

![滚到 1,400px：右半屏 5,400px 全空，标题也已滚走](r3_type/06_full_long_scrolled_1920.png)

---

## 四、一句总评

这一轮把天幕做成了真的深空——青蓝、洋红、赭金三层色，丝状脊和 5,200 颗细星，是整件作品目前最强的一笔；读诗的那块地方也仍然是安静的（σ=2.2e−4）。但**字这一层没有跟着升级**：它既没拿到新的阶梯，也没拿到新的底。1366 的七律读全了、长诗少滚了 6,000px，这是实打实的 +5；可《登高》被两栏拆成 3+5、200 行仍只露 4.4%、9–10px 的灰字从"均匀的黑"掉进"发亮的云"，又把这 5 分赔了回去。**65 分：不是星云不好，是字还站在上轮的位置上，而脚下的地已经换了。**

---

## 五、实拍索引（`评审/r3_type/`）

| 文件 | 内容 |
|---|---|
| `01_default_1920.png` | 1920×1080 默认，程序化星云 |
| `02_card_denggao_1920.png` | 《登高》诗卡，452px |
| `03_full_denggao_1920.png` | 《登高》全屏，3+5 拆联 |
| `07_default_1366.png` | 1366×768 默认 |
| `08_card_denggao_1366.png` | 1366 诗卡，56 字全在框内 |
| `10_full_denggao_1366.png` | 1366 全屏 |
| `04_card_long_1920.png` / `15_longcard.png` | 200 行长诗诗卡，4.4% 可见 |
| `05_full_long_top_1920.png` / `06_full_long_scrolled_1920.png` | 长诗全屏顶 / 滚 1,400px 后右栏消失 |
| `00_bgplate_1920.png` / `00_bgplate_1366.png` | 隐去全部 UI 的天幕空板（亮度测量用） |
| `11_topright_2x.png` / `12_bottom_2x.png` / `13_denggao_split_2x.png` / `14_cardhead_2x.png` | 2× 证据局部 |
| `metrics.json` / `probe.json` / `probe2.json` | 全部实测值原始记录 |
