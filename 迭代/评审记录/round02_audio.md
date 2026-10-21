# 声音设计（声音层 / 交互耦合 / 与气质匹配）· 第 2 轮评审

**评审对象**：`杜诗星海.html`（2026-10-20 13:16:58 构建，5,972,357 B，sha256 `a3342eaf…`，交付 zip 与根单文件哈希一致）＋源码 `web/index.html`（13:22；其中声音段与构建内联段**逐字节一致**，已比对）。
**口径**：Edge headless 1920×1080 / 1366×768 实拍 6 张（参数按任务书）；电平用 OfflineAudioContext 按构建里的节点参数离线复刻（`评审/audio_r02/_offline_mix.html`、`_offline2.html`、`_offline3.html`）；页面状态用 CDP 实时读取（探针副本只加了一行 `window.__AUD=AUD`，不改任何行为）。
**注意**：13:16 构建之后源码在 13:22 又改过一次，构建尚未重打；下面是构建的实测值。

总分：**47 / 100**
与上轮差：**+12（上轮 35）**

| 维度 | 上轮 | 本轮 | 依据 |
|---|---:|---:|---|
| 声音层的存在与交付（25） | 12 | **13** | 现场合成仍在；新增选诗音、开卡纸声、卷积混响、阅读 duck；但默认关、无引导、无记忆，发现率仍是 0 |
| 与作品气质（20） | 7 | **9** | 磬改成非谐分音 + 1.8s 混响，是往「青铜」走了一步；底噪一个参数没动，仍是 55Hz 正弦 pad |
| 与交互/叙事耦合（25） | 3 | **11** | 选诗真的出声（+8.5 dB），开卡有纸声，阅读停钟并压底；但 11 类交互只覆盖 1 类，声像仍是世界坐标 |
| 混音与实现质量（20） | 8 | **9** | 有混响、有 duck；但底噪 100% 能量在 200Hz 以下，选诗音比它高 8.5 dB，干路接了两遍多 5.0 dB，随机钟仍被埋 |
| 控制与可访问性（10） | 5 | **5** | 卡内多了一个声音开关、全屏可静音；仍不可键盘、aria 不更新、无记忆、命中区 35×25 |

## 这 +12 是挣来的（先认账）

1. **选诗真的有音了。** 实测选中一瞬节点 +4 osc +1 buffer（离线复刻 `audSelect`=4 个正弦、纸声=1 段 100ms 噪声）；选诗瞬间 RMS −18.3 dBFS、峰值 −9.9，比底噪高 **8.5 dB**——上一轮「每次点击都哑火」不再是事实。
2. **阅读真的 duck 了，而且停钟了。** master 0.85→0.42（离线测得 **−6.2 dB**），`audDuck(true)` 里 `clearTimeout(AUD.timer)`，读诗时不再随机落磬；全屏里 `#csound` 在 (1696,30)（1890×985 视口）、`hit=self`，点一下 `AUD.on=false`——上一轮「全屏静不了音」修好了。
3. **混响和命名。** 全文件已有 1 个 ConvolverNode（1.8s 指数衰减 IR，wet 0.35）；页脚「诗云 **伪诗**」不再和「声音」抢「白噪音」这个词（图 1）；交付 zip 与根单文件哈希一致。

![默认视角：页脚「诗云 伪诗 / 声音 关」](audio_r02/r02_01_default.png)
图 1 · 默认视角（1920×1080）。声音仍是右下角一枚 12px 灰胶囊「声音 关」，整页没有「有声」二字。

![《登高》诗卡](audio_r02/r02_02_card.png)
图 2 · 《登高》诗卡。卡头新增「声音 关」（与「全屏」并排），这是本轮唯一新增的可达入口。

![全屏阅读](audio_r02/r02_03_full.png)
图 3 · 全屏阅读（1920×1080，过渡已落定）。「声音 关」与「退出」同为金色实心——颜色不随开关状态变。

![1366 适配](audio_r02/r02_04_1366.png)
图 4 · 1366×768。声音胶囊实测 35×25 px（CDP 在 1336×673 视口下量的），比 44×44 的触控下限小一圈。

![长诗全屏](audio_r02/r02_05_long.png)
图 5 · 200 行长诗《秋日夔府咏怀…一百韵》全屏；声音开关同样在右上角。

![声音开＋全屏](audio_r02/r02_07_soundon_card.png)
图 6 · 声音开、全屏阅读（CDP 实时截取）。「声音 开」与「退出」同色实心，状态只剩 11px 的字。

## 三条问题（现在仍然最伤）

### 1. 仍然只有「知道它存在的人」听得见：默认关、无邀请、无记忆、不可键盘、命中区 35×25

- **默认与发现**：默认 `AUD.on=false`；整页 `innerText` 不含「有声／环境声」（实测 `hint_audio=false`）；loader 只写 PICKING STARS，没有任何听觉提示。首次 `pointerdown` 不建 AudioContext（实测 `had_ctx=false → ctx_after=false`）——浏览器给的那次「合规开声手势」仍然被浪费。
- **记忆**：`localStorage` 键数为 **0**（全文件也 0 处 `localStorage`），刷新即回关。
- **键盘**：`#autog` 是 `<span role="switch">`，`tabIndex=-1`，`focus()` 失败，Enter 无效（实测 `focused=false`）；`#csound` 连 `role` 都没有。
- **ARIA 是错的**：点击后 `AUD.on=true`，而 `aria-checked` 仍为 `"false"`（码里 `audToggle` 只改 `textContent`/`class`）。读屏会报告「声音，关」——比不写 ARIA 更糟。
- **命中区**：1366 视口下胶囊 35×25 px；`#au` 整组 82×27。页面上唯一的状态提示是 12px 的「开／关」两个字。
- **顺带一条设计规则**：`#card.reading .readtoggle{background:var(--gold)}` 只按 `.reading` 选择、不看 `AUD.on`，所以阅读态里「声音 关」和「退出」**同为金色实心**（图 3、图 6 对比即是证据；实测 ON 时 `rgb(201,162,39)`）。DESIGN.md §1 的硬规则是「金色只编码关系，同一屏只允许一个金色语义」，这里同一屏有两个，而且声音那枚的颜色与状态无关；页脚 `.s.on` 开时同样是实心金（实测 `rgb(201,162,39)`），只是换了个位置犯同一条规矩。

**为什么伤**：上一轮的第一原则问题原封不动。选诗音做得再对，也没人按得到；把「开声」藏在一枚 35×25 的灰胶囊里，等于交付了一个只有作者知道的图层。

### 2. 底噪一个参数没改，混音层级是反的：100% 能量在 200Hz 以下，选诗音高它 8.5 dB，环境钟只高 0.8 dB

离线复刻（44.1kHz，30s，同一组节点参数）：

| 对象 | RMS | 峰值 | 备注 |
|---|---:|---:|---|
| 底噪（3–5.5s） | −26.8 | −20.1 | 质心 **72Hz**，**100%** 能量 <200Hz |
| 选诗音 196Hz（100ms，单发） | −18.3 | −9.9 | 比底噪高 **8.5 dB** |
| 纸声（2.2kHz，100ms） | — | −9.0～−9.2（与选诗音同帧的合计峰） | 与选诗音同帧触发 |
| 随机钟 587Hz（满音量） | −26.0 | −16.2 | 只比底噪高 **0.8 dB**（峰 +3.9 dB）——仍是被埋的 |
| 阅读 duck 后 | −32.9 | −26.2 | −6.2 dB，压的是 master 总总线 |

- **底噪没改**：`audInit` 的 55/82.5/110Hz、lowpass 220、gain 0.05 与上一轮逐字相同。质心 72Hz 意味着笔记本扬声器（200Hz 以下衰减 10–20dB）上这一层基本消失——用户第一耳听到的其实只有那记 −9.9 dB 的「叮」。
- **干路接了两遍**：`audSelect` 里 `out.connect(AUD.master)` 之后又 `out.connect(AUD.dry)`（0.65）且 `dry→master`，同一信号相加。实测比只接干路响 **5.0 dB**（−9.9 → −14.9）。这是本轮新引入的实现缺陷。
- **「随画面」实测是死的**：`audFollow` 仍在改 `AUD.lp.frequency`（380–800Hz），而音源是 55/82.5/110Hz——lowpass 开到 800 只多放出一丝 triangle 的高次谐波。实测 lp 220→800：RMS **−0.4 dB**、质心仍是 72Hz；`AUD.air` 的 gain 从 0.008 拉到 0.038（4.75 倍），底噪 RMS 变化 **0.0 dB**。两个「随视角呼吸」的参数，一个电平上几乎不动，一个连 0.1 dB 都不动。
- **层级差**：底噪 −26.8 / 钟 −26.0 / 选诗 −18.3。作品里最「氛围」的那一记被埋掉，最「UI」的那一记最响——这正好是环境声设计要避免的倒挂。

**为什么伤**：这不是「音色不够古」，是**播放设备上的实际听感与设计意图相反**。在耳机里是一层嗡，在笔记本上只剩点击声；「夜」和「青铜」都留在了频谱的另一半。

### 3. 一记 196Hz 代表 1468 首诗，也代表机器伪诗；声像按世界坐标，不按屏幕

- **词汇量是 1**：`audSelect` 只在两处调用——`1815`（白噪音伪诗）与 `1839`（真诗）。两处都是 196Hz、同样 4 个分音、同样 3.4s 衰减。于是《登高》和一首机器拼出来的伪诗听起来完全一样——而这部作品最核心的对照恰恰是「机器暗、杜甫亮」。
- **声像不跟眼睛**：`audSelect(((p.dir?p.dir.x:0))*0.6)` 用的是星在**世界坐标**里的 x；相机飞过去之后星落在屏幕正中（图 2 的《登高》就在正中），声像却停在世界的左右。全库 1468 首里 **23.8% 的 |pan|>0.5**（p10 −0.513 / p90 0.519）——近四分之一的选诗，声音从屏幕一侧来，星在正中央。
- **覆盖 1/11**：全文件 `aud*` 的调用只有 `audSelect×2`、`audPaper×2`、`audDuck×2`。悬停、检索回车、着色切换、时期/图例、面板 00–04、关键词胶囊、滚轮缩放——全部无声。选诗之外，声音对叙事没有任何标记。

**为什么伤**：声音层现在有「一记音」，还没有「一套话」。它不能区分真伪、不能指向屏幕、不能标记除选诗外的任何节点；观众听到的是同一个 UI 音效，而不是这座星海在说话。

## 三条改法（都可直接落到 `web/index.html`）

### 改法 1：把「被听见」做完——真开关、记忆、首次手势、允许键盘

**(a) 换掉 span（489 行）**
```html
<button class="s" id="autog" type="button" role="switch" aria-checked="false" aria-label="环境声">关</button>
```
```css
/* 147–149 行 */
#au .s{position:relative;font:inherit;font-size:12.5px;letter-spacing:.14em;color:#a9a496;
  padding:5px 12px;cursor:pointer;border:1px solid rgba(236,231,219,.16);border-radius:1px;background:none;transition:.3s}
#au .s::after{content:"";position:absolute;inset:-9px -8px}       /* 35×25 → 51×43 命中区，不撑高页脚 */
#au .s.on{color:var(--paper);border-color:rgba(236,231,219,.55);background:none}  /* 金色留给关系 */
#au .s:focus-visible{outline:1px solid var(--paper);outline-offset:3px}
```
`#csound`（522 行）同样换成 `<button role="switch" aria-checked="false">`；删掉 264 行那条「一律金色」的规则，改成 `#card.reading #csound{border-color:rgba(236,231,219,.4);background:none;color:var(--paper)}`，让阅读态只剩「退出」一个金色语义。

**(b) audToggle（1648–1659）一次改齐：aria、两处标签、记忆、suspend**
```js
function audToggle(on){
  var c=audInit(); if(!c) return;
  AUD.on=!!on;
  if(AUD.on && c.state==='suspended') c.resume();
  var t=c.currentTime;
  AUD.master.gain.cancelScheduledValues(t);
  AUD.master.gain.linearRampToValueAtTime(AUD.on?0.85:0, t+0.45);   // 1.6s 太慢，静音要 0.45s
  if(AUD.on){ clearTimeout(AUD.timer); AUD.timer=setTimeout(audBell,2500); } else clearTimeout(AUD.timer);
  var b=document.getElementById('autog');
  if(b){ b.textContent=AUD.on?'开':'关'; b.classList.toggle('on',AUD.on);
         b.setAttribute('aria-checked',AUD.on?'true':'false'); }
  var cs=document.getElementById('csound');
  if(cs){ cs.textContent='声音 '+(AUD.on?'开':'关'); cs.setAttribute('aria-checked',AUD.on?'true':'false'); }
  try{ localStorage.setItem('dufu.snd', AUD.on?'1':'0'); }catch(e){}
  if(!AUD.on){ setTimeout(function(){ if(!AUD.on&&AUD.ctx.state==='running') AUD.ctx.suspend(); },600); }
}
```
顺手删掉 1534–1537 那个每 600ms 重写 `#csound` 的 `setInterval`（它会让标签滞后，且永远不停）。

**(c) 首次手势恢复 + 首访提示**
```js
var _sndArmed=false;
document.addEventListener('pointerdown', function(){
  if(_sndArmed) return; _sndArmed=true;
  var was=false; try{ was=localStorage.getItem('dufu.snd')==='1'; }catch(e){}
  if(was) audToggle(true);                       // 上次开过：第一次手势里 0.45s 淡入
}, {capture:true, once:true});

setTimeout(function(){                            // loader 结束 2.35s 之后
  var seen=false; try{ seen=localStorage.getItem('dufu.snd')!==null; }catch(e){}
  if(seen) return;
  var r=document.getElementById('autog').getBoundingClientRect();
  var h=document.createElement('div'); h.textContent='有声 · 点此开';
  h.style.cssText='position:fixed;left:'+(r.left-6)+'px;top:'+(r.top-24)+'px;font-size:11px;'+
    'letter-spacing:.22em;color:#6a675e;z-index:13;pointer-events:none;transition:opacity .8s';
  document.body.appendChild(h);
  setTimeout(function(){ h.style.opacity=0; setTimeout(function(){h.remove();},900); },7000);
},3900);
```
**验收**：新 profile 首访 → 7s 内看到提示；点过一次后刷新 → 第一次手势 1s 内 `AudioContext=running`；Tab 能聚焦、Enter 能开关；`aria-checked` 与 `AUD.on` 始终一致；1366 下命中区 ≥44×44。

### 改法 2：重配三条总线（底噪重新登记到 200–1000Hz，选诗音回到 −20，随机钟回到 −24）

**先修干路**（1627 行）：删掉 `out.connect(AUD.master);`，只留 `out.connect(AUD.dry)`（`dry→master` 已在 1628 行建好）与 `out.connect(AUD.conv)`。实测这一步 −5.0 dB。再给选诗音一个明确 trim（0.6 左右）复测到 **峰 −19±1**，不要凭公式——用 `_offline3.html` 改参数即可复测。

**底噪重新登记**（替换 1557–1573 的三根 55/82.5/110 正弦 + 一层 0.02 空气）：
```js
/* 低：只留耳机里的那口气 */
var sub=ctx.createGain(), lpSub=ctx.createBiquadFilter();
lpSub.type='lowpass'; lpSub.frequency.value=140; lpSub.Q.value=.7; lpSub.connect(sub); sub.connect(master);
[[55,.012],[82.5,.008]].forEach(function(p){ var o=ctx.createOscillator(); o.frequency.value=p[0];
  var g=ctx.createGain(); g.gain.value=p[1]; o.connect(g); g.connect(lpSub); o.start(); });
/* 中：夜气，笔记本能听见的那一层 */
var mid=ctx.createGain(), lpMid=ctx.createBiquadFilter();
lpMid.type='lowpass'; lpMid.frequency.value=900; lpMid.Q.value=.5; lpMid.connect(mid); mid.connect(master);
[[220,.020],[277.18,.014],[329.63,.010]].forEach(function(p){ var o=ctx.createOscillator(); o.frequency.value=p[0];
  var g=ctx.createGain(); g.gain.value=p[1]; o.connect(g); g.connect(lpMid); o.start(); });
/* 空气：同一个噪声源，抬到能听见 */
var bp=ctx.createBiquadFilter(); bp.type='bandpass'; bp.frequency.value=900; bp.Q.value=.7;
var ag=ctx.createGain(); ag.gain.value=0.10; src.connect(bp); bp.connect(ag); ag.connect(master);
AUD.airBP=bp; AUD.air=ag;                  // 两个都存下来，别再只存 gain
```
这组参数我试算过：**RMS −34.1 / 峰 −23.4 / 质心 336Hz / 24% <200Hz / 71% 在 200–1kHz**（`_offline4.html`）——从「100% 在 200Hz 以下」变成笔记本能听见的一层。

**把 audFollow 接到真的会变的参数上**（替换 1661–1676）：只保留 `bp.frequency` 与 `ag.gain`，删掉 `AUD.lp` 那两行：
```js
function audFollow(){
  if(!AUD.on||!AUD.ctx) return;
  var t=AUD.ctx.currentTime;
  var pitch01=0.5-0.5*Math.cos(cam.pitch*2);
  AUD.airBP.frequency.setTargetAtTime(500+600*pitch01, t, .5);        // 500→1100Hz
  var vis=/* 可见伪诗比例，沿用现在的循环 */;
  AUD.air.gain.setTargetAtTime(0.04+0.08*vis, t, .8);                 // 0.04→0.12
}
```
实测这组「随视角」的量：质心 **213 → 453Hz**（+240Hz），而现在是 72→72Hz（+0Hz）。

**随机钟**：9–22s 的间隔改成 20–40s，增益 ×1.6 到 **峰 −24**（现在 −16.2 只比底噪高 3.9 dB，等于没有）；或者干脆删掉——它现在听起来像通知音，不像夜色。

**总线**：master 下分 `bed`、`ambience`、`cue` 三条增益；`audDuck` 只压 bed+ambience（−8 dB），cue 不压。现在的 duck 压的是总总线，读诗时连点击音一起变轻。

### 改法 3：给声音一套语法——每首诗一记自己的音，机器伪诗「没有房间」，声像跟着点击位置

**(a) 声像用点击时的屏幕位置**（1839 行；这里 `cam` 还没被 `fly` 改，正好是用户点下去的那一帧）：
```js
var cy=Math.cos(cam.yaw), sy=Math.sin(cam.yaw);
var sx=(p.dir? p.dir.x*cy - p.dir.z*sy : 0);      // 屏幕左右（−1..1）
audSelect(Math.max(-0.6,Math.min(0.6, sx*0.55)));
```
实测当前 23.8% 的 |pan|>0.5 会因此归零——星在哪，声就在哪。

**(b) 每首诗一个音高（按意象类别取五声音阶，同类同调）**：
```js
var PENTA=[196,220,246.94,293.66,329.63];
function poemBase(p){
  var idx=D.cats.findIndex(function(c){return c.id===p.d;});
  if(idx<0){ idx=0; for(var i=0;i<p.t.length;i++) idx=(idx*31+p.t.charCodeAt(i))%5; }
  return PENTA[idx%5];
}
```
`audSelect` 增加参数 `{base:poemBase(p), dur: p.L.length>=40?5:3.4}`。

**(c) 伪诗必须听起来不一样**（1815 行）：
```js
audSelect(0, {base:146.83, dur:1.2, wet:0});   // 更低、更短、不进混响：机器没有房间
```
这一条同时兑现了 DESIGN.md 的「机器暗一档」——从视觉延伸到听觉。

**(d) 补三个最便宜的节点音**（每个 10 行以内）：悬停真诗 350ms 后一记 −36 dB 的 1.8kHz 短 tick（伪诗不响）；关键词胶囊点击时 `audPaper()` + 一记 196→262Hz 的 220ms 滑音；时期高亮时一记 1.2s 的低频涌起。做完这三处，覆盖从 1/11 到 4/11。

**验收**：同一首诗两次点击音高一致、不同类别可辨；伪诗与真诗盲听可区分；选《登高》时声像与星在屏幕上的位置误差 <0.1；悬停/关键词/时期三处都有音，且都不高于选诗音 6 dB。

## 附：证据文件

- 实拍：`audio_r02/r02_01_default.png`、`r02_02_card.png`、`r02_03_full.png`、`r02_04_1366.png`、`r02_05_long.png`、`r02_07_soundon_card.png`；局部：`crop_foot_1920.png`、`crop_foot_1366.png`、`crop_reading_toggles_off.png`、`crop_reading_toggles_on.png`。
- 电平复测脚本：`audio_r02/_offline_mix.html`（当前混音）、`_offline2.html`（lp/air/钟/干路/连点）、`_offline3.html`（修正后的 cue 与钟）、`_offline4.html`（改法 2 的底噪试算）。
- 页面状态：CDP 探针读的是 `web/_r02_probe_aud.html`（= 当前构建 + 一行 `window.__AUD=AUD`），实测默认关、`tabIndex=-1`、`aria-checked` 不更新、首次 pointerdown 不建 ctx、`#csound` 阅读态可点（`hit=self`）、`AUD.on` 可关。

## 一句总评

这一轮它终于会在你选诗时响一声了，但除了这一声，它还是同一层 55Hz 的嗡、同一记被底噪埋掉的钟、同一套没人找得到的开关——把「被听见」和「分得清」这两件事做完，它才配叫声音设计。
