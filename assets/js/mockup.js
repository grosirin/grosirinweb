/* grosir.in — Coba Desain (coba-desain.html): put a visitor's logo on photos of
   our bags. Runs entirely in the browser; the logo never leaves the device.

   Same engine as the owner's mockup tool in mockup/ (source repo): each photo
   has a fixed print area (four corners on the photo, as the bag hangs), the
   logo is laid flat at the area's real size in cm, warped onto the photo, lit
   by the photo's own light and given the fabric's weave. The bag names, product
   links, print area sizes and DTF prices come from build.py (data-bags on #md),
   so they follow products.json. Changing a print area's corners: fix them in
   the owner's tool (#setup) and copy the numbers into PHOTOS below. */
(function () {
  "use strict";
  var root = document.getElementById("md");
  if (!root || !window.HTMLCanvasElement) return;
  var CFG = JSON.parse(root.getAttribute("data-bags"));
  var IMG = root.getAttribute("data-img");

  // albedo: the fabric's colour in full, even light — each photo's light is measured against it.
  var BAGS = {
    black: { dark: true, albedo: [54, 53, 70] },
    cream: { dark: false, albedo: [246, 242, 232] }
  };
  for (var k in BAGS) {
    var c = CFG[k];
    BAGS[k].area = { w: c.area[0], h: c.area[1] };
    BAGS[k].info = c;
  }
  var flat4 = function () { return [[0, 0], [0, 0], [0, 0], [0, 0]]; };
  var PHOTOS = {
    black: { bag: "black", W: 1125, H: 2000, label: "Tampak depan", quad: [[229, 629], [901, 629], [901, 1572], [229, 1572]] },
    p8540: { bag: "cream", W: 1200, H: 1600, label: "Berdiri", quad: [[450, 878], [808, 838], [882, 1152], [485, 1245]] },
    p8536: { bag: "cream", W: 1600, H: 900, label: "Bersandar", quad: [[618, 575], [813, 515], [875, 677], [660, 747]] },
    p8535: { bag: "cream", W: 1200, H: 1600, label: "Rebah", quad: [[410, 990], [737, 902], [845, 1187], [482, 1282]] },
    p8542: { bag: "cream", W: 1200, H: 1600, label: "Dari atas", quad: [[563, 633], [700, 900], [480, 1068], [318, 753]] },
    p8543: { bag: "cream", W: 1200, H: 1600, label: "Dari atas, dekat", quad: [[480, 653], [598, 891], [400, 1015], [268, 753]] }
  };
  for (var id in PHOTOS) { PHOTOS[id].bend = flat4(); PHOTOS[id].round = 0; }
  var ORDER = ["black", "p8540", "p8536", "p8535", "p8542", "p8543"];
  var FIRST = { "baby-kanvas": "black", "kanvas-kombinasi": "p8540" };
  var MESH = 16, THUMB = 0.5, BLEND = 0.7;

  var $ = function (id) { return document.getElementById(id); };
  var view = $("md-view");
  var logoSrc = null, userLogo = false, logoName = "";
  var logos = {};
  var st = { photo: "black", lx: 0.5, ly: 0.42, size: 55, rot: 0, ink: "auto", knock: false, color: "#b85c4e", guide: true };
  var cm = function (n) { return (Math.round(n * 10) / 10).toString().replace(".", ","); };

  // ---- watermark: faint repeating pattern + the mark in a pill, bottom right
  var wmFont = "Fraunces, Georgia, serif";
  var BAG_ARC = typeof Path2D === "function" ? new Path2D("M8 9C8 5.7 9.8 3.5 12 3.5C14.2 3.5 16 5.7 16 9") : null;
  function pill(g, x, y, w, h) { var r = h / 2; g.beginPath(); g.moveTo(x + r, y); g.lineTo(x + w - r, y); g.arc(x + w - r, y + r, r, -Math.PI / 2, Math.PI / 2); g.lineTo(x + r, y + h); g.arc(x + r, y + r, r, Math.PI / 2, Math.PI * 1.5); g.closePath(); }
  function drawMark(g, x, y, u, color) {
    var icon = u * 0.64, gap = u * 0.22;
    g.save(); g.translate(x, y - icon / 2); g.scale(icon / 24, icon / 24);
    g.strokeStyle = color; g.lineWidth = 1.8; g.lineCap = "round"; g.lineJoin = "round";
    if (BAG_ARC) g.stroke(BAG_ARC);
    g.beginPath(); g.moveTo(7, 9); g.lineTo(17, 9); g.arc(17, 11, 2, -Math.PI / 2, 0); g.lineTo(19, 18.5); g.arc(17, 18.5, 2, 0, Math.PI / 2);
    g.lineTo(7, 20.5); g.arc(7, 18.5, 2, Math.PI / 2, Math.PI); g.lineTo(5, 11); g.arc(7, 11, 2, Math.PI, Math.PI * 1.5); g.closePath(); g.stroke();
    g.globalAlpha *= 0.5; g.lineWidth = 1.3; g.beginPath(); g.moveTo(5, 12.5); g.lineTo(19, 12.5); g.stroke();
    g.restore();
    g.fillStyle = color; g.textBaseline = "middle"; g.fillText("grosir.in", x + icon + gap, y + u * 0.02);
  }
  function markWidth(g, u) { g.font = "500 " + (u * 0.56).toFixed(1) + "px " + wmFont; return u * 0.64 + u * 0.22 + g.measureText("grosir.in").width; }
  function drawWatermark(g, W, H) {
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = "source-over";
    var short = Math.min(W, H), pu = short * 0.045, mw = markWidth(g, pu);
    var stepX = mw + pu * 2.6, stepY = pu * 3.4, R = Math.hypot(W, H) / 2;
    g.translate(W / 2, H / 2); g.rotate(-Math.PI / 7);
    for (var row = -Math.ceil(R / stepY); row * stepY <= R; row++) {
      var off = row % 2 ? stepX / 2 : 0;
      for (var x = -R - stepX + off; x <= R; x += stepX) {
        g.globalAlpha = 0.07; drawMark(g, x + pu * 0.04, row * stepY + pu * 0.04, pu, "#000000");
        g.globalAlpha = 0.16; drawMark(g, x, row * stepY, pu, "#ffffff");
      }
    }
    g.restore();
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = "source-over";
    var u = short * 0.05, tw = markWidth(g, u) - u * 0.86, padX = u * 0.42, pw = padX + u * 0.86 + tw + padX, m = u * 0.6;
    var px = W - m - pw, py = H - m - u;
    pill(g, px, py, pw, u); g.fillStyle = "rgba(26,26,26,.55)"; g.fill();
    drawMark(g, px + padX, py + u / 2, u, "#fffef9");
    g.restore();
  }

  // ---- geometry
  var images = {};
  function photoImage(id) {
    if (!images[id]) { var im = new Image(); im.decoding = "async"; im.src = IMG + id + ".jpg"; images[id] = im; }
    return images[id];
  }
  function loaded(im) {
    if (im.complete && im.naturalWidth) return Promise.resolve(im);
    return new Promise(function (res, rej) { im.addEventListener("load", function () { res(im); }, { once: true }); im.addEventListener("error", rej, { once: true }); });
  }
  function sq2quad(q) {
    var x0 = q[0][0], y0 = q[0][1], x1 = q[1][0], y1 = q[1][1], x2 = q[2][0], y2 = q[2][1], x3 = q[3][0], y3 = q[3][1];
    var dx1 = x1 - x2, dx2 = x3 - x2, dx3 = x0 - x1 + x2 - x3, dy1 = y1 - y2, dy2 = y3 - y2, dy3 = y0 - y1 + y2 - y3, g = 0, h = 0;
    if (Math.abs(dx3) > 1e-9 || Math.abs(dy3) > 1e-9) { var den = dx1 * dy2 - dx2 * dy1; g = (dx3 * dy2 - dx2 * dy3) / den; h = (dx1 * dy3 - dx3 * dy1) / den; }
    var a = x1 - x0 + g * x1, b = x3 - x0 + h * x3, d = y1 - y0 + g * y1, e = y3 - y0 + h * y3;
    return function (u, v) { var w = g * u + h * v + 1; return [(a * u + b * v + x0) / w, (d * u + e * v + y0) / w]; };
  }
  function makeWarp(ph, scale) {
    var hq = sq2quad(ph.quad.map(function (p) { return [p[0] * scale, p[1] * scale]; }));
    var bend = ph.bend.map(function (p) { return [p[0] * scale, p[1] * scale]; });
    var k = ph.round / 100 * 2.4;
    var R = k < 1e-3 ? function (t) { return t; } : function (t) { return 0.5 + 0.5 * Math.sin((t - 0.5) * k) / Math.sin(k / 2); };
    var f = function (u, v) {
      u = R(u); v = R(v);
      var p = hq(u, v), bu = 4 * u * (1 - u), bv = 4 * v * (1 - v);
      return [p[0] + (1 - v) * bu * bend[0][0] + u * bv * bend[1][0] + v * bu * bend[2][0] + (1 - u) * bv * bend[3][0],
              p[1] + (1 - v) * bu * bend[0][1] + u * bv * bend[1][1] + v * bu * bend[2][1] + (1 - u) * bv * bend[3][1]];
    };
    var grid = [];
    for (var j = 0; j <= MESH; j++) { var row = []; for (var i = 0; i <= MESH; i++) row.push(f(i / MESH, j / MESH)); grid.push(row); }
    return { f: f, grid: grid };
  }
  function invert(warp, x, y) {
    var u = 0.5, v = 0.5;
    for (var it = 0; it < 12; it++) {
      var p = warp.f(u, v), e = 1e-3, pu = warp.f(u + e, v), pv = warp.f(u, v + e);
      var a = (pu[0] - p[0]) / e, b = (pv[0] - p[0]) / e, c = (pu[1] - p[1]) / e, d = (pv[1] - p[1]) / e, det = a * d - b * c;
      if (Math.abs(det) < 1e-9) break;
      var rx = x - p[0], ry = y - p[1]; u += (d * rx - b * ry) / det; v += (-c * rx + a * ry) / det;
      if (Math.abs(rx) + Math.abs(ry) < 0.05) break;
    }
    return { u: u, v: v };
  }

  // ---- logo
  function sampleLogo() {
    var c = document.createElement("canvas"); c.width = 900; c.height = 520;
    var g = c.getContext("2d"); g.fillStyle = "#111"; g.strokeStyle = "#111";
    g.lineWidth = 22; g.beginPath(); g.arc(450, 150, 105, 0, Math.PI * 2); g.stroke();
    g.beginPath(); g.moveTo(385, 170); g.lineTo(450, 95); g.lineTo(515, 170); g.closePath(); g.fill();
    g.textAlign = "center"; g.font = "600 112px Fraunces, Georgia, serif";
    g.fillText("LOGO KAMU", 450, 395);
    g.font = "500 46px Inter, Arial, sans-serif";
    g.fillText("C O N T O H", 450, 480);
    return c;
  }
  function processLogo(ink) {
    var sw = logoSrc.naturalWidth || logoSrc.width, sh = logoSrc.naturalHeight || logoSrc.height;
    var k = Math.min(1, 1600 / Math.max(sw, sh));
    var c = document.createElement("canvas"); c.width = Math.max(1, Math.round(sw * k)); c.height = Math.max(1, Math.round(sh * k));
    var g = c.getContext("2d"); g.drawImage(logoSrc, 0, 0, c.width, c.height);
    if (st.knock || ink !== "original") {
      var im = g.getImageData(0, 0, c.width, c.height), d = im.data, r = 255, gg = 255, b = 255;
      if (ink === "custom") { var n = parseInt(st.color.slice(1), 16); r = n >> 16; gg = (n >> 8) & 255; b = n & 255; }
      for (var i = 0; i < d.length; i += 4) {
        if (st.knock) { var m = Math.min(d[i], d[i + 1], d[i + 2]); if (m > 235) d[i + 3] = 0; else if (m > 200) d[i + 3] = d[i + 3] * (235 - m) / 35; }
        if (ink !== "original") { d[i] = r; d[i + 1] = gg; d[i + 2] = b; }
      }
      g.putImageData(im, 0, 0);
    }
    return c;
  }
  function inkFor(bag) { return st.ink === "auto" ? (BAGS[bag].dark ? "white" : "original") : st.ink; }
  function logoFor(bag) { var ink = inkFor(bag); return logos[ink] || (logos[ink] = processLogo(ink)); }
  function resetLogos() { logos = {}; }

  // ---- scenes: one photo at one resolution, with its fabric maps and warp
  function makeScene(id, scale) {
    var ph = PHOTOS[id], W = Math.round(ph.W * scale), H = Math.round(ph.H * scale);
    var mk = function () { var c = document.createElement("canvas"); c.width = W; c.height = H; return c; };
    var s = { id: id, ph: ph, scale: scale, W: W, H: H, mk: mk, img: photoImage(id), light: null, layerA: mk(), layerB: mk(), warp: makeWarp(ph, scale) };
    s.ready = loaded(s.img).then(function () { try { buildFabric(s); } catch (e) { s.light = null; } return s; });
    return s;
  }
  function buildFabric(s) {
    var W = s.W, H = s.H, mk = s.mk;
    var src = mk(), sg = src.getContext("2d", { willReadFrequently: true }); sg.drawImage(s.img, 0, 0, W, H);
    // Blur by halving four times: averaging every step keeps the twill from turning into ripples.
    var small = src;
    for (var k = 0; k < 4; k++) {
      var c = document.createElement("canvas"); c.width = Math.max(1, small.width / 2 | 0); c.height = Math.max(1, small.height / 2 | 0);
      var cg = c.getContext("2d"); cg.imageSmoothingQuality = "high"; cg.drawImage(small, 0, 0, c.width, c.height); small = c;
    }
    var bl = mk(), bg = bl.getContext("2d", { willReadFrequently: true }); bg.imageSmoothingQuality = "high"; bg.drawImage(small, 0, 0, W, H);
    var a = sg.getImageData(0, 0, W, H).data, b = bg.getImageData(0, 0, W, H).data;
    var bag = BAGS[s.ph.bag], alb = bag.albedo, dk = Math.min(1 / Math.max(s.scale, 0.35), 1.6);
    s.light = mk(); s.detail = mk(); s.shade = mk();
    var lg = s.light.getContext("2d"), dg = s.detail.getContext("2d"), hg = s.shade.getContext("2d");
    var li = lg.createImageData(W, H), di = dg.createImageData(W, H), si = hg.createImageData(W, H), l = li.data, f = di.data, sh = si.data;
    var aL = alb[0] * 0.3 + alb[1] * 0.59 + alb[2] * 0.11;
    var lit = function (r) { return (r < 0.2 ? 0.2 : r > 1 ? 1 : r) * 255 | 0; };
    for (var i = 0; i < a.length; i += 4) {
      if (bag.dark) { var r = Math.pow((b[i] * 0.3 + b[i + 1] * 0.59 + b[i + 2] * 0.11) / aL, 0.6); l[i] = l[i + 1] = l[i + 2] = lit(r); }
      else { l[i] = lit(b[i] / alb[0]); l[i + 1] = lit(b[i + 1] / alb[1]); l[i + 2] = lit(b[i + 2] / alb[2]); }
      l[i + 3] = 255;
      var d = ((a[i] * 0.3 + a[i + 1] * 0.59 + a[i + 2] * 0.11) - (b[i] * 0.3 + b[i + 1] * 0.59 + b[i + 2] * 0.11)) * dk;
      var gv = 128 + d * 2.6; gv = gv < 0 ? 0 : gv > 255 ? 255 : gv; f[i] = f[i + 1] = f[i + 2] = gv | 0; f[i + 3] = 255;
      var m = 1 + (d < 0 ? d : 0) * 0.022; m = m < 0.6 ? 0.6 : m; sh[i] = sh[i + 1] = sh[i + 2] = m * 255 | 0; sh[i + 3] = 255;
    }
    lg.putImageData(li, 0, 0); dg.putImageData(di, 0, 0); hg.putImageData(si, 0, 0);
  }
  function tri(L, img, s0, s1, s2, d0, d1, d2) {
    var den = (s1[0] - s0[0]) * (s2[1] - s0[1]) - (s2[0] - s0[0]) * (s1[1] - s0[1]);
    if (Math.abs(den) < 1e-9) return;
    var a = ((d1[0] - d0[0]) * (s2[1] - s0[1]) - (d2[0] - d0[0]) * (s1[1] - s0[1])) / den;
    var c = ((d2[0] - d0[0]) * (s1[0] - s0[0]) - (d1[0] - d0[0]) * (s2[0] - s0[0])) / den;
    var b = ((d1[1] - d0[1]) * (s2[1] - s0[1]) - (d2[1] - d0[1]) * (s1[1] - s0[1])) / den;
    var d = ((d2[1] - d0[1]) * (s1[0] - s0[0]) - (d1[1] - d0[1]) * (s2[0] - s0[0])) / den;
    var e = d0[0] - a * s0[0] - c * s0[1], f = d0[1] - b * s0[0] - d * s0[1];
    var cx = (d0[0] + d1[0] + d2[0]) / 3, cy = (d0[1] + d1[1] + d2[1]) / 3;
    var grow = function (p) { var dx = p[0] - cx, dy = p[1] - cy, l = Math.hypot(dx, dy) || 1; return [p[0] + dx / l * 0.8, p[1] + dy / l * 0.8]; };
    var e0 = grow(d0), e1 = grow(d1), e2 = grow(d2);
    L.save(); L.setTransform(1, 0, 0, 1, 0, 0);
    L.beginPath(); L.moveTo(e0[0], e0[1]); L.lineTo(e1[0], e1[1]); L.lineTo(e2[0], e2[1]); L.closePath(); L.clip();
    L.setTransform(a, b, c, d, e, f);
    var sx = Math.max(0, Math.min(s0[0], s1[0], s2[0]) - 2), sy = Math.max(0, Math.min(s0[1], s1[1], s2[1]) - 2);
    var sw = Math.min(img.width, Math.max(s0[0], s1[0], s2[0]) + 2) - sx, sh = Math.min(img.height, Math.max(s0[1], s1[1], s2[1]) + 2) - sy;
    if (sw > 0 && sh > 0) L.drawImage(img, sx, sy, sw, sh, sx, sy, sw, sh);
    L.restore();
  }

  // ---- render: photo, then the DTF print lit and textured by the photo, then the watermark
  var flat = document.createElement("canvas");
  function render(s, g, withGuide) {
    var W = s.W, H = s.H, grid = s.warp.grid, bag = BAGS[s.ph.bag], area = bag.area;
    g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, W, H);
    if (s.img.complete && s.img.naturalWidth) g.drawImage(s.img, 0, 0, W, H);
    var logo = logoFor(s.ph.bag);
    var across = Math.hypot(grid[0][MESH][0] - grid[0][0][0], grid[0][MESH][1] - grid[0][0][1]) || 1;
    var scale = Math.min(1400, across * 2) / Math.max(area.w, area.h);
    flat.width = Math.max(1, Math.round(area.w * scale)); flat.height = Math.max(1, Math.round(area.h * scale));
    var F = flat.getContext("2d"); F.clearRect(0, 0, flat.width, flat.height);
    var w = flat.width * st.size / 100, h = w * logo.height / logo.width;
    F.save(); F.imageSmoothingQuality = "high"; F.filter = "blur(" + (0.45 * s.scale * flat.width / across).toFixed(2) + "px)";
    F.translate(st.lx * flat.width, st.ly * flat.height); F.rotate(st.rot * Math.PI / 180);
    F.drawImage(logo, -w / 2, -h / 2, w, h); F.restore();
    var r = Math.hypot(w, h) / 2 + 4, lx0 = st.lx * flat.width - r, lx1 = st.lx * flat.width + r, ly0 = st.ly * flat.height - r, ly1 = st.ly * flat.height + r;
    var L = s.layerA.getContext("2d");
    L.setTransform(1, 0, 0, 1, 0, 0); L.globalCompositeOperation = "source-over"; L.globalAlpha = 1; L.clearRect(0, 0, W, H);
    L.imageSmoothingQuality = "high";
    var cw = flat.width / MESH, ch = flat.height / MESH;
    for (var j = 0; j < MESH; j++) for (var i = 0; i < MESH; i++) {
      if ((i + 1) * cw < lx0 || i * cw > lx1 || (j + 1) * ch < ly0 || j * ch > ly1) continue;
      var s00 = [i * cw, j * ch], s10 = [(i + 1) * cw, j * ch], s01 = [i * cw, (j + 1) * ch], s11 = [(i + 1) * cw, (j + 1) * ch];
      tri(L, flat, s00, s10, s11, grid[j][i], grid[j][i + 1], grid[j + 1][i + 1]);
      tri(L, flat, s00, s11, s01, grid[j][i], grid[j + 1][i + 1], grid[j + 1][i]);
    }
    L.setTransform(1, 0, 0, 1, 0, 0);
    if (s.light) {
      var M = s.layerB.getContext("2d");
      var cut = function (srcCanvas) {
        M.globalCompositeOperation = "source-over"; M.globalAlpha = 1; M.clearRect(0, 0, W, H); M.drawImage(srcCanvas, 0, 0);
        M.globalCompositeOperation = "destination-in"; M.drawImage(s.layerA, 0, 0);
      };
      cut(s.light); L.globalCompositeOperation = "multiply"; L.globalAlpha = 1; L.drawImage(s.layerB, 0, 0);
      cut(s.detail); L.globalCompositeOperation = "soft-light"; L.globalAlpha = BLEND * 0.75; L.drawImage(s.layerB, 0, 0);
      cut(s.shade); L.globalCompositeOperation = "multiply"; L.globalAlpha = BLEND * 0.6; L.drawImage(s.layerB, 0, 0);
      L.globalCompositeOperation = "source-over"; L.globalAlpha = 1;
    }
    g.drawImage(s.layerA, 0, 0);
    drawWatermark(g, W, H);
    if (withGuide) {
      var f = s.warp.f, N = 32, lw = Math.max(1.5, Math.max(W, H) / 700), q;
      g.save(); g.beginPath();
      for (var a1 = 0; a1 <= N; a1++) { q = f(a1 / N, 0); if (a1) g.lineTo(q[0], q[1]); else g.moveTo(q[0], q[1]); }
      for (var a2 = 1; a2 <= N; a2++) { q = f(1, a2 / N); g.lineTo(q[0], q[1]); }
      for (var a3 = N - 1; a3 >= 0; a3--) { q = f(a3 / N, 1); g.lineTo(q[0], q[1]); }
      for (var a4 = N - 1; a4 > 0; a4--) { q = f(0, a4 / N); g.lineTo(q[0], q[1]); }
      g.closePath(); g.setLineDash([lw * 5, lw * 4]); g.lineWidth = lw;
      g.strokeStyle = "rgba(0,0,0,.35)"; g.lineDashOffset = lw; g.stroke();
      g.strokeStyle = "rgba(255,255,255,.85)"; g.lineDashOffset = 0; g.stroke();
      g.restore();
    }
  }

  // ---- editor (one photo at full size) and gallery (every photo at half size)
  var editor = null, tiles = [];
  function logoCm(bag) {
    var lg = logoFor(bag), wcm = BAGS[bag].area.w * st.size / 100;
    return [wcm, wcm * lg.height / lg.width];
  }
  function waHref() {
    var bag = BAGS[PHOTOS[st.photo].bag].info, d = logoCm(PHOTOS[st.photo].bag);
    var msg = "Halo grosir.in, saya sudah coba desain di website. Mau tanya harga " + bag.name + " (" + bag.variant +
      ") dengan sablon DTF, logo kira-kira " + cm(d[0]) + " x " + cm(d[1]) + " cm. Gambar mockup-nya saya kirim setelah ini.";
    return "https://wa.me/" + root.getAttribute("data-wa") + "?text=" + encodeURIComponent(msg);
  }
  function draw() {
    if (!editor) return;
    render(editor, view.getContext("2d"), st.guide);
    var bagKey = PHOTOS[st.photo].bag, bag = BAGS[bagKey].info, d = logoCm(bagKey);
    $("md-size-out").textContent = st.size + "%";
    $("md-rot-out").textContent = st.rot + "°";
    $("md-readout").textContent = "Ukuran logo di " + bag.short + ": sekitar " + cm(d[0]) + " x " + cm(d[1]) + " cm (area cetak " + bag.areaLabel + ").";
    $("md-bag").innerHTML = "";
    var t = document.createTextNode(bag.name + " · " + bag.variant + " · sablon DTF +" + bag.dtfLabel + "/sisi · ");
    var a = document.createElement("a"); a.href = bag.href; a.textContent = "Lihat produk →";
    $("md-bag").append(t, a);
    $("md-wa").href = waHref();
  }
  function openEditor(id) {
    st.photo = id;
    var s = makeScene(id, 1); editor = s;
    view.width = s.W; view.height = s.H; view.style.aspectRatio = s.W + "/" + s.H; view.classList.toggle("wide", s.W > s.H);
    tiles.forEach(function (t) { t.pick.setAttribute("aria-pressed", String(t.id === id)); });
    draw();
    s.ready.then(function () { if (editor === s) draw(); }, function () { $("md-file-note").textContent = "Foto tas gagal dimuat. Coba muat ulang halaman."; });
  }
  tiles = ORDER.map(function (id) {
    var ph = PHOTOS[id], bag = BAGS[ph.bag].info, wrap = document.createElement("div"); wrap.className = "md-tile";
    var label = bag.short + " · " + ph.label;
    var pick = document.createElement("button"); pick.type = "button"; pick.className = "md-pick"; pick.setAttribute("aria-label", "Edit di foto " + label);
    var c = document.createElement("canvas"); c.width = Math.round(ph.W * THUMB); c.height = Math.round(ph.H * THUMB); pick.append(c);
    var cap = document.createElement("div"); cap.className = "md-cap";
    var lab = document.createElement("span"), lb = document.createElement("strong"), lv = document.createElement("small");
    lb.textContent = bag.short; lv.textContent = ph.label; lab.append(lb, lv); lab.title = label;
    var save = document.createElement("button"); save.type = "button"; save.textContent = "Simpan"; save.setAttribute("aria-label", "Simpan gambar " + label);
    cap.append(lab, save); wrap.append(pick, cap); $("md-tiles").append(wrap);
    pick.addEventListener("click", function () { if (st.photo !== id) openEditor(id); view.scrollIntoView({ behavior: "smooth", block: "center" }); });
    save.addEventListener("click", function () { saveScene(id); });
    return { id: id, pick: pick, canvas: c, scene: null };
  });
  var galleryTimer = 0, galleryRun = 0;
  function refreshGallery(delay) {
    clearTimeout(galleryTimer);
    galleryTimer = setTimeout(function () {
      var run = ++galleryRun, i = 0;
      (function next() {
        if (run !== galleryRun || i >= tiles.length) return;
        var t = tiles[i++];
        if (!t.scene) t.scene = makeScene(t.id, THUMB);
        t.scene.ready.then(function () {
          if (run !== galleryRun) return;
          render(t.scene, t.canvas.getContext("2d"), false);
          requestAnimationFrame(next);
        }, next);
      })();
    }, delay == null ? 250 : delay);
  }
  var queued = false;
  function schedule() { if (!queued) { queued = true; requestAnimationFrame(function () { queued = false; draw(); }); } refreshGallery(); }
  function changed() { draw(); refreshGallery(); }

  // ---- dragging the logo
  var drag = null;
  function toCanvas(e) { var r = view.getBoundingClientRect(); return { x: (e.clientX - r.left) * editor.W / r.width, y: (e.clientY - r.top) * editor.H / r.height }; }
  function clampPos() { st.lx = Math.min(1, Math.max(0, st.lx)); st.ly = Math.min(1, Math.max(0, st.ly)); }
  view.addEventListener("pointerdown", function (e) {
    if (!editor) return;
    var p = toCanvas(e); drag = { uv0: invert(editor.warp, p.x, p.y), l0: [st.lx, st.ly] };
    view.setPointerCapture(e.pointerId); view.classList.add("dragging");
  });
  view.addEventListener("pointermove", function (e) {
    if (!drag) return;
    var p = toCanvas(e), uv = invert(editor.warp, p.x, p.y);
    st.lx = drag.l0[0] + uv.u - drag.uv0.u; st.ly = drag.l0[1] + uv.v - drag.uv0.v; clampPos(); schedule();
  });
  var end = function () { drag = null; view.classList.remove("dragging"); };
  view.addEventListener("pointerup", end); view.addEventListener("pointercancel", end);
  view.addEventListener("keydown", function (e) {
    var step = e.shiftKey ? 0.04 : 0.01, m = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }[e.key];
    if (!m) return; e.preventDefault(); st.lx += m[0]; st.ly += m[1]; clampPos(); schedule();
  });

  // ---- controls
  function setInk(ink) {
    st.ink = ink;
    root.querySelectorAll("[data-ink]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-ink") === ink)); });
    $("md-ink-color").hidden = ink !== "custom";
  }
  $("md-size").addEventListener("input", function (e) { st.size = +e.target.value; schedule(); });
  $("md-rot").addEventListener("input", function (e) { st.rot = +e.target.value; schedule(); });
  $("md-guide").addEventListener("change", function (e) { st.guide = e.target.checked; draw(); });
  $("md-knock").addEventListener("change", function (e) { st.knock = e.target.checked; resetLogos(); changed(); });
  $("md-center").addEventListener("click", function () { st.lx = 0.5; st.ly = 0.5; changed(); });
  $("md-reset").addEventListener("click", function () { st.lx = 0.5; st.ly = 0.42; st.size = 55; st.rot = 0; $("md-size").value = 55; $("md-rot").value = 0; changed(); });
  root.querySelectorAll("[data-ink]").forEach(function (b) { b.addEventListener("click", function () { setInk(b.getAttribute("data-ink")); changed(); }); });
  $("md-ink-color").addEventListener("input", function (e) { st.color = e.target.value; delete logos.custom; schedule(); });
  $("md-file").addEventListener("change", function (e) {
    var f = e.target.files[0]; if (!f) return;
    var note = $("md-file-note"), url = URL.createObjectURL(f), im = new Image();
    im.onload = function () {
      logoSrc = im; userLogo = true; logoName = f.name; resetLogos();
      note.className = "md-note"; note.textContent = f.name + " — kalau sebagian logo tidak terlihat di salah satu tas, coba tinta Putih atau Satu warna.";
      changed();
    };
    im.onerror = function () { note.className = "md-note err"; note.textContent = "File itu tidak bisa dibaca sebagai gambar. Coba PNG atau JPG."; };
    im.src = url;
  });

  // ---- saving: full size, without the print-area guide
  function saveScene(id) {
    var s = editor && editor.id === id ? editor : makeScene(id, 1);
    s.ready.then(function () {
      var out = document.createElement("canvas"); out.width = s.W; out.height = s.H; render(s, out.getContext("2d"), false);
      out.toBlob(function (blob) {
        if (!blob) return;
        var a = document.createElement("a"); a.href = URL.createObjectURL(blob);
        a.download = "grosirin-mockup-" + BAGS[PHOTOS[id].bag].info.slug + "-" + id + ".png";
        document.body.append(a); a.click(); a.remove();
        setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
      }, "image/png");
    });
  }
  $("md-save").addEventListener("click", function () { saveScene(st.photo); });

  // ---- start: the photo a product page linked to (#baby-kanvas / #kanvas-kombinasi), else the black bag
  logoSrc = sampleLogo();
  setInk("auto");
  openEditor(FIRST[location.hash.slice(1)] || "black");
  refreshGallery(400);
  if (document.fonts && document.fonts.load) {
    Promise.all([document.fonts.load("500 20px Fraunces"), document.fonts.load("600 20px Fraunces")]).then(function () {
      if (!userLogo) logoSrc = sampleLogo();
      resetLogos(); changed();
    }, function () {});
  }
})();
