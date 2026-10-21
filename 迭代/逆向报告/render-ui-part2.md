
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

**(c) 同坐标 + 格律模式**（K=2500；`io()` 从 7.67×10⁶⁰ 个合律组合中解码，并已核验平水韵平仄+押韵通过）：

~~~text
五绝合律组合数 to() = 7666921794634597686673162278027362668753772565759779223896064  (≈10^60.9)
So(pos, total) = 3739618093945689268283583512720961663500241397954082332506443
脱德誉望旋 / 巡篱子径怜 / 头昆漂否遂 / 许浊避鸠烟
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

