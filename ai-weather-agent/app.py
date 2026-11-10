from flask import Flask, request, jsonify, render_template_string, Response
from agent_core import get_weather_json
import json

app = Flask(__name__)

# Skyline Weather mark: a sun setting behind a city skyline. Used as favicon and header logo.
LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#1c3f8f"/><stop offset=".6" stop-color="#ff7a5c"/><stop offset="1" stop-color="#ffc46b"/>
</linearGradient></defs>
<rect width="64" height="64" rx="16" fill="url(#g)"/>
<circle cx="41" cy="33" r="12" fill="#fff3c4"/>
<path d="M0 64V46h8v-8h10v10h6V30h12v18h8V40h8v10h4v14z" fill="#0b1226"/>
</svg>"""

# NOTE: raw string so JS escapes survive; avoid Jinja tokens ({{ {% {#) inside.
HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skyline Weather</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,500;12..96,800&display=swap" rel="stylesheet">
<style>
  @property --a { syntax: '<color>'; inherits: true; initial-value: #1d2b4f; }
  @property --b { syntax: '<color>'; inherits: true; initial-value: #6b5b95; }

  :root {
    --ink: #fff;
    --ink-soft: rgba(255,255,255,.72);
    --glass: rgba(255,255,255,.14);
    --line: rgba(255,255,255,.28);
  }
  /* The whole page is the sky: palette is set in JS from condition, time of day and temperature */
  body[data-ink="dark"] { --ink:#13202f; --ink-soft:rgba(19,32,47,.7); --glass:rgba(255,255,255,.45); --line:rgba(19,32,47,.25); }
  body[data-sky="clear"] .data { text-shadow: 0 2px 24px rgba(0,0,0,.18); }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; }
  body {
    font-family: 'Bricolage Grotesque', system-ui, sans-serif;
    color: var(--ink);
    background: linear-gradient(165deg, var(--a), var(--b));
    transition: --a 1.2s ease, --b 1.2s ease, color .6s ease;
    overflow-x: hidden;
  }
  #fx { position: fixed; inset: 0; width: 100%; height: 100%; pointer-events: none; }

  .stage {
    position: relative; z-index: 1; min-height: 100vh;
    display: grid; grid-template-rows: auto 1fr auto auto;
    padding: clamp(20px, 4vw, 48px);
    max-width: 1200px; margin: 0 auto;
  }

  /* Top bar */
  .top { display: flex; justify-content: space-between; align-items: center; gap: 20px; flex-wrap: wrap; }
  .brand { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 20px; letter-spacing: -.02em; }
  .brand img { width: 30px; height: 30px; display: block; }
  .search {
    display: flex; align-items: center; gap: 10px; min-width: min(100%, 320px);
    padding: 12px 20px; border-radius: 999px;
    background: var(--glass); border: 1px solid var(--line);
    backdrop-filter: blur(18px) saturate(1.4); -webkit-backdrop-filter: blur(18px) saturate(1.4);
  }
  .search:focus-within { outline: 2px solid var(--ink); outline-offset: 3px; }
  .search input { flex: 1; background: none; border: 0; outline: 0; color: var(--ink); font: 500 16px inherit; font-family: inherit; }
  .search input::placeholder { color: var(--ink-soft); }
  .search svg { width: 18px; height: 18px; stroke: var(--ink); fill: none; stroke-width: 2; stroke-linecap: round; flex: none; }
  #status { min-height: 20px; margin-top: 10px; font-size: 14px; color: var(--ink-soft); text-align: right; width: 100%; }

  /* Hero */
  .hero {
    display: grid; grid-template-columns: 1fr auto; gap: clamp(24px, 6vw, 80px);
    align-items: center; padding: 24px 0;
  }
  .place { font-size: clamp(22px, 3vw, 32px); font-weight: 500; letter-spacing: -.01em; }
  .region { color: var(--ink-soft); font-size: 16px; margin-top: 2px; }
  .temp {
    font-weight: 800; line-height: .82; letter-spacing: -.035em;
    font-size: clamp(130px, 26vw, 300px); margin: 18px 0 8px -.04em;
    display: flex; align-items: flex-start;
    font-variation-settings: 'opsz' 96;
  }
  .temp sup { font-size: .3em; font-weight: 300; letter-spacing: 0; margin: .18em 0 0 .05em; }
  body.loading .temp { opacity: .35; }
  .cond { font-size: clamp(24px, 4vw, 40px); font-weight: 300; letter-spacing: -.02em; }
  .feels { color: var(--ink-soft); margin-top: 6px; font-size: 17px; }

  /* Day-range rail: the one memorable instrument */
  .rail-wrap { position: relative; width: 150px; height: min(42vh, 340px); }
  .rail {
    position: absolute; left: 0; top: 0; bottom: 0; width: 18px; border-radius: 99px;
    background: var(--glass); border: 1px solid var(--line);
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  }
  .span {
    position: absolute; left: 3px; right: 3px; border-radius: 99px; min-height: 8px;
    background: linear-gradient(to top, #8aa2ff, #ffb36b 60%, #ff6b5e);
    transition: bottom 1s cubic-bezier(.2,.8,.2,1), height 1s cubic-bezier(.2,.8,.2,1);
  }
  .now {
    position: absolute; left: -5px; width: 28px; height: 28px; margin-bottom: -14px; border-radius: 50%;
    background: var(--ink); box-shadow: 0 0 0 6px var(--glass), 0 6px 24px rgba(0,0,0,.25);
    transition: bottom 1.1s cubic-bezier(.2,.8,.2,1);
  }
  .tag { position: absolute; left: 34px; white-space: nowrap; font-size: 15px; color: var(--ink-soft); transition: bottom 1s cubic-bezier(.2,.8,.2,1); }
  .tag b { color: var(--ink); font-weight: 800; font-size: 20px; }
  .tag.hi { transform: translateY(-4px); }    /* sits above top of span */
  .tag.lo { transform: translateY(calc(100% + 4px)); } /* hangs below bottom of span */
  .tag.nw { transform: translateY(50%); left: 40px; font-size: 14px; }

  /* Instruments */
  .instruments {
    display: grid; grid-template-columns: repeat(3, 1fr);
    border-top: 1px solid var(--line); padding-top: 24px; gap: 24px;
  }
  .inst { display: flex; align-items: center; gap: 18px; }
  .inst + .inst { border-left: 1px solid var(--line); padding-left: 24px; }
  .inst .k { color: var(--ink-soft); font-size: 15px; }
  .inst .v { font-size: 34px; font-weight: 800; letter-spacing: -.03em; }
  .inst .v small { font-size: 16px; font-weight: 500; color: var(--ink-soft); letter-spacing: 0; margin-left: 4px; }

  .streaks { width: 64px; height: 40px; flex: none; }
  .streaks path { fill: none; stroke: var(--ink); stroke-width: 3; stroke-linecap: round; stroke-dasharray: 18 42; animation: flow var(--spd, 3s) linear infinite; }
  .streaks path:nth-child(2) { animation-delay: -.9s; opacity: .7; }
  .streaks path:nth-child(3) { animation-delay: -1.7s; opacity: .5; }
  @keyframes flow { from { stroke-dashoffset: 0; } to { stroke-dashoffset: -60; } }

  .vessel { width: 40px; height: 56px; flex: none; border-radius: 6px 6px 20px 20px; border: 2px solid var(--ink); position: relative; overflow: hidden; }
  .vessel i { position: absolute; left: 0; right: 0; bottom: 0; height: 0; background: var(--ink); opacity: .85; transition: height 1.2s cubic-bezier(.2,.8,.2,1); }

  /* Hourly forecast */
  .hourly { padding: 8px 0 26px; }
  .htitle { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; font-size: 16px; font-weight: 500; margin-bottom: 12px; }
  .htitle span { color: var(--ink-soft); font-size: 14px; font-weight: 400; }
  .hscroll { overflow-x: auto; padding-bottom: 4px; }
  .hrow { display: flex; min-width: 560px; border-top: 1px solid var(--line); padding-top: 16px; }
  .hcol { flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; gap: 8px; }
  .ht { font-size: 13px; color: var(--ink-soft); }
  .hcol.first .ht { color: var(--ink); font-weight: 800; }
  .hic { font-size: 22px; line-height: 1; }
  .hp { font-size: 20px; font-weight: 800; letter-spacing: -.02em; }
  .hcurve { display: block; width: 100%; min-width: 560px; height: 56px; margin-top: 8px; }
  .hcurve path { fill: none; stroke: var(--ink); stroke-width: 2; opacity: .55; vector-effect: non-scaling-stroke; stroke-linecap: round; }

  /* Empty state */
  .empty { grid-column: 1 / -1; max-width: 560px; }
  .empty h2 { font-size: clamp(40px, 8vw, 84px); line-height: .95; letter-spacing: -.045em; font-weight: 800; }
  .empty p { margin-top: 16px; color: var(--ink-soft); font-size: 18px; }
  body.ready .empty { display: none; }
  body:not(.ready) .data, body:not(.ready) .instruments, body:not(.ready) .hourly { visibility: hidden; }

  @media (max-width: 760px) {
    .hero { grid-template-columns: 1fr; }
    .rail-wrap { height: 260px; width: 100%; }
    .instruments { grid-template-columns: 1fr; }
    .inst + .inst { border-left: 0; padding-left: 0; border-top: 1px solid var(--line); padding-top: 18px; }
  }
  @media (prefers-reduced-motion: reduce) {
    * { transition: none !important; animation: none !important; }
  }
</style>
</head>
<body>
<canvas id="fx" aria-hidden="true"></canvas>

<main class="stage">
  <div>
    <div class="top">
      <div class="brand"><img src="/favicon.svg" alt="">Skyline Weather</div>
      <label class="search">
        <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
        <input id="q" type="text" placeholder="Search for a city" autocomplete="off" aria-label="Search for a city">
      </label>
    </div>
    <div id="status" role="status" aria-live="polite"></div>
  </div>

  <section class="hero">
    <div class="empty">
      <h2>Which sky are you under?</h2>
      <p>Type a city and the whole page turns into its weather.</p>
    </div>

    <div class="data">
      <div class="place" id="city">&nbsp;</div>
      <div class="region" id="country">&nbsp;</div>
      <div class="temp"><span id="temp">0</span><sup>&deg;</sup></div>
      <div class="cond" id="cond">&nbsp;</div>
      <div class="feels">Feels like <span id="feels">0</span>&deg;</div>
    </div>

    <div class="rail-wrap" id="railwrap" aria-label="Today's temperature range">
      <div class="rail"><div class="span" id="span"></div></div>
      <div class="now" id="now"></div>
      <div class="tag hi" id="tag-hi"><b id="hi">0&deg;</b> high</div>
      <div class="tag lo" id="tag-lo"><b id="lo">0&deg;</b> low</div>
      <div class="tag nw" id="tag-now">now</div>
    </div>
  </section>

  <section class="hourly" aria-label="Hourly forecast">
    <div class="htitle">Hourly forecast <span id="hnote"></span></div>
    <div class="hscroll">
      <div class="hrow" id="hrow"></div>
      <svg class="hcurve" id="hcurve" viewBox="0 0 800 56" preserveAspectRatio="none" aria-hidden="true"><path id="hpath" d=""/></svg>
    </div>
  </section>

  <section class="instruments">
    <div class="inst">
      <svg class="streaks" id="streaks" viewBox="0 0 64 40" aria-hidden="true">
        <path pathLength="60" d="M2 8 H62"/><path pathLength="60" d="M2 20 H50"/><path pathLength="60" d="M2 32 H58"/>
      </svg>
      <div><div class="k">Wind</div><div class="v"><span id="wind">0</span><small>km/h</small></div></div>
    </div>
    <div class="inst">
      <div class="vessel" aria-hidden="true"><i id="fill"></i></div>
      <div><div class="k">Humidity</div><div class="v"><span id="hum">0</span><small>%</small></div></div>
    </div>
    <div class="inst">
      <div><div class="k">Today&rsquo;s swing</div><div class="v"><span id="swing">0</span><small>&deg; between low and high</small></div></div>
    </div>
  </section>
</main>

<script>
const $ = id => document.getElementById(id);
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- Sky canvas ---------- */
const cv = $('fx'), cx = cv.getContext('2d');
let W, H, parts = [], mode = 'clear', phase = 'day', heat = 'mild', t = 0, flash = 0;
function size() { W = cv.width = innerWidth; H = cv.height = innerHeight; seed(); }
function seed() {
  const n = { rain: 170, storm: 260, snow: 240, cloud: 8, mist: 6, clear: phase === 'night' ? 140 : 0 }[mode];
  parts = Array.from({ length: n }, () => {
    const p = { x: Math.random() * W, y: Math.random() * H };
    if (mode === 'clear') { p.r = .5 + Math.random() * 1.3; p.d = Math.random() * 6; }
    else if (mode === 'rain' || mode === 'storm') { p.l = 10 + Math.random() * 18; p.v = 12 + Math.random() * 10; }
    else if (mode === 'snow') { p.z = Math.random(); p.r = 1.2 + p.z * 3.6; p.v = .5 + p.z * 1.6; p.d = Math.random() * 6; }
    else { p.r = 120 + Math.random() * 180; p.v = .1 + Math.random() * .25; }
    return p;
  });
}
function frame() {
  t += .01; cx.clearRect(0, 0, W, H);
  const glow = (x, y, r, c) => { const g = cx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, 'rgba(' + c + ',.8)'); g.addColorStop(1, 'rgba(' + c + ',0)'); cx.fillStyle = g; cx.fillRect(0, 0, W, H); };
  if (mode === 'cloud' && phase === 'day' && (heat === 'hot' || heat === 'warm')) glow(W * .78, H * .2, heat === 'hot' ? 380 : 300, heat === 'hot' ? '255,200,120' : '255,235,190');
  if (mode === 'clear') {
    if (phase === 'night') {
      cx.fillStyle = '#fff';
      for (const p of parts) { cx.globalAlpha = .35 + .5 * Math.abs(Math.sin(t * 2 + p.d)); cx.beginPath(); cx.arc(p.x, p.y, p.r, 0, 6.3); cx.fill(); }
      cx.globalAlpha = 1; glow(W * .78, H * .2, 220, '200,215,255');
      cx.fillStyle = 'rgba(244,247,255,.96)'; cx.beginPath(); cx.arc(W * .78, H * .2, 34, 0, 6.3); cx.fill();
    } else if (phase === 'dawn' || phase === 'dusk') {
      glow(phase === 'dawn' ? W * .18 : W * .82, H * .8, 380 + Math.sin(t) * 16, '255,160,100');
    } else {
      const c = heat === 'hot' ? '255,190,100' : heat === 'cold' ? '235,246,255' : '255,240,180';
      glow(W * .78, H * .2, (heat === 'hot' ? 330 : 260) + Math.sin(t) * 14, c);
    }
  } else if (mode === 'rain' || mode === 'storm') {
    cx.strokeStyle = 'rgba(200,230,255,.45)'; cx.lineWidth = 1.2; cx.beginPath();
    for (const p of parts) {
      cx.moveTo(p.x, p.y); cx.lineTo(p.x - 3, p.y + p.l);
      p.y += p.v; p.x -= .5; if (p.y > H) { p.y = -20; p.x = Math.random() * W; }
    }
    cx.stroke();
    if (mode === 'storm') { if (Math.random() < .004) flash = 1; cx.fillStyle = 'rgba(255,255,255,' + flash * .25 + ')'; cx.fillRect(0, 0, W, H); flash *= .9; }
  } else if (mode === 'snow') {
    const day = phase !== 'night';
    cx.lineWidth = 1; cx.strokeStyle = 'rgba(70,100,140,.4)';
    for (const p of parts) {
      cx.fillStyle = 'rgba(255,255,255,' + (.6 + p.z * .4) + ')';
      cx.beginPath(); cx.arc(p.x, p.y, p.r, 0, 6.3); cx.fill(); if (day) cx.stroke();
      p.y += p.v; p.x += Math.sin(t * 2 + p.d) * .6 + .35;
      if (p.y > H) { p.y = -8; p.x = Math.random() * W; } if (p.x > W) p.x = 0;
    }
    // snowdrifts settling along the bottom edge
    const g = cx.createLinearGradient(0, H - 90, 0, H);
    g.addColorStop(0, 'rgba(255,255,255,.95)'); g.addColorStop(1, day ? 'rgba(214,226,240,.95)' : 'rgba(160,178,205,.9)');
    cx.fillStyle = g; cx.beginPath(); cx.moveTo(0, H);
    for (let x = 0; x <= W; x += 20) cx.lineTo(x, H - 44 - Math.sin(x * .006 + 1) * 16 - Math.sin(x * .017) * 7);
    cx.lineTo(W, H); cx.closePath(); cx.fill();
  } else {
    for (const p of parts) {
      const g = cx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r);
      g.addColorStop(0, 'rgba(255,255,255,.16)'); g.addColorStop(1, 'rgba(255,255,255,0)');
      cx.fillStyle = g; cx.fillRect(p.x - p.r, p.y - p.r, p.r * 2, p.r * 2);
      p.x += p.v; if (p.x - p.r > W) p.x = -p.r;
    }
  }
  if (!reduce) requestAnimationFrame(frame);
}
function hourOf(v) {
  const m = String(v || '').match(/(\d{1,2}):(\d{2})/); if (!m) return null;
  let h = +m[1] + m[2] / 60; if (/pm/i.test(v) && h < 12) h += 12; if (/am/i.test(v) && h >= 12) h -= 12; return h;
}
function phaseOf(w) {
  let h = w && hourOf(w.local_time); if (h === null || h === undefined) { const d = new Date(); h = d.getHours() + d.getMinutes() / 60; }
  const sr = (w && hourOf(w.sunrise)) ?? 6, ss = (w && hourOf(w.sunset)) ?? 18;
  if (Math.abs(h - sr) <= .75) return 'dawn';
  if (Math.abs(h - ss) <= .75) return 'dusk';
  return h > sr && h < ss ? 'day' : 'night';
}
function palette(sky, ph, temp) {
  const night = ph === 'night';
  if (sky === 'clear') {
    if (night) return ['#070b1f', '#1b2a5c'];
    if (ph === 'dawn') return ['#3b3a7a', '#ffb39a'];
    if (ph === 'dusk') return ['#2a1f55', '#ff7a5c'];
    return { cold: ['#3f86d0', '#cfe9fa'], mild: ['#1c64c8', '#9bd6f7'], warm: ['#1f6fd0', '#f7cf7a'], hot: ['#d9622b', '#ffc46b'] }[heat];
  }
  if (sky === 'cloud' && ph === 'day') {
    if (heat === 'hot') return ['#9a6a4c', '#f0c488'];
    if (heat === 'warm') return ['#68717c', '#d6c6a6'];
  }
  const day = { cloud: ['#52606f', '#aeb9c4'], rain: ['#0b2733', '#2e6a77'], storm: ['#17122b', '#4b3b70'], snow: ['#6a82a3', '#dbe6f2'], mist: ['#7f8d8b', '#d3d9d3'] };
  const nt = { cloud: ['#151b26', '#3a4556'], rain: ['#060f16', '#17363f'], storm: ['#0c0919', '#2a2043'], snow: ['#26344a', '#6a7f9c'], mist: ['#1c2423', '#4a5754'] };
  return (night ? nt : day)[sky];
}
function applySky(sky, w) {
  mode = sky; phase = phaseOf(w);
  const tmp = w ? +w.temp : 24;
  heat = tmp >= 36 ? 'hot' : tmp >= 30 ? 'warm' : tmp <= 15 ? 'cold' : 'mild';
  const [a, b] = palette(sky, phase);
  const st = document.body.style; st.setProperty('--a', a); st.setProperty('--b', b);
  document.body.dataset.sky = sky;
  if ((sky === 'snow' || sky === 'mist') && phase !== 'night') document.body.dataset.ink = 'dark'; else delete document.body.dataset.ink;
  seed(); if (reduce) frame();
}
addEventListener('resize', size); size(); applySky('clear', null); frame();

/* ---------- Helpers ---------- */
function skyFor(c) {
  c = (c || '').toLowerCase();
  if (/thunder|storm/.test(c)) return 'storm';
  if (/rain|drizzle|shower/.test(c)) return 'rain';
  if (/snow|sleet|ice/.test(c)) return 'snow';
  if (/mist|fog|haze|smoke/.test(c)) return 'mist';
  if (/cloud|overcast/.test(c)) return 'cloud';
  return 'clear';
}
function countTo(el, to) {
  to = Math.round(Number(to)); if (reduce) { el.textContent = to; return; }
  const from = Number(el.textContent) || 0, t0 = performance.now();
  (function step(now) {
    const k = Math.min(1, (now - t0) / 900), e = 1 - Math.pow(1 - k, 3);
    el.textContent = Math.round(from + (to - from) * e);
    if (k < 1) requestAnimationFrame(step);
  })(t0);
}
function say(msg) { $('status').textContent = msg || ''; }

/* ---------- Hourly forecast ---------- */
const ICONS = { clear: ['\u2600\uFE0F', '\uD83C\uDF19'], cloud: '\u2601\uFE0F', rain: '\uD83C\uDF27\uFE0F', storm: '\u26C8\uFE0F', snow: '\u2744\uFE0F', mist: '\uD83C\uDF2B\uFE0F' };
const iconFor = (sky, night) => sky === 'clear' ? ICONS.clear[night ? 1 : 0] : ICONS[sky];
const clock = h => { h = ((Math.round(h) % 24) + 24) % 24; return (h % 12 || 12) + ' ' + (h < 12 ? 'AM' : 'PM'); };
function hrOf(v) {
  const m = String(v || '').match(/(\d{1,2})(?::\d{2})?\s*(am|pm)?/i); if (!m) return null;
  let h = +m[1]; if (/pm/i.test(m[2] || '') && h < 12) h += 12; if (/am/i.test(m[2] || '') && h === 12) h = 0; return h;
}
function renderHourly(w, sky) {
  const real = Array.isArray(w.hourly) && w.hourly.length;
  let slots;
  if (real) {
    const sr = hourOf(w.sunrise) ?? 6, ss = hourOf(w.sunset) ?? 18, nowH = hourOf(w.local_time) ?? new Date().getHours();
    slots = w.hourly.slice(0, 8).map(x => { const h = hrOf(x.time) ?? nowH; return { label: x.time, temp: +x.temp, sky: skyFor(x.condition || w.condition), night: h < sr || h >= ss }; });
  } else {
    // No hourly data from the agent: estimate a daily curve from today's low/high, anchored to the current temperature
    const now = hourOf(w.local_time) ?? (new Date().getHours() + new Date().getMinutes() / 60);
    const start = Math.floor(now), mean = (+w.high + +w.low) / 2, amp = (+w.high - +w.low) / 2;
    const curve = h => mean + amp * Math.cos(2 * Math.PI * (h - 15) / 24), off = +w.temp - curve(start);
    slots = Array.from({ length: 8 }, (_, i) => { const h = start + i * 3, hh = ((h % 24) + 24) % 24;
      return { label: i === 0 ? 'Now' : clock(h), temp: curve(h) + off * Math.max(0, 1 - i / 3), sky, night: hh < 6 || hh >= 19 }; });
  }
  $('hnote').textContent = real ? '' : 'Estimated from today\u2019s high and low';
  $('hrow').innerHTML = slots.map((s, i) => '<div class="hcol' + (i === 0 ? ' first' : '') + '"><div class="ht">' + s.label +
    '</div><div class="hic">' + iconFor(s.sky, s.night) + '</div><div class="hp">' + Math.round(s.temp) + '&deg;</div></div>').join('');
  const ts = slots.map(s => s.temp), mn = Math.min(...ts), mx = Math.max(...ts), r = mx - mn;
  const pts = slots.map((s, i) => [(i + .5) / slots.length * 800, r ? 50 - (s.temp - mn) / r * 40 : 28]);
  let d = 'M' + pts[0][0] + ' ' + pts[0][1];
  for (let i = 1; i < pts.length; i++) { const [x0, y0] = pts[i - 1], [x1, y1] = pts[i], mx2 = (x0 + x1) / 2; d += ' C' + mx2 + ' ' + y0 + ' ' + mx2 + ' ' + y1 + ' ' + x1 + ' ' + y1; }
  $('hpath').setAttribute('d', d);
}

/* ---------- Render ---------- */
function render(w) {
  const temp = +w.temp, hi = +w.high, lo = +w.low, wind = +w.wind;
  $('city').textContent = w.city; $('country').textContent = w.country || '';
  $('cond').textContent = w.condition || ''; $('feels').textContent = Math.round(w.feels_like);
  countTo($('temp'), temp);
  $('wind').textContent = Math.round(wind); $('hum').textContent = Math.round(w.humidity);
  $('hi').innerHTML = Math.round(hi) + '&deg;'; $('lo').innerHTML = Math.round(lo) + '&deg;';
  $('swing').textContent = Math.max(0, Math.round(hi - lo));
  $('fill').style.height = Math.max(0, Math.min(100, w.humidity)) + '%';
  $('streaks').style.setProperty('--spd', Math.max(.8, 6 - wind / 8) + 's');

  // Range rail: scale from (min - 2) to (max + 2) so equal high/low still reads
  const min = Math.min(lo, temp) - 2, max = Math.max(hi, temp) + 2, rng = max - min || 1;
  const pos = v => ((v - min) / rng) * 100;
  $('span').style.bottom = pos(lo) + '%';
  $('span').style.height = Math.max(2, pos(hi) - pos(lo)) + '%';
  $('now').style.bottom = pos(temp) + '%';
  $('tag-now').style.bottom = pos(temp) + '%';
  $('tag-hi').style.bottom = Math.max(pos(hi), pos(lo) + 2) + '%';
  $('tag-lo').style.bottom = pos(lo) + '%';

  renderHourly(w, skyFor(w.condition));
  applySky(skyFor(w.condition), w);
  document.body.classList.add('ready');
}

/* ---------- Fetch ---------- */
async function fetchWeather() {
  const input = $('q'), query = input.value.trim();
  if (!query) return;
  document.body.classList.add('loading'); say('Looking up ' + query + '\u2026');
  try {
    const res = await fetch('/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query }) });
    const data = await res.json();
    let w;
    try { w = JSON.parse(data.answer.replace(/```json/g, '').replace(/```/g, '').trim()); }
    catch (e) { say('The weather service sent back something unreadable. Try the search again.'); return; }
    if (w.error) { say(w.error); return; }
    render(w); say(w.note || ''); input.value = ''; input.blur();
  } catch (err) {
    console.error(err); say('Couldn\u2019t reach the server. Check that the app is running, then try again.');
  } finally { document.body.classList.remove('loading'); }
}
$('q').addEventListener('keydown', e => { if (e.key === 'Enter') fetchWeather(); });
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/favicon.svg')
def favicon():
    return Response(LOGO, mimetype='image/svg+xml')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('query', '').strip()
    if not user_input:
        return jsonify({'answer': json.dumps({"error": "Enter a city name to search."})})
    return jsonify({'answer': get_weather_json(user_input)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)