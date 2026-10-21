
---

## 6. UI：从首屏到"赠诗漫游"

### 6.1 组件树（来自 `Xl()` 的挂载列表 `:13360-13445`）

~~~text
Xl()  App
├── <Canvas>                       ← §1 那 9 个 R3F 层
├── Jl({visible,suspended})        手势 HUD（默认关闭）        :12655
├── Os()                          HUD 顶栏 + 底栏              :7802
├── Xc()                          全站认领计数                 :11882
├── Ic()                          设置（"更多"）               :10771
├── cc()                          检索（诗人/寻诗/探诗/朝代）   :9159
├── fc()                          赠诗漫游                     :9794
├── Lc()                          悬停诗名 tooltip             :11263
├── Vs()                          诗卡（虚空里捞出的诗）        :8056
├── Js()                          诗人面板                     :8477
├── Kc()                          留影 / cinema                :11321
├── qc()                          开发者工具（流星）            :11683
├── Qc()                          我的认领                     :11943
├── Ac()                          新手引导（3 步）              :10281
└── loading-screen                "正在点亮 32,657 位诗人…"     :13422
~~~

（`scroll` 说明：面板组件名是两个字母，但每个都带一段稳定的 className 前缀，便于对照：`hud-top` / `poem-panel` / `poet-panel` / `search-tabs` / `giftroam` / `settings` / `cinema` / `onb-card` / `fbv-overlay`。）

### 6.2 状态：一个 zustand store（`:3519-3784`）

~~~js
J = St((e) => ({
  loaded: !1, form: "wujue", lushiFilter: !1, commonOnly: !1,
  hidden: new Set(),            // 被隐藏的朝代 key 集合
  selected: null,               // 当前"虚空诗" {form, lines, babelIndex, babelDigits, lushiIndex, valid, pos}
  pulls: [],                    // 每次点虚空留下的坐标（决定 ≤40 个涟漪标记）
  hoverPoetId: null, hoverPoem: null,
  selectedPoet: null, poetPoems: null, poetPoemsProgress: null, poetPoemsError: null,
  showGifts: !1, giftTrail: [], pathStart: null, pathEnd: null, pathResult: null,
  showAllPoems: !1, quality: Mt ? "low" : "high", uiHidden: !1,
  freeMove: !q,                 // ★ 触屏默认锁定轨道，桌面默认自由飞
  allowRandomPoem: !0, gravity: !0, speed: 1,
  meteorsOn: !0, claimFeed: null, myClaims: [], meteorMinGap: 2, meteorMaxGap: 10,
  cinema: !1, cinemaPoemIdx: null, cinemaCopy: 0, cinemaTextColor: "#fbf7ec",
  shiyi: zt(),                  // "拾遗"= 本地收藏（localStorage）
  flyTarget: null, lockPoetId: null, lockPoemIdx: null,
}))
~~~

动作（同一处 `:3598-3784`）：`setForm / toggleCommon / toggleLushi / toggleQuality / toggleGravity / toggleAllPoems / toggleRandomPoem / toggleUI / toggleCinema / setSpeed / keepShiyi / dropShiyi / requestMeteor / setFlyTarget / lockPoet / lockPoem / unlock / selectPoet / selectPoem / pulseAt / hopToPoet / toggleDynasty`。

渲染层与 React 之间还有一个**模块级单例**（`:4571`）：

~~~js
var zr = { poets: [], pick: null, snap: null, poemLayer: null };
// ni() 挂载时写入 zr.pick / zr.snap；li() 挂载时写入 zr.poemLayer
~~~

### 6.3 逐面板：结构 + 关键状态

| 面板 | 组件 | 关键状态 / 数据 | 结构要点 |
|---|---|---|---|
| HUD 顶栏 | `Os()` `:7802` | `form, commonOnly, lushiFilter, settingsOpen, quality, speed, loaded` | 标题（10 s 内连点 5 次开开发者工具，`:7842-7846`）+ 诗体分段器 + 常用字/格律/更多/画质 + 统计 `poetCount · poemCount` + 隐藏界面；底栏提示 + 速度 |
| 诗卡 | `Vs()` `:8056` | `selected`, `pulls`, `myClaims`, `shiyi` | 诗体 / 全集编号（N 位 + 复制）/ 格律编号（律印或"非格律·虚空目录"）/ 认领 / 分享 / 留影 / 拾遗；移动端折叠成 `sheet-peek`，`Is()` 控折叠 |
| 诗人面板 | `Js()` `:8477` | `selectedPoet, poetPoems, poetPoemsProgress, poetPoemsError` | 名字 + 朝代色 + `N 首`/`存目 N 条` + 作品列表（`Zo()` 按桶懒加载，`:7101`）。**没有生卒/生平/字号——数据里没有这些字段** |
| 检索 | `cc()` `:9159` | `tab(poet|poem|probe|dynasty), q, results, aliasNote, form, hidden` | 4 tab；"探诗"= 把任意文本算成虚空编号（`qo/Yo`）；"编号反查"= `Xo(idx)` 反解；朝代 tab 控制 `hidden` |
| 赠诗漫游 | `fc()` `:9794` | `showGifts, giftTrail, pathStart/End/Result, giftHoverId` | 左栏：赠/答双方 + 朝代 + 往来计数；点一条边 → 相机 `hopToPoet` |
| 设置 | `Ic()` `:10771` | `settingsOpen, guideMode/Coverage/Seconds/Brightness/Style, showAllPoems, showGifts, gravity, meteorsOn, freeMove, gestureEnabled/Fps/Backend` | 6 组：行星指引线 / 显示层 / 漫游·交互 / 拾遗 / 我的认领 / 关于·反馈 |
| 留影 | `Kc()` `:11321` | `cinema, cinemaPoemIdx, cinemaCopy, cinemaShowBg, cinemaTextColor, cinemaHideTagline, cinemaShowHandle` | 全屏诗句 + 字号槽（±/复位）+ 上下句 + 背景/文字色/签名开关 = **给用户截图的干净构图器** |
| 拾遗 | `Cc()` `:10163` | `shiyi, shiyiOpen` | 本地收藏的诗列表，可"回到这首诗"（重新定位） |
| 我的认领 | `Qc()` `:11943` | `myClaims, myClaimsOpen` | 认领编号 + 时间 + 一键飞回 |
| 反馈 | `jc()` `:10426` | `open, text, state` | `POST /api/feedback`（`:10118`），只发正文与时间 |
| 开发者工具 | `qc()` `:11683` | `devToolOpen, meteorLook, meteorMinGap/MaxGap, meteorSpawnReq` | 手动生成流星、调流星参数 |
| 引导 | `Ac()` `:10281` | `step, done`，键 `shiyun_onboarded_v3` | 3 步：①诗云·一切可能的诗 ②点星·点虚空 ③飞出去（桌面）/出发（触屏）；可 `shiyun:replay-onboarding` 重放 |

### 6.4 首屏 → 漫游 → 得诗 → 诗人 → 检索 → 赠诗

1. **首屏**：`mr()` 并发拉 charset / poets.index / manifest / lexicon（`:13273-13281`）→ `setLoaded(true)` → `Ns()` 处理深链。加载期显示"正在点亮 32,657 位诗人…"。
2. **漫游**：HUD 底栏文案（`:7923-7927`）直接当说明书：
   `WASD 飞行 · 拖拽转向 · Q/E 滚转 · 滚轮调速 · F 全屏 · 点诗星看其真作 · 点虚空从噪声里捞诗`
3. **点虚空得诗**：诗卡出现；首次 3 次（`Rs=3`，键 `shiyun_voidreveal_n`）会插一条 `void-reveal` 提示："这首诗此前并不存在 —— 它是你点下的那一刻，从那个坐标当场算出来的。同一个点，永远捞出同一首。"（`:8133-8138`）
4. **点诗人**：相机锁到星团、诗星层展开（§3.3 的 flare 出生动画），诗人面板列出作品。
5. **检索**：`探诗` 的文案解释了"为什么某些名人不在星图上"（`:9063-9076`）——庄子/老子/诸葛亮传世的是文不是诗，但"他们的文章和一切可能的文字一样，躺在虚空的某个编号上"。
6. **赠诗**：开关打开 → 5,051 条边 + 沿线脉冲 → 左栏"赠诗漫游"。

### 6.5 深链与分享

`ks()/As()/Ns()`（`:7946-7997`）支持 `#p=<编号>`（诗）、`#a=<诗人id>`（诗人），也读 `?p=/?a=`。恢复路径：`Xo(idx)` 反解出诗与坐标 → `selectPoem` + `setFlyTarget(pos)` → **相机飞过去**。
`Ps/Fs`（`:7999-8025`）只做 `navigator.clipboard.writeText(location.href)`。

### 6.6 界面上的世界观文案（`:11306-11320`）

> 一切可能的诗都已写就，藏在这片噪声里
> 在诗云里，杰作不被创作，只被找到
> 一个文明算尽了所有的字，写下了每一首诗
> 这首诗有一个住址，长达数十位

---

## 7. 移动端、可访问性、降级、分享

### 7.1 设备判定与画质档

~~~js
var q = typeof matchMedia < "u" && matchMedia("(pointer: coarse)").matches;   // :3290 触屏
function jt() {                                  // :3291 弱设备
  if (typeof navigator > "u") return !1;
  if (q) return !0;                              // 触屏一律算移动
  let e = navigator.hardwareConcurrency ?? 8, t = navigator.deviceMemory ?? 8;
  return t <= 2 || (e <= 2 && t <= 4);
}
var Mt = jt(), Yl = Mt ? 1.5 : 2;                // :13260  ★ DPR 上限 1.5 / 2
quality: Mt ? "low" : "high"                     // :3549
~~~

| 档 | 背景粒子 | 辉光 | DPR 上限 | 全诗层 |
|---|---|---|---|---|
| high | 120k + 9k + 64k | Bloom 1.4 | 2 | 允许 |
| low | 42k + 3.5k + 24k | **关** | 1.5 | 移动端在设置里禁用（`:11006` `disabled: Mt && !p`） |

### 7.2 性能手段（可对照抄）

| 手段 | 做法 | 证据 |
|---|---|---|
| DPR 上限 | `dpr:[1, Mt?1.5:2]` | `:13334`, `:13260` |
| 画质档 | 粒子数 / 辉光 / 全诗层 三处联动 | `:3849-3853`, `:13349` |
| 点径上限 | shader clamp 到 70 / 64 / 48 / 44 px，避免近处糊屏 | 各 shader |
| 视锥裁剪 | **主点云全部 `frustumCulled = !1`**（整体包围盒≈全屏，裁剪无意义且会闪） | `:4905, 3956, 4633, 4678` |
| 绘制范围 | `setDrawRange(0, f)` 只画有效点 | `:5070, 5951, 6043` |
| 离屏小窗拾取 | 只渲染 17²~57² 像素，不重绘全屏 | `:4713-4726` |
| 节流 | 悬停拾取 70 ms；动画钟 `hn.t += min(dt, 0.05)` 防切后台炸帧 | `:7402, 5180` |
| 几何一次性上传 | 每层 `useMemo` 建几何，之后只改 uniform；仅"每帧会变"的属性用 `DynamicDrawUsage` | `:5019-5024, 5947-5950` |
| 资源释放 | 卸载 dispose；诗星层先淡出再 dispose | `:5170-5178, 5192-5197` |
| 前后台 | three 自带 `visibilitychange` 暂停 rAF；r3f 用默认 `frameloop:'always'` | `three-CjFqNL11.js:485` |
| 能力门 | 入口先探 `BigInt` 与 `getContext('webgl2')||('webgl')`，不满足则不挂 React，直接出中文提示 | `index.html` capability gate |

**没有的东西**（别以为漏了）：无 LOD 分级、无 chunk 流式加载（点云一次建完）、无 `InstancedMesh`、无 Worker/时间切片、无 `frameloop:'demand'`。它能跑 32k 点靠的是"点很小 + 加色 + 不写深度 + 只改 uniform"。

### 7.3 可访问性

- 20+ 个 `aria-label`（关闭 / 上一句 / 下一句 / 字体槽缩小…）；进度条 `role="progressbar"`（`:8449`）、手势 HUD `role="status"`（`:13188`）、红色数据告警 `role="alert"`（`:13380`）。
- 键盘：`H` 隐 UI、`F` 全屏、`WASD/QE/Shift/Space` 飞行、`Esc` 解锁（`hs` 集合 `:7160-7168`）。
- `prefers-reduced-motion` **只作用于 CSS 加载骨架**（`index-DZz16_0d.css`：`.spinner{animation-duration:2.4s}.sk-row{animation:none}.load-bar{transition:none}`）；**3D 的自动旋转 / 闪烁 / 相机缓动没有降级开关** —— 明确的可改进项。
- 触屏：`viewport-fit=cover` + `safe-area-inset-*` 共 14 处；面板折叠为底部 sheet（`Is()` `:8026`）；点击容差 14 px（`:7447`）。
- 画布本身没有 `aria-label`/替代文本，但**所有信息都有 DOM 面板承载**（Canvas 只是可视化，不是唯一入口）——这点做对了。

### 7.4 分享卡片 / OG

**没有动态 OG 生成**。`index.html` 里是静态 `/og.jpg` + 固定标题；"分享"= 复制带 `#p=<编号>` 的 URL（`:8012-8024`）。
需要图片时只能靠 `Kc()` **留影模式**：隐藏全部 UI、放大字号槽、切背景/文字色/签名、上下句翻页 —— 一个**给用户自己截图**的干净构图器，而不是服务端出图。认领后还有"化作流星"的仪式动画（`La.ceremony` 最亮的一档，`:6171-6205`）。

