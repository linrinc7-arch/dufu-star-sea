# 声音设计（是否有声音层/如何加/与作品气质是否匹配） · 第 1 轮评审

**评审对象**：`杜诗星海.html`（12:52 重新构建，5,964,400 B）＋源码 `web/index.html`
**实拍**：1920×1080，Edge headless + SwiftShader，双击 file:// 打开真实构建。图见 `audio_shots/`。
**口径说明**：12:48 第一次实拍时单文件里**完全没有声音层**；12:52 重建后才出现 WebAudio 合成层。本轮以 12:52 构建为准，并按源码同一组节点参数在 OfflineAudioContext 里复刻 26s 测了真实电平（底噪 + 6s/20s 两记磬）。

总分：**35/100**

| 维度 | 分 | 依据 |
|---|---|---|
| 声音层的存在与交付（25） | 12 | 有 WebAudio 现场合成，随单文件交付、点了就能出声（实测 AudioContext 由 0→1、state=running）；但默认关、无引导、无记忆，不点就永远无声 |
| 与作品气质的匹配（20） | 7 | 55/82.5/110Hz 正弦 pad + 纯正弦「磬」＝通用冥想/科幻音色；没有纸、墨、风、水、青铜任何材质；只对上了「夜」，没对上「杜甫」 |
| 与交互/叙事的耦合（25） | 3 | 没有一个交互 cue；唯一「随画面」的 audFollow 接在底噪低通上、量程 380–800Hz，对 55/110Hz 源近乎无效；声像是随机的，与星位无关 |
| 混音与实现质量（20） | 8 | 实测底噪 RMS −26.8 dBFS / 峰 −20，磬峰 −14，只高出 6dB 被埋；无混响、无 ducking；关闭后不 suspend |
| 控制与可访问性（10） | 5 | 11–12px 灰胶囊、无 aria/键盘、全屏阅读时被卡片盖住、刷新即回关 |

图 1 · 默认视角（页脚最右一枚「声音 关」，无任何提示）
![默认视角](audio_shots/rev_audio_default.png)

图 2 · 《登高》诗卡（金色星座亮起，声音无任何反应）
![诗卡](audio_shots/rev_audio_card.png)

图 3 · 全屏阅读（声音开关被 #card 盖住，磬仍按 9–22s 随机落下）
![全屏阅读](audio_shots/rev_audio_full.png)

图 4 · 开场 loader：3.6 秒，全静音，唯一的「合规开声手势」窗口被浪费
![开场](audio_shots/rev_audio_loader.png)

图 5 · 页脚局部：「白噪音」和「声音」并排，两个词在互相拆台
![页脚](audio_shots/rev_audio_footpick.png)

---

## 最伤的三个问题（每条带证据）

### 1. 声音是「播放器」，不是「设计」：所有交互都不发声，读诗反而被随机磬打断

- **证据（代码）**：`web/index.html:1511` 的 `audBell` 只被自己的 `setTimeout(audBell, 9000+Math.random()*13000)` 递归调用；`select()`（约 1675 行）、`card.classList.add('on')`（约 1734）、`readtoggle`（约 1833）、`sweep` 转场（约 1948）**没有一处在调 aud\***。全文件唯一与画面挂钩的只有 `audFollow`，在渲染循环里每 30 帧调一次（约 1415）。
- **证据（实拍）**：图 2 里《登高》带出一串金色星座、配图、竖排诗；图 3 里全屏双栏；两张图对应的听觉事件为零。观众点开的是一首「名篇」，耳朵听到的却和点开一颗白噪音星完全一样。
- **证据（可达性）**：实测 `#foot` z-index=12、`#card` z-index=16 —— 全屏阅读时声音开关在屏幕上**点不到**（图 3 里页脚确实消失），而磬仍会落在「万里悲秋常作客」的句读之间。
- **为什么伤**：这不是「少了一层」，是**声音在与作品抢解释权**。随机钟声把「读诗」变成「禅修背景音」，而真正的叙事节点（选中、连星、开卡、全屏、回到星海）全部哑火。

### 2. 默认关 + 找不到 + 命名撞车：绝大多数人一辈子听不到它

- **证据（实拍）**：图 5 里「声音 关」是一个 11px 标签 + 12px 灰胶囊，和「着色」「诗云 白噪音」挤在同一排；在图 1 的整片星海面前，它的视觉权重接近零。没有首次引导，loader（图 4）只在说 PICKING STARS，没有一句「有声」。
- **证据（代码）**：全文件 **0 处 `localStorage`**（实测 grep），刷新即回关；**0 处 `aria-*` / `tabindex`**，按钮不可键盘操作；`body{cursor:none}` 且胶囊没有 pointer 反馈。
- **证据（语义）**：本作的「白噪音」指 DESIGN.md §3 里 15 万首机器伪诗，不是听觉白噪声；现在「诗云 白噪音」和「声音 关」并排（图 5），用户完全可能以为「白噪音」才是音频开关。这是两个系统共用一个词。
- **为什么伤**：声音设计的第一原则是「被听见」。默认关 + 无邀请 + 无记忆，等于交付了一个**只有作者知道存在**的图层。

### 3. 音色不对、混音反了，「随画面变化」还是接错的

- **音色**：`audInit`（约 1464）是 55Hz sine + 82.5Hz sine(+6 cent) + 110Hz triangle(−9 cent) → 220Hz lowpass，标准 ambient pad；笔记本扬声器 200Hz 以下衰减严重，实际听到的多半只是一点「嗡嗡」。`audBell`（约 1493）是 f / 2.01f / 3.02f 三个**纯正弦**、12ms 起音、4.2s 指数衰减，**没有敲击瞬态、没有 ConvolverNode**（全文件 0 处）——听起来是测试音/冥想 App 提示音，不是青铜磬。
- **混音（实测）**：同一节点参数离线复刻 26s，44.1kHz：

  | 段 | RMS | 峰值 |
  |---|---|---|
  | 只有底噪（0.5–5.5s） | −26.8 dBFS | −20.0 dBFS |
  | 磬（6–7s） | −25.4 dBFS | −14.0 dBFS |
  | 磬尾（8–10s） | −26.8 dBFS | −20.1 dBFS |

  磬只比底噪高 **6 dB**，尾段 RMS 和底噪完全一样 → **底太响、磬被埋**。−26.8 RMS 对「边读诗边听」来说也偏响，安静房间里会一直有存在感。
- **耦合接错**：`audFollow()`（约 1526）改的是 `AUD.lp`（底噪 lowpass），f=380+420(0.5−0.5cos(2·pitch))；55/82.5/110Hz 的基频不变，开到 800Hz 也只是让 triangle 的高次谐波透出一点。注释写的「空气层高频」对应的是 `bp`（520Hz bandpass），它**没有被保存**（`AUD.air` 存的是 gain），也没有被调制。声像 `pan = Math.random()*1.6-0.8` 是随机的——星星在你手指底下，声音却可能在另一边。
- **实现**：关闭时只把 master 拉到 0，从不 `ctx.suspend()`；振荡器和 2s 噪声 buffer 常驻。`#au .s.on` 用金色填充——按 DESIGN.md 硬规则，金色只编码「关系」，这里直接破例。
- **为什么伤**：观众听到的第一耳是「一个低音嗡嗡 + 偶尔叮一声」，既不像夜空，也不像唐诗；而它本来最该像的，是这作品自己的「白噪音」概念。

---

## 三条改法（每条具体到怎么改）

### 改法 1：给 5 个节点配事件谱，阅读模式必须 ducking + 可静音（JS）

在 `web/index.html` 里加一个统一入口，所有 cue 都走它，音量、声像、空间一次管住（`AUD.wet` 是磬总线、`AUD.duck` 是阅读时压底的增益，都在 `audInit` 里建：`AUD.duck=createGain(); AUD.duck.gain.value=1; AUD.duck.connect(master)`，再把 `AUD.wet` 接到它）：

```js
/* 约 1524 行后：一次性事件音。select 用星位做声像，不再随机 */
function audCue(kind,o){
  if(!AUD.on||!AUD.ctx) return;
  var ctx=AUD.ctx,t=ctx.currentTime,pan=ctx.createStereoPanner();
  pan.pan.value=o&&o.pan||0;
  pan.connect(AUD.wet);                       // wet = 磬总线（接混响）
  if(kind==='select'){                        // 一记 196Hz 青铜磬，非谐分音
    var g=ctx.createGain(); g.gain.value=0;
    var f=o&&o.f||196, P=[1,2.76,5.40,8.93], A=[.085,.032,.012,.006];
    P.forEach(function(r,i){ var os=ctx.createOscillator(); os.type='sine';
      os.frequency.value=f*r; var og=ctx.createGain(); og.gain.value=A[i];
      os.connect(og); og.connect(g); os.start(t); os.stop(t+5); });
    g.gain.setValueAtTime(0,t); g.gain.linearRampToValueAtTime(1,t+.008);
    g.gain.exponentialRampToValueAtTime(.0001,t+4.8); g.connect(pan);
  }
  if(kind==='card'){                          // 开卡：90ms 纸/气摩擦
    var n=ctx.createBufferSource(), b=ctx.createBuffer(1,ctx.sampleRate*.12,ctx.sampleRate);
    var d=b.getChannelData(0); for(var i=0;i<d.length;i++) d[i]=(Math.random()*2-1)*Math.pow(1-i/d.length,2);
    n.buffer=b; var bp=ctx.createBiquadFilter(); bp.type='bandpass'; bp.frequency.value=2400; bp.Q.value=.7;
    var ng=ctx.createGain(); ng.gain.value=.02; n.connect(bp); bp.connect(ng); ng.connect(pan); n.start(t);
  }
  if(kind==='tick'){ /* 只有真诗星悬停才响；白噪音星不响，见改法 2 */ }
}
```

接入点（都要改）：
- `select(p)` 末尾：`audCue('select',{pan:(p._q?p._q.sx/W*2-1:0), f:196})`；白噪音用 `selectNoise`，给更低的 146Hz。
- `card.classList.add('on')` 之后：`audCue('card')`。
- `readtoggle.onclick`（约 1833）：进入时 `AUD.duck.gain.setTargetAtTime(.35,t,.4); clearTimeout(AUD.timer)`，退出恢复 1、重排磬；**阅读期间不落随机钟**。
- 全屏时把 `#foot` 的 z-index 提到 17，或用 `body:has(#card.reading) #foot{z-index:17}`，并只留 `#au` 一个控件（图 3 现在根本静不了音）。

### 改法 2：把「白噪音」这个已有的视觉概念直接可听化；音色换成噪声 + 青铜（JS）

别再叠三根正弦当宇宙底。改成两件事：

```js
/* 底：一层极低的滤波噪声，音量=当前可见白噪音星数；音色随相机俯仰移动带通 */
var bp2=ctx.createBiquadFilter(); bp2.type='bandpass'; bp2.frequency.value=460; bp2.Q.value=.35;
var air2=ctx.createGain(); air2.gain.value=0;
src.connect(bp2); bp2.connect(air2); air2.connect(master);   // src = audInit 里那段循环噪声
AUD.air=bp2; AUD.airG=air2;              // 之前 AUD.air 存的是 gain，bp 丢了
/* audFollow() 里（每 30 帧）只动这两个参数，别再动低噪 lowpass */
var t=AUD.ctx.currentTime;
AUD.air.frequency.setTargetAtTime(420+340*(0.5-0.5*Math.cos(cam.pitch*2)), t, .5);
AUD.airG.gain.setTargetAtTime(noiseOn?0.016*visRatio:0.003, t, .8); // visRatio=可见伪诗/9000
```

```js
/* 磬：6ms 噪声敲击 + 3.2s 卷积混响（现在一处 ConvolverNode 都没有） */
function makeIR(ctx,s){ var n=Math.floor(ctx.sampleRate*s), b=ctx.createBuffer(2,n,ctx.sampleRate);
  for(var c=0;c<2;c++){ var d=b.getChannelData(c);
    for(var i=0;i<n;i++) d[i]=(Math.random()*2-1)*Math.pow(1-i/n,3.2); } return b; }
AUD.rev=ctx.createConvolver(); AUD.rev.buffer=makeIR(ctx,3.2); AUD.rev.connect(master);
AUD.wet=ctx.createGain(); AUD.wet.connect(AUD.rev); AUD.wet.connect(master); // 干湿各一
```

配平目标（把上面实测反过来）：底噪 RMS −40±2 dBFS，磬峰 −18，差值 ≥ 20dB；磬的落点用 `pan` 对到星位，不要 `Math.random()`。

### 改法 3：默认策略、文案、CSS、可访问性（HTML/CSS/文案）

- **换词**：`<div id="au"><span class="lab">声音</span>`（约 464 行）→ `环境声`；同一排的 `诗云 白噪音` 改成 `诗云 伪诗`（或 `白噪音诗`），让「白噪音」只属于视觉概念。加 `title="环境声：现场合成，无一音频文件"`。
- **给第一屏一个合规的开声手势**：loader 结束时（约 2350ms）在底部浮一行 `轻触星海 · 有声`（11px、letter-spacing .22em、#6a675e），6s 后淡出；`document.addEventListener('pointerdown', once)` 里 `audToggle(true)`。这一次点击同时满足浏览器手势策略。
- **记住**：`localStorage.setItem('dufu.snd',AUD.on?1:0)`，下次启动在**第一次手势**里恢复（不能直接自动播放）。
- **CSS**：`#au .s.on` 不要金色填充（违反唯一金色语义），改 `background:none;color:var(--paper);border-color:rgba(201,162,39,.55)`；`#au .s{cursor:pointer}` 破一次 `cursor:none`；加 `:focus-visible{outline:1px solid var(--gold);outline-offset:3px}`。
- **可访问性**：`role="switch" aria-checked="false" tabindex="0"`，Enter/Space 切换；文案 `开/关` 之外补 `aria-label="环境声"`。
- **省电**：`audToggle(false)` 里 `AUD.ctx.suspend()`，打开再 `resume()`。

---

## 附：两条交付风险（不是声音问题，但会直接在耳朵上暴露）

1. **交付包与根目录单文件不是同一次构建**：`杜诗星海_交付.zip` 里的单文件 sha256 以 `eeec6a42…` 开头，根目录 12:52 版是 `97483923…`，两者大小也不同（5,963,958 vs 5,964,400）。声音层已经在两版里都有，但其余改动未必；交之前必须重打 zip。
2. **评审期间文件在变**：12:48 实拍时单文件没有任何声音代码，12:52 重建后才出现。任何「有声/无声」的验收结论都要带构建时间，否则会互相打架。

## 一句总评

它有声音，但还没有声音设计：一层 −27dBFS 的通用 pad、一记被底噪埋掉 6dB 的随机磬，和杜甫、和星海、和任何一次点击都没有关系；现在最划算的一步不是加音乐，是把作品自己已经写好的「白噪音」概念接到耳朵上，并让每一次选诗都有一记只属于那颗星的响。
