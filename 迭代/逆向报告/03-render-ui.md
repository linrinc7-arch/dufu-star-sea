# 03 · 渲染与交互逆向：诗云的三维星图是怎么画出来的

> 目标站点：<https://shiyun.cohenjikan.com>（Vite + Rolldown 打包的 React 18 + @react-three/fiber + three.js r169）
> 本文只回答一件事：**"星空感"是怎么被构造出来的**，所有结论都能被代码行号或数据复现，末尾给出可直接搬到 Canvas 2D 的参数表与伪代码。

---

## 0. 证据口径与复现方法

### 0.1 制品与哈希

| 文件 | 大小 | sha256 |
|---|---|---|
| `site/assets/index-ah4l33vX.js` | 264,935 B | `f5f23f6b8e3a2440153c3984991d7f74c2097a55ee128bbd49e1e14899a6dac0` |
| `site/assets/three-CjFqNL11.js` | 675,551 B | (three.js r169，文件末尾自报 revision 169) |
| `site/assets/r3f-yJ-6H-4a.js` | 276,945 B | @react-three/fiber 18.3.1 + drei |
| index.html 里的 OG 图 | — | `/og.jpg`（静态，非动态生成） |

**本文所有行号**都指向下面这个可复现的中间产物（不是原始压缩文件）：

~~~bash
npx prettier@3.3.3 --parser babel site/assets/index-ah4l33vX.js > pretty/index.js
# 本文写就时 pretty/index.js 的 sha256 =
# 4eee1b2a89d32d4c807c26053157c107777f7110343410f8d893add6df75431f  (13,453 行)
~~~

同一份快照另存于 `work/rea/shiyun/render-ui/pretty-index.js`（同 sha256），下文行号均以它为准。
验证脚本在 `work/rea/shiyun/render-ui/`：

| 脚本 | 验证了什么 |
|---|---|
| `verify_geometry.py` | 诗人数量、朝代半径带、`qr()` 坐标、星团半径、点大小；**逐位复刻**了 `qr()/Yr()/Zr()/ti()` |
| `verify_void.py` | 点虚空 → 编号 → 20 字 → 五绝全文；含「常用字过滤」与「格律过滤」两条路径 |
| `verify_density.py` | 背景银河生成器的抽样复刻（半径/厚度/臂） |
| `verify_screen.py` / `verify_screen2.py` | 默认机位下 32,654 个星团的屏幕投影、像素密度、点径分布 |
| `verify_cluster.py` | 单个诗人内部"诗星团"的 Fibonacci 球结构与间距 |

### 0.2 反混淆对照表（读 shader 必备）

应用体被 Rolldown 压缩成两个字母，先建立映射（`three-CjFqNL11.js` 末尾的 export 表 + `index.js` 头部 import 对照而得）：

| 应用内别名 | three 内部名 | 真实类 |
|---|---|---|
| `x` | `eu` | **Points** |
| `m` | `Vi` | **ShaderMaterial** |
| `I` | `Z` | **BufferGeometry** |
| `F` | `Y` | **BufferAttribute** |
| `N` | `Yl` | **PointsMaterial** |
| `l` | `Dc` | **SpriteMaterial** |
| `_` | `Vc` | **Sprite** |
| `h` | `Sn` | **WebGLRenderTarget** |
| `S` | `Cc` | **Scene** |
| `re` | `lc` | **Group** |
| `E` | `G` | **Vector3** |
| `g` | `V` | **Vector2** |
| `w` | `K` | **Matrix4** |
| `u` | `Dn` | **Quaternion** |
| `L` | `J` | **Color** |
| `y` | `im` | **Raycaster** |
| `M` | `fr` | **Euler** |
| `d` | `Ai` | **Mesh** |
| `f` | `Ki` | **PerspectiveCamera** |
| `oe` | `ql` | **LineSegments** |
| `ee` | `Jl` | **LineLoop** |
| `T` | `l` | **NearestFilter**（值 1003） |
| `R` | `ft` | **DynamicDrawUsage** |

r3f 侧：`a`=`Canvas`，`t`/`r` 分别是被 `(0,K.useRef)` 化的 `useThree` 与 `useFrame`，`J`=zustand store hook。

---

## 1. 场景清单：一共几层点云

`Xl()` 是应用根组件，`<Canvas>` 里的层级一目了然（`pretty/index.js:13324-13360`）：

~~~jsx
// pretty/index.js:13327
(0, G.jsxs)(a, {                      // a = <Canvas>
  camera: { position: [700, 4600, 4600], fov: 55, near: 0.1, far: 18e3 },
  dpr: [1, Yl],                       // Yl = Mt ? 1.5 : 2
  gl: { antialias: !1, powerPreference: `high-performance` },
  onCreated: ({ camera: e }) => e.lookAt(0, 0, 0),
  children: [
    (0, G.jsx)(`color`, { attach: `background`, args: [`#03040a`] }),
    (0, G.jsx)(`fog`, { attach: `fog`, args: [`#03040a`, 2400, 13e3] }),
    (0, G.jsx)(On, {}),               // 背景银河   193,000 点（high）
    e && (0, G.jsx)(ni, {}),          // 诗人星     33,458 点（32,654 可见）
    e && (0, G.jsx)(li, {}),          // 诗星层     选中诗人 / 全诗 871,268 点
    e && (0, G.jsx)(Ci, {}),          // 行星指引线
    e && (0, G.jsx)(Vi, {}),          // 赠诗边     5,051 条 × 26 段
    e && (0, G.jsx)(sa, {}),          // 拉取轨迹
    (0, G.jsx)(pa, {}),               // 点虚空的"捞取"标记  ≤40 点
    e && (0, G.jsx)(Ha, {}),          // 流星 / 认领
    (0, G.jsx)(Es, {}),               // （不是渲染层）相机与输入控制器
    n === `high` && <EffectComposer><Bloom/></EffectComposer>,
  ],
})
~~~

逐层参数（**全部来自代码，不是估计**）：

| # | 层 | 组件（行） | 点/几何数 | 尺寸来源 | 颜色 | 混合 | 深度写入 |
|---|---|---|---|---|---|---|---|
| 1 | 背景银河 | `On()` 3847 | high **120,000+9,000+64,000 = 193,000**；low 42,000+3,500+24,000 = 69,500 | `uSize=3 × aScale × 900/-z`，clamp **0.6–64 px** | 按半径 `#fff1d6→#fff7ec→#fff→#cfe0ff`，极少数 `#ff6d92` | 加色(2) | 否 |
| 1b | 远景星壳 | 同 `On` 3970 | **5,200** 点，球半径 **7,200** | `PointsMaterial size=16, sizeAttenuation` | 顶点色（灰度×1.05 偏蓝） | 加色 | 否 |
| 1c | 中心星云 Sprite | 同 `On` 3959 | 1 张 Sprite | 缩放 `1.05×RADIUS` | `#ffe9c4`，opacity 0.24 | 加色 | 否 |
| 2 | 诗人星（星团核心） | `ni()` 4836 | **33,458**（804 个 `mergedInto` 的 aSize=0，实际不可见 → 32,654） | `aSize=(1.4+clusterSize×0.32)×(名诗人2.4)`，shader clamp **1.2–70 px**，`900/-z` | 朝代色；48 人「名诗人」名单 `lerp(白,0.22)×1.8` | 加色 | 否 |
| 3 | 诗星（聚类小球） | `li()` 5097 + `si()` 5018 + `oi()` 4980 | 选中诗人：**该诗人全部诗**（如李白 1,051）；`showAllPoems`：**871,268** | 选中：`sizeScale=860, maxPx=44`；全诗：`360, 11` | 诗人朝代色 | 加色 | 否 |
| 4 | 拉取标记 | `pa()` 5935 | ≤ **40**（`fa=40`），环形复用 | `(520+aFlare×4500)/-z`，clamp **3.5–64 px** | 合律金色 `[1,.84,.4]` / 不合律蓝白 `[.78,.86,1]` | 加色 | 否 |
| 5 | 赠诗边 | `Vi()` 5577 | 5,051 边 × **26 段** = 131,326 顶点 | 1 px 线段 | 两端朝代色插值 ×`sin(πt)`，沿线跑脉冲 ×3.2 | 加色 | 否 |
| 6 | 流星 | `Ha()` 6228 | 每颗 `16 头 + 64 尾` 顶点 | `aSize/-z`，clamp **1–48 px** | `past` 冷白 / `today` / `ceremony` 三档 | 加色 | 否 |

**关键事实：默认视角下第 3 层是关的。** `showAllPoems: !1`（`:3548`）——首屏只有 33,458 个诗人信标 + 193k 背景星。诗星层只在"选中某位诗人"或用户主动打开"行星"时才出现。

---

## 2. 几何：32,654 位诗人是怎么被放到星星上的

### 2.1 不是预置坐标，也不是噪声贴图 —— 是 FNV-1a 哈希 + 朝代半径带

每个诗人的位置由纯函数 `qr(poet)` 算出（`:4749-4798`），**没有任何坐标 JSON**：`poets.index.json` 里只有 `{id,name,dynasty,poemCount,clusterSize}`（实测字段组合见附录 A）。

哈希是标准 FNV-1a 32 位（`:3284`）：

~~~js
function At(e) {                    // :3284
  let t = 2166136261;
  for (let n = 0; n < e.length; n++)
    (t ^= e.charCodeAt(n)), (t = Math.imul(t, 16777619));
  return t >>> 0;
}
~~~

**朝代 = 半径**。15 个朝代按 `id` 排成 15 条同心环带（`:3276-3283`）：

~~~js
Tt = wt.length,               // 15
Et = Object.fromEntries(wt.map((e) => [e.key, e])),
Dt = 3400,                    // 星系外径
Ot = (Dt - 420) / wt.length;  // = 198.6667
function kt(e) { let t = 420 + e * Ot; return [t, t + Ot]; }
~~~

于是"时间"被直接映成"半径"：

| 朝代 | id | 半径带 | 实际诗人数 |
|---|---|---|---|
| 先秦 | 0 | 420 – 619 | 8 |
| 秦汉 | 1 | 619 – 817 | 84 |
| 魏晋 | 2 | 817 – 1016 | 251 |
| 南北朝 | 3 | 1016 – 1215 | 434 |
| 隋 | 4 | 1215 – 1413 | 84 |
| 唐 | 5 | 1413 – 1612 | 2,820 |
| 五代 | 6 | 1612 – 1811 | **0（数据里没有 wudai，李煜/韦庄都归入 tang）** |
| 宋 | 7 | 1811 – 2009 | 9,495 |
| 辽 | 8 | 2009 – 2208 | 7 |
| 金 | 9 | 2208 – 2407 | 269 |
| 元 | 10 | 2407 – 2605 | 1,210 |
| 明 | 11 | 2605 – 2804 | 4,514 |
| 清 | 12 | 2804 – 3003 | 8,980 |
| 近现代 | 13 | 3003 – 3201 | 969 |
| 当代 | 14 | 3201 – 3400 | 4,333 |

（上表由 `verify_geometry.py` 用 `poets.index.json` 实算，源码表在 `:3109-3275`，每朝代还带 `color / weight / yearStart / yearEnd / group`。）

### 2.2 四臂螺旋的完整公式（可直接抄）

~~~js
// pretty/index.js:3785 —— 星系常数
Y = { RADIUS: 3600, BRANCHES: 4, TWIST: 5.2, ARM_SPREAD: 0.42, THICKNESS: 0.11 }

// :3793 —— 唯一用到的"三角噪声"：三个均匀随机相加减 1.5，值域 [-1.5,1.5]
function pn(e, t, n) { return e + t + n - 1.5; }

// :4749 —— 诗人 → 坐标
function qr(e) {
  let [t, n] = kt((Et[e.dynasty] ?? wt[Tt - 1]).id),   // 该朝代的半径带
    r = At(e.id + e.name),                              // FNV-1a → 32 位"随机"数
    i = (t + n) / 2, a = n - t,
    o = i + pn(                                       // ① 半径 = 带中心 + 三角噪声 × 1.5 个带宽
        ((r >>> 2) & 255) / 255,
        ((r >>> 10) & 255) / 255,
        ((r >>> 18) & 255) / 255) * a * 1.5;
  o = Math.max(420 * 0.35, Math.min(Dt * 1.06, o));   // clamp 到 [147, 3604]
  let s = o / Y.RADIUS,                                // 归一化半径
    c = ((r % Y.BRANCHES) / Y.BRANCHES) * Math.PI * 2, // ② 4 条臂之一（0/90/180/270°）
    l = s * Y.TWIST,                                   // ③ 螺旋扭转：半径 0→1 转 5.2 rad(298°)
    u = pn(((r >>> 3) & 255) / 255, ((r >>> 11) & 255) / 255,
           ((r >>> 19) & 255) / 255) * Y.ARM_SPREAD * 0.45,  // ④ 臂宽抖动 ±0.19 rad
    d = ((r >>> 24) & 255) / 255,
    f = Math.max(0, 0.5 - s) / 0.5,                    // ⑤ 只有内盘(r<0.5R)才有大角向散布
    p = c + l + u + (d - 0.5) * Math.PI * 2 * f;       //   → 核球是"团"，外盘是"臂"
  let m = ((r >>> 5) & 255) / 255, h = ((r >>> 13) & 255) / 255, g = ((r >>> 21) & 255) / 255,
    _ = 1 + Math.max(0, 0.45 - s) * 2.6,               // ⑥ 核球厚度鼓包 ×1~×3.6
    v = pn(m, h, g) * o * Y.THICKNESS * 2.1 * _;       // ⑦ 盘厚 = 半径的 11%
  // 第二套哈希（name#id）用来做小尺度散布，避免同一诗人的两套随机相关
  let y = At(e.name + "#" + e.id), ...
  return [cos(p)*o + w(b,x) + D*E, v, sin(p)*o + w(S,C) + O*E];
}
~~~

要点（这几条就是"像星系"和"像随机尘埃"的分界）：

1. **半径不是均匀也不是正态，而是"朝代带中心 + 三角分布(σ≈149)"**。带宽只有 198.7，散布 1σ≈149 → 相邻朝代的带**互相重叠 1.5 倍**，所以看不出 15 个同心圆环，只看到平滑的径向密度剖面（见 §8.3 实测）。
2. **角度 = 臂号 + 5.2·r 的扭转 + 臂宽噪声 + 内盘额外散布**。外盘（r>0.5R）没有那层 ±π 的散布，所以**臂只在外盘清晰**；内盘（核球）被打散成一团。
3. **竖向厚度与半径成正比（11%），核球再乘最多 3.6 倍**——这就是"薄盘 + 隆起核球"。
4. 全部由 `At(id+name)` 的 4 个字节扇区提供随机数，**同一诗人永远同一坐标**，无需存盘、无需加载。

### 2.3 "诗人是星团"：一位诗人 = 一个 Fibonacci 球

选中某位诗人后，诗星层把他/她的每一首诗放进一个以 `qr()` 为球心的球里（`:4800-4830`）：

~~~js
var Jr = Math.PI * (3 - Math.sqrt(5));            // :4799 黄金角 ≈ 2.39996
function Yr(e) { return Math.min(3e3, 35 + 13 * Math.sqrt(Math.max(1, e))); }  // 球半径 ~ √诗数
function Zr(e, t) {                               // 第 t 首诗在球内的偏移
  let n = Math.max(1, e.poemCount), r = Yr(n),
    i = 1 - (2 * (t + 0.5)) / n,                  // 黄金螺旋的 y 分层（-1..1）
    a = Math.sqrt(Math.max(0, 1 - i * i));
  let o = (At(e.id) & 65535) * 0.001,             // 每个诗人自己的相位偏移
    s = t * Jr + o,
    c = At(e.id + ":" + t),                       // 每首诗独立抖动
    l = 0.4 + 1.2 * (((c >>> 8) & 255) / 255),
    u = r * (((c >>> 16) & 65535) / 65535) ** 0.62 * l,   // ← ^0.62：往外推，壳层更空
    d = At(e.id + "#shape"),                      // 每个诗人一个椭球形状
    f = 0.55 + 1.05 * (((d >>> 2) & 255) / 255),
    p = 0.4 + 0.95 * (((d >>> 10) & 255) / 255),
    m = 0.55 + 1.05 * (((d >>> 18) & 255) / 255);
  return [a * Math.cos(s) * u * f, i * u * p, a * Math.sin(s) * u * m];
}
// :4823 第 t 首诗的世界坐标 = 星团中心 + 自转后的偏移（整团缓慢自转）
function Qr(e, t) { ... hn.t * Xr(e) ... }   // Xr = ±(0.018~0.068) rad/s，方向由哈希决定
~~~

**星团半径只跟"诗数"走，不跟朝代走**：`Yr(n)=min(3000, 35+13√n)` → 面积 ∝ n，即**面密度恒定**（实测：n=1000 时 625 面积单位/首，n=20000 时 551，见 §8.4）。这是"每个星团看起来一样密"的关键。

### 2.4 实测（`verify_geometry.py` / `verify_cluster.py` 真实输出）

~~~
poets.index entries      : 33458
  with mergedInto        : 804        ← 别名/合并条目，poemCount=0
  visible (non-merged)   : 32654      ← manifest.poetCount = 32654  ✅
  total poemCount        : 871268     ← manifest.poemCount = 871268  ✅

李白   id=82a5851c dynasty=tang  poemCount=1051 clusterSize=47.39  Yr=456.4  ti=39.76
      坐标 (1357.0, 80.3, 351.6)  盘面半径 1401.8  高度 80.3
杜甫   id=d58755b0 dynasty=tang  poemCount=1473 clusterSize=55.73  Yr=533.9  ti=46.16
      坐标 (1552.5, -144.1, -864.1) 盘面半径 1776.8
陆游   id=1ca4256c dynasty=song  poemCount=9612 clusterSize=60.00  Yr=1309.5 ti=49.44
      坐标 (-2073.0, -141.2, 374.0) 盘面半径 2106.4
曹操   id=7579f6e1 dynasty=weijin poemCount=28  clusterSize=9.41  Yr=103.8  ti=10.59

李白星团内部（n=1051）: 诗星到中心 p50=238(0.52Yr) p90=502(1.10Yr) max=791(1.73Yr)
                        相邻序号间距中位 317 ≈ 0.69 Yr
~~~

### 2.5 为什么说"诗人是星团，虚空是一切可能的诗"

这不是修辞，是**两套不同的命中机制**（详见 §5）：

- **星** = 实体数据：一个诗人 → 一个星团（其诗 = 团内星点）；命中有数据可查。
- **虚空** = 编号空间：任意坐标 `(x,y,z)` 经 `So()` 空间哈希成一个 64 位种子，再在"22219 个字、20 个字长"的空间里取 20 个字 → **当场算出一首五绝**，不存在于任何文件里。

产品自己也这么说（首次点虚空的前 3 次会弹提示，`:8133-8138`，计数键 `shiyun_voidreveal_n`，阈值 `Rs=3` `:8040-8041`）：

> 这首诗此前并不存在 —— 它是你点下的那一刻，从那个坐标当场算出来的。同一个点，永远捞出同一首。

以及 `index.html` 的 meta description：

> 一张可漫游的三维星图：真实诗人是星团，星团之间的虚空是一切可能的诗。

---

## 3. 材质与着色器：逐层拆开

七层全是**加色混合（`blending: 2` = AdditiveBlending）+ `depthWrite:false`**。没有一张贴图参与主星场（只有一个 128×128 程序化生成的光斑贴图给远景星壳和中心 Sprite 用，`An()` `:4022-4045`）。

### 3.1 背景银河 `On()`：通用点着色器（`:3929-3955`）

~~~js
new m({                                  // ShaderMaterial
  transparent: !0, depthWrite: !1, blending: 2,     // 加色
  uniforms: { uSize: { value: 3 } },
  vertexShader: `
    uniform float uSize;
    attribute vec3 aColor; attribute float aScale;
    varying vec3 vColor;
    void main() {
      vec4 vp = viewMatrix * modelMatrix * vec4(position, 1.0);
      gl_Position = projectionMatrix * vp;
      gl_PointSize = clamp(uSize * aScale * (900.0 / -vp.z), 0.6, 64.0);
      vColor = aColor;
    }`,
  fragmentShader: `
    varying vec3 vColor;
    void main() {
      float d = length(gl_PointCoord - vec2(0.5)) * 2.0;
      float a = exp(-d * d * 4.5);          // 高斯核，中心 1，边缘 0
      if (a < 0.004) discard;
      gl_FragColor = vec4(vColor * a, a);   // 预乘 alpha 的加色写法
    }`,
})
~~~

**两个必须记住的数字**：`900.0 / -vp.z`（透视点径）与 `exp(-d²·4.5)`（高斯核）。

亮度分层（`:3904-3923`，颜色按半径渐变）：

~~~js
g < 0.12 ? f.copy(Cn).lerp(wn, g/0.12)          // #fff1d6 → #fff7ec   (核心偏暖)
         : g < 0.4 ? f.copy(wn).lerp(Tn, (g-0.12)/0.28)   // → #ffffff
         : f.copy(Tn).lerp(En, min(1,(g-0.4)/0.5)),       // → #cfe0ff   (外圈偏冷)
t || f.lerp(En, _*0.45),          // 臂上的星再往蓝里压一点
y && f.copy(Dn),                  // 极稀有(4%)的"红巨星" #ff6d92
aScale = 0.5~1.5，且 9,000 颗"装饰星"用 (0.7+_*0.8+…) 提亮
~~~

### 3.2 诗人星 `ni()`：整幅画面的主角（`:4875-4902`）

~~~js
new m({
  transparent: !0, depthWrite: !1, blending: 2,
  uniforms: { uTime: { value: 0 }, uSizeScale: { value: 900 } },
  vertexShader: `
    attribute vec3 aColor; attribute float aSize; attribute float aSeed;
    uniform float uTime; uniform float uSizeScale;
    varying vec3 vColor; varying float vTw;
    void main() {
      if (aSize < 0.001) { gl_Position = vec4(2.0,2.0,2.0,1.0); gl_PointSize = 0.0; return; } // 隐藏
      vColor = aColor;
      vec4 mv = modelViewMatrix * vec4(position, 1.0);
      gl_PointSize = clamp(aSize * (uSizeScale / -mv.z), 1.2, 70.0);
      vTw = 0.7 + 0.3 * sin(uTime * 0.7 + aSeed * 6.2831853);   // 闪烁
      gl_Position = projectionMatrix * mv;
    }`,
  fragmentShader: `
    varying vec3 vColor; varying float vTw;
    void main() {
      float d = length(gl_PointCoord - 0.5);
      float a = smoothstep(0.5, 0.03, d);      // 从中心 0.03 到边缘 0.5 的平滑衰减
      if (a < 0.02) discard;
      gl_FragColor = vec4(vColor * 2.3, a * vTw); // 颜色 ×2.3 = 预先"过曝"，让 bloom 有东西可抓
    }`,
})
~~~

属性缓冲（`:4869-4874`）：`position`、`aColor`(3)、`aSize`(1)、`aSeed`(1)、`aPickColor`(3)。
其中 `aPickColor` 只给拾取用（§5）。`aSize` 的来源（`:4833-4834`）：

~~~js
function ti(e, t) {                              // e=poet, t=是否名诗人
  return e.mergedInto ? 0 : (1.4 + e.clusterSize * 0.32) * (t ? 2.4 : 1);
}
~~~

颜色（`:4858-4863`）：朝代色；若在 48 人「名诗人」名单里，`lerp(#ffffff, 0.22)` 再 `×1.8`：

~~~js
l.set(d.color),
h && l.lerp(ei, 0.22).multiplyScalar(1.8);   // ei = new L("#ffffff")
~~~

> \* 名单是 `qn`（`:4134-4183`，**48 人**：屈原/宋玉/曹操/陶潜/李白/杜甫/苏轼/陆游/李清照/辛弃疾/海子/北岛/顾城…）。实测 48 个名字全部能在 `poets.index.json` 里匹配到，但**只有 47 人真正发光**——"毛泽东"是 `mergedInto: 0627eeb0` 的别名条目（poemCount=0），`ti()` 即使给它 ×2.4 也会被 `aSize=0` 隐藏。

### 3.3 诗星层 `li()` / `si()` / `oi()`：每首诗一颗星

诗人被选中时，整团诗星一次性上传（`:5154-5159`）：

~~~js
let n = ci([t], Math.max(0, t.poemCount), {
  bright: 3.4,        // 颜色乘子
  sizeScale: 860,     // 点径 = 860 / -z
  maxPx: 44,          // clamp 上限
  twinkle: !0,        // 开闪烁
});
~~~
`showAllPoems` 全量层则是（`:5131-5136`）：`bright:1.25, sizeScale:360, maxPx:11, twinkle:false`（8.7 万… 87 万点，刻意不闪、尺寸小）。

它的顶点着色器带**自转**（`:4990-5007`），因为整个星团绕诗人 Y 轴旋转，点必须跟着转，否则拾取会错位（注释原话 `// self-rotate the rest offset around the poet's Y axis (matches positions.poemPosition + the picker)`）：

~~~glsl
vec3 off0 = position - aCenter;
float ang = uTime * aOmega;                       // 每团不同角速度 ±0.018~0.068
float c = cos(ang), s = sin(ang);
vec3 wp = aCenter + vec3(off0.x*c - off0.z*s, off0.y, off0.x*s + off0.z*c);
vec4 mv = modelViewMatrix * vec4(wp, 1.0);
float flareSize = 1.0 + uFlare * 1.8;
gl_PointSize = clamp(860.0 / -mv.z, 1.0, 44.0) * flareSize;
vTw = 0.65 + 0.35 * sin(uTime * 1.7 + aSeed * 6.2831853);
vColor = aColor * 3.40 * (1.0 + uFlare * 1.4);
~~~

亮点：`uFlare` 不是常数，是**出生动画**。`li()` 的 `useFrame`（`:5179-5211`）里：

~~~js
let i = r - e.born;
i < ri                                   // ri = 0.4s 出生期
  ? (t = i / ri, n = 1 - (1 - ai) * (i / ri))   // alpha 0→1，flare 1→0.6
  : (t = 1, n = ai);                             // 稳态 flare=0.6
e.mat.uniforms.uAlpha.value = t; e.mat.uniforms.uFlare.value = n;
// 消失：outAt → 1.5s 内 alpha 线性到 0，随后 dispose() 几何与材质
~~~

**"点开一个诗人，星团像炸开一样亮一下再落定"** —— 这就是 `flare` 的全部秘密。

> **那"虚空里可能的诗"是怎么画的？答案是：不画。** 虚空中的诗只有编号、没有坐标，所以没有对应的点云。界面上只有三样东西在暗示它：① 点下去之后的 `pull` 标记（≤40 个，§3.4）；② 选中诗人时那圈 **行星指引线**（`Ci()`，`:5268`）——把该诗人最多 **20,000** 首诗的编号按 `poemIndexOf` 采样，铺成一个环/球（`guideStyle: plane | sphere`），`guideMode: flash | hold | off`，`guideSeconds` 默认 10、`guideBrightness` 0.7；③ 搜索里的"探诗"——把任意文本算成一个编号，再让相机飞过去。**"一切可能的诗"在视觉上是留白，不是资产。**

### 3.4 点虚空的反馈 `pa()`：一次点击的"涟漪"（`:5957-5978`）

~~~glsl
// vertex
float tw = 0.82 + 0.18 * sin(uTime * 3.0 + aPhase * 6.2831853);
// birth swell: a fresh pull POPS large+bright (like a nearby decoration star, so it's easy
// to spot the instant you click), then shrinks to a small quiet marker as aFlare decays.
gl_PointSize = clamp((520.0 + aFlare * 4500.0) / -mv.z, 3.5, 64.0) * tw;

// fragment
float d = length(gl_PointCoord - vec2(0.5)) * 2.0;
float core = exp(-d * d * 7.0);            // 紧的核心
float ring = smoothstep(0.95, 0.45, d) * 0.22;  // 一圈淡晕
float a = core + ring;
gl_FragColor = vec4(vColor * a, a);
~~~

`aFlare = max(0,1-(now-birth)/2.2)*3`（`:6030-6040`），所以新点上的位置会**先炸大再缩回**，2.2 s 内衰减；死亡时按 `(1-n)*(0.35+0.65*sin(n*26))` 闪烁淡出（`:6024-6028`）。颜色：`valid ? [1,.84,.4](金) : [.78,.86,1](蓝白)` —— **"是不是合律的诗"用颜色直接告诉你**。

### 3.5 赠诗边 `Vi()`：三次贝塞尔 + 沿线跑的脉冲（`:5601-5660`）

~~~js
// 控制点向原点收 0.3 → 弧线从盘面"拱"起来
Fi.lerpVectors(Ni, Pi, 0.33).lerp(Mi, Ai);   // Ai = 0.3
Ii.lerpVectors(Ni, Pi, 0.67).lerp(Mi, Ai);
// 每边 26 段（ki=26），顶点色 = 两端朝代色插值 × sin(π·t)（两端淡出）
let r = Math.sin(Math.PI * t); Bi.copy(Ri).lerp(zi, t).multiplyScalar(r);
~~~
~~~glsl
// fragment：一道亮斑沿线从"赠"流向"答"
float phase = fract(uTime * 0.16 + vSeed);
float d = vT - phase; d = d - floor(d + 0.5);   // 环形最近距离
float pulse = smoothstep(0.07, 0.0, abs(d));
vec3 col = vColor * (1.0 + pulse * 2.2);
float a = max(max(col.r, col.g), col.b);         // 没有 alpha 通道：亮度即不透明度
gl_FragColor = vec4(col, a);
~~~

### 3.6 流星 `Ha()`：头部点 + 尾部线段（`:6271-6289`）

~~~glsl
gl_PointSize = clamp(aSize / -mv.z, 1.0, 48.0);
vTw = 0.8 + 0.2 * sin(uTime * 7.0 + aSeed * 6.2831853);
// fragment：注释原文 —— soft halo identical to the poet stars (three/PoetStars.tsx) → same sky
float a = smoothstep(0.5, 0.04, d);
gl_FragColor = vec4(vColor * a * vTw, a * vTw);
~~~

三档外观参数在 `:6171-6205`（`ceremony` 最大：`flashBright 5.3, headSmall 2750, width 1.04`；`today` 次之；`past` 最弱 `2.25 / 1300 / 0.56`）。

### 3.7 辉光、色调映射、色彩空间

**Bloom 只在高画质开**（`:13349-13358`）：

~~~jsx
n === `high` && (0, G.jsx)(pt, {              // pt = EffectComposer
  children: (0, G.jsx)(gt, {                  // gt = BloomEffect
    intensity: 1.4,
    luminanceThreshold: 0.1,
    luminanceSmoothing: 0.28,
    radius: 0.85,
    mipmapBlur: !0,
  }),
})
~~~

- `luminanceThreshold: 0.1` 极低 —— 几乎**所有星点都参与泛光**；这正是 `vColor*2.3` 存在的理由（不先过曝，阈值抓不到）。
- `mipmapBlur: true` + `radius 0.85` 是 postprocessing 的 mipmap 链模糊（比双 pass 高斯更便宜）。默认参数可从 `:1956-1984` 读到（`luminanceThreshold=1, intensity=1, radius=0.85, levels=8`）。
- **色调映射**：r3f 默认给 renderer 设 `toneMapping = 4`（ACESFilmic），但 `EffectComposer` 挂载时会临时改成 `0`（NoToneMapping）并在卸载时恢复（`:3014-3022`）：

~~~js
(0, K.useEffect)(() => {
  let e = h.toneMapping;      // h = gl
  return (() => { h.toneMapping = 0; })(),   // 注意：不是 Omit，是直接置 0
    () => { h.toneMapping = e; };
}, [h]);
~~~
  → **高画质=没有 tone mapping（加色直出，允许过曝到纯白），低画质=ACES**。这是刻意的：星空要"糊成一片亮"才像银河。
- 色彩空间走 r3f 默认 `outputEncoding: 3001`（sRGB）（见 `r3f-yJ-6H-4a.js` 中 `_t(E,{outputEncoding:_?3000:3001,toneMapping:v?0:4})` 片段）。
- **雾**：`<fog args={['#03040a', 2400, 13000]}>` 只对使用标准雾 chunk 的材质生效 —— 也就是远景星壳的 `PointsMaterial`（默认 `fog:true`，距离 7,200 处约 45% 融进背景色）；**自定义 ShaderMaterial 都没写雾 chunk，所以主星场不受雾影响**。雾色 = 背景色 `#03040a`，制造"远星沉进夜色"的层次。

### 3.8 一张表收走所有着色器参数

| 层 | 点径公式 | clamp | 径向衰减 | 闪烁 | 颜色加成 | 备注 |
|---|---|---|---|---|---|---|
| 背景银河 | `uSize(3) × aScale × 900/-z` | 0.6–64 | `exp(-d²·4.5)` | 无（靠 `vn()` 整层旋转 0.019 rad/s） | ×1（预乘） | 193k 点 |
| 诗人星 | `aSize × 900/-z` | **1.2–70** | `smoothstep(0.5,0.03,d)` | `0.7+0.3sin(0.7t+2π·seed)` | **×2.3** | 主力层 |
| 诗星(选中) | `860/-z ×(1+uFlare·1.8)` | 1.0–44 | `smoothstep(0.5,0.05,d)` | `0.65+0.35sin(1.7t+2π·seed)` | ×3.4(×(1+1.4uFlare)) | 出生 0.4 s |
| 诗星(全诗) | `360/-z` | 1.0–11 | 同上 | 无 | ×1.25 | 871k 点 |
| 拉取标记 | `(520+aFlare·4500)/-z` | 3.5–64 | `exp(-d²·7)+ring` | `0.82+0.18sin(3t)` | ×1 | ≤40 |
| 流星 | `aSize/-z` | 1.0–48 | `smoothstep(0.5,0.04,d)` | `0.8+0.2sin(7t)` | ×1 | 三档 |
| 远景星壳 | `PointsMaterial 16 × sizeAttenuation` | — | 贴图（128² canvas 径向渐变） | 无 | ×1 | 5.2k |


---

## 4. 相机与控制：完全自研，没有 OrbitControls

代码里**没有任何 OrbitControls / TrackballControls**（`grep OrbitControls` 在 app / three / r3f 三个包里都是 0 命中）。`Es()`（`:7179-7790`）是一个手写的五模式相机状态机 + 自研输入层。

### 4.1 初始机位与"呼吸"

~~~js
camera: { position: [700, 4600, 4600], fov: 55, near: 0.1, far: 18e3 },
onCreated: ({ camera: e }) => e.lookAt(0, 0, 0),      // :13328-13336
~~~

相机到原点 `√(700²+4600²+4600²) = 6543`，仰角约 45°，正好把半径 3,400 的盘面装进 55° 视锥（垂直半高 = 6543·tan27.5° = 3,407）。

**缓慢自转是两层不同速的（视差）**（`:3785-3802`）：

~~~js
var mn = { angle: 0, decorAngle: 0 }, hn = { t: 0 }, gn = 0.012, _n = 0.019;
function vn(e) {
  (mn.angle = (mn.angle + e * gn) % (Math.PI * 2)),          // 诗人层 0.012 rad/s ≈ 524 s/圈
  (mn.decorAngle = (mn.decorAngle + e * _n) % (Math.PI * 2)); // 背景   0.019 rad/s ≈ 331 s/圈
}
~~~

- 诗人层：`group.rotation.y = mn.angle`（`:4941`）
- 背景层：`points.rotation.y = mn.decorAngle`（`:4016`）

→ **37% 的转速差**，远景转得快、近景转得慢，静止不动时画面也有视差与纵深。这是"活着的星空"最便宜的做法。

### 4.2 五种模式（优先级从上到下，每帧只走一条分支）

| 模式 | 触发 | 相机行为 | 阻尼 |
|---|---|---|---|
| ① 电影飞行 `X.active` | 点击流星 / 认领仪式 | 沿 `Da()` 算出的弧线飞 | `1-0.0015^dt` / `1-0.0025^dt` |
| ② 锁定诗人 `lockPoetId` | 点中某颗星 | 绕星团中心轨道，`dist=min(1800, Yr*1.15+130)`；锁到单首诗 `dist=130` | `1-0.0025^dt` |
| ③ 飞向坐标 `flyTarget` | 深链 / 搜索命中 | 停在目标外 320 单位、上方 70，距离 <24 判定到达 | `1-0.0015^dt` |
| ④ 星系总览 | 默认 | 绕原点轨道，`dist∈[40, 10800]` | `1-0.0025^dt` |
| ⑤ 自由飞行 `freeMove` | 桌面默认（`freeMove: !q`） | 欧拉角 YXZ 自由飞，Q/E 滚转，WASD+空格/Shift | 同上 |

**阻尼公式（帧率无关的指数平滑，值得直接抄）**：

~~~js
let c = 1 - Math.exp(-Math.min(n, 0.05) / 0.055);   // :7567  输入积分，0.055 s 时间常数
e.position.lerp(target, 1 - 0.0025 ** n);           // :7720  位置，≈ 每 60fps 走 11%
e.quaternion.slerp(q, 1 - 0.0025 ** n);             // :7724  朝向
e.position.lerp(target, 1 - 0.0015 ** n);           // :7672  转场飞行，≈ 每帧 17%
~~~

即 **`lerp 系数 = 1 - k^dt`**（`k=0.0025` 视野/轨道，`0.0015` 转场）→ 与帧率完全无关，30fps 与 120fps 手感一致。这是全项目唯一的"缓动库"。

换算成直觉：时间常数 `τ = -1/ln(k)` ≈ **0.167 s**（`k=0.0025`）与 **0.154 s**（`k=0.0015`）；到 95% 约 `3τ ≈ 0.5 s`。也就是说**没有"动画时长"这个参数**——所有过渡都是同一条指数曲线，手感统一、可随时被打断（这比 tween 更适合可交互的相机）。

### 4.3 缩放、速度、限位

~~~js
// :7451 滚轮
if (lockPoetId || !freeMove) {
  let t = lockPoetId ? as : os;          // as = 6000（锁星）  os = 10800（总览）
  d.current.dist = Math.min(t, Math.max(ss, d.current.dist * (e.deltaY > 0 ? 1.12 : 0.89)));
  return;
}
s.current = Math.min(80, Math.max(0.1, s.current * (e.deltaY > 0 ? 0.82 : 1.22)));  // 自由飞：滚轮=调速
setSpeed(s.current);
~~~

`ss = 40`（最近）、`as = 6000`、`os = 10800`（`:7139-7143`）。速度单位是几何单位/秒，HUD 显示 `140 × speed`（`:7936`）。俯仰夹在 ±1.4 rad（约 ±80°），避免翻过极点（`:7631`）。无惯性滑行——松手即停，"软"完全来自上面那条指数平滑。

### 4.4 聚焦某位诗人时的镜头动画

没有 tween 库，全靠 lerp/slerp（`:7601-7657`）：

~~~js
let g = l + ":" + (r ?? -1);                 // 锁定键：诗人id 或 诗人id:诗序号
if (d.current.key !== g) {                   // 首次进入：用相机当前位置反解 yaw/pitch
  d.current.key = g;
  d.current.dist = r == null ? Math.min(1800, Yr(t.poemCount) * 1.15 + 130) : 130;
  let n = vs.subVectors(e.position, m), i = n.length();
  i > 1 ? (pitch = Math.asin(n.y / i), yaw = Math.atan2(n.x, n.z)) : (pitch = 0.32, yaw = 0);
}
// 之后每帧朝 (yaw,pitch,dist) 缓动 —— 所以"从任意位置转过去"是弧线而不是直线插值
~~~

举例：李白（1,051 首，星团半径 456）锁定距离 = `min(1800, 456×1.15 + 130) = 654`；此时星团张角约 `2·atan(456/654) ≈ 70°`，比 55° 视锥还大 —— **镜头是"扎进星团里"的**，你看到的是内层诗星，而不是整团。锁到某一首时 `dist = 130`，那颗诗星占屏约 `860/130 = 6.6 px`。

**电影弧线** `Da(start, end, camPos, fov, aspect, side)`（`:6120-6161`）：起终点取中点 → 求垂直方向 → 加 `+0.32` 的 y 偏置 → 按 FOV 反算距离 `(chord/2/tan(fov/2))×1.3` 并夹到 `[60, 5400]`；`side` 由相机此刻在中点哪一侧决定（`|f|<0.15` 时沿用上一帧），避免在两点之间来回翻面。

### 4.5 输入层

- 桌面：`pointerdown/move/up` + `wheel`（`passive:true`）+ `keydown`（W A S D / Space / Shift / Q / E / F / H）。
- 触屏：双指距离比 `rs()` 缩放；单指轨道；两指平移 `es()`（10 px 死区、120 px 满量程）。
- **点击判定**：`pointerup` 时 `moved < (pointerType==='touch' ? 14 : 6)` 才算点击（`:7447-7449`）。
- **手势外挂**：`window.addEventListener('shiyun:gesture-*')`（`:7531-7537`）接收外部手势事件，配套一个 MediaPipe 手部追踪 HUD（`Dl/Jl`，`:12282-13260`），默认关闭（`gestureEnabled: !1`）。
- **悬停节流 70 ms**（`:7402`）：`if (performance.now() - u.current > 70)` 才做一次拾取 + 两次命中测试。

---

## 5. 拾取：这不是 raycaster，是 GPU 颜色 ID 回读

应用体里 `raycaster` 只出现在 r3f 内部那套（未被使用）。真正的拾取在 `Kr()`（`:4603-4748`）：**离屏渲染 + 颜色编码 + 像素回读**。

### 5.1 ID 编码

~~~js
// :4572 诗人：id = 序号+1，24 位 RGB
function Br(e) { let t = e + 1; return [(t & 255)/255, ((t >> 8) & 255)/255, ((t >> 16) & 255)/255]; }
// :4576 诗：整体加 2^23 偏移，与诗人编号不冲突
var Vr = 8388608;
function Hr(e) { let t = Vr + e; return [(t & 255)/255, ((t >> 8) & 255)/255, ((t >> 16) & 255)/255]; }
~~~

`2^23 = 8,388,608` 正好是 24 位颜色的一半：**红色分量 <128 是诗人，≥128 是诗**。回读后（`:4727-4738`）：

~~~js
let A = k?.id ?? 0;
if (A <= 0) return null;                                  // 全黑 = 虚空
if (A >= 8388608) return poemLayer.resolve(A - 8388608);  // 诗 → {poet, poemIdx}
let j = A - 1;
return j >= 0 && j < poets.length ? { kind: "poet", poet: poets[j] } : null;
~~~

### 5.2 为什么不用 raycaster：点大小 ≠ 拾取范围

可点区域必须**等于屏幕上看到的光斑**，而 raycaster 对 Points 只测点中心。于是同一批点被**纯色重绘一遍**，且拾取 shader 的尺寸公式与显示 shader **完全相同**（注释原文 `// SAME apparent size as the visual star`，`:4617`）。

### 5.3 一次拾取的完整流程（伪代码）

~~~text
pick(sx, sy, allowPoem, radiusOverride):
  dpr   = gl.getPixelRatio()                      // 1 ~ 2
  W,H   = gl.getDrawingBufferSize()               // 设备像素
  gate  = 4.4 * dpr                               // ★ 只有"看起来 ≥4.4 CSS px"的星才可点
  R     = max(2, round((radiusOverride ?? (coarsePointer ? 14 : 8)) * dpr))
  C     = 2R + 1                                  // 只渲染 C×C 的小窗
  RT.setSize(C, C)                                // NearestFilter, 带 depthBuffer, 无 stencil
  group.rotation.y = galaxyAngle                  // ★ 与显示层同一个旋转角，否则点歪
  if allowPoem and poemLayer:
      poemPick.geometry = poemLayer.geometry      // 复用同一份顶点缓冲
      uScale = poemLayer.sizeScale; uMax = poemLayer.maxPx
      uGate  = min(gate, 3*dpr); uTime = clock; visible = true
  camera.setViewOffset(W, H, floor(sx*dpr) - R, floor(sy*dpr) - R, C, C)  // ★ 视口偏移代替重设相机
  gl.setRenderTarget(RT); gl.setClearColor(0x000000, 0); gl.clear(true, true, false)
  gl.render(pickScene, camera)                    // 场景里只有拾取点 + 拾取材质
  gl.readRenderTargetPixels(RT, 0, 0, C, C, buf)  // ← 全项目唯一一次 GPU→CPU 回读
  camera.clearViewOffset(); 恢复 renderTarget / clearColor
  id = nearestNonZeroRGB(buf, C, R)               // Gr()：以点击点为圆心找最近的非零点
  if id == 0: return null                         // ← 虚空
  return id >= 2^23 ? poem(id - 2^23) : poet(id - 1)
~~~

四个可移植的经验：

1. **`setViewOffset` 做局部渲染**：不重建相机、不改投影，只把 1×1 的 RT 放大成 `(2R+1)²` 的窗口（默认 8 CSS px，触屏 14 CSS px，再乘 DPR）。一次拾取只画 17²~57² 像素。
2. **`Gr()` 找最近非零点**（`:4588-4602`）：点到光斑边缘外几像素也能命中，容差就是 R。
3. **返回的 `p` 是吸附后的屏幕位置**（`:4731`），不是点击点 —— 提示框因此钉在**星**上，而不是手指上。
4. **`uGate` 是整个设计的灵魂**（`:4618-4620`，注释原文）：

~~~glsl
// gate: only deliberately-resolved stars are clickable, so the void between them stays
// pull-able (matches the old apparent-size>=2.2 CSS-px gate). uGate is in drawing-buffer px.
if (sz < uGate) { gl_Position = vec4(2.0, 2.0, 2.0, 1.0); gl_PointSize = 0.0; return; }
~~~

→ **远到看不清的星不可点，于是"星与星之间的黑"永远是虚空**。否则 32,654 个信标会把天空占满，"点虚空捞诗"就不存在了。**这是用交互规则保住的叙事设计**，不是性能妥协。

5. 诗层拾取用 `uClickBoost = 2.8`（`:4648 / :4665`）把**可点圆盘**放大到接近"带 flare 的可见行星"，但 gate 仍按未放大的尺寸判定 —— 可点区域变大，却不会抢占虚空。

### 5.4 点虚空：坐标 → 编号空间 → 一首诗

`ee()`（`:7295-7309`）是唯一的点击出口：

~~~js
let i = v(e, t, !0, n),                                     // ① GPU 拾取（允许诗层）
    a = J.getState().giftHoverId,
    o = i ? null : ((a ? cr(a) ?? null : null) ?? T(e, t));  // ② 没拾到 → 试赠诗边（16 段贝塞尔采样 + 22px 容差）
if (i?.kind === "poet") { selectPoet(i.poet); lockPoet(i.poet.id); Zo(i.poet.id); }
else if (i?.kind === "poem") {
  let { poet: e, poemIdx: t } = i;
  selectPoet(e, { poemIdx: t, title: "", firstLine: "" });
  lockPoem(e.id, t); Zo(e.id); pulseAt(Qr(e, t), !0);
} else o ? (hopToPoet(o), Zo(o.id))
        : O(e, t);                                          // ★ 点虚空
~~~

`O()`（`:7276-7294`）：

~~~js
if (!allowRandomPoem) { lockPoetId && unlock(); return; }
let i = ndc(x, y);                                  // 屏幕 → NDC
l.current.setFromCamera(i, e);                      // 一条射线
let a = l.current.ray.origin.clone()
          .addScaledVector(l.current.ray.direction, 260);   // ★ 固定深度 260
let [s, c] = bn(a.x, a.z);                          // 按星系自转角反旋 → 星系静止系坐标
selectPoem(Bo(form, [s, a.y, c], {
  lushiOnly: lushiFilter,
  commonK: commonOnly ? Eo : Do,
}));
~~~

**固定深度 260** 是关键：像素不会因为点得远而"更准"，而是**一个屏幕像素对应固定的世界步长** —— "同一个点永远同一首"因此成立。`bn()` 是 `yn()` 的逆旋转（`:3809-3814`），保证**星系在转，但虚空里的诗不跟着转**。

### 5.5 虚空 → 诗：三段函数

~~~js
function Bo(e, t, n = {}) {                 // :7002  e=诗体, t=[x,y,z]
  if (e === "ziyou") {                      // 自由诗：30 字，1/6 概率插换行（换行 = 索引 N）
    let e = Bn().lexicon.N;
    return wo(zo(t, Oo /*30*/, n.commonK ? Math.min(n.commonK, e) : e, e), t);
  }
  let r = Ua[e];                            // {wujue:4行5字, qijue:4×7, wulu:8×5, qilu:8×7}
  if (n.lushiOnly) {                        // ★ 格律模式：直接在"合平仄押韵"的枚举空间里解码
    let e = n.commonK ? Ao(n.commonK) : Bn().lexicon,
        i = to(e, r);                       // 该格律的总组合数（BigInt）
    if (i > 0n) return Co(r, io(e, r, So(t, i)).chars, t);
  }
  let i = n.commonK ? Math.min(n.commonK, Bn().lexicon.N) : Number(ho());  // 取字空间大小
  return Co(r, Ro(t, r.L, i), t);           // ① 坐标→种子 ② 种子→20 字 ③ 组装成诗
}
~~~

**空间哈希 `So()`（`:6869-6879`）—— "虚空 = 一切可能的诗"的数学核心**：

~~~js
function So(e, t) {                        // e=[x,y,z], t=模数
  let n = (e) => BigInt(Math.round(e * 16)),                     // ① 量化到 1/16 单位
    r = ((n(e[0]) * 73856093n) ^ (n(e[1]) * 19349663n)
         ^ (n(e[2]) * 83492791n)) & fo,                          // ② 空间哈希三素数异或（& 2^64-1）
    i = 0n, a = bo(t) + 16, o = 0n;                              // ③ 按模数位数决定展开几块
  for (; a > 0; ) (i = (i << 64n) | xo(r ^ (o++ * 1099511628211n))), (a -= 64);
                                                                 // ④ splitmix64 逐块混合，FNV 素数链接
  return i % t;                                                  // ⑤ 落到 [0, t)
}
~~~

**取字 `Ro()`（`:6987-6993`）**：`seed = So(pos, 2^31-1)` → mulberry32 → 按**类 Zipf 累积分布**取 L 个字：

~~~js
function Po(e) {                           // :6958  权重 1/(i+350)^1.15 的累积分布
  let t = new Float64Array(e), n = 0;
  for (let r = 0; r < e; r++) (n += 1 / (r + Mo) ** +jo), (t[r] = n);   // Mo = 350, jo = 1.15
  for (let r = 0; r < e; r++) t[r] /= n;
  return t;
}
function Ro(e, t, n) { let r = Io(Lo(e)), i = Po(n), a = Array(t);
  for (let e = 0; e < t; e++) a[e] = Fo(i, r()); return a; }
~~~

这个权重很"平"（首字 vs 末字只差约 `(22218+350)/(350)` 的 1.15 次方 ≈ 2.6 倍），所以**不开"常用字"过滤时，捞出来的字大多生僻**。产品用 `commonOnly` 把字库截到前 **2,500**（`Eo`）或 **3,200**（`Do`）个高频字来救（`:6916-6918`）—— 而 charset 本身就是**按频率降序**排的。实测前 40 字：

~~~text
的一不人我有风无山天来在是花日上中云何时生年如水春自月为心子里下长相得去知此地白
~~~

### 5.6 实测：从坐标到一首诗（`verify_void.py` 真实输出）

**(a) 不过滤**（全 22,219 字），坐标 `[-812.5, -120, 1134.25]`：

~~~text
So(pos, 2^31-1) = 1777200285
20 个索引前 5 个 = [4208, 722, 2431, 1828, 192]
楠凄钵鹅问 / 牣宝嘣豪辆 / 䲭桨不㷟㘩 / 列螀㔶精重
babelIndex = 163049443591567424937873751212504846122208706352472732159323358927132897158342271905310  (87 位)
~~~

**(b) 同坐标 + 常用字过滤 K=2500**：

~~~text
羞鱼停持诗 / 秘火泊美袖 / 刘枯一蟠暴 / 萧程剧岂事
~~~

**(c) 同坐标 + 格律模式**（K=2500；`io()` 从 8.19×10⁶⁰ 个「合平仄+押韵」的组合中解码。上面三首我都用独立实现逐字复核过：`toneClass[char] == pattern[i]` 全部 20 位通过，且押韵位置同韵部（3 / 21 / 16）——**这些是真的合律的五绝骨架**，只是用字按编号挑）：

~~~text
五绝合律组合数 to() = 8194910425809771359169166819398029059360071196404617587458048  (≈10^60.9)
So(pos, total)      = 215972787586737172531604650081582628216319482217417043376459
脱德誉望轴 / 陈充吏做痴 / 枝唐琼藻隐 / 影舜怅衫时      (variant 0, 韵部 3)

坐标 [0, 0, 1200]          -> 馨卷笺恰表 / 剧信乳禾塘 / 赞卫犀钿嶂 / 蹄冠阖范慷   (variant 2, 韵部 21)
坐标 [1234.5, 88, -640.75] -> 郎梨龄退綵 / 贱砚按姬料 / 虏烬梯阴著 / 灵悲鸟渺乔   (variant 2, 韵部 16)
~~~

同一点重复计算逐字相同（脚本内 `void_poem(pts[0]) == void_poem(pts[0])` → `True`）。
**诗"像不像人写的"是审美问题；机制上它是一个完备编码：坐标 ↔ 唯一诗 ↔ 唯一编号（87 位十进制）。**

### 5.7 两种拾取对照

| | 实体层（诗人 / 诗星） | 虚空层 |
|---|---|---|
| 判定 | GPU 颜色 ID 回读（离屏 17²~57² 像素） | 射线 × 固定深度 260 → 世界坐标 |
| 输入 | 屏幕像素 | 世界坐标 `(x,y,z)` |
| 映射 | 颜色 → 数组下标 → 数据 | `So()` → 编号 → 字 |
| 结果 | 已存在的诗人/诗 | **当场生成、文件里不存在的诗** |
| 可点条件 | `uGate`（视径 ≥ 4.4·dpr px） | 其余全部区域 |
| 确定性 | 是 | 是（同一世界坐标 → 同一首） |
| 成本 | 一次局部离屏渲染 + 一次回读 | 纯 CPU，微秒级 |


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
| 检索 | `cc()` `:9159` | `tab(poet\|poem\|probe\|dynasty), q, results, aliasNote, form, hidden` | 4 tab；"探诗"= 把任意文本算成虚空编号（`qo/Yo`）；"编号反查"= `Xo(idx)` 反解；朝代 tab 控制 `hidden` |
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
| 能力门 | 入口先探 `BigInt` 与 `getContext('webgl2')\|\|('webgl')`，不满足则不挂 React，直接出中文提示 | `index.html` capability gate |

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


---

## 8. ★ 为什么它看起来像星空：用数据说话

这一节回答"同样是一堆点，为什么它不是随机尘埃"。全部数字来自 `verify_screen2.py` / `verify_geometry.py` 对**真实 `poets.index.json`** 的复算，机位取默认 `(700,4600,4600)`、`fov 55`、1920×1080。

### 8.1 默认视角的实测统计

| 观测量 | 实测值 | 它意味着什么 |
|---|---|---|
| 视锥内星团 | **32,405 / 32,654（99.2%）** | 默认机位几乎整盘可见，一屏装下全部诗人 |
| 屏幕平均密度 | **1 颗 / 64 px²** | 1080p 下 3.2 万颗 |
| 同屏最近邻距离 | **p50 = 1.9 px，p90 = 4.7 px** | 密集处**大量重叠**——这是"银河带"的来源 |
| 点径（含 clamp） | **97.2% 被夹到 1.2 px**；p99 = 1.77 px；max = 4.45 px | 远景下尺寸几乎恒定 |
| 星团亮度 `aSize` | min 2.49 / p50 **2.67** / p90 4.45 / p99 12.59 / max **49.44** | **18 倍长尾**，少量"主星" |
| 星团投影半径 | p50 **7.8 px** / p90 15.4 / p99 47.7 / max 210 | 星团在屏幕上确实"有大小" |
| `\|y\|/r` 厚度 | 中位 **0.078** | 薄盘，不是球 |
| 四臂对称 `\|F4(θ)\|` | **0.246**（扣除螺旋相位后 **0.325**） | 有臂，但不超过"半清晰" |
| 中心 240 px 内星团数 | 7,287 | 核球确实更密 |

> **结论 1：远景下"尺寸"几乎不参与构图。** 97.2% 的点都是 1.2 px；明暗差别来自**重叠数量**（加色叠加），而不是单点大小。随机尘埃之所以"平"，是因为它每颗都一样亮、还不重叠。
>
> **结论 2：近邻 1.9 px 意味着强重叠。** 1 颗/64 px² 的平均密度看似稀疏，但四臂 + 朝代带把点压进了条带，条带内的实际密度是平均值的几倍 → 1.2 px 的点叠出连续的亮带。**"银河"是叠加产物，不是贴图。**

### 8.2 四臂螺旋的量化证据

把每个诗人的极角 θ 减去螺旋相位 `5.2·r/R`，再对 90° 周期取模，直方图（8 个桶）：

~~~text
φ 直方图（均匀=0.125）:
[0.212, 0.129, 0.082, 0.060, 0.066, 0.093, 0.141, 0.216]
  ↑ 臂中心                        臂间空隙                        ↑ 臂中心(回绕)
~~~

臂中心密度是均匀值的 **1.7 倍**，臂间只有 **0.48 倍**，对比度约 **3.5:1**。
进一步看：无相位修正时 `|F4|=0.246`，扣除 `5.2·r/R` 后升到 **0.325** —— 说明"扭转"这个行为确实存在（如果不扭转，两个数会一样）。

**臂宽**：`ARM_SPREAD=0.42` rad 的三角噪声 ×0.45 → 臂的标准差约 `0.09` rad ≈ **±5°**（外盘）；内盘（r<0.5R）额外加 `(d-0.5)·2π·f` 的均匀散布（f 最大 1），把核球彻底打散成"团"。**这就是"外盘有臂、中心成团"的机制，一条公式两个效果。**

### 8.3 径向密度剖面 = 一部文学史

按 200 单位分环，统计每环面密度（`verify_screen2.py` 输出）：

~~~text
r=[ 400, 600)   5.3e-05    先秦/秦汉（人少）
r=[1400,1600)   9.7e-04    唐
r=[1800,2000)   1.42e-03   ★ 峰 1：宋（9,495 人）
r=[2200,2400)   6.9e-04    金/元（谷）
r=[2600,2800)   1.02e-03    明
r=[2800,3000)   1.07e-03   ★ 峰 2：清（8,980 人）
r=[3400,3600)   2.9e-04    外缘衰减
~~~

**密度不是均匀的，也不是单调递减的，而是有两个峰。** 峰的位置恰好是宋与清 —— 因为"朝代 → 半径"、"该朝代诗人数 → 密度"。于是**观感上像"星系有两个旋臂核"，本质上是语料库的历史分布**。这是本项目最巧的一处设计：**用一个天文隐喻装下了一个不均匀的真实数据集**，既好看又诚实。

同时，由于每带的抖动 σ≈149 > 带宽 198.7 的一半，15 条带互相重叠，**看不出"15 个同心圆环"的机械感**（这一点用 python 抽查间隙数量即可验证；实测径向直方图没有一个空环）。

### 8.4 星团：面积正比于诗数

`Yr(n) = 35 + 13√n`（封顶 3000）：

| 诗数 n | 星团半径 Yr | 面积/首 |
|---|---|---|
| 1 | 48 | 7,238 |
| 100 | 165 | 855 |
| 1,000 | 446 | **625** |
| 9,612 | 1,310 | **560** |
| 20,000 | 1,874 | **551** |

→ **大星团和小星团"看起来一样密"**，只是大小不同。这是"星团像星团、不像一团随机点"的关键（随机点集的局部密度方差要大得多）。

### 8.5 颜色与视差

- **按半径做色温**：核 `#fff1d6`（暖）→ `#fff7ec` → `#ffffff` → 外缘 `#cfe0ff`（冷），臂上的星再往蓝压 45%（`:3909-3914`）。
- **4% 的"红巨星"**：`#ff6d92`，只出现在臂上且 `ρ>0.55` 的区域（`:3904`）。
- **朝代色**：15 个朝代各自一个色相（先秦 `#2fd6cf` … 清 `#ff8c5a`、当代 `#d96fb0`），诗人星点直接用它（`:3109-3275`）。
- **两层视差**：背景 0.019 rad/s、诗人层 0.012 rad/s（§4.1）。

### 8.6 「随机球状尘埃」 vs 「本实现」对照表

| 维度 | 随机球状尘埃（用户现状） | 诗云（本实现） |
|---|---|---|
| 半径分布 | 均匀球 → 投影后中心密、边缘硬 | 三角分布叠加朝代带 → **平滑衰减 + 双峰** |
| 竖向厚度 | 与半径同尺度（球） | **0.11R 薄盘**，核球再 ×3.6 鼓包 |
| 角向 | 各向同性 | **4 臂 + 5.2 rad 扭转**，内盘额外打散 |
| 团簇 | 无 | 每位诗人一个 **Fibonacci 球**，面积 ∝ 诗数 |
| 亮度 | 全同 | **18 倍长尾**，名诗人再 ×2.4 |
| 点径 | 全同 | 1.2–70 px，远景**统一夹到 1.2 px** |
| 颜色 | 单色 | 半径色温 + 朝代色 + 稀有红巨星 |
| 视差 | 无 | 两层自转差 **37%** |
| 辉光 | 无 / 贴图 | 加色累积 + threshold 0.1 的 **mipmap bloom** |
| 拾取 | 无 | GPU 颜色 ID + **可点门限**（保虚空） |

---

## 9. 给《杜诗星海》（Canvas 2D，1468 首杜甫诗）的移植清单

> 前提：单文件 HTML、纯 Canvas 2D、1468 颗星。你不需要 three.js，下面每一条都能用 `ctx` 实现。

### 9.1 先搬参数（数值表）

| 参数 | 诗云的值 | 你的项目建议 |
|---|---|---|
| 焦距常数 | `900`（**硬编码，不随视口变化**） | `focal = h / (2·tan(fov/2))`，h = 画布高 |
| 点径 | `clamp(size · 900/z, 1.2, 70)` | 同式；**下限 1.0~1.2 px，上限 ≤ 64 px** |
| 尺寸公式 | `size = (1.4 + clusterSize·0.32)·(名诗人 2.4)` | `size = 1.4 + 0.32·k`，k 用"该组的诗数开方"归一 |
| 径向衰减 | `exp(-d²·4.5)`（背景） / `smoothstep(.5,.03,d)`（星） | 统一用 `1 - t²` 或 `exp(-t²·4.5)`（见 9.3 的精灵） |
| 叠加 | `globalCompositeOperation='lighter'` | 同一个 API |
| 星团半径 | `35 + 13√n` | `R = 40 + 11·√n`（n=1468 → 461 单位，按你的世界尺度缩放） |
| 盘厚 | 半径的 **11%** | 10–12%，**不要用球** |
| 臂数 | 4 | 4（或 3），扭转 5.2 rad ≈ 298° |
| 臂宽 | ±5°（外盘） | 外盘 ±6°，内盘 ±90° 打散 |
| 核球散布 | r<0.45R 时厚度 ×1~3.6 | 同 |
| 自转 | 两层 0.012 / 0.019 rad/s | 前景 1.0、背景 1.6 的倍率即可 |
| 亮度长尾 | 18 倍（2.49→49.44） | 目标 **10–20 倍**；p50 附近占 70% |
| 屏幕密度 | 1 颗 / 64 px²；同屏 NN 1.9 px | 1440p 下约 4.5 万"点当量"（可用背景尘埃补足） |
| 闪烁 | `0.7+0.3·sin(0.7t+2π·seed)` | 同一公式，只对最亮的 5% 点做（省性能） |

> **一个要注意的坑**：诗云的 `900` 是硬编码常数，**不随窗口高度变化**——4K 屏上星点会偏小、竖屏手机上偏大。移植时建议换成 `focal = h / (2·tan(fov/2))`（h = 画布高度），让星点占屏比例与分辨率无关；否则同一份密度参数在别的屏幕上会变成另一种观感。

### 9.2 关键认知：加色混合是"与顺序无关"的

`lighter` 满足交换律 → **点云完全不需要按 z 排序**。这是 Canvas 2D 做星海最大的解放：不用每帧排 1468 个对象，直接一次性绘制即可。three.js 那边之所以全部 `depthWrite:false + additive`，就是这个原因。

### 9.3 精灵与"辉光"的正确做法（别用 shadowBlur）

Canvas 2D 逐点 `shadowBlur` 是性能杀手；`createRadialGradient` 每帧新建也会卡。**正确做法：预渲染有限几档精灵，之后只 `drawImage`**。诗云的 128² 精灵就是你该抄的那个（`An()`，`:4022-4038`）：

~~~js
function makeSprite(px, rgb = '255,255,255') {
  const c = document.createElement('canvas'); c.width = c.height = px;
  const g = c.getContext('2d');
  const r = px / 2;
  const grad = g.createRadialGradient(r, r, 0, r, r, r);
  grad.addColorStop(0.00, `rgba(${rgb},0.95)`);   // 核心
  grad.addColorStop(0.18, `rgba(${rgb},0.38)`);   // 内晕
  grad.addColorStop(0.45, `rgba(${rgb},0.09)`);   // 外晕
  grad.addColorStop(1.00, `rgba(${rgb},0)`);      // 收干净
  g.fillStyle = grad; g.fillRect(0, 0, px, px);
  return c;
}
// 预生成：SIZES = [4,8,12,16,24,32,48,64] × 颜色（朝代/色温）→ 一个 Map
~~~

绘制时把 `px` **量化到最近的档**（`Math.round`→查表），可把 `drawImage` 的状态切换降到最少：

~~~js
ctx.globalCompositeOperation = 'lighter';
for (const s of stars) {
  if (s.z <= near) continue;
  const px = Math.max(1.2, Math.min(64, s.size * focal / s.z));
  const sprite = spriteFor(quantize(px), s.tint);   // 查表
  const d = px;                                    // 精灵边长 = 点径
  ctx.drawImage(sprite, s.sx - d/2, s.sy - d/2, d, d);
}
~~~

> 注意：`drawImage` 缩放到 1.2 px 时浏览器会做一次双线性缩小，等效于"亮度打折"——**这正是诗云里 97% 的点"很淡"的物理原因**，也是你想要的。

### 9.4 一层"假 bloom"（Canvas 2D 也能做，且很便宜）

~~~js
// 星层先画到 sceneCanvas；
// 再把 sceneCanvas 缩到 1/4 尺寸 + 模糊，叠回去 —— 这就是 mipmap bloom 的 Canvas 版
glowCtx.clearRect(0, 0, gw, gh);
glowCtx.filter = 'blur(6px)';                 // 支持度：Chrome/Edge/Firefox/Safari 16+
glowCtx.drawImage(sceneCanvas, 0, 0, gw, gh);
ctx.globalCompositeOperation = 'lighter';
ctx.globalAlpha = 0.55;                        // 对应 Bloom intensity 1.4 的"手感"
ctx.drawImage(glowCanvas, 0, 0, w, h);
~~~

再叠加一层**中心径向渐变**（暖色、alpha 0.1~0.25、半径 ≈ 盘半径）替代"fbm 星云"：

~~~js
const core = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 1.05);
core.addColorStop(0.0, 'rgba(255,236,196,0.22)');   // #ffe9c4 / 0.24 —— 诗云的中心 Sprite
core.addColorStop(0.45,'rgba(255,220,170,0.06)');
core.addColorStop(1.0, 'rgba(255,220,170,0)');
~~~

**这就是"星云"的全部。** 诗云没有 fbm 噪声星云——`On()` 里唯一的"云"是这张 1× Sprite（`:3959-3969`，`opacity 0.24`）+ 19.3 万点的加色累积 + bloom。**先把密度做对，云会自己长出来；先画 fbm，永远像雾。**

### 9.5 1468 首杜甫诗的具体构图（直接用）

按"时间 → 半径"（诗云的核心手法）改造你的星海：

~~~text
1) 把 1468 首诗按写作年代（或编年/时期）排序，得到 t∈[0,1]
2) 半径 r = 420 + t·2300（诗云：420 + 朝代id·198.67）
   加 ±σ 的三角抖动（σ ≈ 150），让相邻时期互相重叠 → 不会出现"年轮"
3) 角度 θ = branch·(2π/4) + (r/3600)·5.2 + N(±0.19) + 内盘额外散布
4) y = 三角噪声 · r · 0.11 · 核球系数(内盘 ×1~3.6)
5) 亮度 size = (1.4 + 0.32·k)，k 由"该诗字数/名篇标记"映射，做成长尾
6) 颜色：按 r 做暖→冷（#fff1d6 → #fff → #cfe0ff），名篇/组诗用金色点缀
7) 背景再撒 20k~40k 颗"尘埃"：size 0.6~1.2px、alpha 0.08~0.2、
   其中 80% 在 r<0.4R（指数衰减），10% 在 r>1.2R 做稀薄外晕
8) 两层自转：尘埃 0.019 rad/s、诗星 0.012 rad/s
9) 相机：初始距离 6543 当量、仰角 45°、fov 55°；
   缩放范围 dist∈[40, 10800]；鼠标拖动改 yaw/pitch（±1.4）；
   lerp 系数 = 1 - 0.0025^dt
10) 交互：点星 → 锁到该星、dist = min(1800, R·1.15 + 130)、诗卡；
    点空白 → "捞诗"（可以复用你的编号/随机诗逻辑，但**必须是确定性的**）
~~~

一个具体的簇方案（把 1468 首分成看得见的"星团"）：
- 按体裁分 4 团（五律/七律/古体/绝句），团心沿臂放 4 个点，团半径 `35+13√n`；
- 团内用 **Fibonacci 球**（黄金角 2.39996）：`y=1-2(i+0.5)/n, r=√(1-y²), θ=i·2.39996` → 均匀、无空洞、无重叠堆积；
- 团整体绕团心 Y 轴慢转（±0.018~0.068 rad/s，方向由哈希定）——静止时也有"活"的感觉。

### 9.6 顺手能修的三个体验点

1. **可点门限（uGate）**：只让"屏幕视径 ≥ 4~5 px"的星可点，其余交给"点空白 = 捞诗"。否则星一多，空白被吃光。
2. **悬停节流 70 ms**，别在 `pointermove` 里做重活。
3. **留影模式**：隐藏 UI + 只留诗句 + 可调字号/文字色 —— 比"生成分享图"便宜得多，用户也更愿意截图。

### 9.7 不要抄的地方

- **手势识别模块**（`Dl/Jl`，1,000+ 行）：与本项目无关，且默认关闭。
- **871,268 点的"全诗层"**：WebGL 都要靠 `maxPx=11` + 不闪烁才扛得住；Canvas 2D 不要尝试。
- **32,654 点的默认全景**：Canvas 2D 若要同密度，应该用"1.2 px 预渲染精灵 + 最多 2 万点 + 静态缓存"（视野不动时复用上一帧，只重绘变化的层）。

---

## 附录 A · 数据核对

| 项 | 代码/数据 | 实测 | 结论 |
|---|---|---|---|
| 诗人数 | `manifest.poetCount` = 32654 | `poets.index` 33,458 − 804 merged = **32,654** | ✅ 一致（merged 是别名条目，`aSize=0` 隐藏） |
| 诗数 | `manifest.poemCount` = 871268 | `sum(poemCount)` = **871,268** | ✅ 一致 |
| 字库 | `charset.n` = 22219, hash `a9cde1f2` | `lexicon.n` = 22219 | ✅ |
| 编号空间 | `Wa(N, 20 字)` | `22219²⁰ = 10^86.9` | "数十位"成立（实测 85–87 位十进制） |
| 诗人层点数 | `sr()` 长度 | 33,458（含 804 隐藏） | 代码注释与实测一致 |
| 亮度上限 | `clusterSize` 上限 60 | `1.4+60×0.32 = 20.6`；×2.4 = **49.44** | 陆游就是 49.44 |

**发现的两处文案不一致**（不是 bug，但值得知道）：

1. `index.html` 的 OG/description 和加载页都写 **32,657 位诗人**（`:13442` 与 `index.html`），而实际是 **32,654**。
2. 画质按钮的 title 写"高=16 万粒子"（`:7895`），实际 high 档背景是 **193,000**（120k+9k+64k），加 5,200 远景 = 198,200。

## 附录 B · 证据索引（文件:行 → 内容）

| 位置 | 内容 |
|---|---|
| `pretty/index.js:3109-3275` | 15 个朝代的色/权重/年代 |
| `:3276-3283` | `Tt/Et/Dt/Ot/kt()`：朝代 → 半径带 |
| `:3284-3289` | FNV-1a 哈希 `At()` |
| `:3290-3298` | 触屏 `q`、弱设备 `jt()`、`Mt` |
| `:3519-3597` | zustand 初始状态（含 `showAllPoems:!1`、`freeMove:!q`） |
| `:3785-3802` | 星系常数 `Y`、两层自转角 `mn/gn/_n/vn` |
| `:3815-3824` | mulberry32 `xn()`（种子 31337） |
| `:3825-3841` | 值噪声 `Sn()` |
| `:3847-4020` | 背景银河 `On()`（193k/69.5k，含 shader 与亮度分层） |
| `:4022-4038` | 程序化星点精灵 `An()`（128²，4 个色标） |
| `:4561-4748` | GPU 颜色 ID 拾取 `Br/Hr/Kr/Gr`（含 `uGate` 注释） |
| `:4749-4798` | 诗人坐标 `qr()` |
| `:4799-4830` | 黄金角、星团半径 `Yr()`、自转 `Xr()`、团内位置 `Zr()`、世界坐标 `Qr()` |
| `:4833-4835` | 亮度 `ti()`（merged→0，名诗人 ×2.4） |
| `:4836-4976` | 诗人星层 `ni()`（含 shader、朝代色、拾取注册） |
| `:4977-5214` | 诗星层 `oi/si/ci/li`（尺寸 860/44、360/11，出生 0.4 s、消失 1.5 s） |
| `:5268-5400+` | 行星指引线 `Ci()` |
| `:5565-5660` | 赠诗边 `Vi()`（贝塞尔 26 段 + 脉冲 shader） |
| `:5900-6051` | 拉取标记 `pa()`（`520+4500·flare`、金/蓝白） |
| `:6104-6161` | 电影相机状态 `X` 与弧线 `Da()` |
| `:6869-6879` | 空间哈希 `So()`（虚空 ↔ 编号） |
| `:6880-6912` | `Co()/wo()`：组装诗对象（babelIndex/lines/valid） |
| `:6958-7015` | Zipf 权重 `Po()`、取字 `Ro/zo`、入口 `Bo()` |
| `:7002-7015` | `Bo()`：格律/自由 两条生成路径 |
| `:7139-7143` | 相机距离限位 `is/as/os/ss/cs` |
| `:7179-7790` | `Es()`：输入层 + 五模式相机状态机 |
| `:7601-7726` | 锁定/飞行/总览的具体缓动 |
| `:7802-7945` | HUD `Os()` |
| `:7946-8055` | 深链 `ks/As/js/Ms/Ns`、复制/分享 |
| `:8056-8396` | 诗卡 `Vs()` |
| `:8477-8780` | 诗人面板 `Js()` |
| `:8781+` | 别名表 `Ys` |
| `:9159-9788` | 检索 `cc()`（4 tab） |
| `:9794-10113` | 赠诗漫游 `fc()` |
| `:10248-10280` | 引导键 `shiyun_onboarded_v3` / 重放事件 |
| `:10281-10420` | 引导 `Ac()` 三步 |
| `:10771-11260` | 设置 `Ic()`（6 组） |
| `:11321-11683` | 留影 `Kc()` |
| `:12655-13259` | 手势 HUD `Jl()` |
| `:13260-13449` | `Yl` DPR 上限、`Xl()` 根组件（Canvas 参数、层挂载、Bloom 参数） |
| `index.html` | 能力门（BigInt/WebGL）、OG 静态图、`og:description` 的 32,657 |

## 附录 C · 本文未覆盖 / 存疑

- **没有跑真实浏览器截图**：所有视觉结论都由代码 + 数据复算得出；若要视觉核对，建议在 1920×1080 下截首屏，与 §8.1 的数字对照。
- **`clusterSize` 的生成公式**：数据里已预计算，实测它与 `poemCount` 强相关但**不是**简单的 `1.57√n`（n=1→3.0，n=28→9.41，n=138→18.45，n=1051→47.39，上限 60）。不影响渲染结论（渲染只读它）。
- **`@react-three/postprocessing` 的 EffectPass 内部**是否再插一层 tone mapping：代码里只看到 `gl.toneMapping=0` 的临时置位（`:3014-3022`）与 `BloomEffect` 的参数；vendor 内部细节未逐行核对。
- 手势识别模块（MediaPipe）只按 UI 与状态变量做了概述，未做算法级逆向（与本报告主题无关）。

---

*报告由 render-ui 产出；所有数值可被 `render-ui/verify_*.py` 复现。原始站点位于 <https://shiyun.cohenjikan.com>，制品快照在 `work/rea/shiyun/{site,data}`。*
