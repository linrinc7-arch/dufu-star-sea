/* 杜诗星海 · 生平面板
   —— 对外只挂两个函数，不依赖主文件里的任何变量：
        window.renderLifePanel()  返回整块「生平」面板的 HTML
        window.bindLifePanel(root) 面板插入 DOM 后绑事件（动效 / 悬停 / 色例）
      数据只读 window.LIFE_DATA，缺了就退回 window.META.life，再缺就退回纯文本。
      任何异常都在 try/catch 里收住，绝不把错误抛给主程序。 */
(function () {
  'use strict';

  var STYLE_ID = 'lif-style';
  var W = 1080, H = 560;                       /* 画布 */
  var PAD = { l: 104, r: 86, t: 78, b: 74 };   /* 留白：左右给标签，上下给标题与色例 */
  var COLORS = ['#e0b464', '#c4904a', '#b4664b', '#64909b', '#8a7fa6'];  /* 暖金 赭 朱 青 灰紫 */
  var ROMAN = ['壹', '贰', '叁', '肆', '伍'];
  var LAB_FS = 11.5, LAB_LS = 0.5;             /* 地名标签字号 / 字距 */
  var LAST = null;                             /* 最近一次渲染的中间结果，给 bind 用 */

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function f(n) { return Math.round(n * 10) / 10; }

  /* ---------------- 样式（全部以 lif- 前缀收在自己的命名空间里） ---------------- */
  function buildCSS() {
    var css = [];
    css.push('.lif{max-width:1080px;color:#d9d3c6}');
    css.push('.lif-kick{font-family:"Helvetica Neue",Arial,sans-serif;font-size:9.5px;letter-spacing:.36em;color:#8e897d;margin:0 0 22px}');
    css.push('.lif-head{display:flex;align-items:flex-end;gap:26px;flex-wrap:wrap;padding-bottom:20px;border-bottom:1px solid rgba(236,231,219,.09)}');
    css.push('.lif-name{font-size:clamp(26px,3.4vw,34px);line-height:1.18;letter-spacing:.30em;color:#ece7db;font-weight:400;margin:0}');
    css.push('.lif-dates{font-family:"Helvetica Neue",Arial,sans-serif;font-size:11.5px;letter-spacing:.22em;color:#a8a294;padding-bottom:7px;font-variant-numeric:tabular-nums}');
    css.push('.lif-alias{font-size:11.5px;letter-spacing:.18em;color:#a8a294;padding-bottom:7px}');
    css.push('.lif-lede{margin:26px 0 0;max-width:660px;font-size:15px;line-height:1.95;letter-spacing:.045em;color:#d9d3c6}');
    css.push('.lif-lede em{font-style:normal;color:#ece7db}');
    css.push('.lif-quote1{margin:14px 0 0;font-size:13px;line-height:1.9;letter-spacing:.12em;color:#a8a294}');

    /* 行迹图 */
    css.push('.lif-mapbox{position:relative;margin:44px 0 0}');
    css.push('.lif-map{display:block;width:100%;height:auto;overflow:visible}');
    css.push('.lif-mtitle{position:absolute;right:16px;top:10px;text-align:right;pointer-events:none;font-family:"Helvetica Neue",Arial,sans-serif;font-size:9.5px;letter-spacing:.30em;color:#8e897d;line-height:1.95;font-variant-numeric:tabular-nums}');
    css.push('.lif-mtitle b{display:block;font-weight:400;font-size:11px;letter-spacing:.26em;color:#c9c3b5}');
    css.push('.lif-legend{position:absolute;left:4px;bottom:16px;display:flex;gap:15px;flex-wrap:wrap;max-width:90%}');
    css.push('.lif-lg{display:flex;align-items:center;gap:7px;font-family:"Helvetica Neue",Arial,sans-serif;font-size:9.5px;letter-spacing:.14em;color:#a8a294;transition:color .3s;user-select:none;white-space:nowrap}');
    css.push('.lif-lg i{display:block;width:15px;height:2px;border-radius:2px;transition:width .3s cubic-bezier(.16,.84,.24,1)}');
    css.push('.lif-lg u{text-decoration:none;font-size:9px;letter-spacing:.12em;color:#7e7a6e;transition:color .3s;font-variant-numeric:tabular-nums}');
    css.push('.lif-lg:hover{color:#e6e1d4}');
    css.push('.lif-lg.on{color:#ece7db}');
    css.push('.lif-lg.on i{width:24px}');
    css.push('.lif-lg.on u{color:#c9c3b5}');
    css.push('.lif-mnote{margin:12px 0 0;font-size:11.5px;line-height:1.85;letter-spacing:.06em;color:#8e897d;max-width:640px}');

    /* SVG 内部 */
    css.push('.lif-map .lif-frame{fill:none;stroke:rgba(236,231,219,.07);stroke-width:1}');
    css.push('.lif-map .lif-grid{stroke:rgba(236,231,219,.045);stroke-width:1}');
    css.push('.lif-map .lif-region{font-size:11px;letter-spacing:.52em;fill:#ece7db;opacity:.14}');
    css.push('.lif-map .lif-ridge{stroke:rgba(236,231,219,.12);stroke-width:.7;stroke-linecap:round}');
    css.push('.lif-map .lif-river{fill:none;stroke:rgba(120,158,176,.17);stroke-width:1;stroke-linecap:round}');
    css.push('.lif-map .lif-rivlab{font-size:9px;letter-spacing:.44em;fill:#8fa6b0;opacity:.34}');
    css.push('.lif-map .lif-seg{fill:none;stroke-linecap:round;stroke-linejoin:round}');
    css.push('.lif-map .lif-seg-halo{opacity:.16;filter:url(#lifBlur)}');
    css.push('.lif-map .lif-g{transition:opacity .5s ease}');
    css.push('.lif-map .lif-hit{fill:none;pointer-events:all}');
    css.push('.lif-map .lif-pop{animation:lifPop .72s cubic-bezier(.16,.84,.24,1) both;transform-box:fill-box;transform-origin:50% 50%}');
    css.push('@keyframes lifPop{from{opacity:0;transform:scale(.35)}to{opacity:1;transform:scale(1)}}');
    css.push('.lif-map .lif-dot{transition:transform .3s cubic-bezier(.16,.84,.24,1);transform-box:fill-box;transform-origin:50% 50%}');
    css.push('.lif-map .lif-node:hover .lif-dot{transform:scale(1.75)}');
    css.push('.lif-map .lif-ring{opacity:0;transition:opacity .3s}');
    css.push('.lif-map .lif-node:hover .lif-ring{opacity:.9}');
    css.push('.lif-map .lif-lab-g{opacity:0;animation:lifIn .85s cubic-bezier(.16,.84,.24,1) both}');
    css.push('@keyframes lifIn{from{opacity:0}to{opacity:1}}');
    css.push('.lif-map .lif-lead{stroke:rgba(236,231,219,.24);stroke-width:.7;fill:none}');
    css.push('.lif-map .lif-lab{font-size:' + LAB_FS + 'px;letter-spacing:' + LAB_LS + 'px;fill:#cfc9bb;transition:fill .25s}');
    css.push('.lif-map .lif-node:hover .lif-lab{fill:#f2eee4}');
    css.push('.lif-map .lif-yr{font-family:"Helvetica Neue",Arial,sans-serif;font-size:8.5px;letter-spacing:.20em;fill:#c9a227;opacity:.82;font-variant-numeric:tabular-nums}');
    css.push('.lif-map .lif-yr-g{opacity:0;animation:lifIn 1s ease both}');
    /* 点色例：其余四期压低 */
    for (var k = 1; k <= 5; k++) {
      css.push('.lif-map[data-focus="' + k + '"] .lif-g[data-p]:not([data-p="' + k + '"]){opacity:.12}');
    }
    css.push('.lif-tip{position:absolute;left:0;top:0;min-width:150px;max-width:250px;padding:11px 13px 12px;background:rgba(5,6,11,.95);border:1px solid rgba(201,162,39,.24);opacity:0;visibility:hidden;transform:translate(-50%,-114%);transition:opacity .22s,visibility .22s;pointer-events:none;z-index:4}');
    css.push('.lif-tip.on{opacity:1;visibility:visible}');
    css.push('.lif-tip b{display:block;font-size:12.5px;font-weight:400;letter-spacing:.16em;color:#ece7db;margin-bottom:5px}');
    css.push('.lif-tip .lif-ty{display:block;font-family:"Helvetica Neue",Arial,sans-serif;font-size:9px;letter-spacing:.18em;color:#c9a227;margin-bottom:7px;font-variant-numeric:tabular-nums}');
    css.push('.lif-tip p{font-size:11.5px;line-height:1.78;letter-spacing:.03em;color:#c2bcae}');
    css.push('.lif-tip .lif-ts{display:block;margin-top:6px;font-size:9px;letter-spacing:.14em;color:#7e7a6e;font-variant-numeric:tabular-nums}');

    /* 五期长文 */
    css.push('.lif-eras{margin:56px 0 0}');
    css.push('.lif-era{margin:0 0 68px;max-width:820px}');
    css.push('.lif-eh{display:flex;align-items:baseline;gap:16px}');
    css.push('.lif-eno{font-family:"Helvetica Neue",Arial,sans-serif;font-size:9.5px;letter-spacing:.3em;color:#7e7a6e;min-width:22px;padding-bottom:4px}');
    css.push('.lif-enm{font-size:23px;letter-spacing:.20em;color:#ece7db;font-weight:400;line-height:1.45}');
    css.push('.lif-eyr{font-family:"Helvetica Neue",Arial,sans-serif;font-size:10px;letter-spacing:.24em;color:#a8a294;margin:6px 0 0 38px;font-variant-numeric:tabular-nums}');
    css.push('.lif-eyr em{font-style:normal;color:#8e897d;padding:0 2px}');
    css.push('.lif-blk{margin:26px 0 0 38px}');
    css.push('.lif-lab-k{font-family:"Helvetica Neue",Arial,sans-serif;font-size:9px;letter-spacing:.32em;color:#8e897d;margin:0 0 9px}');
    css.push('.lif-tx{font-size:15px;line-height:1.95;letter-spacing:.045em;color:#d9d3c6;margin:0}');
    css.push('.lif-qs{margin:30px 0 0 38px;padding:2px 0 2px 20px;border-left:1px solid rgba(236,231,219,.10);max-width:620px}');
    css.push('.lif-q{font-size:17px;line-height:1.9;letter-spacing:.07em;color:#ece7db;margin:0}');
    css.push('.lif-qf{font-family:"Helvetica Neue",Arial,sans-serif;font-size:9.5px;letter-spacing:.2em;color:#8e897d;margin:5px 0 16px}');
    css.push('.lif-qf:last-child{margin-bottom:0}');
    css.push('.lif-evs{margin:28px 0 0 38px}');
    css.push('.lif-ev{display:flex;gap:16px;padding:8px 0;border-bottom:1px solid rgba(236,231,219,.05);font-size:12.5px;line-height:1.9;letter-spacing:.05em;color:#c9c3b5}');
    css.push('.lif-ev b{font-weight:400;color:#a8a294;min-width:46px;font-family:"Helvetica Neue",Arial,sans-serif;font-size:11.5px;letter-spacing:.1em;font-variant-numeric:tabular-nums}');
    css.push('.lif-chips{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0 0 38px}');
    css.push('.lif-chips .chip{font-size:11.5px;letter-spacing:.13em;padding:5px 10px}');
    css.push('.lif-keep{margin:20px 0 0 38px;font-size:12.5px;line-height:1.9;letter-spacing:.09em;color:#8e897d}');
    css.push('.lif-keep:before{content:"·";padding-right:8px;color:#c9a227}');
    css.push('.lif-close{margin:20px 0 0;padding-top:28px;border-top:1px solid rgba(236,231,219,.08);max-width:640px;font-size:15px;line-height:1.95;letter-spacing:.06em;color:#cdc7b9}');
    css.push('.lif-fb{font-size:13px;line-height:1.95;color:#d9d3c6}');

    /* 降级动效 */
    css.push('@media (prefers-reduced-motion:reduce){.lif-map .lif-pop,.lif-map .lif-lab-g,.lif-map .lif-yr-g{animation:none!important;opacity:1!important;transform:none!important}}');
    return css.join('') + (typeof EXTRA_CSS === 'string' ? EXTRA_CSS : '');
  }

  function ensureStyle() {
    if (typeof document === 'undefined' || !document.head) return;
    if (document.getElementById(STYLE_ID)) return;
    var el = document.createElement('style');
    el.id = STYLE_ID;
    el.appendChild(document.createTextNode(buildCSS()));
    document.head.appendChild(el);
  }

  /* ---------------- 取数据：LIFE_DATA 优先，其次 META.life，都没有就 null ---------------- */
  function firstYear(s) {
    var m = String(s == null ? '' : s).match(/(\d{3,4})/);
    return m ? parseInt(m[1], 10) : 9999;
  }

  function fromMeta(M) {
    var L = M.life || M, i, j;
    var periods = [], route = [];
    var ps = M.periods || [];
    for (i = 0; i < ps.length; i++) {
      var p = ps[i], evs = [];
      var tl = M.timeline || [];
      for (j = 0; j < tl.length; j++) {
        if (tl[j].year >= p.start && tl[j].year <= p.end) {
          evs.push({ y: String(tl[j].year), t: tl[j].event });
        }
      }
      periods.push({
        no: ROMAN[i] || '', id: p.id || i + 1, name: p.name || '',
        years: p.start + ' — ' + p.end, start: p.start, end: p.end,
        age: p.age || '', theme: p.theme || '',
        era: '', self: '', mind: '', lines: [],
        events: evs, poems: (p.representative || []).slice(0, 8), keep: ''
      });
    }
    var places = (M.places || []).slice().sort(function (a, b) { return firstYear(a.years) - firstYear(b.years); });
    for (i = 0; i < places.length; i++) {
      var pl = places[i], yr = firstYear(pl.years), per = 1;
      for (j = 0; j < periods.length; j++) {
        if (yr >= periods[j].start && yr <= periods[j].end) { per = j + 1; break; }
        if (yr < periods[0].start) { per = 1; break; }
      }
      route.push({
        n: pl.name, y: pl.years || '', p: per,
        lon: pl.lon, lat: pl.lat,
        stay: /—/.test(String(pl.years || '')) ? 0.8 : 0.3,
        poems: 0, dir: ['r', 'l', 't', 'b', 'tr', 'bl', 'br', 'tl'][i % 8],
        line: pl.note || '', mark: i === 0 ? String(firstYear(pl.years)) : ''
      });
    }
    return {
      name: '杜甫', birth: L.birth || 712, death: L.death || 770,
      birthplace: L.birthplace || '河南巩县',
      oneLine: '', intro: '', routeTitle: '行迹', routeSub: '', routeNote: '',
      regions: [], river: [], periods: periods, route: route, closing: ''
    };
  }

  function pickData() {
    var w = (typeof window !== 'undefined') ? window : {};
    var D = w.LIFE_DATA;
    if (D && D.periods && D.periods.length) return D;
    if (w.META && w.META.life) {
      var D2 = fromMeta(w.META.life);
      if (D2 && D2.periods.length) return D2;
    }
    return null;
  }

  /* ---------------- 投影 ---------------- */
  function makeProj(route) {
    var minLon = 1e9, maxLon = -1e9, minLat = 1e9, maxLat = -1e9;
    for (var i = 0; i < route.length; i++) {
      var p = route[i];
      if (p.lon < minLon) minLon = p.lon;
      if (p.lon > maxLon) maxLon = p.lon;
      if (p.lat < minLat) minLat = p.lat;
      if (p.lat > maxLat) maxLat = p.lat;
    }
    var iw = W - PAD.l - PAD.r, ih = H - PAD.t - PAD.b;
    var sx = iw / ((maxLon - minLon) || 1), sy = ih / ((maxLat - minLat) || 1);
    return {
      sx: sx, sy: sy,
      minLon: minLon, maxLon: maxLon, minLat: minLat, maxLat: maxLat,
      x: function (lon) { return PAD.l + (lon - minLon) * sx; },
      y: function (lat) { return PAD.t + (maxLat - lat) * sy; }
    };
  }

  /* ---------------- 平滑曲线：Catmull-Rom 转三次贝塞尔 ---------------- */
  function smoothPath(list) {
    if (!list || list.length < 2) return '';
    var d = 'M' + f(list[0].x) + ' ' + f(list[0].y), i;
    if (list.length === 2) {
      var a = list[0], b = list[1];
      var mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      var dx = b.x - a.x, dy = b.y - a.y;
      var len = Math.sqrt(dx * dx + dy * dy) || 1;
      var k = Math.min(24, len * 0.16);
      return d + ' Q' + f(mx - dy / len * k) + ' ' + f(my + dx / len * k) + ' ' + f(b.x) + ' ' + f(b.y);
    }
    for (i = 0; i < list.length - 1; i++) {
      var p0 = list[i - 1] || list[i], p1 = list[i], p2 = list[i + 1], p3 = list[i + 2] || list[i + 1];
      var c1x = p1.x + (p2.x - p0.x) / 6, c1y = p1.y + (p2.y - p0.y) / 6;
      var c2x = p2.x - (p3.x - p1.x) / 6, c2y = p2.y - (p3.y - p1.y) / 6;
      d += ' C' + f(c1x) + ' ' + f(c1y) + ',' + f(c2x) + ' ' + f(c2y) + ',' + f(p2.x) + ' ' + f(p2.y);
    }
    return d;
  }

  /* 沿 Catmull-Rom 采样，供标签避让判断「压不压线」 */
  function samplePath(list, per) {
    var out = [], i, t, seg;
    if (!list || list.length < 2) return out;
    if (list.length === 2) {
      for (t = 0; t <= 1.0001; t += 1 / per) {
        out.push({ x: list[0].x + (list[1].x - list[0].x) * t, y: list[0].y + (list[1].y - list[0].y) * t });
      }
      return out;
    }
    for (i = 0; i < list.length - 1; i++) {
      var p0 = list[i - 1] || list[i], p1 = list[i], p2 = list[i + 1], p3 = list[i + 2] || list[i + 1];
      for (seg = 0; seg < per; seg++) {
        t = seg / per;
        var t2 = t * t, t3 = t2 * t;
        out.push({
          x: 0.5 * ((2 * p1.x) + (-p0.x + p2.x) * t + (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2 + (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3),
          y: 0.5 * ((2 * p1.y) + (-p0.y + p2.y) * t + (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * t2 + (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * t3)
        });
      }
    }
    return out;
  }

  /* ---------------- 标签排布：贪心选址 + 四向八位错位 + 引线 ---------------- */
  var DIRS = ['r', 'l', 't', 'b', 'tr', 'tl', 'br', 'bl'];

  function reorder(pref) {
    var out = [], i;
    if (pref !== '') {
      for (i = 0; i < DIRS.length; i++) if (DIRS[i] === pref) out.push(pref);
    }
    for (i = 0; i < DIRS.length; i++) if (DIRS[i] !== pref) out.push(DIRS[i]);
    return out;
  }

  function textWidth(s, size, ls) {
    var w = 0, i, c;
    for (i = 0; i < s.length; i++) {
      c = s.charCodeAt(i);
      w += (c > 255 ? size : size * 0.56) + ls;
    }
    return w;
  }

  function makeBox(n, dir, dist, w, h) {
    var ax, ay, anchor;
    if (dir === 'r') { ax = n.x + dist; ay = n.y; anchor = 'start'; }
    else if (dir === 'l') { ax = n.x - dist; ay = n.y; anchor = 'end'; }
    else if (dir === 't') { ax = n.x; ay = n.y - dist; anchor = 'middle'; }
    else if (dir === 'b') { ax = n.x; ay = n.y + dist; anchor = 'middle'; }
    else if (dir === 'tr') { ax = n.x + dist * 0.74; ay = n.y - dist * 0.74; anchor = 'start'; }
    else if (dir === 'tl') { ax = n.x - dist * 0.74; ay = n.y - dist * 0.74; anchor = 'end'; }
    else if (dir === 'br') { ax = n.x + dist * 0.74; ay = n.y + dist * 0.74; anchor = 'start'; }
    else { ax = n.x - dist * 0.74; ay = n.y + dist * 0.74; anchor = 'end'; }
    var x0 = anchor === 'start' ? ax : (anchor === 'end' ? ax - w : ax - w / 2);
    var y0 = ay - h / 2;
    return { d: dir, ax: ax, ay: ay, anchor: anchor, x0: x0, y0: y0, x1: x0 + w, y1: y0 + h, w: w, h: h };
  }

  function overlapArea(a, b) {
    var ox = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0);
    var oy = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0);
    if (ox <= 0 || oy <= 0) return 0;
    return ox * oy;
  }

  /* 候选框打分：越接近 0 越干净 */
  function scoreBox(b, nodes, placed, samples) {
    var s = 0, i, n, dx, dy, p, rr;
    if (b.x0 < 16 || b.x1 > W - 10 || b.y0 < 30 || b.y1 > H - 32) s += 500;   /* 出画 / 压到标题与色例 */
    for (i = 0; i < placed.length; i++) {
      var ov = overlapArea(b, placed[i]);
      if (ov > 0) s += 40 + ov / 6;
    }
    for (i = 0; i < nodes.length; i++) {
      n = nodes[i]; rr = n.r + 4.5;
      dx = n.x - Math.max(b.x0, Math.min(n.x, b.x1));
      dy = n.y - Math.max(b.y0, Math.min(n.y, b.y1));
      if (dx * dx + dy * dy < rr * rr) s += 26;
    }
    for (i = 0; i < samples.length; i++) {
      p = samples[i];
      if (p.x > b.x0 - 4 && p.x < b.x1 + 4 && p.y > b.y0 - 3 && p.y < b.y1 + 3) s += 22;   /* 标签不许压线 */
    }
    return s;
  }

  function placeOne(n, label, size, ls, hgt, nodes, placed, samples, prefDirs, dists) {
    var w = textWidth(label, size, ls) + 2;
    var dirs = reorder(prefDirs || n.dir || 'r');
    var bestS = 1e9, bestB = null, di, dd, b, s;
    for (di = 0; di < dirs.length; di++) {
      for (dd = 0; dd < dists.length; dd++) {
        b = makeBox(n, dirs[di], dists[dd], w, hgt);
        s = scoreBox(b, nodes, placed, samples) + dd * 0.8;
        if (s < bestS) { bestS = s; bestB = b; }
        if (bestS < 0.5) break;
      }
      if (bestS < 0.5) break;
    }
    placed.push(bestB);
    return bestB;
  }

  /* ---------------- 行迹图 ---------------- */
  function buildMap(D) {
    var route = (D.route || []).filter(function (p) { return isFinite(p.lon) && isFinite(p.lat); });
    if (route.length < 2) return { html: '', nodes: [] };

    var pr = makeProj(route);
    var i, k, n;
    var nodes = [];
    for (i = 0; i < route.length; i++) {
      var p = route[i], stay = (typeof p.stay === 'number' && p.stay > 0) ? p.stay : 0.3;
      nodes.push({
        i: i, n: p.n || '', ys: p.y || '', p: p.p || 1, line: p.line || '',
        x: pr.x(p.lon), y: pr.y(p.lat),
        r: 2.6 + Math.min(7.2, Math.sqrt(stay) * 2.25),
        dir: p.dir || 'r', mark: p.mark || '', md: p.md || '', poems: p.poems || 0, stay: stay
      });
    }

    /* 按期分组（每组路径从上一期最后一站接上，线才是连的） */
    var groups = [[], [], [], [], []];
    for (i = 0; i < nodes.length; i++) {
      var gi = Math.max(1, Math.min(5, nodes[i].p)) - 1;
      groups[gi].push(nodes[i]);
    }
    var segs = [], samples = [], prevLast = null;
    for (k = 0; k < 5; k++) {
      if (!groups[k].length) continue;
      var list = groups[k].slice();
      if (prevLast) list = [prevLast].concat(list);
      segs.push({ p: k + 1, d: smoothPath(list), a: list[0], b: list[list.length - 1], nodes: groups[k] });
      samples = samples.concat(samplePath(list, 12));
      prevLast = groups[k][groups[k].length - 1];
    }

    /* 标签先排（大点优先），年份标注后排，互相避让 */
    var placed = [];
    var order = nodes.slice().sort(function (a, b) { return b.r - a.r; });
    for (i = 0; i < order.length; i++) {
      n = order[i];
      var d0 = (n.i === 0 || n.i === nodes.length - 1) ? 4.5 : 0;   /* 首末站有双环，标签再让开一点 */
      n.box = placeOne(n, n.n, LAB_FS, LAB_LS, 14, nodes, placed, samples, n.dir, [n.r + 9 + d0, n.r + 21 + d0, n.r + 33 + d0, n.r + 45 + d0]);
    }
    for (i = 0; i < nodes.length; i++) {
      n = nodes[i];
      if (!n.mark) continue;
      var prefs = n.box && n.box.d ? n.box.d : 'b';
      var alt = ['b', 't', 'br', 'bl', 'tr', 'tl', 'r', 'l'];
      var alts = [];
      for (k = 0; k < alt.length; k++) if (alt[k] !== prefs) alts.push(alt[k]);
      n.markBox = placeOne(n, n.mark, 8.5, 1.7, 11, nodes, placed, samples, n.md || alts[0], [n.r + 10, n.r + 18, n.r + 26]);
    }

    LAST = { nodes: nodes, W: W, H: H };

    var s = [];
    s.push('<svg class="lif-map" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="xMidYMid meet" role="img" aria-label="杜甫行迹图：二十九州县，五期分段">');

    /* --- defs --- */
    s.push('<defs>');
    s.push('<radialGradient id="lif-bg" cx="46%" cy="34%" r="80%">');
    s.push('<stop offset="0" stop-color="#0b0d16"/><stop offset=".56" stop-color="#070810"/><stop offset="1" stop-color="#04050a"/>');
    s.push('</radialGradient>');
    s.push('<radialGradient id="lif-warm" cx="50%" cy="50%" r="50%">');
    s.push('<stop offset="0" stop-color="#c9a227" stop-opacity=".085"/><stop offset="1" stop-color="#c9a227" stop-opacity="0"/>');
    s.push('</radialGradient>');
    s.push('<filter id="lifBlur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.4"/></filter>');
    for (k = 0; k < segs.length; k++) {
      var sg = segs[k], col = COLORS[sg.p - 1];
      s.push('<linearGradient id="lif-gr' + sg.p + '" gradientUnits="userSpaceOnUse" x1="' + f(sg.a.x) + '" y1="' + f(sg.a.y) +
        '" x2="' + f(sg.b.x) + '" y2="' + f(sg.b.y) + '">');
      s.push('<stop offset="0" stop-color="' + col + '" stop-opacity=".38"/>');
      s.push('<stop offset=" .55" stop-color="' + col + '" stop-opacity=".78"/>');
      s.push('<stop offset="1" stop-color="' + col + '" stop-opacity="1"/>');
      s.push('</linearGradient>');
    }
    s.push('</defs>');

    /* --- 底：径向暗场 + 两团极淡的光 --- */
    s.push('<rect x="0" y="0" width="' + W + '" height="' + H + '" fill="url(#lif-bg)"/>');
    s.push('<ellipse cx="' + f(pr.x(109.6)) + '" cy="' + f(pr.y(34.4)) + '" rx="230" ry="150" fill="url(#lif-warm)"/>');
    s.push('<ellipse cx="' + f(pr.x(105.5)) + '" cy="' + f(pr.y(30.7)) + '" rx="170" ry="120" fill="url(#lif-warm)" opacity=".6"/>');

    /* --- 经纬网 --- */
    s.push('<g class="lif-grid-g" fill="none">');
    var lon, lat, cnt;
    for (lon = Math.ceil(pr.minLon / 3) * 3; lon <= pr.maxLon; lon += 3) {
      s.push('<line class="lif-grid" x1="' + f(pr.x(lon)) + '" y1="' + (PAD.t - 26) + '" x2="' + f(pr.x(lon)) + '" y2="' + (H - PAD.b + 26) + '"/>');
    }
    for (lat = Math.ceil(pr.minLat / 3) * 3; lat <= pr.maxLat; lat += 3) {
      s.push('<line class="lif-grid" x1="' + (PAD.l - 62) + '" y1="' + f(pr.y(lat)) + '" x2="' + (W - PAD.r + 34) + '" y2="' + f(pr.y(lat)) + '"/>');
    }
    s.push('</g>');
    s.push('<rect class="lif-frame" x="18" y="14" width="' + (W - 36) + '" height="' + (H - 28) + '"/>');

    /* --- 地理暗示：关中—中原—巴蜀—荆湘 四个方位名 + 秦岭折线 + 长江曲线 --- */
    var regs = D.regions || [];
    for (i = 0; i < regs.length; i++) {
      s.push('<text class="lif-region" x="' + f(pr.x(regs[i].lon)) + '" y="' + f(pr.y(regs[i].lat)) +
        '" text-anchor="middle">' + esc(regs[i].n) + '</text>');
    }
    /* 秦岭一带的山形线（只是地貌暗示，不画边界） */
    function ridge(a, b, cnt, h) {
      var x1 = pr.x(a[0]), y1 = pr.y(a[1]), x2 = pr.x(b[0]), y2 = pr.y(b[1]);
      var dx = x2 - x1, dy = y2 - y1, len = Math.sqrt(dx * dx + dy * dy) || 1;
      var nx = -dy / len, ny = dx / len, out = '', j, t, cx, cy, hh;
      for (j = 0; j < cnt; j++) {
        t = (j + 0.5) / cnt;
        cx = x1 + dx * t; cy = y1 + dy * t;
        hh = h * (0.5 + 0.5 * Math.abs(Math.sin(j * 1.9 + 0.6)));
        out += 'M' + f(cx) + ' ' + f(cy) + ' L' + f(cx + nx * hh) + ' ' + f(cy + ny * hh) + ' ';
      }
      return out;
    }
    s.push('<g class="lif-ridge-g" fill="none" opacity=".55">');
    s.push('<path class="lif-ridge" d="' + ridge([106.2, 34.05], [110.9, 33.62], 11, 9) + '"/>');
    s.push('<path class="lif-ridge" d="' + ridge([104.9, 32.55], [107.9, 32.2], 5, 7) + '"/>');
    s.push('</g>');

    /* 长江：用行迹里确实在江边的几站连成，只当示意 */
    var riverPts = [];
    for (i = 0; i < (D.river || []).length; i++) {
      for (k = 0; k < route.length; k++) {
        if (route[k].n === D.river[i]) { riverPts.push({ x: pr.x(route[k].lon), y: pr.y(route[k].lat) }); break; }
      }
    }
    if (riverPts.length > 2) {
      s.push('<path class="lif-river" d="' + smoothPath(riverPts) + '"/>');
    }
    if (D.riverLabel) {
      s.push('<text class="lif-rivlab" x="' + f(pr.x(D.riverLabel.lon)) + '" y="' + f(pr.y(D.riverLabel.lat)) +
        '" text-anchor="middle">' + esc(D.riverLabel.n) + '</text>');
    }

    /* --- 行迹：每期一段，光晕垫底 + 主线（线宽随期递加，颜色用渐变收口） --- */
    for (k = 0; k < segs.length; k++) {
      sg = segs[k]; col = COLORS[sg.p - 1];
      var wd = f(1.35 + (sg.p - 1) * 0.27);
      s.push('<g class="lif-g" data-p="' + sg.p + '">');
      s.push('<path class="lif-seg lif-seg-halo" d="' + sg.d + '" stroke="' + col + '" stroke-width="' + (parseFloat(wd) + 3.6) + '"/>');
      s.push('<path class="lif-seg lif-seg-body" data-p="' + sg.p + '" d="' + sg.d + '" stroke="url(#lif-gr' + sg.p + ')" stroke-width="' + wd + '"/>');
      s.push('</g>');
    }

    /* --- 节点：大小按时长，首末双环 --- */
    for (k = 0; k < 5; k++) {
      if (!groups[k].length) continue;
      s.push('<g class="lif-g lif-nodes" data-p="' + (k + 1) + '">');
      for (i = 0; i < groups[k].length; i++) {
        n = groups[k][i];
        var cx = f(n.x), cy = f(n.y), c = COLORS[k];
        var rr = f(n.r), isEnd = (n.i === 0 || n.i === nodes.length - 1);
        var delay = f(1.05 + n.i * 0.045);
        s.push('<g class="lif-node" data-i="' + n.i + '" data-n="' + esc(n.n) + '">');
        s.push('<circle class="lif-hit" cx="' + cx + '" cy="' + cy + '" r="' + f(Math.max(14, n.r + 9)) + '"/>');
        s.push('<g class="lif-pop" style="animation-delay:' + delay + 's">');
        if (isEnd) {
          s.push('<circle cx="' + cx + '" cy="' + cy + '" r="' + f(n.r + 9.5) + '" fill="none" stroke="' + c + '" stroke-opacity=".22" stroke-width=".8"/>');
          s.push('<circle cx="' + cx + '" cy="' + cy + '" r="' + f(n.r + 5) + '" fill="none" stroke="' + c + '" stroke-opacity=".48" stroke-width=".9"/>');
        }
        s.push('<circle class="lif-ring" cx="' + cx + '" cy="' + cy + '" r="' + f(n.r + 5.5) + '" fill="none" stroke="' + c + '" stroke-width="1"/>');
        s.push('<circle class="lif-dot" cx="' + cx + '" cy="' + cy + '" r="' + rr + '" fill="' + c + '" stroke="rgba(4,5,10,.78)" stroke-width=".9"/>');
        s.push('</g></g>');
      }
      s.push('</g>');
    }

    /* --- 地名标签 + 引线 --- */
    for (k = 0; k < 5; k++) {
      if (!groups[k].length) continue;
      s.push('<g class="lif-g lif-labs" data-p="' + (k + 1) + '">');
      for (i = 0; i < groups[k].length; i++) {
        n = groups[k][i];
        if (!n.box) continue;
        var bx = n.box, lx = f(bx.ax), ly = f(bx.ay);
        var edge = { x: n.x + (bx.ax - n.x) / (Math.sqrt(Math.pow(bx.ax - n.x, 2) + Math.pow(bx.ay - n.y, 2)) || 1) * (n.r + 2.5),
                     y: n.y + (bx.ay - n.y) / (Math.sqrt(Math.pow(bx.ax - n.x, 2) + Math.pow(bx.ay - n.y, 2)) || 1) * (n.r + 2.5) };
        var lx2 = bx.anchor === 'start' ? bx.ax - 3 : (bx.anchor === 'end' ? bx.ax + 3 : bx.ax);
        var lead = 'M' + f(edge.x) + ' ' + f(edge.y) + ' L' + f(lx2) + ' ' + f(ly);
        s.push('<g class="lif-lab-g" data-i="' + n.i + '" data-d="' + (bx.d || '') + '" style="animation-delay:' + f(1.55 + n.i * 0.02) + 's">');
        s.push('<path class="lif-lead" d="' + lead + '"/>');
        s.push('<text class="lif-lab" x="' + lx + '" y="' + ly + '" text-anchor="' + bx.anchor + '" dominant-baseline="middle">' + esc(n.n) + '</text>');
        s.push('</g>');
      }
      s.push('</g>');
    }

    /* --- 年份：极小、字距大、压在路径旁边 --- */
    s.push('<g class="lif-years">');
    for (i = 0; i < nodes.length; i++) {
      n = nodes[i];
      if (!n.mark || !n.markBox) continue;
      s.push('<g class="lif-yr-g" style="animation-delay:' + f(1.85 + i * 0.03) + 's">');
      s.push('<text class="lif-yr" x="' + f(n.markBox.ax) + '" y="' + f(n.markBox.ay) + '" text-anchor="' + n.markBox.anchor + '" dominant-baseline="middle">' + esc(n.mark) + '</text>');
      s.push('</g>');
    }
    s.push('</g>');

    s.push('</svg>');

    /* --- 右上小标题 + 左下色例 + 悬停卡（HTML 叠在图上，字才够清） --- */
    var html = [];
    html.push('<div class="lif-mapbox">');
    html.push('<div class="lif-mtitle"><b>' + esc(D.routeTitle || '行迹') + '</b>' + esc(D.routeSub || '') + '</div>');
    html.push(s.join(''));
    html.push('<div class="lif-legend">');
    for (k = 0; k < (D.periods || []).length && k < 5; k++) {
      var pd = D.periods[k];
      html.push('<span class="lif-lg" data-p="' + (k + 1) + '"><i style="background:' + COLORS[k] + '"></i>' +
        esc(pd.name) + '<u>' + esc(String(pd.years || '').replace(/ — /g, '–')) + '</u></span>');
    }
    html.push('</div>');
    html.push('<div class="lif-tip"><b></b><span class="lif-ty"></span><p></p><span class="lif-ts"></span></div>');
    html.push('</div>');
    if (D.routeNote) html.push('<div class="lif-mnote">' + esc(D.routeNote) + '</div>');

    return { html: html.join(''), nodes: nodes };
  }

  /* 后补的几条样式（顶部大标题与身份行、悬停时标签提亮） */
  var EXTRA_CSS = [
    '.lif-h1{font-size:clamp(23px,3.2vw,34px);letter-spacing:.16em;line-height:1.22;color:#ece7db;font-weight:400;margin:0 0 24px}',
    '.lif-idr{display:flex;align-items:baseline;gap:18px;flex-wrap:wrap;margin:0 0 22px;padding-bottom:18px;border-bottom:1px solid rgba(236,231,219,.07)}',
    '.lif-idr b{font-size:20px;font-weight:400;letter-spacing:.26em;color:#ece7db}',
    '.lif-idr span{font-family:"Helvetica Neue",Arial,sans-serif;font-size:10px;letter-spacing:.22em;color:#a8a294;font-variant-numeric:tabular-nums}',
    '.lif-idr em{font-style:normal;color:#8e897d;padding:0 3px}',
    '.lif-map .lif-lab-g.hot .lif-lab{fill:#f6f3ea}',
    '.lif-map .lif-lab-g.hot .lif-lead{stroke:rgba(236,231,219,.5)}',
    '.no-anim .lif-pop,.no-anim .lif-lab-g,.no-anim .lif-yr-g{animation:none!important;opacity:1!important;transform:none!important}'
  ].join('');

  /* ---------------- 五期长文 ---------------- */
  function eraHTML(D, p, i) {
    var h = [];
    h.push('<div class="lif-era">');
    h.push('<div class="lif-eh"><span class="lif-eno">' + esc(p.no || ROMAN[i] || '') + '</span>' +
      '<span class="lif-enm">' + esc(p.name || '') + '</span></div>');
    var meta = [esc(p.years || '')];
    if (p.age) meta.push(esc(p.age));
    if (p.theme) meta.push(esc(p.theme));
    h.push('<div class="lif-eyr">' + meta.join('<em>·</em>') + '</div>');

    if (p.era) h.push('<div class="lif-blk"><div class="lif-lab-k">时代背景</div><p class="lif-tx">' + esc(p.era) + '</p></div>');
    if (p.self) h.push('<div class="lif-blk"><div class="lif-lab-k">杜甫处境</div><p class="lif-tx">' + esc(p.self) + '</p></div>');
    if (p.mind) h.push('<div class="lif-blk"><div class="lif-lab-k">心境与诗风</div><p class="lif-tx">' + esc(p.mind) + '</p></div>');

    if (p.lines && p.lines.length) {
      h.push('<div class="lif-qs">');
      for (var q = 0; q < p.lines.length; q++) {
        h.push('<p class="lif-q">「' + esc(p.lines[q].q) + '」</p>');
        h.push('<div class="lif-qf">《' + esc(p.lines[q].from) + '》</div>');
      }
      h.push('</div>');
    }

    if (p.events && p.events.length) {
      h.push('<div class="lif-evs">');
      for (var e = 0; e < p.events.length; e++) {
        h.push('<div class="lif-ev"><b>' + esc(p.events[e].y) + '</b><span>' + esc(p.events[e].t) + '</span></div>');
      }
      h.push('</div>');
    }

    var chips = [];
    var cnt = 0;
    if (typeof window !== 'undefined' && window.pts && window.pts.length) {
      for (var k = 0; k < window.pts.length; k++) if (window.pts[k].pd === i) cnt++;
    }
    if (cnt > 0) {
      chips.push('<span class="chip" data-period="' + i + '">在星海中看这 ' + cnt + ' 首 ›</span>');
    }
    if (p.poems && p.poems.length) {
      for (var t = 0; t < p.poems.length; t++) {
        chips.push('<span class="chip" data-t="' + esc(p.poems[t]) + '">' + esc(p.poems[t]) + '</span>');
      }
    }
    if (chips.length) h.push('<div class="lif-chips">' + chips.join('') + '</div>');

    if (p.keep) h.push('<div class="lif-keep">' + esc(p.keep) + '</div>');
    h.push('</div>');
    return h.join('');
  }

  /* ---------------- 兜底：没有数据时也给一段能读的纯文本 ---------------- */
  function plainPanel() {
    return '<div class="lif">' +
      '<div class="lif-kick">02 / LIFE</div>' +
      '<h2 class="lif-h1">生平</h2>' +
      '<div class="lif-idr"><b>杜甫</b><span>712 — 770</span><span>字子美 · 少陵野老</span><span>河南巩县</span></div>' +
      '<p class="lif-tx">杜甫，字子美，河南巩县（今河南巩义）人。开元年间南游吴越、北游齐赵；天宝年间困守长安十年。' +
      '755 年安史之乱起，他陷贼、奔行在、贬华州，759 年弃官入蜀，在成都浣花溪畔筑草堂；765 年离蜀，768 年出峡，' +
      '770 年卒于湘江舟中，年五十九。</p></div>';
  }

  /* ---------------- 主函数 ---------------- */
  function renderLifePanel() {
    var html = '';
    try {
      ensureStyle();
      /* 静态截图模式：window.LIFE_NO_ANIM = true 时动效直接落定（配合 .no-anim） */
      try {
        if (window.LIFE_NO_ANIM && document.documentElement) document.documentElement.classList.add('no-anim');
      } catch (e0) { }
      var D = pickData();
      if (!D) return plainPanel();

      var h = [];
      h.push('<div class="lif">');
      h.push('<div class="lif-kick">02 / LIFE</div>');
      h.push('<h2 class="lif-h1">一个人的星轨</h2>');
      h.push('<div class="lif-idr"><b>' + esc(D.name || '杜甫') + '</b>' +
        '<span>' + esc(D.birth || 712) + '<em>—</em>' + esc(D.death || 770) + '</span>' +
        (D.zi ? '<span>字' + esc(D.zi) + '</span>' : '') +
        (D.hao ? '<span>' + esc(D.hao) + '</span>' : '') +
        (D.birthplace ? '<span>生于' + esc(D.birthplace) + '</span>' : '') + '</div>');
      var lede = [];
      if (D.oneLine) lede.push('<em>' + esc(D.oneLine) + '</em>');
      if (D.intro) lede.push(esc(D.intro));
      if (lede.length) h.push('<p class="lif-lede">' + lede.join('<br>') + '</p>');

      /* 行迹图 */
      var map = { html: '', nodes: [] };
      try { map = buildMap(D); } catch (e) { map = { html: '', nodes: [] }; }
      if (map.html) h.push(map.html);

      /* 五期 */
      h.push('<div class="lif-eras">');
      for (var i = 0; i < (D.periods || []).length; i++) {
        h.push(eraHTML(D, D.periods[i], i));
      }
      h.push('</div>');

      if (D.closing) h.push('<div class="lif-close">' + esc(D.closing) + '</div>');
      h.push('</div>');
      html = h.join('');
      return html;
    } catch (e) {
      try { return plainPanel(); } catch (e2) { return '<div class="lif-fb">生平（数据未就绪）</div>'; }
    }
  }

  /* ---------------- 绑事件：画线、悬停、色例 ---------------- */
  function fmtStay(v) {
    if (!v) return '';
    if (v >= 1) return (Math.round(v * 10) / 10) + ' 年';
    var m = Math.round(v * 12);
    return (m < 1 ? '不足一月' : m + ' 个月');
  }

  function bindLifePanel(root) {
    try {
      root = root || (typeof document !== 'undefined' ? document : null);
      if (!root || !root.querySelector) return;
      var svg = root.querySelector('.lif-map');
      if (!svg || svg.getAttribute('data-bound') === '1') return;
      svg.setAttribute('data-bound', '1');

      var reduce = false;
      try { reduce = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); } catch (e) { reduce = false; }
      /* 静态截图模式：给 <html> 或 <body> 加 no-anim，所有动效直接落定 */
      try {
        var he = document.documentElement, bd = document.body;
        if ((he && he.className && String(he.className).indexOf('no-anim') >= 0) ||
            (bd && bd.className && String(bd.className).indexOf('no-anim') >= 0)) reduce = true;
      } catch (e2) { }

      /* 1) 线：stroke-dashoffset 画出来（1.6s），光晕随后浮上 */
      var bodies = svg.querySelectorAll('.lif-seg-body');
      for (var i = 0; i < bodies.length; i++) {
        (function (el, idx) {
          var len = 0;
          try { len = el.getTotalLength(); } catch (e) { len = 0; }
          var halo = el.parentNode ? el.parentNode.querySelector('.lif-seg-halo') : null;
          if (!len || reduce) { if (halo) halo.style.opacity = ''; return; }
          var delay = 60 + idx * 130;
          el.style.strokeDasharray = len + ' ' + len;
          el.style.strokeDashoffset = len;
          if (halo) halo.style.opacity = '0';
          setTimeout(function () {
            el.style.transition = 'stroke-dashoffset 1.6s cubic-bezier(.25,.8,.35,1)';
            el.style.strokeDashoffset = '0';
            if (halo) { halo.style.transition = 'opacity 1.4s ease'; halo.style.opacity = ''; }
          }, delay);
        })(bodies[i], i);
      }

      /* 2) 色例：点一期，其余压暗；再点一次复原 */
      var lgs = root.querySelectorAll('.lif-lg');
      var clearLg = function (except) {
        for (var j = 0; j < lgs.length; j++) if (lgs[j] !== except) lgs[j].classList.remove('on');
      };
      for (i = 0; i < lgs.length; i++) {
        (function (lg) {
          lg.addEventListener('click', function (ev) {
            if (ev && ev.preventDefault) ev.preventDefault();
            var p = lg.getAttribute('data-p');
            if (svg.getAttribute('data-focus') === p) {
              svg.removeAttribute('data-focus'); lg.classList.remove('on'); return;
            }
            svg.setAttribute('data-focus', p);
            clearLg(lg); lg.classList.add('on');
          });
        })(lgs[i]);
      }

      /* 3) 悬停：节点放大 + 标签提亮 + 卡片刻度 */
      var tip = root.querySelector('.lif-tip');
      var box = root.querySelector('.lif-mapbox');
      var byIdx = {};
      if (LAST && LAST.nodes) for (i = 0; i < LAST.nodes.length; i++) byIdx[LAST.nodes[i].i] = LAST.nodes[i];
      var nodes = svg.querySelectorAll('.lif-node');
      for (i = 0; i < nodes.length; i++) {
        (function (g) {
          var idx = parseInt(g.getAttribute('data-i'), 10);
          var nd = byIdx[idx];
          if (!nd) return;
          var lab = null;
          var labs = svg.querySelectorAll('.lif-lab-g');
          for (var q = 0; q < labs.length; q++) {
            if (parseInt(labs[q].getAttribute('data-i'), 10) === idx) { lab = labs[q]; break; }
          }
          function show() {
            if (lab) lab.classList.add('hot');
            if (!tip || !box) return;
            var scale = box.clientWidth / W;
            var px = nd.x * scale, py = nd.y * scale;
            var minX = 132, maxX = Math.max(minX, box.clientWidth - 132);
            tip.style.left = Math.max(minX, Math.min(maxX, px)) + 'px';
            tip.style.top = Math.max(64, py - 6) + 'px';
            tip.querySelector('b').textContent = nd.n;
            tip.querySelector('.lif-ty').textContent = (nd.ys || '') + (nd.stay ? ' · 停留约 ' + fmtStay(nd.stay) : '');
            tip.querySelector('p').textContent = nd.line || '';
            tip.querySelector('.lif-ts').textContent = nd.poems ? '期内存诗约 ' + nd.poems + ' 首' : '';
            tip.classList.add('on');
          }
          function hide() {
            if (lab) lab.classList.remove('hot');
            if (tip) tip.classList.remove('on');
          }
          g.addEventListener('mouseenter', show);
          g.addEventListener('mouseleave', hide);
          g.addEventListener('focus', show);
          g.addEventListener('blur', hide);
        })(nodes[i]);
      }

      /* 4) chips 交给主文件的 bindChips；只有没人接时才自己兜一层 */
      var chips = root.querySelectorAll('.lif-chips .chip');
      for (i = 0; i < chips.length; i++) {
        (function (c) {
          if (c.onclick) return;
          c.onclick = function () {
            var t = c.getAttribute('data-t'), per = c.getAttribute('data-period');
            try { if (typeof window.closePanel === 'function') window.closePanel(); } catch (e) { }
            var dbg = window.__DUFU_DEBUG;
            if (!dbg) return;
            if (per !== null && dbg.setPeriod) {
              setTimeout(function () { try { dbg.setPeriod(parseInt(per, 10)); } catch (e) { } }, 400);
            } else if (t && dbg.selectAndFly) {
              setTimeout(function () { try { dbg.selectAndFly(t); } catch (e) { } }, 400);
            }
          };
        })(chips[i]);
      }
    } catch (e) { /* 绑定失败不影响面板显示 */ }
  }

  window.renderLifePanel = renderLifePanel;
  window.bindLifePanel = bindLifePanel;
})();
