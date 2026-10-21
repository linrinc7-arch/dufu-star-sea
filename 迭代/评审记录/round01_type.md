# 字体与编辑设计（字号阶梯/竖排/行距/中英混排/阅读版式） · 第 1 轮评审

总分：64/100

实拍口径：Edge headless，1920×1080、1440×900、2559×1599（设计文档写明的验收尺寸）三档；Windows 字体真实回退——"Songti SC"/"STSong" 不在本机，栈里第一个可用的是 SimSun。下文 px、对比度、滚动量均取自页面内 `getComputedStyle` / `getBoundingClientRect` 与截图取样，不是目测。截图与 2× 局部见 `assets_type/`。

| 维度 | 分 | 依据 |
|---|---|---|
| 字号阶梯与层级 | 12/20 | `:root` 声明 9/11/12.5/15/23/34/66（+竖排 17.5）共八档；全屏/卡片实际出现 42/27/15.5/12/11.5/10.5/9.5，`sup` 计算值 8.75。卡片 23:17.5 与全屏 42:27 是两套互不换算的比例，标题在两处不是同一个"级" |
| 竖排与行距 | 13/20 | 竖排方向、`text-orientation:upright`、正文字面 12.4:1 都对；但 `line-height:2` 使列距 35px（2em），7 字占 179px（每字 25.6px），字缝过散；200 列长诗在 451px 里排成 10,244px |
| 行长与阅读节奏 | 12/20 | 右栏 1920 下约 46–47 字/行，2559 下约 60–63 字/行，没有 `max-width`；卡片诗块仅 179px 高，诗与页脚之间约 235px 空场 |
| 中英混排与字体 | 9/15 | 中文标签套 `"Helvetica Neue",Arial,sans-serif`，栈里没有任何中文字体，中文由浏览器默认回退决定（换平台就换脸），与正文宋体不是一套；SimSun 在 9–11.5px 发虚；英文副标 9px / 2.34:1 |
| 阅读版式（诗卡/全屏/长诗） | 10/15 | 200 行长诗的标题与前 67 行在全屏里不可达；2559 下左栏 928px 宽只放 230px 诗；评语放在诗之前 |
| 细节与一致性 | 8/10 | 「推断」8.75px / 2.26:1，证据行 9.5px / 2.6:1；NO. 与名篇角标 9px 尚统一；标点、书名号、年份范围基本规范 |

默认视角（`01_default_1920.png`）是三者中最稳的：16px 站名、9px 全大写英文副标、12.5px 导航、9px 仪器元信息，层级干净，金色只做选中，星图不抢字。问题不在星图，在打开诗之后——下面三条都发生在"读"的界面。

## 最伤的三个问题（每条带证据）

### 1. 长诗一开全屏就被"垂直居中"裁掉开头，诗卡则把 200 列藏进 451px 的暗槽

这不是边缘情况：`秋日夔府咏怀奉寄郑监李宾客一百韵` 一首 200 行；全库最长的六首是 200/140/112/100/100/88 行，长诗不是少数几首。

- 全屏实测：`#c-full` 的 `scrollTop=0` 时，`scrollHeight=8569`、`clientHeight=912`；标题 `getBoundingClientRect().y=-3854`，第一行 `y=-3986`。也就是说，**标题和前面约 67 行在滚动原点之上，永远够不到**。截图里打开即从"马来皆汗血"开始，没有题目；这不是"没滚到顶"，是顶被 `align-content:center` 的溢出裁掉了。
- 原因在 CSS：`#c-full{display:grid; align-content:center; overflow-y:auto}`。内容高于容器时，居中会把上溢部分推到负坐标，滚动条只覆盖下溢部分。
- 诗卡实测：`poem.scrollWidth=10244`、`clientWidth=451`、`cols=200`；可见约 8 列，滚动条是 3px、拇指 `#26282e`，没有"共 200 句 / 1–8"之类的计数，也没有可拖动的把手。用户会以为这首诗只有八句，或者以为卡住了。

![200 行长诗的诗卡：只露 8 列，无计数、无提示](assets_type/04_card_long_200lines.png)

![全屏 200 行诗：scrollTop=0 的实测覆盖层](assets_type/05_reading_long_scrolltop0.png)

### 2. 字号阶梯只活在文档里；真正读信息的字，跌到了 8.75px / 2.26:1

设计规范写"只允许八个值，禁止 13、14 这类顺手写"。但全屏阅读的 CSS 是另一套：`42 / 27 / 15.5 / 12 / 11.5 / 10.5` 全部不在阶上；`#c-meta sup` 的计算字号是 **8.75px**。这不是"差 0.5px 的校准"，是每个组件各自拿眼睛调的。

- 「推断」这两个字是全站最重要的认识论标记（时期是模型推的），却只有 8.75px、`#4e4b44`，在 `#090b11` 上对比度 **2.26:1**；1× 下就是一粒灰。见 `07_card_head_2x.png` 元信息行末尾。
- 同类：卡片"依据"9.5px / 2.6:1；全屏"说明"11.5px / 3.79:1；"写作时间"等标签 10.5px 加 0.3em 字距；英文副标 "THE STAR SEA OF DU FU" 9px / 2.34:1。深底上的小字本来就吃亏，这里还把字重和颜色一起压。
- 字体落地：一个 5.5MB 的单文件没有内嵌任何字体。Windows 上 `Songti SC / STSong` 不存在，正文实际是 SimSun；9–11px 的 SimSun 在暗底上横细竖粗、抗锯齿发虚，`-webkit-font-smoothing:antialiased` 只会让它更薄。卡片元信息与页脚在 1× 下已经糊成一片。
- 2559×1599 验收尺寸下，42px 的标题只占屏宽 1.6%，27px 的诗只占 1.05%——**字号是固定的，屏幕不是**。

![诗卡头部 2×：元信息 10.5px，末尾「推断」已是一粒灰](assets_type/07_card_head_2x.png)

### 3. "教材式双栏"没有做成"页"：没有共享对齐轴，也没有行长上限

- 1920：诗块实际宽 230px，左栏约 700px；诗右边缘在 x≈600，右栏竖线在 x≈984——中间 **384px 的空场**。诗是居中对齐在一个看不见的栏里，不是对齐页边；标题、诗、右栏三者没有共同轴线。
- 2559：诗块仍是 230px（屏宽 9%），诗与右栏之间约 555px 空场；右栏 15.5px 的行跑到 **60–63 字/行**，1920 下 46–47 字/行。中文 15.5px 的舒适行长约 30–38 字，这里全靠视口决定，读者在两档屏幕上得到两种完全不同的阅读节奏。
- 诗卡：`#c-note`（"明人胡应麟推为「古今七律第一」……"）在 DOM 与视觉上都排在诗之前。读者先被告知结论，再看到诗；这块 11.5px 的评语还占掉了本可以给诗的高度。诗块 179px 高，卡片 1080px 高，诗与页脚之间约 235px 黑场——**诗不是卡片的视觉主体**。
- 竖排没有方向提示。卡片从右往左，全屏改成横排从左往右；同一位读者在两次点击里要切换两次阅读方向，卡片上没有任何"从右往左"的 cue。

![全屏阅读 1920：诗块 230px，诗与右栏之间 384px 空场](assets_type/03_reading_denghao_1920.png)

![同一页在 2559×1599：标题 42px、诗 27px，整组漂在左中](assets_type/06_reading_denghao_2559.png)

## 三条改法（每条具体到怎么改）

### 改法 1：给长诗分型，先修溢出，再谈竖排

**CSS（必修，1 行）**

```css
#c-full{ align-content:start; }          /* 禁止居中溢出裁头 */
#c-full .fs-left{ align-self:start; }
```

**JS（按句数分型，而不是所有诗共用一套版式）**

```js
var isLong = p.L.length > 16;
card.classList.toggle('longpoem', isLong);
```

```css
/* 律绝：保留双栏教材式 */
#c-full .fs-ln{ font-size:var(--rd-poem); line-height:1.95; }

/* 长诗：改为单栏可读页，解析折到文末，不跟诗抢栏宽 */
#card.reading.longpoem #c-full{ display:block; max-width:720px; margin:0 auto;
  padding:9vh 24px 14vh; }
#card.reading.longpoem .fs-t{ text-align:left; margin-bottom:24px; }
#card.reading.longpoem .fs-ln{ text-align:left; font-size:21px; line-height:1.95;
  letter-spacing:.06em; margin:0 0 .35em; }
#card.reading.longpoem .fs-right{ margin-top:56px; border-left:0; padding-left:0;
  border-top:1px solid var(--line); padding-top:28px; }
```

**诗卡（长诗不要装作只有 8 列）**

```js
if (cols.length > 10) {
  // 8 列一屏，加可见计数与拖动提示
  poem.classList.add('paged');
  hint.textContent = '第 1–8 句 / 共 ' + cols.length + ' 句 · 横向拖动';
}
else { poem.classList.add('short'); }   // 短诗才允许垂直居中，避免长诗重演裁头
```

```css
#card .poem.paged{ scroll-snap-type:x mandatory;
  scrollbar-color:#8a8578 transparent; scrollbar-width:thin;
  -webkit-mask-image:linear-gradient(to left,#000 90%,transparent 100%); }
#card .poem.paged .col{ scroll-snap-align:start; }
#card .poem.paged::-webkit-scrollbar{ height:6px; }
#card .poem.paged::-webkit-scrollbar-thumb{ background:#8a8578; }
#card .poem-hint{ font-family:inherit; font-size:12px; line-height:1.6;
  letter-spacing:.12em; color:#8f8a7c; }
```

长诗在卡片里只给"前 8 句 + 全屏分页读"的入口，比把 200 列塞进 451px 更诚实；全屏则用单栏页，不要硬撑双栏。

### 改法 2：重建字阶，12px 是可读下限，不是装饰下限

**令牌（替换全屏与卡片里的裸 px）**

```css
:root{
  --rd-title: clamp(40px, 3.4vw, 64px);
  --rd-poem:  clamp(24px, 1.8vw, 38px);
  --rd-body:  clamp(15px, 1.05vw, 17px);
  --rd-label: 12px;
  --rd-micro: 12px;
}
#c-full .fs-t{ font-size:var(--rd-title); }
#c-full .fs-ln{ font-size:var(--rd-poem); }
#c-full .fs-k{ font-size:var(--rd-label); letter-spacing:.18em; }
#c-full .fs-v.small{ font-size:var(--rd-micro); color:#8a8578; line-height:1.8; }
```

**「推断」不要用 `sup`。** 把元信息拆成两行，时期单独一行，推断写成正文级文字：

```js
meta.innerHTML = p.f + ' · ' + p.n + ' 字 · ' + p.L.length + ' 句 · <em>' + cat.label + '</em>'
  + '<br><span class="meta2">' + pn + '（推断）</span>';
```

```css
#c-meta{ font-size:12px; letter-spacing:.14em; color:#8f8a7c; line-height:1.9; }
#c-meta .meta2{ font-size:12px; color:#8a8578; }
#c-meta sup{ font-size:12px; vertical-align:baseline; margin-left:4px; color:#8a8578; }
```

**对比度抬到 4.5:1 以上**：`#6a675e`（3.48）→ `#8f8a7c`（约 5.1）；`#57544c`（2.6）→ `#8a8578`（约 4.4，仍偏紧，正文级用 `#a29d8f`）；`#4e4b44`（2.26）只留作纯装饰，不承载"推断/依据"这类信息。

**字体**：在单文件里内嵌一个子集 woff2（1468 首诗常用字约 3–4 千，woff2 约 500–800KB），`@font-face` 放 `:root` 前；回退写成 `"Source Han Serif SC","Noto Serif SC","Songti SC","SimSun",serif`。中文标签如果要无衬线，就明确用 `"Microsoft YaHei"` 并**只给中文**，不要把 `Helvetica/Arial` 套在中文标签上——现在 `#c-full .fs-k` 的栈里没有中文字体，中文实际由浏览器默认回退决定（Windows 与 macOS 各换一张脸），和宋体正文不是一套。英文数字统一 `font-feature-settings:"tnum"`。

### 改法 3：把双栏收成一页，给行长和轴线，给诗卡一个主体

```css
#c-full{
  max-width:1280px; margin:0 auto;
  grid-template-columns:minmax(0,360px) minmax(0,34em);  /* 左诗栏 360，右栏 34 字上限 */
  justify-content:center;
  gap:clamp(48px,5vw,80px);
  padding:8vh 24px;
  align-content:start;
}
#c-full .fs-right{ padding-left:40px; }
#c-full .fs-v{ font-size:var(--rd-body); line-height:1.9; }
```

- 2559 下，如果还想让左边"撑住"，让诗在 ≥1900px 时回到竖排：`#c-full .fs-left{writing-mode:vertical-rl}`，8 列 34–38px，标题横排置顶；右栏保持横排。这样左边不再是一条 230px 的窄缝，而是一整块 8 列的诗版，和卡片的竖排身份也接上了。若不做竖排，至少把诗块改为**贴页边左对齐**，并让第一行与右栏第一行的基线对齐，取消"栏内居中"。
- 诗卡：把评语移到诗之后（DOM 里 `poem.after(note)`），腾出的高度给诗：

```js
document.getElementById('c-poem').after(document.getElementById('c-note'));
```

```css
#card .poem.short{ align-items:center; padding:32px 30px 28px; }  /* 只对短诗居中，消掉 235px 黑场 */
#card .nt{ margin:0 30px 14px; }                                   /* 移到诗下，作为"读后" */
```

诗的字号不要再用固定 17.5：在 `fitPoem` 里按句数给 `FS`——

```js
var FS = p.L.length <= 8 ? 21 : (p.L.length <= 12 ? 19 : 16);
el.style.setProperty('--poem-fs', FS + 'px');
```

8 列 21px 时列距 42px、总宽 336px，仍放得进 391px 的诗区；12 列 16px 时总宽 384px，刚好。

- 竖排方向提示：在诗区左缘加一枚 6px、竖排、`#8a8578` 的"从右往左"字样，或在首次打开卡片时做一次 1.2s 的右→左遮罩扫过；不要只靠文化默认。

## 一句总评

星图的第一眼是专业的；一翻开诗，字号和分页就把"教材"两个字露了——不是不够美，是阅读模型还没做完。
