# 美术指导（色彩 / 构图 / 光影 / 材质 / 视觉层级）· 第 2 轮评审

**总分：61 / 100**
**与上轮差：+18（43 → 61）**

> **实拍条件**：Edge `--headless=new --no-sandbox --use-angle=swiftshader --enable-unsafe-swiftshader`，1920×1080 / 1366×768，`--virtual-time-budget 9000`，直接打开交付的 `杜诗星海.html`（5,972,096 B，mtime 13:12）。共 7 张主图 + 2 张 A/B + 2 张改法验证，全在 `评审/r2/`：
> `r2_01_default.png`（默认）、`r2_02_card_denggao.png`（《登高》诗卡）、`r2_03_full_denggao.png`（全屏）、`r2_04_full_200lines.png`（200 行长诗全屏）、`r2_05_1366_default.png`、`r2_06_1366_card.png`、`r2_07_novig.png` / `r2_08_vig1.png`（暗角 A/B）、`r2_09_cardfix1366.png` / `r2_10_cardfix1920.png`（诗卡改法验证）、`r2_12/13_readfix.png`（读诗页改法验证）。
> 文中数字都是对 PNG 的像素测量（Python + numpy），不是目测。

| 维度 | 上轮 | 本轮 | 关键证据（同一口径重测上轮图） |
|---|---|---|---|
| 光影 | 33 | **63** | 核心区 ≥250 的像素 **12.08% → 0.07%**；全帧 ≥250 0.245% → 0.007%；最亮 170×160 窗口只剩 0.118%。代价：亮部变“平均”，全屏 p95 仍只有 16.35，暗角又把 chrome 压到 0.5×。 |
| 材质 | 38 | **60** | 4× 放大：轴对齐方块没了，换成径向 sprite（`crop_core4x.png`）；但过软，读作“散景”而非“星”。颗粒平坦区 std 0.66 → **0.92**（仍等于没加）；水墨只在诗卡（均值 L 94.3 / p95 173.8），全屏归零。 |
| 色彩 | 46 | **65** | 亮部平均色度 **0.094 → 0.163**；色度<0.10 的亮像素 **57.8% → 37.1%**；图例十色在画面里认得出（日月蓝 / 江山青 / 草木绿 / 兵戈红）。但 L>150 的最亮星平均 RGB(199,190,179)，色相仍被奶油白核吃掉。 |
| 构图 | 53 | **58** | 亮质心 (873,582) → **(975,502)**，离画心只差 (+15,−38)；右上受光面积（L>8）**3.72% → 24.17%**，四个象限 12.1/24.2/25.1/11.0 成对角主带；12 个题名开始承担“读图索引”。失分在两张阅读面（卡 / 全屏）的版面。 |
| 视觉层级 | 40 | **57** | 白洞不再抢焦点；12 个题名 + 依据 10.5px/5.48:1（上轮 2.7:1）都回来了；但 `#vig` 把 POEMS 压到 **1.42:1**、检索占位 **1.36:1**、提示 2.10:1，图例金块 3.48:1（应为 8.42:1）。 |

**先说这轮修好的（别回滚）**：① 过曝真的治住了（12.08%→0.07%），方块粒子换成径向 sprite；② 类别色回来了，图例和星场能对上；③ 诗卡已在暗角之上（`名篇` 徽标实测 200,161,39 = `--gold` 原色）；④ `align-content:safe center` 生效——200 行诗的标题从 y=98 起，没有被裁头；⑤ 首屏 12 个题名、1366 布局、检索回车都能用。

---

## 三条问题（现在仍然最伤）

### 1. 暗角仍压在**全部 chrome** 上：品牌、检索、图例被压到 1.4:1–3.7:1

- 层级没归位完。`#vig{z-index:14}`（web/index.html:44）在 `#top` / `#side` / `#foot` 的 `z-index:12`（:57 / :78 / :111）之上，只有 `#card`（:196，z16）逃出来了。实测把 `#vig` 放回 z1 的 A/B（`r2_08_vig1.png`）：

| 元素 | 现在（vig 14） | `#vig{z-index:1}` 后 | 规范值 |
|---|---|---|---|
| 品牌「杜詩星海」 | (150,147,141) | **(236,231,219)** | `--paper` #ece7db |
| 检索「意象」金块 | (122,98,23) | **(199,159,38)** | `--gold` #c9a227 |
| 图例「日月」 | (108,105,97) | **(192,186,171)** | #c2bcae |
| 右上 POEMS | (43,42,39) → **1.42:1** | (66,64,59) → 2.61:1 | #55524a |

  对应 WCAG：POEMS **1.42:1**（即便去掉暗角也只有 2.61）、检索占位 **1.36:1**（原始色也只有 1.88）、右下提示 **2.10:1**、图例 3.71:1（应为 10.76）、金块 3.48:1（应为 8.42）。**全屏里唯一说出「1468 首」的地方，和唯一的检索入口，恰恰是首屏最看不清的两行字。**
- 底栏没有底衬。热门星的十字芒直接穿进图例：`r2_01` 在「兵戈 130」处测得星芒 L=**164**，而同排图例字峰值只有 **111**——星比标签亮 1.5 倍（裁图 `crop_footer_star.png`）。1366 下同样有一枚星芒压着「病老 157」。
- 后果：品牌读成灰字而不是纸白，金块读成土黄，图例读成“半透明注释”。这不是风格问题，是 0.5–0.65 倍的整层乘算。

### 2. 全屏阅读仍是死黑板；200 行长诗 = 11 屏滚动，右栏第四屏就空了

- **材质被扔了。** `#card.reading .art{display:none!important}`（:233）+ `setReading()` 里 `art.style.display='none'`（:2179），把全片唯一有笔触的材料（诗卡里均值 L **94.3**、p95 **173.8** 的水墨）关掉了。全屏 200×400 平坦区实测：**mean 7.54 / std 0.92 / min 6 / max 11**（上轮 0.66），p95 16.35，41.7% 像素 <8——是“死黑”，不是“夜”。
- **长诗变成 11 屏。** 200 行 × 27px/2.2 → `.fs-left` 高 **12,134px**，1080 视口约 **11.2 屏**；右栏只有 578px，滚到第二屏以后整页右边是空的（`r2_04`）。
- **标题断在词里。** 42px 标题折成两行，断点是「…郑监李宾客一 / 百韵」，留一个 2 字孤行（title bbox x148–810，y98–239）。
- 268 字的《登高》这页是好看的：27px 竖排、56 字宽的分栏、落款都对。但它是一张**黑网页**，不是一张**诗页**——这是这一层和上一轮几乎没有变化的原因。

### 3. 诗卡把诗挤在面板上半截；1366 还横向溢出 32px

- **1920：诗只占面板 39%。** 诗块墨迹 y **461–630**（169px），诗面板约 y **400–838**（438px），下方空到「依据」首行 **868** 才接上——**238px 空档**，诗块中心 545 比面板中心 619 高 74px。原因是 `.poem{align-items:flex-start}`（:270）从没改过，上一轮提的“给诗让位”只改了字号阶梯，没改对齐。
- **1366：8 列装不进 360px。** 卡宽 420（媒体查询 `:435`），内容宽 360；8 列需要 8×35 + 7×16 = **392px → 溢出 32px**。墨迹实测 x **963**（距卡左缘 17px）到 x **1337**（距窗口右缘 29px），本该是 30px 内边距；右列「风急天高猿啸哀」几乎贴住窗口边。
- **1366 的元信息断在词里。** 「≈767 年秋（大历二年）」被折成「≈767 年 / 秋（大历二年）」，`推定` 上标孤悬在第二行。
- **配图被 flex 偷偷吃掉。** `.art` 写的 `height:24%`，但作为 flex 子项默认 `flex-shrink:1`：1920 实测只有 **220px（20.4%）**、1366 只有 **156px（20.3%）**，海报比设计值矮了 39px。

（附带：`NO.0825` 仍是 9px #4e4b44 = 2.26:1；全屏右栏 15.5px 与左诗 27px 的比例没问题，但全屏没有“书页”的边距感。）

---

## 三条改法

### 改法 1：暗角放回画布，chrome 抬到正常值（一行 + 三处色值 + 一条底衬）

```css
#vig{z-index:1}                       /* 只压 canvas，不压 #top/#side/#foot；天空观感不变 */
#meta-r .num{color:#8a8578}            /* 1.42 → 5.4:1 */
#search input::placeholder{color:#7e7a6e}
#hint{color:#8a8578}
#foot:before{content:"";position:fixed;left:0;right:0;bottom:0;height:200px;z-index:-1;
  pointer-events:none;background:linear-gradient(180deg,rgba(4,5,10,0),rgba(4,5,10,.86) 55%,#04050a)}
```

- `#vig` 与 canvas 自带的 `buildVig()` 本来就是两层暗角；z1 后天空取样不变（角 (2,2,5)、心 (4,5,11) 与改前一致，见 `r2_08`），只是 UI 不再被乘 0.5–0.65。
- 底衬接住热门星的十字芒，图例区不再出现 164 > 111 的“星比字亮”。
- **验收**：金块回到 (201,162,39)、品牌 (236,231,219)、图例 (194,188,174)；POEMS ≥4.5:1；图例带内最大亮度 ≤130。

### 改法 2：把水墨搬回全屏（用长手写，别用 shorthand），长诗两栏 + 右栏 sticky

```css
#card.reading::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:var(--hero);background-size:cover;background-repeat:no-repeat;
  background-position:center 42%;
  filter:grayscale(1) contrast(1.4) brightness(.55);
  opacity:.05;mix-blend-mode:screen}
#grain{opacity:.03;mix-blend-mode:screen}          /* 纯黑上 overlay 无效，必须 screen */
#card.reading #c-full{position:relative;z-index:1}
#c-full.long .fs-left{column-count:2;column-gap:4.5vw}
#c-full.long .fs-t,#c-full.long .fs-a,#c-full.long .fs-rule,#c-full.long .fs-note{column-span:all}
#c-full.long .fs-ln{font-size:22px;line-height:1.95;break-inside:avoid}
#c-full .fs-right{position:sticky;top:6vh;align-self:start}
```

```js
// setReading(true) 里
var img=document.getElementById('c-img');
card.style.setProperty('--hero', img.style.backgroundImage);
// renderFull 末尾
if(p.L.length>40) el.classList.add('long');
// 长标题：>14 字加 class，34px + text-wrap:balance，或在「奉寄」处硬断
```

- 必须用 `background-image` / `background-size` 长手写：我第一版用 `background:var(--hero) center/cover`，art 被平铺成 3 张（`r2_12`）。第二版 7% + grain .04 时 std 已到 **2.66**，但 mean 被抬到 **21.8**（原 11.2），页面发灰；所以墨再收到 4–5%、grain .03。
- **验收**：平坦区 **std 2.2–3.0、mean ≤16**（现在 0.92 / 7.5）；200 行高度 12,134 → ≤6,000px（约 4–5 屏）；标题两行字数 9/9，不出现「一 / 百韵」。

### 改法 3：诗卡——垂直居中、24% 归还、1366 换列距（三条 CSS）

```css
#card .art{flex:0 0 24%}                 /* 别再被 flex 缩成 20.4% */
#card .poem{align-items:center}          /* 诗块居中：上/下各约 134px，而不是上 61 / 下 208 */
@media (max-width:1400px){
  #card .col{line-height:1.75;letter-spacing:.13em}
  #card .poem{gap:9px}
  #card .mt{font-size:10.5px}
  #card .mt .pd{display:block;margin-top:2px}   /* 「≈767 年秋」整块换行，不再断在“年/秋” */
}
```

- 1366：8×1.75×17.5 + 7×9 = 308px < 360，列不再溢到内边距；1920：诗块居中，上/下留白从 61/208 变 ~134/134（验证图 `r2_09` / `r2_10`）。
- 若还想让诗更大：`--poem-fs = min(17.5, (contentW − 7×gap) / (cols×1.75))`，1366 可到 19px；不要再靠 `line-height:2` 吃宽度。
- **验收**：1366 首列墨迹 ≥976、末列 ≤1336；1920 诗块上下留白差 ≤20px；art 回到 259px。

---

## 一句总评

这一轮把最刺眼的白洞和灰星修掉了——星海第一次有颜色、有名字、有中心；但界面仍被自己的暗角按在 0.6 倍亮度里，读诗页仍是一块死黑板，诗卡仍把诗挤在格子顶端：**概念已经看得见了，仪式感还没做出来。**
