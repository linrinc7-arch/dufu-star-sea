# 字体与编辑设计（字号阶梯/竖排/行距/中英混排/阅读版式） · 第 2 轮评审

**总分：66/100**
**与上轮差：+2（64 → 66）**

实拍口径：Edge headless（`--use-angle=swiftshader`），1920×1080 与 1366×768 两档；所有 px、行数、滚动量取自页面内 `getComputedStyle` / `getBoundingClientRect` / `Range` 实测，不是目测。截图见 `assets_type2/`。

---

## 一、与上轮的差：+2，加的是"能读到开头"，不是"读得舒服"

| 变化 | 分 | 证据（实测值） |
|---|---|---|
| 全屏长诗不再被居中裁头 | **+3** | 200 行长诗 `#c-full` `scrollTop=0` 时标题 `y=78.3`（视口 938 时；1080 下约 95）、首行 `y=286.3`（上轮同一首是 `−3854 / −3986`）；计算值 `align-content: safe center`，溢出时回落到 start |
| 元信息把统计口径写明白 | +1 | `#c-meta` 行内出现「意象偏向 鸟兽（统计）」，`analysisFor` 回退文案也写「这是统计口径，不是题材判定」 |
| 首屏 12 颗名篇挂题名 | +1 | 1920 下 12 条题名（《望岳》《登高》《秋兴八首 一》《新婚别》…），上轮首屏只有星点 |
| 1366 适配没盖住"读"的界面 | **−1** | 1366×768 打开《登高》：诗区 `clientH=152`、列高 `179`、`scrollH=211` → 每列末尾 1 字被切；`scrollW=432 > clientW=409`，最左一列横向也出界（见 `11_card_1366_poem_2x.png`） |
| 新加的「共 N 列」提示是死代码 | −1 | 实测 `#c-cns` `innerText.length=53`、`hasCount=false`、`hasFull=false`：提示在 1875 行写入，1896 行又调一次 `renderRelations(p)`，`el.innerHTML=txt` 把它整个盖掉 |
| 新加的题名不在字阶里 | −1 | canvas `ctx.font='11.5px'` + `globalAlpha=.55`，既不在 9/11/12.5 八档内，也不受深底对比度约束 |

不是更多，是因为这一轮基本没碰排版：`--t1…--t7`、`.fs-t 42 / .fs-ln 27 / .fs-v 15.5 / .fs-k 10.5 / .fs-note 10.5`、`#c-meta 11px` 与上轮逐字相同。新东西只有 `safe center` 和一条 1366 媒体查询（且只改容器，不改字号）。

![默认 1920：12 个题名挂上去了，层级仍是干净的](assets_type2/01_default_1920.png)

![诗卡 1920：卡片 1080 高，诗墨只占 179px](assets_type2/02_card_denggao_1920.png)

![全屏 1920：裁头修好了，但左右两栏之间仍有 392px 空场](assets_type2/03_full_denggao_1920.png)

---

## 二、现在仍然最伤的三条

### 1. 诗卡里"诗"依旧不是主体：200 列塞进 451px，1366 下连七律都读不全

- **长诗**：`#c-poem` `clientW=451`、`scrollW=10,244`——是可视宽度的 **22.7 倍**。200 列、列宽 35px、`gap:16px`，列距 51px，一屏 8 列，即 **4%**。
- **诗区高度浪费**：长诗卡诗区 `clientH=504`，诗墨只有 `127.8px`（25%），下方 376px 黑场；1080px 的卡片里，诗占 **11.8%**。
- **1366 下短诗被裁**：`clientH=152` vs 列高 `179`——七律七字，末字永远在视口外；截图里"潦倒新停浊酒"下面的"杯"只剩上半截，且横向还差 23px。滚动条是 3px 的 `#26282e`，在 `#06070c` 上等于没有。
- **给了提示但没落地**：这轮显然想补「共 200 列 · 点全屏整首读」，实测文字不在 DOM 里（被第二次 `renderRelations` 覆盖）。用户既读不到剩下的 192 列，也不知道还有 192 列。
- 评语 `#c-note` 仍在诗**之前**（`beforePoem: true`，note y=394.5 / 诗 y=456.5），11.5px 的结论压在诗上。

![200 列长诗的诗卡：8 列、无计数、下方 376px 黑场](assets_type2/04_card_long_200.png)

![1366×768 的《登高》：每列末字被切，第八列横向出界](assets_type2/11_card_1366_poem_2x.png)

### 2. 全屏长诗是一根 13 屏的单栏，右栏滚一屏就消失

- 200 行：`scrollH=12,265` / `clientH=916` = **13.4 屏**；27px 字、行距 **59.4px**（2.2 倍），全诗读完要滚过约 12,000px。
- `.fs-right` 没有 `position:sticky`，高度只有 578px：滚过一屏之后，右半屏永久空白。截图 `09` 是滚到 1,400px 的样子——**2/3 的屏幕是空的**，也没有"第 37/200 行"这类进度。
- 1920 下两栏并没有咬合：诗行墨迹右缘 2,531.5、右栏竖线 2,923.7，中间 **392px** 空场；右栏正文墨迹 435px 落在 780px 栏里，右侧再空 **273px**。合计 **665px ≈ 35% 屏宽**没有字。
- 一句话：`safe center` 把"够不到开头"换成了"读不到中间"。

![全屏 200 行：标题可达了，代价是 13 屏滚动](assets_type2/05_full_long_top.png)

![滚到 1,400px：右栏已经滚走，右半屏全空](assets_type2/09_full_long_scrolled.png)

### 3. 字号还是两套；最重要的「推定」只有 9.17px / 3.52:1

- 八档令牌是 9 / 11 / 12.5 / 15 / 23 / 34 / 66，全屏实测却是 **42 / 27 / 15.5 / 12 / 12.5 / 10.5 / 10.5**——七个值里五个不在档上。
- 同一"级"两种比例：卡片 `23 : 17.5 = 1.31`，全屏 `42 : 27 = 1.56`；标题在两处不是同一个层级。
- 「推定」：`<sup>` 计算 **9.17px**、`#6a665c`、对比度 **3.52:1**（上轮 8.75px / 2.26:1，抬了，但仍是全站最重要的认识论标记里最小的一粒）。
- 「名篇 · 五言长诗 · 1000 字」：`10.5px`、`#57544c`、**2.66:1**；卡片元信息 11px；题名 canvas 11.5px / alpha .55（等效约 4.3:1，压在亮星团上更低）。
- 中英混排：`.fs-k`、`#dims .lab`、`#view .lab` 仍是 `"Helvetica Neue",Arial,sans-serif` 套中文——栈里没有一个中文字体，靠系统默认回退。

![诗卡头部 2×：11px 元信息挤成一行，「推定」两字是一粒灰](assets_type2/10_card_head_2x.png)

---

## 三、三条改法（可直接落地）

### 改法 1：诗卡按"句数 × 可用高度"排版；提示写到不会被覆盖的节点

```js
// fitPoem() 现在算完 need/needW 就 return（2192–2207），等于没做；改成真的落字号
var FS = p.L.length <= 8 ? 21 : (p.L.length <= 16 ? 18 : 15);
el.style.setProperty('--poem-fs', FS + 'px');

// 先在 #c-poem 后加 <div id="c-poemhint" class="poemhint"></div>；
// 别写进 c-cns——它在 1870 和 1896 被 renderRelations 重写两次
var hint = document.getElementById('c-poemhint');
hint.textContent = p.L.length > 10
  ? '第 1–8 列 / 共 ' + p.L.length + ' 列 · 横向拖动或用 → 键'
  : '';
```

```css
#card .poem{scroll-snap-type:x mandatory; scrollbar-color:#8a8578 transparent}
#card .poem .col{scroll-snap-align:start}
#card .poemhint{font-size:12px;letter-spacing:.12em;color:#8f8a7c;padding:0 30px 12px}
#card .poem::-webkit-scrollbar{height:6px}
#card .poem::-webkit-scrollbar-thumb{background:#8a8578}

/* 1366×768：诗要占回高度——藏配图、收头部，别让七律少一个字 */
@media (max-height:820px){
  #card .art{display:none!important}
  #card .hd{padding:14px 24px 6px}
  #card .tt{font-size:20px;margin-top:8px}
  #card .poem{padding:12px 18px}
}
```

再把评语移到诗后，诗的视觉重量才对得起"诗卡"：`document.getElementById('c-poem').after(document.getElementById('c-note'));`

### 改法 2：长诗分型——页边左对齐 + 右栏 sticky，行距收到 1.85

```js
el.classList.toggle('longpoem', p.L.length > 24);
```

```css
/* 右栏常驻：滚到第 100 行时，写作时间/诗中之意还在 */
#c-full .fs-right{position:sticky;top:6vh;align-self:start;max-height:86vh;overflow:auto}

/* 长诗：不再是一张海报，是一页书 */
#c-full.longpoem{grid-template-columns:minmax(0,30em) minmax(0,24em);
  align-content:start;justify-content:center;gap:64px}
#c-full.longpoem .fs-t{font-size:34px;text-align:left;letter-spacing:.10em;line-height:1.35}
#c-full.longpoem .fs-a{text-align:left}
#c-full.longpoem .fs-rule{margin:20px 0}
#c-full.longpoem .fs-ln{font-size:21px;line-height:1.85;text-align:left;
  letter-spacing:.08em;white-space:normal}
```

200 行行距从 59.4 → 38.85，`scrollH` 从 12,265 → 约 **7,800**，少滚 4 屏；左对齐后才像"读一首长诗"，而不是"看一块排字"。短诗（≤24 行）保持现在的居中对称，不动。

### 改法 3：字阶落到 token + clamp；12px 以下不许承载信息

```css
:root{
  --rd-title:clamp(34px,3.0vw,56px);
  --rd-poem: clamp(20px,1.45vw,30px);
  --rd-body: clamp(15px,1.00vw,16px);
  --rd-label:12px;   /* 下限，不再是装饰 */
}
#c-full .fs-t{font-size:var(--rd-title)}
#c-full .fs-ln{font-size:var(--rd-poem)}
#c-full .fs-v{font-size:var(--rd-body)}
#c-full .fs-k,#c-full .fs-note{font-size:var(--rd-label);color:#8f8a7c}  /* 2.66 → 5.85:1 */

#c-meta{font-size:12px;letter-spacing:.14em;line-height:1.9}
#c-meta sup{font-size:12px;vertical-align:baseline;margin-left:4px;color:#8f8a7c}  /* 9.17 → 12px */

/* 中文标签不许再套 Helvetica */
.fs-k,#dims .lab,#view .lab{font-family:"Microsoft YaHei","PingFang SC",sans-serif}
```

首屏 12 个题名要么进 token（DOM 化，用 `--t3` + `text-shadow`），要么至少改成：`ctx.font='13px "Microsoft YaHei",serif'; ctx.globalAlpha=0.80;`——现在的 11.5px / 55% 是这轮唯一新增的文字，却没进体系。

---

## 四、一句总评

裁头那一刀缝得干净（标题从 −3854px 回到 +78px），但这一轮动的是"能不能看到"，不是"好不好读"：一开诗卡，200 列仍是 451px 暗槽、1366 少一个字、提示被自己的渲染流程吃掉；一进全屏，长诗还是一条 13 屏的单栏，中间 35% 的屏幕没有字。**66 分，比上轮多的 2 分全在"可达"，剩下的 34 分全在"可读"。**
