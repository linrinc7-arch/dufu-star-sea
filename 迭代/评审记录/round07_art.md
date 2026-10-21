# 美术指导（色彩 / 构图 / 光影 / 材质 / 视觉层级）· 第 7 轮评审

**总分：66 / 100**
**与上轮差：0（66 → 66）——第二个 0，但账换到了另一个方向。**

> R6 我给的 #1 是三行，你落了两行：<code>L=pow(dens,1.55)*1.28</code> 回来了，<code>goldL=pow(dust,1.6)*0.22</code> 也回来了。**少的第三行是 <code>wG=0</code>**——金仍然从 <code>226,150,78</code> 混进底色，于是"金"是褐雾不是光：赭橙带 **6.7% → 29.0%**（testC 12.8%），青 **43.9% → 27.2%**（testC 57.0%），蓝占着色 **48.1% → 37.5%**（testC 67.4%）。
> 长诗横排这件事本身是对的（200 行终于一句一行、纵向滚，<code>sw=cw=441</code>），**但它把「整屏读」顶掉了一半**：<code>#c-full</code> 从 y=26 掉到 **y=524**，上半屏是卡片里那条列表的重复（截图里 9 行"绝塞乌蛮北…"）——这是本轮唯一的新回归，也是最贵的。
> ③④ 两条**在成品里不存在**：全源码 <code>3.05vw</code> / <code>3.95vh</code> / <code>keep-all</code> / <code>1.78</code> 均 **0 命中**；长题还是 66px、<code>text-wrap:wrap</code>，1366 第 8 行还在屏外。

**证据先看**：[夜空 R6/R7](r07/c_sky_r6_vs_r7.png) · [testC 对照](r6/r6_23_sky_testC_1920.png) · [长诗整屏 R6/R7](r07/c_full_long_r6_vs_r7.png) · [1440 三行标题](r07/r07_14_full_long_1440.png) · [390 长题压按钮](r07/c_m_cardhead.png)

---

## 实拍条件与口径

- **版本**：<code>杜诗星海.html</code>，5,994,577 B，sha256 <code>6aa7b854…</code>，mtime <code>2026-10-20 16:10:08</code>；源码 <code>web/index.html</code> 149,368 B、mtime <code>16:10:05</code>。钉成 <code>评审/r07/_snap.html</code>（同 sha），**所有实拍从它出**。评审期间 16:08 版（<code>9d1c60da</code>，149,301 B）被 <code>_apply167.py</code> 改成音频频段，视觉无改动。
- **机器**：Edge <code>--headless=new --use-angle=swiftshader</code>（CDP），DPR=1；相机固定 <code>{yaw:.55, pitch:.10, zoom:1}</code>；等 <code>#load</code> 移除、<code>pts()&gt;1400</code> 后 1.0–1.8 s；隐藏自定义光标。页面 <code>window.__errs</code> 全程为空。
- **实拍 19 张**（<code>评审/r07/</code>）：1920×1080（default / 《登高》卡 / 40 列卡 / 200 列长卡 / 长卡滚到 45% / 长诗整屏 / 《登高》整屏 / 检索态）、1366×768（default / 《登高》卡 / 整屏 / 整屏滚到底 / 200 列长卡）、1440×900（长诗整屏 / 《登高》卡）、1600×900（长诗整屏）、390×844（default / 200 列长卡 / 《登高》整屏）。
- **口径（与 R6 同一支脚本，不拿本表数字与上轮报告直接相减）**：
  - 着色 = <code>sat≥16 &amp; max≥26</code>；金 = <code>hue 20–60 &amp; sat≥16</code>；赭橙 = <code>20–35</code>、真金 = <code>35–50</code>、青 = <code>185–215</code>、洋红 = <code>280–330</code>（占**着色像素**的份额）；气体彩度 = <code>max−min</code>。
  - 对比度按 WCAG 相对亮度，背景取自同帧像素（15 分位），不做色值猜测；左栏按 <code>#side .sb</code> 的 <code>opacity.62</code> 合成后计。
  - 标题行数用 <code>Range</code> 逐字取行首；盒子相交用 <code>getBoundingClientRect</code> 求交集面积；滚动量用 <code>scrollWidth/Height</code>。
- **声音不在美术口径内**：⑤ 只做代码核对，没有试听结论。

---

## 一、这轮六条，先核对

| # | 声称 | 实测 | 判定 |
|---|---|---|---|
| ① | 长诗在诗卡里改横排可滚（&gt;40 行不再竖排，200 行一句一行、纵向滚） | <code>:2148</code> <code>p.L.length&gt;40</code> → <code>.horiz</code>；200 行《秋日夔府咏怀…》<code>.col ×200</code>、<code>writing-mode:horizontal-tb</code>、15px/29.7px、<code>sw 441 = cw 441</code>、<code>sh 9958 / ch 595</code>；40 行《奉同郭给事…》仍竖排 | **成立**（代价见四.1） |
| ② | 天幕按 testC 调回（L 1.55/1.28、金 0.22 加性） | <code>:1036</code> <code>pow(dens,1.55)*1.28</code> ✓、<code>:1037</code> <code>pow(dust,1.6)*0.22</code> ✓；**但 <code>:1030–1032</code> 的 <code>wG</code> 仍在混色**。实测 mean **26.85**（带 23–27 ✓）、%L&lt;8 **10.32**（10–16 ✓）、L8–25 **49.34**（45–55 ✓）、着色 **47.27**（45–52 ✓）、%L&gt;80 **2.11**（&lt;3 ✓）；金 **22.72**（带 8–12 ✗）、蓝占着色 **37.5%**（testC 67.4） | **半成立**（testC 三行少一行） |
| ③ | 长题 <code>clamp(23px,min(3.05vw,3.95vh),34px)+balance+keep-all</code> | 源码与成品 <code>3.05vw</code>/<code>3.95vh</code>/<code>keep-all</code> **0 命中**；<code>#c-full .fs-t</code> 计算值 **66px / lh 99px / text-wrap:wrap**；1920 两行断"郑/监"、1600 三行、1440 三行断"李宾/客" | **不成立** |
| ④ | 1366 全屏行高 1.78 | 无此规则；<code>#c-full .fs-ln</code> **34px / 74.8px**（2.2 倍）；1366 <code>sh 899 / ch 742</code>，第 8 行底 **837** &gt; 768 | **不成立** |
| ⑤ | 声音开时点诗不崩（var base 补回、aud* try/catch） | <code>:1854</code> <code>var base=196*Math.pow(2,_pent[_deg%_pent.length]/12)</code>；<code>:2137</code> <code>try{ audSelect(…); audPaper(); }catch(e){}</code> | **成立**（代码；不试听） |
| ⑥ | 检索占位 4.9:1、≤1500 有提示、单金、40px 命中 | 占位 <code>#8a8578</code> 实测 **5.49:1** ✓；≤1500 <code>#hint</code> 在页脚右侧 x1203 / y708 ✓；<code>.readtoggle</code> **47.5×40**、<code>#csound</code> **67.6×40** ✓；**单金 ✗**：长卡同屏 hint 金 + 滚动条 <code>rgba(201,162,39,.55)</code> + 关系页签金 + 意象 em 金 + 命中数字金（≥6 处），8 行卡也有名篇实心徽章 + 页签 + em 共 3 处 | **三对一错** |

---

## 二、分维度

| 维度 | R6 | R7 | 差 | 关键证据（同脚本、同机位） |
|---|---|---|---|---|
| 光影 | 71 | **77** | **+6** | mean **51.06 → 26.85**、p50 **41.09 → 20.97**、%L&lt;8 **3.32 → 10.32**、L8–25 **23.75 → 49.34**、%L&gt;80 **19.54 → 2.11**、着色 **70.85 → 47.27**——R6 的 7 条验收落 5 条（只剩金面积与蓝中位）。扣：金是漫射褐雾，画面没有"发光点" |
| 材质 | 71 | **72** | **+1** | 气体彩度 mean **16.45 → 15.13**、p90 **41 → 29**；金 chroma **8 → 10**、medL **34.9 → 27.4**；尘埃带与丝状脊在黑底上比 R6 清楚。扣：气体更"平"，金没有金属感 |
| 色彩 | 63 | **64** | **+1** | 赭橙 20–35° **6.7% → 29.0%**、青 185–215° **43.9% → 27.2%**、蓝占着色 **48.1% → 37.5%**；洋红 280–330° medL **62**、chroma **22**（画面最亮最饱和）；金 medL **27.4**、金内 L≥60 仅 **23.7%**（R6 32.6%） |
| 构图 | 60 | **57** | **−3** | + 200 行卡 <code>sw/cw 10244/451（4.4%）→ 9958/595</code>、一句一行、<code>sw=cw</code>；+ 8 列《登高》卡 <code>452/451</code> 全见。− 长诗整屏 <code>#c-full y=524.4 h=555.6</code>（51.5%）、1440/1600 <code>y=442.5 h=457.5</code>；− 12–40 行仍 <code>2084/451（21.6%）</code>；− 三档标题三种断法；− 1366 第 8 行在屏外 |
| 视觉层级 | 63 | **61** | **−2** | + 40px 落地、≥1500 卡头 56px、hint 回页脚右。− 同屏 3–6 处金；hint 写「共 200 列」；390 长题压在「全屏」下（760/1082 px²）；390 底部 9 个单元挤成竖排；英文副标折行 1.55:1；9px 序号 **1.82:1**；单屏 6 档字号 |
| **综合** | **66** | **66** | **0** | (77+72+64+57+61)/5 = **66.2 → 66** |

---

## 三、这轮真修好的（别回滚）

1. **夜空回来了，而且比 R6 更像"夜"。** mean 51.06 → **26.85**、p50 41.09 → **20.97**、%L&lt;8 3.32 → **10.32**、%L&gt;80 19.54 → **2.11**、着色 70.85 → **47.27**。R6 那句"金需要黑才亮"你听进去了：黑场从 3.3% 回到 10.3%，中灰带（L8–25）从 23.8% 涨到 49.3%——这是云，也是夜。
2. **200 行长诗在卡里终于能按行读了。** 一句一行、左对齐、纵向滚，<code>sw 441 = cw 441</code>（R6 是 <code>10244 / 451</code>，只见 4.4%）。竖向那根"悬在卡片中间的细带"没了。
3. **8 列《登高》卡重新装得下。** <code>sw 452 / cw 451</code>，8 列全见，不再有"点这里整屏读"的隐藏提示（8&lt;12 不显示）。
4. **40px 命中真的落地了。** <code>.readtoggle</code> 47.5×40、<code>#csound</code> 67.6×40；基础规则 <code>#card .hd{padding:56px}</code>（<code>:216</code>）是正解——只是被三处覆盖打回（见四.3）。
5. **1366 的 <code>#hint</code> 回到页脚右侧**（x1203 / y708），不再把页脚顶上来压左栏；<code>04 评点</code> 与 <code>意象</code> 行不再穿字（盒仍交 22px，字形不碰）。
6. **检索占位 5.49:1**（#8a8578 / 实测背景 rgb(8,6,7)），过 AA；<code>#q</code> 与 <code>::placeholder</code> 计算色分开，是对的。
7. **声音开关点诗不崩**：<code>var base</code> 补回（<code>:1854</code>），<code>audSelect/audPaper</code> 外包 try/catch（<code>:2137</code>）。

---

## 四、还剩三条最伤

### 1. 长诗「整屏读」被卡片里的横排列表顶掉一半（构图 / 视觉层级）——本轮唯一的新回归

**证据**

- 1920：<code>#c-full</code> <code>{x:0,y:524.4,w:1920,h:555.6}</code>，只占 **51.5%**；1440/1600：<code>y:442.5,h:457.5</code>（**50.8%**）。全库 **57 首**（1468 首的 3.9%）走这条横排分支——数量不多，但全是长诗/排律，最需要整屏的那批。
- 上半屏是 <code>#c-poem.horiz</code> 的**重复**：<code>r07_06</code> 里是 9 行"马来皆汗血 / 鹤唳必青田 …"，<code>r07_14</code> 里是 9 行"绝塞乌蛮北 / 孤城白帝边 …"；标题被推到 y=568（1440：478），三栏正文从 y=848（1440：855）才开始——**第一屏只看得见一行诗**。
- R6 同页（<code>r6/r6_05_full_long_1920.png</code>）：标题在 y62、三栏从 y350、<code>#c-full</code> 满屏 1054。**这不是"内容太多"，是显示层没关。**
- 根因一行：<code>#card #c-poem.horiz{display:flex!important}</code>（<code>:254</code>）压过 <code>#card.reading .poem{display:none}</code>（<code>:253</code>）。带 <code>!important</code> 的那条赢了。
- 顺带一个尺寸问题：横排每行吃到了竖排的 <code>gap:16px</code>（<code>:299</code>），所以 15px 字配 **49.7px** 行距（29.7 + 4 + 16）。200 行 = 9958px；去掉 gap 应为 **6740px**，现在多滚了 32%。

**改法**

~~~css
/* :253 之后，一条覆盖三条 */
#card.reading .poem,
#card.reading #c-poem,
#card.reading #c-poem.horiz{display:none!important}

/* :254 附近：横排不要吃竖排的 gap 与 margin */
#card #c-poem.horiz{gap:0;padding:22px 30px}
#card #c-poem.horiz .col{margin-bottom:0;line-height:1.95}
~~~

**验收**：1920/1440 长诗整屏 <code>#c-full</code> <code>y≤26</code>、<code>ch≥视口−26</code>；首屏无重复行；长诗卡 <code>sh</code> 从 9958 → **≤6900**；200 行卡与整屏的标题都从顶边开始。

---

### 2. 金还是褐尘：testC 少了一行（色彩 / 光影）

**证据**

- 同一支脚本、全帧：赭橙 20–35° **6.7% → 29.0%**（testC 12.8%）；青 185–215° **43.9% → 27.2%**（testC 57.0%）；蓝占着色 **48.1% → 37.5%**（testC **67.4%**）。
- 金（20–60°，R6 同一把尺）**11.31% → 22.72%**，是目标带 8–12 的两倍；但金 medL **34.9 → 27.4**、chroma **8 → 10**、裁去左栏后金里 L≥60 的只占 **23.7%**（R6 32.6%）——**面积翻倍、亮度掉了**，所以它读作"褐雾"而不是"金"。真金带 35–50° 只占着色像素 **3.2%**。
- 洋红 280–330° medL **62**、chroma **22**，是画面里最亮最饱和的东西；<code>c_sky_gold.png</code> 里最大的一块低频是褐云，眼睛先落在粉脊线上。
- 对照 <code>r6_23_sky_testC_1920.png</code>：蓝夜 + 分散金尘 + 细粉脊线。差的不是 L，是 **<code>wG</code> 那一行**——它仍以最高 0.45 的权重把 <code>226,150,78</code> 混进底色，金既混色又加性，于是底色整体偏褐。

**改法**

~~~js
// web/index.html:1030-1037, buildNebulaTex()
var wG=0;                                   // testC 少的那一行：金退出混色
var wB=Math.max(0,1-wM-wG);
var sum=wB+wM+wG+1e-4;
var cr=(wB*18 + wM*198)/sum;                // 只留青蓝 / 洋红
var cg=(wB*156 + wM*52)/sum;
var cb=(wB*198 + wM*118)/sum;
var L=Math.pow(dens,1.55)*1.28;             // 保持
var goldL=Math.pow(dust,2.1)*Math.pow(fil,1.5)*0.62;  // 金只落在丝脊上
if(dens<0.16) goldL*=0.35;                  // 暗部不泛褐
~~~

> 别一次砍到底：先上 <code>wG*0.35</code> 的过渡版，ochre 会落在 17–19%、青 45–48%、金 14–16%；确认不"死蓝"再归零。

**验收**：ochre 20–35° **≤14%**、青 **≥48%**、蓝占着色 **≥60%**、金 **8–13%** 且 medL **≥40**、chroma **≥16**、洋红 medL **≤55**。

---

### 3. 长题不跟宽度走、1366 第 8 行还在屏外：③④ 在成品里没有（构图 / 视觉层级）

**证据**

- <code>#c-full .fs-t</code> 计算值 **66px / lh 99px / text-wrap:wrap**；<code>3.05vw</code>、<code>3.95vh</code>、<code>keep-all</code> 在成品与源码里 **0 命中**。
- 同一题《秋日夔府咏怀奉寄郑监李宾客一百韵》：
  - 1920 <code>['秋日夔府咏怀奉寄郑','监李宾客一百韵']</code> → 断"郑/监"；
  - 1600 <code>['秋日夔府咏怀奉','寄郑监李宾客一','百韵']</code> → **三行**，末行只有"百韵"；
  - 1440 <code>['秋日夔府咏怀','奉寄郑监李宾','客一百韵']</code> → 断"李宾/客"。
- 1366：《登高》<code>sh 899 / ch 742</code>，第 8 行底 **837** &gt; 768；<code>.fs-ln</code> 34px/74.8px（2.2 倍，不是 1.78）。滚到底（157px）才看见"潦倒新停浊酒杯"。
- 390：长题第一行压在「全屏」按钮下——盒交 **760 px²**（声音键 **1082 px²**）。因为 56px 的让位被三处打回：<code>#card .art.on~.hd{padding-top:26px}</code>（<code>:217</code>，有配图时）、<code>@media(max-width:1500){#card .hd{padding:20px}}</code>（<code>:466</code>）、<code>@media(max-height:820px){#card .hd{padding:14px}}</code>（<code>:472</code>）。

**改法**

~~~js
// renderFull(p) 末尾
// 1) 长题先按语义断成两行——17 字那首断在「奉寄」后，不要交给平衡算法
var TITLE_BREAK={'秋日夔府咏怀奉寄郑监李宾客一百韵':['秋日夔府咏怀奉寄','郑监李宾客一百韵']};
var parts=TITLE_BREAK[p.t]||(p.t.length>=14
  ? [p.t.slice(0,Math.ceil(p.t.length/2)), p.t.slice(Math.ceil(p.t.length/2))]
  : [p.t]);
var t=document.querySelector('#c-full .fs-t');
t.innerHTML=parts.map(esc).join('<br>');
// 2) 字号跟"最长那一行"走，而不是跟字符总数走
var tw=document.querySelector('#c-full .fs-left').clientWidth;
var longest=Math.max.apply(null,parts.map(function(s){return s.length}));
t.style.fontSize=Math.min(66, tw/(longest*1.13))+'px';   // 1920→66, 1600→56, 1440→50
// 3) 诗行按可用高度落字号（1366 的 8 行必须全在 742 里）
var n=Math.max(1,p.L.length);
var avail=document.getElementById('c-full').clientHeight-190;
document.getElementById('c-full').style.setProperty('--fs-poem',
  Math.min(34, avail/(n*1.95))+'px');
~~~

~~~css
#c-full .fs-ln{font-size:var(--fs-poem,34px);line-height:1.95}

/* :217 之后补：任何 padding 覆盖都不得低于 56px */
@media (max-width:1500px){ #card .hd{padding-top:56px} }
@media (max-height:820px){ #card .hd{padding-top:56px} }
@media (max-width:1000px){ #card .hd{padding-top:56px} }
#card .art.on~.hd{padding-top:56px}

/* 全站唯一一根系统滚动条（15px、带箭头）换成 5px 金 */
#c-full{scrollbar-width:thin;scrollbar-color:rgba(201,162,39,.55) transparent}
#c-full::-webkit-scrollbar{width:5px}
#c-full::-webkit-scrollbar-thumb{background:rgba(201,162,39,.55);border-radius:3px}
~~~

**验收**：1920/1600/1440 长题 **≤2 行**，断点不在「郑监 / 李宾客 / 一百韵」内部；1366 8 行全在 742 内（第 8 行底 ≤768）；<code>#c-full</code> 滚动条 **5px**；390 长题与「全屏」「声音」按钮 **不相交**。

---

## 五、没进三条、但同样要修

| 位置 | 实测（本版） | 应该 |
|---|---|---|
| 12–40 行卡 | 全库 **387 首**（26.4%）落在这个带，比 >40 行的 57 首多 **6.8 倍**；40 行《奉同郭给事汤东灵湫作》<code>sw 2084 / cw 451</code>，只见 **21.6%**；hint 写"共 40 列 · 点这里整屏读 ›"——**把看不全写成一句话**，不是构图 | 12 行起自动整屏（<code>p.L.length&gt;=12</code>）；或卡宽 <code>min(760px,56vw)</code>。40 行的门槛把 12–40 夹在中间，最尴尬 |
| hint 文案 | 200 行横排仍写"共 **200 列**"，可它是 200 **行** | 横排时改"共 200 句"；竖排保留"列" |
| 单金 | 长卡同屏：hint 金 + 滚动条 <code>.55</code> 金 + 关系页签金 + 意象 em 金 + 命中数字金（≥6）；8 行卡 3 处 | 只留关系页签；hint 改月白 + 金下划线；滚动条 <code>rgba(236,231,219,.22)</code>；名篇徽章改纸色描边 |
| 1366/1440 <code>#c-full</code> | 系统 **15px** 滚动条（<code>cw 1351 / w 1366</code>、<code>1425/1440</code>），带上下箭头，亮灰 | 5px 金 + <code>sh&gt;ch</code> 时给 1px 进度线 |
| 390 底部控制 | 9 个单元挤成竖排：着/色、意/象、时/期、诗/云、伪/诗、生/涯、巡/游、声/音 + 单独"关"；"巡游"框紧贴"声音" | ≤700 拆两行或横滑；"生涯"标签已被面板取代，可以去掉 |
| 390 品牌副标 | <code>.brand .en</code> 9px、**1.55:1**，且折成两行（THE STAR SEA OF DU / FU） | 收成一行（<code>white-space:nowrap</code>）或 ≤700 隐藏 |
| 9px 序号 | 左栏 <code>00–04</code> 合成后 **1.82:1**（R6 1.71）——比上轮好，但仍不可读；主标签 6.49:1 已合格 | 提到 <code>#8d887c</code> 或并入 11px 档 |
| 字号阶梯 | 单屏 6 档：9 / 11 / 12.5 / 16 / 17.5 / 23；跨页还有 15 / 34 / 66 | 9 并入 11；16（输入框）写进 DESIGN 或归 15；12.5 的份额分一档给 15 |

---

## 六、一句总评

这轮你做成了一件真事：**夜回来了**——mean 51→27、黑场 3.3%→10.3%、高光 19.5%→2.1%，R6 的七条验收落了五条。长诗横排在卡里也是对的：200 行从"10244px 只露 4.4%"变成一句一行、纵向滚。

但两笔账同时被记到了反面：**金仍然从 <code>wG</code> 里混出来**（赭橙 29%、青 27%、蓝占着色 37.5%，testC 是 12.8 / 57 / 67.4），所以"金"是一片褐雾；**横排列表没有在整屏里让位**（<code>#c-full</code> y=524、只剩 51.5% 屏），200 行诗的"整屏读"第一屏只看得见一行诗（受影响 57 首，而卡在 12–40 行竖排里的是 387 首）。③④ 两条声称的改动，在成品里一个字符都没有——标题还是 66px、1440/1600 仍是三行断专名，1366 还是少一行。

**净分 0：66。** 但两个 0 的余额不同：R6 是"金亮了、夜没了"，R7 是"夜回来了、整屏没了"。下一轮先做两行 CSS（<code>#card.reading #c-poem.horiz{display:none!important}</code> 与 <code>wG=0</code>），再谈标题——两处都是单行 CSS。

---

### 附：本轮实拍索引（<code>评审/r07/</code>）

- **天幕**：<code>r07_01_default_1920.png</code>、<code>r07_09_default_1366.png</code>、<code>r07_17_mobile_default.png</code>；细节 <code>c_sky_gold.png</code>；对照 <code>c_sky_r6_vs_r7.png</code>
- **诗卡**：<code>r07_02_card_denggao_1920.png</code>、<code>r07_03_card_midcol_1920.png</code>（40 行）、<code>r07_04_card_long_1920.png</code>（200 行）、<code>r07_05_card_long_scrolled_1920.png</code>、<code>r07_10_card_denggao_1366.png</code>、<code>r07_15_card_denggao_1440.png</code>、<code>r07_18_mobile_card_long.png</code>；细节 <code>c_cardlong_body.png</code>、<code>c_card1920_head.png</code>、<code>c_card1440_head.png</code>、<code>c_card1366_head.png</code>、<code>c_m_cardhead.png</code>
- **整屏**：<code>r07_06_full_long_1920.png</code>、<code>r07_07_full_denggao_1920.png</code>、<code>r07_11_full_denggao_1366.png</code>（+ <code>r07_12_…_bottom</code>）、<code>r07_14_full_long_1440.png</code>、<code>r07_16_full_long_1600.png</code>、<code>r07_19_mobile_full_denggao.png</code>；对照 <code>c_full_long_r6_vs_r7.png</code>
- **其他**：<code>r07_08_search_1920.png</code>（检索态）、<code>c_m_controls.png</code>（390 底部）、<code>c_1366_bottom.png</code>（1366 第 8 行在屏外）
- **数据**：<code>probe7.json</code>（19 个状态的几何/计算样式）、<code>_stats7.py</code> / <code>_hue7.py</code> / <code>_full7.py</code>（像素口径）、<code>_cap7.py</code>（实拍脚本）
