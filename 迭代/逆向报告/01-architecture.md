# 01 · 架构层逆向：诗云（shiyun.cohenjikan.com）

> **分析对象**：`work/rea/shiyun/site/` 下的 7 个静态制品（全部为已下载原件，未重新抓取；唯一例外见 §1.6）。
> **分析日期**：2026-10-20
> **方法**：prettier 美化 → acorn AST 建"声明-引用"图 → 按区域切分 → REA `analyze-javascript-application` 交叉验证。
> **证据约定**：
> - `pretty/index.js:1234` = 美化后的主包（13,454 行，由 264,935 B 的 `index-ah4l33vX.js` 生成），行号可复现（命令见 §6）。
> - `@123456` = **压缩原件**里的字节偏移（vendor 文件整包只有 1 行，只能按字节定位）。
> - 每条结论标注 **确定 / 强推断 / 推断 / 未定**，推测一律写明推测链。

---

## 0. 一页结论

| # | 结论 | 关键证据 | 置信度 |
|---|---|---|---|
| 1 | 打包器是 **Rolldown**（不是 Rollup），构建器是 **Vite**（`vite.config.ts`），即 **rolldown-vite / Vite 7 线** | 独立的 `rolldown-runtime-QTnfLwEv.js`（694 B，只导出 3 个运行时 helper）；每个 chunk 首行都 import 它；index.html 注释点名 `vite.config.ts` | 确定（Rolldown）/ 强推断（Vite 7 线） |
| 2 | three.js = **r169** | three chunk 自报 revision 169（@675035）、`window.__THREE__=169`（@675163）、"removed in r172" 弃用文案（@674754） | 确定 |
| 3 | React 系 = **18.3.1 线**（react + react-dom + react-dom/client），**不是 19** | react-dom 自报 `version: 18.3.1-next-f1338f8080-20240426`（@137088）；无 `react.transitional.element`（React 19.1 的符号），只有 `react.element` | 确定 |
| 4 | 3D 层 = **@react-three/fiber v8 线** + **drei 的 Html** + **postprocessing（vanilla）** | `reconcilerVersion: 18.0.0-fc46dba67-20220329`（react-reconciler 0.27 线，@235347）；`rendererPackageName:@react-three/fiber`（@261071）；drei Html 的 `zIndexRange` 默认值（@271046） | 强推断（fiber v8 / drei v9） |
| 5 | 状态管理 = **zustand v5 单 store**，123 个属性（60 数据 + 63 action），**173 处单字段选择器订阅** | `getInitialState`（@69609）+ `useSyncExternalStore`（@69750）是 v5 特征；store 定义在 `pretty/index.js:3519-3784` | 确定 |
| 6 | 渲染调度 = **9 个 useFrame 回调直接改 three 对象**；React 只在 store 字段变化时重渲染；帧内只做 `J.getState()` 读取（28 处），不做订阅 | 9 处 `r((e,t)=>{…})`（r = fiber 的 useFrame）：pretty:4015 / 4939 / 5179 / 5315 / 5712 / 5896 / 5987 / 6391 / 7563 | 确定 |
| 7 | 路由 = **没有路由**。URL 是"一次性输入 + 单向输出"：`?a=<诗人id>` / `?p=<编号>` 同时写进 query 与 hash，写回只用 `history.replaceState` | `pretty/index.js:7946-7981`；全包 **0** 处 `pushState / popstate / hashchange` | 确定 |
| 8 | 语言 = **纯中文单语**，没有 i18n 框架；英文只做品牌装饰（`Poetry Cloud`、`title-en`） | `<html lang="zh-CN">`；无 `navigator.language`；`lang` 属性只在 6 处 JSX 上做标注 | 确定 |
| 9 | CSS = 单文件 49,931 B / 533 条规则 / **0 个 @layer**；只有 6 个设计变量 + 2 个运行期变量；**零 @font-face**（全部系统字体） | `index-DZz16_0d.css:1` 的 `:root{--ink…}`；grep `@layer` = 0、`@font-face` = 0 | 确定 |
| 10 | 打包之外还有 **3 类 public 根目录脚本**：公告横幅、手势 Worker、MediaPipe 运行时 | `/announce-202607.js`（index.html:61）；`new Worker('/gesture-worker.js')`（@237856）；worker 里 `importScripts("/mediapipe-vision.js")`、`wasmRoot:/mediapipe-wasm`、`modelUrl:/gesture_recognizer.task` | 确定 |

**一句话架构**：一个 Vite（Rolldown）打包的单页应用——React 18 负责"面板 / 浮层"这类低频 UI，R3F v8 的 `useFrame` 负责"星空 / 行星 / 流星"这类每帧动画，zustand 作为二者之间唯一的共享状态；数据全部是静态 JSON 分桶，构建期由离线管线（pinyin-pro / opencc-js）生成，客户端只做 BigInt 编号解码与按桶 Range 取数。

---

## 1. 构建体系

### 1.1 制品清单（`/assets` 与根目录）

| 文件 | 字节 | gzip | sha256(前16) | 角色 |
|---|---:|---:|---|---|
| `site/index.html` | 4,172 | 2,004 | `67633c73857ee32d` | 入口 + 能力门 + 预加载清单 |
| `site/assets/index-ah4l33vX.js` | 264,935 | 82,674 | `f5f23f6b8e3a2440` | **应用主包**（含 postprocessing 库） |
| `site/assets/r3f-yJ-6H-4a.js` | 276,945 | 88,089 | `36de75f5aa5729b1` | react + react-dom + react-dom/client + reconciler + fiber + drei |
| `site/assets/three-CjFqNL11.js` | 675,551 | 168,786 | `915598bc2d64f3b2` | three.js r169（纯净，无二次封装） |
| `site/assets/rolldown-runtime-QTnfLwEv.js` | 694 | 423 | `5db5ba82eef00d1d` | Rolldown 运行时 helper |
| `site/assets/index-DZz16_0d.css` | 49,931 | 10,010 | `eb3ae699819ad115` | 全站样式（单文件） |
| `site/announce-202607.js` | 16,233 | 7,064 | `1b19158cf5fcb7da` | 公告横幅（**不在 assets、无哈希**） |

合计 1,288,461 B（≈1.23 MiB 原始 / ≈344 KiB gzip），其中 JS 1,218,125 B（≈340 KiB gzip）。4 个 JS + 1 个 CSS 就是全部可执行面，**没有** `.map`、没有 worker chunk、没有字体、没有图片。

> 注：`three-CjFqNL11.js` 的 sha256 `915598bc2d64f3b2…` 与 REA Evidence 里 three 产物的 `artifact_id` 完全一致（§2.6），说明两边分析的是同一份字节。

### 1.2 打包器：Rolldown（确定）

**证据 A —— 独立的 runtime chunk，且只导出 3 个 helper。** `rolldown-runtime-QTnfLwEv.js` 全文一行，结尾（@665）：

```js
export{s as n,l as r,o as t};
```

而主包第 1 行（`pretty/index.js:1`，原件字节 0）是：

```js
import{r as e}from"./rolldown-runtime-QTnfLwEv.js";
```

主包拿到的 `e` 就是 `l`（CJS interop helper），用来把 React 的 CJS exports 包成带 default 的命名空间：`K = e(i(), 1)`。

**结论**：Rollup / Vite（经典）会把 `_interopDefault / __esModule / __export` 这类 helper **内联进每个 chunk**，不会产出独立的 `rolldown-runtime` 模块；"runtime 作为独立 chunk 且只暴露 3 个函数"是 Rolldown 的输出指纹。**确定。**

**证据 B —— 没有 Vite/Rollup 自己的运行时残留：**

```
$ grep -c '__vite'      site/assets/index-ah4l33vX.js  → 0
$ grep -c 'import.meta' site/assets/index-ah4l33vX.js  → 0
```

即没有动态 `import()`（因此没有 `__vite__mapDeps`）、没有 `import.meta.url` 形式的资源解析、没有 `import.meta.env` 残留（构建期已内联替换）。

### 1.3 Vite 特征：能确认什么、不能确认什么

| 特征 | 证据 | 说明 |
|---|---|---|
| modulepreload polyfill | `pretty/index.js:55-84`：`document.createElement('link').relList` … `MutationObserver` | Vite 的 `build.modulePreload.polyfill` 默认产物（逐行与 Vite 官方 polyfill 一致） |
| 入口 script 形态 | index.html:23 `<script type="module" crossorigin src="/assets/index-ah4l33vX.js">` | `crossorigin` 无值即 anonymous，Vite 对 module 入口的固定写法 |
| 预加载清单 | index.html:24-26 三条 `<link rel="modulepreload" crossorigin …>` | 与主包的 3 条静态 import 一一对应（runtime / three / r3f） |
| 样式注入顺序 | index.html:27 `<link rel="stylesheet" crossorigin …>`，**在 script 之后** | Vite 5.1+ 会给 CSS link 加 `crossorigin`；顺序是先 js 后 css |
| 文件名哈希 | `index-ah4l33vX.js` / `index-DZz16_0d.css` / `three-CjFqNL11.js` | `[name]-[hash][ext]`，hash 为 8 位 base64url（可含 `-` / `_`）。Vite ≤4 用点号分隔（index.abc123.css），点号改连字符是 **Vite 5+** 的默认 |
| base | 所有资源都是绝对路径 `/assets/…`、`/favicon.png` | `base: '/'` |
| 构建期 HTML 变量替换 | index.html:11-13 注释 | 见 §1.7 |
| 无 sourcemap / 无 legacy / 无 SW | 目录里没有 `.map`；只有一条 `type=module` script，无 `nomodule`；无 `serviceWorker.register` | 目标浏览器一次性限定为 ES2022（配合 BigInt 能力门） |

**能确定**：打包器 Rolldown；构建器 Vite（index.html 注释直接写 `vite.config.ts`）；Vite ≥ 5.1（CSS link 带 crossorigin + 连字符哈希）。
**不能确定**：Vite / Rolldown 的**具体小版本**——产物里没有版本横幅、没有 `__vite__` 版本串、没有 manifest。
**推断**：Rolldown 当打包器、又保留 modulepreload polyfill 与 Vite 的 HTML 注入顺序 → 工程走的是 **rolldown-vite（Vite 7 的 Rolldown 分支）**，而不是"Vite 6 + 官方 rollup"或"Rolldown 裸用"。**强推断**（缺一个能直接读版本号的字符串）。

### 1.4 依赖栈与版本证据

| 依赖 | 版本 | 证据（压缩原件） | 置信度 |
|---|---|---|---|
| three.js | **r169** | three chunk：`revision:169`（@675035）、`window.__THREE__=169`（@675163）、"deprecated … removed in r172"文案（@674754） | 确定 |
| react-dom | **18.3.1-next-f1338f8080-20240426** | r3f chunk `reconcilerVersion:18.3.1-next-f1338f8080-20240426`（@137088）；同文件导出 `e.version=18.3.1-next-f1338f8080-20240426` | 确定 |
| react | 18.3.x（同一构建线） | 元素符号只有 `react.element`（4 次），**无** `react.transitional.element`（React 19.1 起改用后者）；用了 `K.StrictMode` 与 `Ct.createRoot(...)` | 强推断 |
| react-reconciler | 18.0.0-fc46dba67（0.27.x 线） | r3f chunk `reconcilerVersion:18.0.0-fc46dba67-20220329`（@235347） | 确定（字符串）/ 强推断（对应 0.27.x） |
| @react-three/fiber | **v8.x** | r3f chunk `injectIntoDevTools({bundleType:0,rendererPackageName:@react-three/fiber,version:18.3.1})`（@261071）；`useFrame` 实现（§3.4）与 v8 一致；v9 要求 React 19，此处是 React 18 | 强推断 |
| @react-three/drei | v9.x（只用 Html） | r3f chunk `zIndexRange:v=[16777271,0],calculatePosition:y=Qt,as:b=div,wrapperClass:x…`（@271046）—— drei Html 的完整 props 签名 | 强推断 |
| postprocessing（vanilla） | 版本不可恢复 | 主包 85-2903 行（2,819 行）内 `EffectComposer / BloomEffect / KawaseBlurPass / LuminancePass / DepthDownsamplingPass` 全套；`pt`/`gt` 是 @react-three/postprocessing 的 `EffectComposer`/`Bloom` 封装（props：intensity / luminanceThreshold / luminanceSmoothing / radius / mipmapBlur） | 确定（在包里）/ 未定（版本） |
| zustand | **v5** | @69609 `{setState:r,getState:i,getInitialState:()=>o,subscribe:…}`；@69750 `K.useSyncExternalStore(e.subscribe, useCallback(()=>t(e.getState())), useCallback(()=>t(e.getInitialState())))`——`getInitialState` 是 v5 才有的 API | 强推断 |
| typescript | 是（构建期） | GLSL 注释里带源码路径：`// soft halo identical to the poet stars (three/PoetStars.tsx)`（`pretty/index.js:6284`）——源文件是 `.tsx` | 确定 |
| pinyin-pro / opencc-js | **不在客户端** | 两词只出现在"开源致谢"文案里（`pretty/index.js:10539` / `10545`），包里没有实现代码 → 属于**数据构建管线**依赖 | 确定 |

**为什么版本钉得这么死**：React / R3F / three 都会在 devtools 注入或全局变量里留**自报版本字符串**，这些字符串在模板字符串里、压缩器不会改，属于硬证据；而 fiber v8 / drei v9 / zustand v5 是"用可观测 API 形状 + 依赖线"推出来的，标为强推断。

### 1.5 分块策略

| chunk | 内容（按字符串与符号判定） | 体积 | 预加载 |
|---|---|---:|---|
| `index-ah4l33vX.js` | 应用全部源码 + `postprocessing` 库 + zustand | 264,935 | 入口 script |
| `three-CjFqNL11.js` | three.js r169（末尾 `export{Dn as A,y as B,…}` 共 40 个导出） | 675,551 | modulepreload |
| `r3f-yJ-6H-4a.js` | react / react-dom / react-dom-client / react-reconciler / fiber / drei Html / jsx-runtime（9 个导出，全是"惰性 CJS 工厂"） | 276,945 | modulepreload |
| `rolldown-runtime-QTnfLwEv.js` | Rolldown helper | 694 | modulepreload |

`r3f` 的 9 个导出是 **CJS 工厂**（形如 `o=t((e,t)=>{t.exports=ae()})`），调用才返回模块对象。主包的绑定关系：

| r3f 导出 | 实际绑定 | 证据（r3f chunk 内定义） |
|---|---|---|
| `a` = `ct` | **useThree** | `function ct(e=e=>e,t){return st()(e,t)}` |
| `c` = `v` | react-dom（CJS 工厂） | `v=t(((e,t)=>{…t.exports=_()}))` |
| `i` = `lt` | **useFrame** | `function lt(e,t=0){let n=st(),r=n.getState().internal.subscribe,i=Se(e);return xe(()=>r(i,t,n),[t,r,n]),null}` |
| `l` = `m` | react（CJS 工厂） | `m=t(((e,t)=>{t.exports=p()}))` |
| `n` = `Kt` | **Canvas** | `Kt=C.forwardRef(function(e,t){return(0,ue.jsx)(Ht,{children:(0,ue.jsx)(I,{...e,ref:t})})})` |
| `o` = `oe` | react/jsx-runtime（CJS 工厂） | `oe=t(((e,t)=>{t.exports=ae()}))` |
| `r` = `me` | **extend** | `me=e=>void Object.assign(pe,e)` |
| `s` = `y` | react-dom/client | `y=t((e=>{var t=v();e.createRoot=t.createRoot,e.hydrateRoot=t.hydrateRoot}))` |
| `t` = `sn` | **drei Html** | `sn=C.forwardRef(({…,zIndexRange:v=[16777271,0],…})` |

主包侧的别名：`G = o()`（jsx-runtime）、`K = e(i(),1)`（React）、`pc = n()`（react-dom，供 `createPortal`）、`Ct = e(c(),1)`（react-dom/client，供 `createRoot`）、`a` = Canvas、`r` = useFrame、`t` = useThree、`s` = extend、`l` = Html、`q` = 触屏判定。

**结论**：chunk 名 `three` / `r3f` 是**人工命名的分组**，最可能来自 `vite.config.ts` 里 `build.rollupOptions.output.manualChunks`（Rolldown 下为 `build.advancedChunks.groups`），规则大致是 `node_modules/three/** → three`、`node_modules/(react|react-dom|@react-three)/** → r3f`。**推断**（分组本身确定，配置写法推断）。没有业务级懒加载——所有面板都在主包里，说明作者选择了"首屏一次拿全、交互零等待"。

### 1.6 打包之外的运行时脚本（3 类）

| 脚本 | 加载方式 | 证据 | 性质 |
|---|---|---|---|
| `/announce-202607.js` | index.html:61 `<script src="/announce-202607.js" defer>` | 文件头注释："这段脚本会被运维上传到 prod dist 根目录，并在【旧版】index.html 的 body 结束前手动注入" | **运维注入**，不在 Vite 产物里；自带过期时间戳 `Date.UTC(2026,6,31,16,0,0)` 与 `localStorage['shiyun_announce_202607_pre']` 幂等守卫 |
| `/gesture-worker.js` | `new Worker('/gesture-worker.js')`（@237856；`pretty/index.js:12736`） | 我补抓了这一份（**唯一一次联网**，因为它是模块拓扑里缺失的一环）：HTTP 200 / 4,583 B | **public 根目录**，不走打包器；MediaPipe GestureRecognizer 推理线程 |
| `mediapipe-vision.js` + `/mediapipe-wasm/*` + `/gesture_recognizer.task` | worker 内 `importScripts("/mediapipe-vision.js")`；主线程 INIT 传 `{wasmRoot:'/mediapipe-wasm', modelUrl:'/gesture_recognizer.task'}` | `pretty/index.js:13020-13026` | ML 运行时（WASM + .task 模型），只有开手势模式才拉 |

`gesture-worker.js` 的头注释把协议写得很清楚，可直接当架构文档用：

```
// Protocol (main → worker):
//   INIT  {wasmRoot, modelUrl, backend: "cpu"|"gpu"}  → READY {backend} | ERROR {message, fatal}
//   FRAME {bitmap, ts, seq}                           → RESULT {seq, ts, inferenceMs, hand|null}
//   RESET                                             → tracker re-created
//   STOP
```

**因此本站的"模块边界"实际有两层**：打包器内部的 ESM 图（4 个文件），以及打包器之外、由 public 根目录直接提供的脚本（公告 / Worker / ML 运行时）。后者是**显式设计**（注释写明"运维上传、手动注入"），不是构建事故。

### 1.7 构建期的 HTML 变量替换（VITE_SITE_ORIGIN）

index.html:11-13（原文；HTML 不经压缩）：

```html
<!-- share preview (OG/Twitter). https://shiyun.cohenjikan.com is replaced at build time from VITE_SITE_ORIGIN
     (vite.config.ts) — unset it falls back to a root-relative path, which most CN apps and
     Telegram resolve; set it before deploy so Facebook/X also get an absolute URL. -->
```

**判断**：这是 Vite `transformIndexHtml` 钩子 + `%VITE_SITE_ORIGIN%` 式占位替换（或自定义插件）做的**构建期注入**，与 `import.meta.env` 属同一套环境变量机制、只是用在 HTML 侧。
**观察**：产物里 4 个社交标签都已是绝对地址（index.html:18 `content="https://shiyun.cohenjikan.com/og.jpg"`，:22 同）→ **构建时 VITE_SITE_ORIGIN 已设置**，不是注释里"unset 回退成相对路径"的情况。

### 1.8 构建体系的"未知项"（不要过度解读）

- Vite / Rolldown 具体版本号：**未定**（产物无任何版本串）。
- 是否用了 `vite-plugin-*`：**推断有**（`VITE_SITE_ORIGIN` 注释为证），插件名**未定**。
- 数据管线（charset / lexicon / poems 分桶）不在客户端包里，其构建命令与依赖版本**未定**（只能从"开源致谢"看到 pinyin-pro / opencc-js 的用途）。

---

## 2. 模块图

### 2.1 方法：为什么"切模块"要靠推断

Rolldown 把 ESM 图**打平成单个作用域**：模块边界、`//#region` 标记、原始 import 语句全部消失，标识符被重命名为全局唯一的短名（`e/t/n/r/o/s/c/l/u/d/f/p/m/h/g/_/y/b/x`… 以及双字母序列）。因此本报告不声称"还原了原始的 40 个 .ts 文件"，而是给出三样可验证的东西：

1. **物理图**：4 个 JS 文件之间的 import 关系（ESM 静态 import，确定）。
2. **逻辑区域**：把主包 13,454 行按"连续行区间 + 引用闭包 + 字符串/Shader 指纹"切成 27 个区域，每个区域给行号区间、顶层声明数、首尾符号（可复现）。
3. **依赖方向**：用 acorn 对 539 个顶层声明建"声明 → 引用"有向图（`tool/ast2.js`），区域之间的引用只允许朝一个方向（下图），**没有发现反向引用**（即不存在 UI 层被场景层调用的情形）。

复现命令：

```bash
npx prettier@3.3.3 --parser babel site/assets/index-ah4l33vX.js > pretty/index.js   # 264,935 B → 13,454 行
node tool/ast2.js        # 539 个顶层声明 + 每个声明的引用集合 → pretty/_ast.json
node tool/regions.js     # 26 个区域的行号/行数/声明数
```

> 注意一个反直觉的观测：**连通分量分析在这份包上无效**——539 个声明在引用图上连成 1 个巨分量（因为所有东西最终都引用 store `J` 或几个根工具）。所以"区域"只能用**行号连续性 + 语义指纹**切，这也是为什么下面每行都给出具体符号与字符串，方便复核。

### 2.2 物理模块图（文件级，确定）

```
index.html
 ├─ <script type=module>  /assets/index-ah4l33vX.js   ← 入口（应用 + postprocessing + zustand）
 │    ├─ import{r as e}   ./rolldown-runtime-QTnfLwEv.js   (helper: interop / namespace / CJS)
 │    ├─ import{...9}     ./r3f-yJ-6H-4a.js                (react, react-dom, react-dom/client,
 │    │                                                     reconciler, fiber, drei/Html, jsx-runtime)
 │    └─ import{...40}    ./three-CjFqNL11.js              (three r169)
 ├─ <link rel=modulepreload> ×3（runtime / three / r3f）
 ├─ <link rel=stylesheet>  /assets/index-DZz16_0d.css
 ├─ <script src=/announce-202607.js defer>                  ← 运维注入，非打包产物
 └─ (运行时) new Worker('/gesture-worker.js')               ← public 根目录
      └─ importScripts('/mediapipe-vision.js') + /mediapipe-wasm + /gesture_recognizer.task
```

### 2.3 主包逻辑区域表（A0-A26 共 27 段，覆盖 13,423 / 13,454 行 = 99.8%）

`pretty/index.js`：

| # | 区域 | 行号 | 行数 | 声明数 | 关键符号（首见行） | 职责 |
|---|---|---:|---:|---|---|---|
| A0 | import + modulepreload polyfill | 1-84 | 84 | 0 | — | 3 条静态 import + Vite 预加载垫片 |
| A1 | **postprocessing 库** | 85-2903 | 2,819 | 58 | `ue(85) Se(530) Ee(827) H(975) Oe(1150) Ie(1482) Je(1953) Ye(2096) Xe(2187) nt(2357) at(2498) ot(2608)` | 渲染后期：EffectComposer / Bloom / Kawase 模糊 / Copy / Mask / Clear / 深度降采样 |
| A2 | **React·R3F·zustand 绑定** | 2904-3108 | 205 | 17 | `G(2921) K(2922) dt(2923) pt(2925) gt(3046) _t(3070) bt(3094) xt(3102) St(3107) Ct(3108)` | jsx-runtime / React / 唯一的 createContext / EffectComposer+Bloom 的 R3F 封装 / zustand 内核（store 工厂 + useSyncExternalStore 钩子）/ react-dom-client |
| A3 | **常量·设备·存储·认领 API** | 3109-3517 | 409 | 42 | `wt(3109) Tt(3276) Et(3277) kt(3280) q(3290) jt(3291) Mt(3298) Nt(3299) an(3466) sn(3468) cn(3486)` | 14 朝代表（`wt`）、朝代索引、设备档位探测、localStorage 读写（诗忆）、`/api/claim` 客户端 |
| A4 | **应用 store + 场景常量** | 3519-3791 | 273 | 2 | `J(3519) Y(3785)` | zustand 单 store（123 属性）；`Y={RADIUS:3600,BRANCHES:4,TWIST:5.2,…}` 星系形态参数 |
| A5 | **场景数学 + 装饰星场 + 词库引导** | 3792-4081 | 290 | 25 | `mn(3795) vn(3799) xn(3815) On(3847) An(4022) Ln(4047)` | 模块级动画累加器；种子随机；`On` = 12 万/4.2 万颗装饰星（含 shader）；词库惰性初始化 |
| A6 | **编号数据接口 + 诗人目录** | 4082-4183 | 102 | 10 | `Rn(4082) Vn(4087) Un(4093) Wn(4118) Gn(4124) Kn(4125) qn(4134)` | lexicon/charset 装配、FNV-1a 指纹、字库哈希校验、唐诗诗人白名单 |
| A7 | **数据访问层** | 4184-4600 | 417 | 52 | `Yn(4185) ur(4200) fr(4210) pr(4216) mr(4251) hr(4272) gr(4281) _r(4300) wr(4363) Dr(4378) Ar(4409) Pr(4496) Fr(4509) Ir(4533) Rr(4562)` | `/data` 基址、诗人 id 规范化、四种分桶读取（poems / poems.idx sidecar / lines / search）、赠诗边、搜索、缓存 Map |
| A8 | **星图几何** | 4603-4835 | 233 | 10 | `Kr(4603) qr(4749) Jr(4799)` | 星云/星系几何生成（shader 内置）、`qr` = 诗人 → 三维坐标（确定性哈希）、黄金角 |
| A9 | **场景 A：诗人星 / 行星 / 指引线** | 4836-5565 | 730 | 28 | `ni(4836) oi(4980) li(5097) Ci(5268) Ti(5353) Di(5490) Oi(5533)` | 诗人星点云 + 拾取 shader、选中诗人的"行星"、行星指引线（平面段 + 垂直段） |
| A10 | **场景 B：赠诗边 / 轨迹 / 捞起标记** | 5566-6051 | 486 | 38 | `Yi(5767) Ji(5758) Vi(5577) sa(5876) pa(5935)` | 赠诗关系弧线、脉冲动画、BFS 最短路（`Yi`）、捞起诗的出生/衰减标记 |
| A11 | **位运算 / 几何工具** | 6052-6227 | 176 | 30 | `ma(6052) ha(6061) ga(6067) X(6104) Da(6120) Va(6216)` | 从哈希里按位取浮点、几何体拼装、颜色常量 |
| A12 | **场景 C：认领流星** | 6228-6587 | 360 | 1 | `Ha(6228)` | 认领事件 → 流星从银心飞向诗人（含 4 段 shader） |
| A13 | **编号引擎（BigInt）** | 6595-7178 | 584 | 90 | `Q(6595) Wa(6596) Ga(6602) Ka(6609) Ya(6625) io(6693) ho(6815) So(6869) Co(6880) wo(6894) To(6913)` | 编号 ⇄ 字序列（混进制）、校验、字 → 位置映射；leads 到 `ho()` 的 N |
| A14 | **相机与飞行控制** | 7179-7790 | 612 | 1 | `Es(7179)` | 拖拽/滚轮/双指/WASD/QE/全屏/手势事件，飞行插值、"到达"回调 |
| A15 | **HUD / 深链 / 复制分享** | 7791-8055 | 265 | 14 | `Ds(7791) Os(7802) ks(7946) As(7953) js(7970) Ms(7978) Ns(7983) Ps(7999) Fs(8012) Is(8026)` | 诗体表、顶部 HUD（含 `--hud-h` 上报）、URL 构造与解析、分享按钮、移动端折叠判定 |
| A16 | **诗卡 / 诗人面板 / 别名表** | 8056-9140 | 1,085 | 21 | `Vs(8056) Js(8477) Ys(8781) Qs(9081) $s(9091)` | 捞到诗后的底部卡片、诗人作品目录、`Ys` = 122 条古人别名 → 本名（陶渊明→陶潜…） |
| A17 | **搜索面板** | 9159-9788 | 630 | 1 | `cc(9159)` | 三 tab（诗人 / 寻诗 / 探诗）、按字/句/篇检索、朝代折叠 |
| A18 | **赠诗漫游** | 9789-10112 | 324 | 4 | `fc(9794)` | 赠答网络面板：赠出 ↔ 收到、路径、点亮 |
| A19 | **设置 / 反馈 / 致谢 / 新手引导** | 10113-10770 | 658 | 23 | `pc(10113) Cc(10163) Ac(10281) jc(10426) Mc(10480) Nc(10588)` | 设置抽屉、`/api/feedback` + 本地草稿、开源致谢（**自带技术栈清单**）、三步 onboarding |
| A20 | **指引设置面板** | 10771-11320 | 550 | 10 | `Ic(10771) Lc(11263)` | 指引线开关/样式/时长/亮度/覆盖策略、拖动条 |
| A21 | **影院模式** | 11321-11682 | 362 | 1 | `Kc(11321)` | 全屏单诗阅读：字号槽、上下句、真伪/版权标记 |
| A22 | **开发者工具** | 11683-11879 | 197 | 1 | `qc(11683)` | 流星参数、赠诗调试、认领模拟 |
| A23 | **认领计数 / 我的认领** | 11880-12120 | 241 | 9 | `Xc(11882) Zc(11938) Qc(11943)` | 全站认领总数滚动条、我的认领列表 |
| A24 | **手势引擎与布局工具** | 12123-12654 | 532 | 44 | `Al(12311) Tl(12278) Dl(12282) jl(12585)` | 21 点手部几何、pinch/drag/push/tap 状态机、One-Euro 滤波、安全框、帧率档位 |
| A25 | **手势层组件** | 12655-13259 | 605 | 1 | `Jl(12655)` | 摄像头采集 → Worker → 手势 → CustomEvent；HUD 预览 |
| A26 | **入口与挂载** | 13260-13453 | 194 | 2 | `Yl(13260) Xl(13261)` | 数据引导、键盘快捷键、深链应用、`createRoot().render(<StrictMode>)` |

### 2.4 依赖方向（按引用图归纳，单向）

```
[入口 A26] ─┬─> [数据访问 A7] ──> [编号数据 A6] ──> [编号引擎 A13]
            ├─> [深链 A15] ──> [store A4]
            ├─> [UI 面板 A16..A23] ──┐
            └─> [场景组件 A9/A10/A12/A14] ──┼──> [store A4]（订阅）
                                            └──> [星图几何 A8] ──> [工具 A11]
[所有层] ──> [常量 A3]（朝代表 / 设备档 / 存储）
[所有层] ──> [A2 绑定层]（React / R3F / zustand 内核）
[所有层] ──> [A1 postprocessing]（仅 A2 的 pt/gt 与场景 C 使用）
```

**证据**：`tool/ast2.js` 输出的 `refs` 集合里，A1/A2/A3 三级被 A9~A26 引用，但 A1/A2/A3 从不引用 A4~A26；A13（编号引擎）只被 A6/A7/A15 引用，且 A13 只引用 A11 与三个工具函数。**确定。**

### 2.5 按任务要求归类的八个子系统

| 子系统 | 行区间 | 关键符号 | 说明（含证据） |
|---|---|---|---|
| **数据层** | 4184-4600 | `Yn='/data'`(4185)、`mr`(4251)、`hr`(4272)、`wr`(4363)、`Pr`(4496)、`Rr`(4562) | `mr()` 一次性 `Promise.all` 拉 charset / poets.index / manifest / lexicon；`hr` 读 `poems/<b>.json`，有 sidecar 时改用 `poems/<b>.idx.json` + Range；`wr` → `lines/<b>.json`；`Pr` → `search/<b>.json`；404 当作"空"并写进缓存（`n.status===404&&Nr.set(e,{})`）。细节归 02-data 报告 |
| **编号引擎** | 6595-7178 | `Q=e=>BigInt(e)`(6595)、`Wa`(6596)、`ho()`(6815)、`Kn`(4125) | 编号 ⇄ 字序列；`ho()` 取 `BigInt(Bn().lexicon.N)` 作为基数；`Kn(chars, hash)` 校验 FNV-1a 指纹 `a9cde1f2`，不符则 console.error + HUD 红条（"数据与本版本不匹配：编号链接可能错位"）。细节归 04-numbering 报告 |
| **R3F 场景** | 4836-6587 + 7179-7790 | `On/ni/li/Ci/Vi/sa/pa/Ha/Es` | 9 个 `useFrame` 驱动单元（§3.4）；全部用 `ShaderMaterial`（GLSL 内联在包中，最长的 2.1 KB）；拾取用 **GPU 颜色拾取**（`aPickColor` + `uGate` + `readRenderTargetPixels`），**不用** Raycaster。细节归 03-render-ui 报告 |
| **UI 面板** | 7791-12120 | `Os/Vs/Js/cc/fc/Cc/Ic/Kc/qc/Xc/Qc/Nc` | 31 个含 JSX 的顶层声明；面板全部是"store 选择器 + 受控 input"，没有 CSS-in-JS，靠 319 个类名（§4.3） |
| **状态** | 3519-3784 | `J` | 123 属性，见 §3 |
| **i18n** | 无独立模块 | — | 见 §4.1：**没有 i18n 层**，中文字符串硬编码在 JSX 里（612 条去重，见 §4.1） |
| **反馈** | 10113-10240 | `vc='/api/feedback'`(10118)、`yc`(10119)、`xc`(10141) | POST `{message}`，`keepalive:true`；同时写本地草稿 `shiyun_feedback_v1`（上限 5,000 汉字，超出从旧到新丢弃）；UI 明示"仅保存正文与接收时间" |
| **公告** | 不在包里 | `/announce-202607.js` | 纯 ES5 IIFE、单一职责、全身 try/catch、自带到期自杀（2026-07-31T16:00Z）与 `localStorage` 幂等；设计目标写在注释里："星图不能因为一条横幅黑屏" |

### 2.6 REA Evidence 附录（`analyze-javascript-application`）

命令（由 lead 指定的标准跑法，本机 6.7.0）：

```bash
bash ~/.dsh/skills/rea-reverse/scripts/rea.sh analyze-javascript-application work/rea/shiyun/site --format json > work/rea/shiyun/rea-js.jsonl
```

产物 81,812,563 B / 20 行 JSONL（19 行进度 + 1 行 Evidence），`REA_EXIT=0`。关键字段：

| 字段 | 值 |
|---|---|
| `evidence_id` | `ev_d29eca9fc42a2668314523800b53951251607a0d4e2a4da18b574ef9674ea771` |
| `predicate_type` / `operation` | `rea.javascript-application-analysis` / `analyze_javascript_application` |
| `subject.digest.sha256` | `c72b5f63d634b1dd136d522702ddace309b0d4d9dee0321880d7f8008a6c1402`（= site 目录内容根） |
| `graph.graph_id` | `jag_724e3911df3d95eb84ef4d4d888f95f6bfe4f4db56589a3d07b47226cb35ff49` |
| `statistics` | `relevant_files:6, parsed_javascript_files:4, skipped:1, visited_ast_nodes:251091, findings:171, modules:0, parse_failures:0` |
| `graph` | 112 节点 / 184 边（`imports:55, exposes:50, calls:49, persists_to:13, contains:13, loads:3, maps_to:1`） |
| `coverage` | `status: partial`，限额 `javascript_analysis_worker_heap_limit_bytes: 1098907648`（1 GiB）、`timeout_ms: 300000` |

**REA 读到的事实（对架构有用的部分）**：

1. **端点 12 个真值**（其余 28 个 "endpoint" 是 three.js 的 WebGL 扩展名与 JS 关键字误报，见 limitations）：
   `${e}/charset.json`、`${e}/manifest.json`、`${e}/lexicon.json`、`${e}/poets.index.json`、`${e}/gifts.json`、`${t}/poems/${e}.json`、`${t}/poems/${i}.json`、`${t}/poems/${i}.idx.json`、`${t}/lines/${e}.json`、`${t}/linesf/${e}.json`、`${t}/search/${e}.json`、`${an}/feed?limit=${e}`
   —— 与我读到的 `mr/hr/wr/Pr/Rr/cn` 完全对得上，可交叉验证。
2. **storage 7 个节点**：`localStorage.getItem/setItem/removeItem` + 两条自定义键 `shiyun:gesture-backend` / `shiyun:gesture-fps`（与 §3.7 的键表互相印证）。
3. **Worker 节点**：new Worker 指向 /gesture-worker.js —— REA 独立发现了这个"包外模块"，与 §1.6 一致。
4. **Electron 面全部为 0**：`browser_windows:0, preload_entrypoints:0, context_bridge_apis:0, ipc.operations:0, native_addon_bindings:0` —— 证伪"这是 Electron 应用"的猜测，是纯 Web。
5. **两条必须写进报告的限制**（REA 自己声明）：
   - `assets/r3f-yJ-6H-4a.js: … Owned JavaScript worker exhausted its heap while analyzing …"`（`parsed_javascript_files:4 / skipped:1` 即此）—— **vendor 部分（React/fiber）REA 未完成解析**，所以本报告 §1.4 的版本结论走的是"字符串自报值"而不是 REA 的图。
   - `index.html has 1 inline JavaScript body starting at line 31 that was not analyzed` —— 能力门那段内联 ES5 不在图里（本报告 §5.5 用原文引用它）。

> REA 的 `modules: 0` 恰好印证 §2.1 的判断：它对打包产物**不做模块边界恢复**，只做 import/export 绑定、端点、存储、Worker、Electron 边界。模块图只能靠本报告的多路证据法。

---

## 3. 状态管理与渲染调度

### 3.1 只有一个 store：zustand v5，123 个属性（60 数据 + 63 action）

定义在 `pretty/index.js:3519-3784`，形如 `J = St((e) => ({ … }))`，其中 `St` 是 zustand 的 `create`（`St = (e) => (e ? xt(e) : xt)`，`pretty/index.js:3107`）。

- **数据字段 60 个**：`loaded, form, lushiFilter, commonOnly, hidden, selected, pulls, hoverPoetId, hoverPoem, selectedPoet, poetAliasNote, poetPoems, poetPoemsError, poetPoemsProgress, poetFocus, showGifts, guideMode, guideCoverage, guideSeconds, guideBrightness, guideStyle, settingsOpen, giftTrail, pathStart, pathEnd, pathResult, pathDimEgo, giftHoverId, showAllPoems, quality, uiHidden, gestureEnabled, gestureFps, gestureBackend, cinema, cinemaCopy, cinemaPoemIdx, cinemaShowBg, cinemaTextColor, cinemaHideTagline, cinemaShowHandle, shiyi, shiyiOpen, meteorsOn, claimFeed, myClaims, myClaimsOpen, claimCeremony, devToolOpen, meteorMinGap, meteorMaxGap, meteorSpawnReq, meteorLook, freeMove, allowRandomPoem, gravity, speed, flyTarget, lockPoetId, lockPoemIdx`
- **动作 63 个**：`setLoaded, setForm, toggleLushi, toggleCommon, toggleDynasty, showAllDynasties, showOnly, selectPoem, pulseAt, clearSelection, setHover, setHoverPoem, selectPoet, setPoetPoems, setPoetPoemsError, setPoetPoemsProgress, clearPoet, hopToPoet, clearTrail, setPath, toggleGifts, setGuideMode, …, setFlyTarget, lockPoet, lockPoem, unlock`（全表可用 `node tool/store.js` 复现）

**初始化时的"读外部状态"**（说明 store 不做持久化，只在构造时读一次）：

```js
quality: Mt ? `low` : `high`,            // Mt = 设备档位（见 §3.8）
gestureEnabled: !1,                       // 手势默认关，必须显式开
gestureFps: (() => {
  try {
    if (typeof localStorage > `u`) return `balanced`;
    let e = localStorage.getItem(`shiyun:gesture-fps`);
    return e === `eco` || e === `smooth` ? e : `balanced`;
  } catch { return `balanced`; }
})(),
```

（`pretty/index.js:3556-3566`）

### 3.2 订阅模型：173 处**单字段**选择器，无自定义相等函数

grep `J((e) => e.<字段>` 共 **173** 处；模式全部是"取一个字段"，没有 `useShallow`、没有 `shallow`、没有返回对象的选择器。

| 被订阅字段 | 次数 | 典型组件 |
|---|---:|---|
| `selectedPoet` | 8 | 行星 `li`、指引线 `Ci`、诗人面板 `Js` |
| `myClaims` | 7 | 流星 `Ha`、诗卡 `Vs`、我的认领 `Qc` |
| `showGifts` | 4 | 赠诗边 `Vi`、赠诗漫游 `fc` |
| `setFlyTarget` | 4 | 面板里的"飞过去"动作 |
| `claimFeed` | 4 | 流星 + 认领计数 |
| `selected` / `quality` / `hidden` / `meteorsOn` / `poetPoems` | 各 3 | — |

**结论**：作者有意把 store 切成"细粒度字段 + 单字段选择器"，这样 `selected` 变化不会连带重渲染整个 UI——zustand 的 `useStore` 用 `useSyncExternalStore` + `Object.is` 比较，选择器返回标量或稳定引用。**确定**（代码形态即证据）。

### 3.3 React Context 只有 1 个，且不是应用的

`pretty/index.js:2923`：`dt = (0, K.createContext)(null)` —— 它在 `pt`（EffectComposer 的 R3F 封装，`K.memo(K.forwardRef(...))`）里被 `dt.Provider` 提供一次、由 `gt`（Bloom）消费一次，是 **@react-three/postprocessing 的内部 context**，只传递 composer 实例。

全包 `createContext` 出现 **1** 次、`useContext` **0** 次 → **应用自身没有用 Context 做状态传递**：跨组件共享走 zustand，跨"层"（React ↔ 手势 ↔ 相机）走 DOM CustomEvent（§3.6）。

### 3.4 三层更新模型：per-frame / per-effect / per-render

这是本报告最核心的架构结论：**同一个 three 对象会被三种不同节奏的代码修改**，作者严格区分了它们。

| 层 | 触发频率 | 做法 | 证据 |
|---|---|---|---|
| **L1 每帧（uniform）** | 60 fps | 在 `useFrame` 里直接改 `uniforms.uTime.value` / `rotation.y`，**不 setState** | `s.points.material.uniforms.uTime.value += t`（4940）、`c.current.rotation.y = mn.angle`（4941） |
| **L2 每个 prop 变化（attribute）** | 选择变化时 | 在 `useEffect(…, [e, s, i])` 里改 `BufferAttribute` 数组 + `needsUpdate = true`，不重建 geometry | 4934-4936：`r[e] = s.poets[e].id === i ? s.baseSize[e]*1.8 : s.baseSize[e]; n.needsUpdate = !0` |
| **L3 每次 UI 变更（React）** | 用户操作时 | 改 store → 选择器命中 → 重渲染面板 | §3.2 的 173 处订阅 |

**9 个 useFrame 站点**（`r((e,t)=>{…})`，r = fiber 的 useFrame，见 §1.5）：

| 行 | 组件 | 每帧做什么 |
|---|---|---|
| 4015 | `On` 装饰星场 | `vn(n)` 推进角度、`t.points.rotation.y = mn.decorAngle`；`J.getState().cinema` 时暂停 |
| 4939 | `ni` 诗人星 | `uTime += delta` + 星云自转 |
| 5179 | `li` 行星（诗） | `hn.t += Math.min(t, 0.05)`（**delta 上限 50 ms**，切后台回来不会瞬移） |
| 5315 | `Ci` 指引线 | 读 `guideMode / guideSeconds / guideBrightness`，算生长进度 |
| 5712 | `Vi` 赠诗边 | `uTime += delta` + 随星云自转 |
| 5896 | `sa` 赠诗轨迹 | 两条材质 `uTime` 同步推进 |
| 5987 | `pa` 捞起标记 | 出生/衰减曲线，`cinema` 时 early-return |
| 6391 | `Ha` 认领流星 | 读 `meteorsOn`，`setDrawRange` 控制段数 |
| 7563 | `Es` 相机 | WASD/QE 速度、飞行插值、到点判定 |

**帧内对 store 的访问**：28 处 `J.getState()`，全部是命令式读，不走订阅。帧内**唯一**的写操作是"飞行抵达"那一帧：`J.getState().setFlyTarget(null)`（7583 / 7679）——"动画结束 → 用一次 setState 通知 UI"，被限制在事件边界上。

### 3.5 命令式单例：不在 React 里的可变状态

```js
var mn = { angle: 0, decorAngle: 0 },   // 全局旋转累加器（3795）
  hn = { t: 0 },                        // 行星时钟（3796）
  gn = 0.012, _n = 0.019;               // 两个角速度（3797-3798）
```

同类"模块级缓存"还有：`kn = null`（4021，词典）、`Hi = null`（5725，赠诗图邻接表）、`Lr = null`（4561，赠诗数据）、`Vo = null`（7016）。它们不进 store，因为"每帧都变"或"只读大对象"的值放 store 会引发每秒 60 次订阅通知或冗余深比较。**确定**（模块级 `var`、无 setter、直接赋值）。

### 3.6 跨层总线：9 个 shiyun:gesture-* DOM 事件

手势层（A25 `Jl`）与相机（A14 `Es`）之间**没有**直接 import 调用，也没有 store 中转，而是 `window.dispatchEvent(new CustomEvent(...))`：

| 事件 | 发射方 | 监听方 | 载荷 |
|---|---|---|---|
| `shiyun:gesture-select` | 手势层（12888） | `Es`（7531） | `{x, y}` 屏幕坐标，触发拾取 |
| `shiyun:gesture-orbit` / `-look` | 手势层 | `Es` | `{dx, dy}`（已限幅 ±40） |
| `shiyun:gesture-zoom` | 手势层 | `Es` | `{ratio}`（钳在 0.9-1.1） |
| `shiyun:gesture-fly` / `-fly-stop` | 手势层 | `Es` | `{x,y,z}` 归一化推力 |
| `shiyun:gesture-random-poem` | 手势层 | 面板层 | — |
| `shiyun:gesture-fps` / `-backend` | 设置面板 | 手势层 | 运行时切换帧率档 / 推理后端 |

同样用事件做"解耦信号"的还有 `shiyun:replay-onboarding`（`Tc`，10249；`window.dispatchEvent(new Event(Tc))` 10254，开发者工具"重看引导"）。**结论**：这是"React 之外的第二条数据流"，用来避免把相机逻辑卷进 React 渲染周期。**确定**。

### 3.7 持久化：7 个应用键 + 1 个公告键，全部不在 store 里

| 键 | 语义 | 读写点 | 内容 |
|---|---|---|---|
| `shiyun_shiyi_v1` | 诗忆 | `Nt`(3299)、`zt`(3324)、`Bt`(3335) | 最近"捞起/留影"的诗（index + ts + preview，≤14 条 / 200 字） |
| `shiyun_claims_v1` | 认领 | `Ut`(3356) 起 | 本机认领记录 |
| `shiyun_voidreveal_n` | 虚空揭秘计数 | `Ls`(8040) | 首次点虚空的提示计数（默认 `Rs=3`） |
| `shiyun_onboarded_v3` | 新手引导 | `wc`(10248)、`kc`(10274) | 看过引导则不再弹 |
| `shiyun_feedback_v1` | 反馈草稿 | `mc`(10114) | 未发出的草稿（≤5,000 汉字） |
| `shiyun:gesture-fps` | 手势帧率档 | store 初始化 + 设置面板 | `eco / smooth` |
| `shiyun:gesture-backend` | 手势推理后端 | 同上 | `cpu / gpu`（gpu 标注"实验"） |
| `shiyun_announce_202607_pre` | 公告已读 | `announce-202607.js` | 与主包无关的独立键 |

**确定性**：主 store **没有任何** `persist` 中间件（store 只有 `create` 包装）；持久化散落在各个 `try { localStorage… } catch {}` 小函数里，且都做了"隐私模式抛异常"兜底。**确定**。

### 3.8 重渲染触发点清单（谁真的重画）

| 触发 | 影响范围 | 证据 |
|---|---|---|
| `selectPoet / selectPoem / clearSelection` | 诗卡、面板、行星组件 | `Vs / Js / cc / li` 的 `J((e)=>e.selected…)` |
| 拖动 / 滚轮 / 键盘 | **不触发重渲染**（只改 `ref` 与相机矩阵） | `Es` 的输入状态全在 `K.useRef({})`（7180） |
| 飞行抵达 | 1 次（`setFlyTarget(null)`） | 7583 / 7679 |
| 认领轮询 | 每 90 s 一次（`setInterval(t, 9e4)`，13319） | `cn()` → `setClaimFeed` |
| 窗口尺寸变化 | 布局组件（含 `--hud-h`） | `ResizeObserver`（7823-7830） |
| 手势事件 | 只影响相机/拾取，**不改 store** | §3.6 |

---

## 4. i18n 与主题

### 4.1 语言：单语中文，没有 i18n 层

| 观测 | 数值/证据 |
|---|---|
| 文档语言 | index.html:2 `<html lang="zh-CN">` |
| i18n 库 | `i18n`=0、`locale`=0、`Intl`=0、`formatMessage`=0、`navigator.language`=0（grep 计数） |
| 硬编码中文字符串 | **864 处字符串出现 / 612 条去重 / 7,401 字**（`python pretty/_i18n.py`） |
| 英文出现位置 | 只做品牌与署名：`<title>诗云 · Poetry Cloud</title>`（index.html:6）、`title-en` 类（CSS）、`og:site_name`、开源致谢里的库名与技术说明 |
| 语言标注 | `lang: 'zh'` 作为 JSX 属性出现在 6 处（8165 / 9562 / 9665 / 10216 / 11538 / 12001），给读屏器与排版用，不参与切换 |
| 无障碍 | `aria-label` 16 处（关闭、上一句、下一句、复制分享等） |
| 无语言切换 UI | 设置面板（A20）只有指引线/亮度/覆盖/手势/画质等选项，没有语言项 |

**结论**：这是**单语产品**，中文文案直接写在 JSX 里；"Poetry Cloud" 是品牌副标，不是第二语言。因此"i18n 模块"在模块图里**不存在**——不要去找 locale 文件，找不到是对的。**确定**。

### 4.2 字体：全系统栈，零字体请求

`index-DZz16_0d.css:1` 的 `:root` 只有两条字体声明（原文）：

```css
--serif:"Kaiti SC", "STKaiti", KaiTi, "楷体", "Source Han Serif SC", "Noto Serif SC", "Songti SC", STSong, SimSun, serif;
font-family:PingFang SC,Microsoft YaHei,Noto Sans CJK SC,system-ui,sans-serif
```

- **0 个 @font-face**、0 次 `preconnect`、0 个字体文件 → 首屏没有任何字体网络请求（对中国大陆访问是硬性友好）。
- 两个字体族分工：正文/UI 走无衬线（PingFang / 雅黑 / Noto Sans CJK），**诗文本体**（`.pi-body`、`.compose-text`、`.compose-grid .cell`）走 `var(--serif)` 楷体/宋体栈。
- 3D 场景里的诗人名字**不是贴图**，而是 drei 的 `Html`（DOM 元素，类名 `poet-label`），因此同样继承这两套字体栈——这也是为什么 `--serif` 只被引用 11 次，却出现在最重要的阅读区。

### 4.3 CSS 体系：单文件、无分层、扁平类名

| 指标 | 数值 | 采集方式 |
|---|---:|---|
| 文件大小 | 49,931 B（gzip 10,010） | 字节计数 |
| 规则数（{ 计数） | 533 | 正则计数 |
| 唯一类名 | 319 | 选择器解析去重 |
| 自定义属性（设计令牌） | **6**（`--ink --gold --gold-soft --fg --muted --serif`） | `:root{}` |
| 运行期属性 | **2**（`--hud-h`、`--pinch`） | JS 写入 |
| `@layer` | **0** | grep |
| `@supports` | **0** | grep |
| `@media` | 4 | 见 §4.5 |
| CSS Modules / 哈希类名 | 无（类名全是语义化 kebab-case） | 类名清单 |

**结论**：没有 cascade layer、没有原子化框架、没有 CSS-in-JS。全部样式集中在一个文件里、靠类名前缀做"命名空间"：

| 前缀 | 唯一类名数 | 对应区域 | 前缀 | 唯一类名数 | 对应区域 |
|---|---:|---|---|---:|---|
| `cinema-` | 28 | A21 影院模式 | `dev-` | 10 | A22 开发者工具 |
| `gr-` | 27 | A18 赠诗漫游 | `fbv-` | 9 | A23 我的认领 |
| `set-` | 19 | A19/A20 设置 | `shiyi-` | 8 | 诗忆 |
| `claim-` | 16 | 认领 | `poet-` | 7 | 诗人面板 |
| `onb-` | 14 | A19 新手引导 | `myclaim-` | 7 | 我的认领 |
| `credits-` | 14 | A19 开源致谢 | `legend-` | 6 | 图例 |
| `gesture-` | 13 | A24/A25 手势 | `search-` | 5 | A17 搜索 |
| `pi-` | 13 | 诗句行（poem item） | `peek-` | 5 | A16 底部卡 |

**这条前缀表本身就是模块图的旁证**：CSS 里出现的 `cinema- / gesture- / credits- / onb- / fbv-` 前缀，与 §2.3 的 A21 / A25 / A19 / A19 / A23 区域一一对应，说明 UI 是按"面板"垂直切分的，而不是按"组件库"横切。

### 4.4 颜色与主题：单套深色，没有浅色方案

| 令牌 | 值 | 用途 |
|---|---|---|
| `--ink` | `#04050a` | 页面底色 |
| `--gold` | `#ffd27a` | 主强调（标题、按钮、选中） |
| `--gold-soft` | `#f6dca6` | 次级强调 |
| `--fg` | `#e8ecf4` | 正文 |
| `--muted` | `#8b93a7` | 次要文字（用量最大：70 次 `var(--muted)`） |
| `--serif` | 见 §4.2 | 诗文 |

WebGL 侧同色系：`<color attach="background" args={["#03040a"]}>`、`<fog attach="fog" args={["#03040a", 2400, 13000]}>`（`pretty/index.js:13338-13339`）；另有浅金常量 `Cn = new L("#fff1d6")`（3842）。

- `prefers-color-scheme` **0 次** → 没有浅色主题，也不响应系统主题。
- 页面 `<meta name="theme-color" content="#07080f">`（index.html:8），能力门兜底页背景也是 `#07080f`（index.html:54）。
- 观测到三个近似黑值同时存在：`#07080f`（meta / 兜底页）、`#04050a`（`--ink`）、`#03040a`（WebGL 背景）——不是 bug，而是"浏览器 chrome / DOM / canvas"三段各自的取色，肉眼不可辨。

### 4.5 四条媒体查询（全部内容）

| 查询 | 命中内容 | 说明 |
|---|---|---|
| `@media (prefers-reduced-motion:reduce)` | `.spinner{animation-duration:2.4s} .sk-row{animation:none} .load-bar{transition:none}`（共 82 B） | **只降级加载动画**；WebGL 星空/行星/流星**完全没有** reduced-motion 分支（JS 里也 0 次 grep）→ 动效偏好只能影响骨架屏 |
| `@media (max-width:600px)` | HUD 顶/底、`.title`、`.poem-panel / .poet-panel / .settings / .giftroam`、`.search`、`.compose-text`、`.poem-body`、`@keyframes sheet-up`（1,108 B） | 手机竖屏：面板变全宽底部抽屉、字号降级、多一个上滑动画 |
| `@media (max-width:720px)` | `.gesture-hud`、`.gesture-preview-wrap canvas`、`.gesture-readout`…（510 B） | 手势预览面板在窄屏缩小 |
| `@media (max-width:600px) and (pointer:coarse)` | `.panel-close / .set-close`、`.copy-btn / .pi-locate / .pi-cinema`、`.seg-btn / .filter / .stab / .gr-node…`、`.pi-row`、`.legend-row / .search-row`（256 B） | **触屏专用**：把可点区域整体放大 |

**结论**：移动端策略是"**布局重排 + 命中区放大 + 画质降档**"，而不是"移动端砍功能"——搜索、认领、影院、手势在手机上都在，只是换了排布。**确定**。

---

## 5. URL、深链与特性开关

### 5.1 没有路由：URL 是"一次性输入 + 单向输出"

grep 结果（全包）：`pushState` **0**、`popstate` **0**、`hashchange` **0**、路由库 **0**。只有 3 个 URL 相关函数（下面按美化后的源码摘录，模板字符串的反引号按原样保留）：

```js
function ks(e, t) {                       // 7946：把当前选择写成 URL
  let n = new URLSearchParams(e.search);
  n.delete(`a`), n.delete(`p`);
  t?.kind === `a` && n.set(`a`, t.value);
  let r = n.toString(),
    i = t ? `#${t.kind}=${t.value}` : ``;
  return e.pathname + (r ? `?` + r : ``) + i;
}

function Ms() {                           // 7978：只在选择变化时写回（replaceState）
  let e = ks(location, js());
  e !== location.pathname + location.search + location.hash &&
    history.replaceState(null, ``, e);
}
```

- **输入**：`Ns()`（7983）在**数据加载完成后**被调用一次（`Xl` 的 `mr().then(...)`，13274），解析 URL → 恢复诗人/诗。
- **输出**：`Ms()` 在 `useEffect(…, [e, r, i])`（loaded / selected / selectedPoet）里调用，把当前选择写回地址栏。
- **没有回退**：因为是 `replaceState`，浏览器"后退"会**直接离开站点**，不会退回上一个诗云状态。这是有意取舍（避免刷屏式历史），代价是"分享链接"必须由 `Fs` 按钮主动复制（8012：`navigator.clipboard.writeText(location.href)`）。

### 5.2 深链格式与解析优先级

| 形式 | 语义 | 解析代码 | 备注 |
|---|---|---|---|
| `?a=<id>` 或 `#a=<id>` | 定位到**诗人** | `As`(7953) → `cr(id)` → `ur()` 规范化 → `selectPoet` + `setFlyTarget(qr(poet))` | `<id>` 是 `poets.index.json` 里的诗人 id（8 位十六进制）；若该诗人已并入他人，会弹 `fr()` 提示"「X」已并入「Y」"（4210） |
| `?p=<digits>` 或 `#p=<digits>` | 定位到**诗**（按编号） | `As` → `Xo('ziyou', digits)` → `selectPoem` + `setFlyTarget` | 解析前先 `replace(/[^0-9]/g,'')` 只留数字；允许 `wujue.123` 这种"诗体.编号"写法，但**诗体前缀被丢弃**（`Xo` 7089 不读第一个参数），一律按 `ziyou` 目录解编号 |
| 其它参数 | 原样保留 | `ks` 只增删 `a` / `p` | 为将来扩展留位 |

**解析优先级**：`As(location)` 先读 **hash**（形如 `#a=值` / `#p=值`，`decodeURIComponent` 后必须非空），没有再读 **query**。**确定**（7953-7969）。

**双写**：`ks` 同时写出 `?p=123` 与 `#p=123`。源码注释没解释，但从 `As` 的优先级可推断：hash 更不容易被中间的跳转/统计脚本吞掉，query 更兼容老链接与第三方分享面板。**推断**。

### 5.3 特性开关与运行期开关清单

| 开关 | 取值 | 默认 | 作用点 | 证据 |
|---|---|---|---|---|
| 画质档 | `high / low` | 由设备决定（`Mt`） | 装饰星 12 万 vs 4.2 万；是否挂 Bloom | 3852-3854、13349 |
| 触屏判定 | `q` | `matchMedia('(pointer: coarse)')` | 引导文案、面板折叠、DPR 上限 | 3290 |
| 设备档位 | `Mt = jt()` | 见 §5.4 | `quality` 初值、DPR | 3291-3298、13260 |
| DPR 上限 | `[1, 1.5]` / `[1, 2]` | 手机 1.5、桌面 2 | `dpr: [1, Yl]` | 13260、13334 |
| 手势 | `gestureEnabled` | **false** | 开了才创建 Worker、要摄像头 | 3557、12736 |
| 手势帧率 | `eco 15 / balanced 24 / smooth 30`（cameraFps） | `balanced` | Worker 送帧节奏 | `jl` 12586-12588、12729 |
| 手势后端 | `cpu / gpu` | `cpu`（gpu 标"实验"） | MediaPipe delegate | worker 第 20-23 行 |
| 指引线模式 | `off / flash / hold / all` | `flash` | 选中诗人后亮多久 | 3535、5315 |
| 指引线样式 | `plane / line` | `plane` | 平面坐标式 vs 直线旧版 | 3538 |
| 指引覆盖 | `optimized / all` | `optimized` | 只画可见范围 vs 全量 | 3537 |
| 流星 | `meteorsOn` | 开 | 认领流星 | 6391 |
| 影院模式 | `cinema` | 关 | 隐藏 HUD、暂停动画 | 13376、5988 |
| UI 隐藏 | `uiHidden` | 关 | 键盘 `KeyH` 切换 | 13288 |
| 全屏 | — | — | 键盘 `KeyF` | 13289 |
| 随机诗 | `allowRandomPoem` | 由引导决定 | 手势"✌"随机 | 10256 |
| 自由移动 | `freeMove` | 关 | 手势推动 vs 轨道 | 7568 |

### 5.4 移动端 / 弱设备降级清单

**设备档位判定（原文，3291-3297）**：

```js
function jt() {
  if (typeof navigator > `u`) return !1;
  if (q) return !0;                                   // q = (pointer: coarse)
  let e = navigator.hardwareConcurrency ?? 8,
    t = navigator.deviceMemory ?? 8;
  return t <= 2 || (e <= 2 && t <= 4);
}
var Mt = jt();
```

| 降级项 | 手机 / 弱设备 | 桌面 | 证据 |
|---|---|---|---|
| 装饰星数量 | 42,000 | 120,000 | 3852-3854 |
| 装饰星尺寸参数 | 3,500 / 24,000 | 9,000 / 64,000 | 3853-3854 |
| Bloom 后期 | **不挂** | `<EffectComposer><Bloom intensity=1.4 …>` | 13349-13360 |
| DPR 上限 | 1.5 | 2 | 13260 |
| 引导第三屏文案 | "出发" | "飞出去" | 10256-10270 |
| 面板形态 | 全宽底部抽屉（`.search.collapsed`、`sheet-up` 动画） | 侧边浮层 | CSS 600px 查询 |
| 命中区 | 放大（panel-close / copy-btn / seg-btn / pi-row） | 常规 | CSS `(pointer:coarse)` 查询 |
| 手势 HUD | 缩小预览 | 完整 | CSS 720px 查询 |
| 3D 渲染参数 | `antialias:false`、`powerPreference:"high-performance"`（两端一致） | 同 | 13335 |

### 5.5 能力门：比主包更早的 ES5 兜底

index.html:31-59 内联了一段**手写 ES5**（在 ES2022 主包之前的最后防线）：

- BigInt 缺失 → "你的浏览器过旧（缺少 BigInt），无法运行诗云的编号引擎……"
- WebGL 缺失 → "此设备或浏览器没有可用的 WebGL，无法渲染诗云星图……"
- 命中时置 `window.__SHIYUN_UNSUPPORTED__ = true` 并直接把提示写进 `#root`。

主包最后一行用同一个标志决定是否挂载（`pretty/index.js:13450`）：

```js
window.__SHIYUN_UNSUPPORTED__ || Ct.createRoot(document.getElementById(`root`)).render(
  (0, G.jsx)(K.StrictMode, { children: (0, G.jsx)(Xl, {}) }),
);
```

**结论**：能力门与挂载点是**同一个契约的两端**（HTML 侧写标志、JS 侧读标志）；这也解释了内联脚本为什么用 ES5——它必须能在"连 ES2022 都解析不了"的浏览器上运行。**确定**。REA 的 limitations 明确说这段内联脚本"未分析"（§2.6），所以这里证据来自原文阅读。

### 5.6 网络接口（全部同源，无 CDN）

| 接口 | 方法 | 何时 | 证据 |
|---|---|---|---|
| `/data/charset.json`、`/data/poets.index.json`、`/data/manifest.json`、`/data/lexicon.json` | GET | 启动一次（`Promise.all`） | 4251-4261 |
| `/data/poems/<bucket>.json` + `poems/<bucket>.idx.json` | GET / Range | 点诗人时 | 4272-4300 |
| `/data/lines/<b>.json`、`linesf/<b>.json` | GET | 搜索 / 行库 | 4363、4378 |
| `/data/search/<b>.json` | GET | 检索 | 4496 |
| `/data/gifts.json` | GET | 开赠诗模式 | 4562 |
| `/api/claim` | POST | 点"认领这首诗" | 3466-3485 |
| `/api/claim/feed?limit=N` | GET | 每 90 s 轮询 + 启动 | 3486-3514、13319 |
| `/api/feedback` | POST `{message}`、`keepalive:true` | 用户提交反馈 | 10118-10133 |

没有第三方域名、没有分析脚本、没有 CDN、没有 cookie —— 只有 `localStorage`。

---

## 6. 复现与附录

### 6.1 复现命令（全部在本仓库内可跑）

```bash
cd work/rea/shiyun

# 1) 美化主包（264,935 B → 13,454 行）
npx --yes prettier@3.3.3 --parser babel site/assets/index-ah4l33vX.js > pretty/index.js

# 2) 解析器（仅本报告使用）
mkdir -p tool && cd tool && npm i acorn@8 acorn-walk@8 && cd ..

# 3) 顶层声明 + 引用图 → pretty/_ast.json（539 条）
node tool/ast2.js

# 4) 27 个区域的行号/行数/声明数
node tool/regions.js

# 5) store 形状（123 属性 = 60 数据 + 63 动作）
node tool/store.js

# 6) 任意符号的前 12 行 + 中文字符串
node tool/show.js On ni li Ci Vi sa pa Ha Es

# 7) REA 结构化视图（81 MB JSONL，最后一行是 Evidence）
bash ~/.dsh/skills/rea-reverse/scripts/rea.sh analyze-javascript-application work/rea/shiyun/site --format json > rea-js.jsonl
python pretty/_rea_sum.py        # 摘要
python pretty/_rea_edges.py      # 边与端点
```

### 6.2 本报告用到的分析产物（都在 work/rea/shiyun/ 下）

| 文件 | 说明 |
|---|---|
| `pretty/index.js` | 美化后的主包（13,454 行） |
| `pretty/_ast.json` | 539 个顶层声明的行号 / 引用 / 字符串 |
| `pretty/_outline.tsv` | 每条声明的行号 + 标志（JSX/HOOK/SHADER/IO/LS）+ 首批中文字符串 |
| `tool/ast2.js`、`tool/regions.js`、`tool/store.js`、`tool/show.js`、`tool/defs.js` | 分析与取证脚本 |
| `rea-js.jsonl`、`rea-evidence.json` | REA Evidence（81 MB / 规范化 JSON） |
| `extra/gesture-worker.js` | 补抓的 Worker（唯一一次联网），4,583 B |

### 6.3 未解决 / 值得后续确认的点

1. **Vite / Rolldown 精确版本**：产物无版本串，只能定到"Rolldown + Vite ≥5.1 + rolldown-vite 线"。拿到 `vite.config.ts` 或 `package.json` 即可钉死。
2. **postprocessing 版本**：库内没有版本常量；可用 `EffectComposer` 的 API 形状（`StableDepth / Buffer` 两个 target 名）比对 npm 版本区间。
3. **数据管线**：charset / lexicon / poems 分桶的生成脚本不在客户端；`manifest.json` 的 `version:3 / pullK:13564` 是唯一线索（见 02-data）。
4. **linesf 的语义**：`?f` 分支（4378）与 `lines/` 并列，而 `data/linesf/00.json` 实测 404（代码把 404 视为空并缓存）。是"全文本行"还是"过滤后行"，需要 02-data 的实测。
5. **手势 Worker 的真实时延**：注释里的 56 ms / 174 ms 是作者机器的实测，不能当作线上表现。

### 6.4 与其他报告的分工

- **02-data**：桶 / sidecar / Range / 缓存 / 预取 / 数据 schema（本报告只回答"谁在什么时候发哪个请求"）。
- **03-render-ui**：星云几何、GPU 拾取、shader、交互与面板流程（本报告只回答"哪个组件负责哪一层、用什么节奏更新"）。
- **04-numbering**：BigInt 进制转换、lexicon、编号 ⇄ 坐标的可逆性（本报告只回答"编号引擎在哪、被谁调用"）。
