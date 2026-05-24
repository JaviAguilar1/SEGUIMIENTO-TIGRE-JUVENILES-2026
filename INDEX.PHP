<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#0a0f1e">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>Tigre 2026 — Divisiones Inferiores</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow+Condensed:wght@400;600;700&family=Barlow:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg:        #05080f;
  --surface:   #0a0f1e;
  --surface2:  #0d1528;
  --surface3:  #111e38;
  --border:    #1a2d5a;
  --border2:   #243f7a;
  --red:       #c0152a;
  --red2:      #e01830;
  --red-glow:  rgba(192,21,42,0.35);
  --blue:      #1a3a8f;
  --blue2:     #2450c0;
  --blue-glow: rgba(26,58,143,0.35);
  --gold:      #c9a227;
  --gold2:     #f0c040;
  --win:       #22c55e;
  --draw:      #f59e0b;
  --loss:      #ef4444;
  --text:      #d8e4ff;
  --muted:     #5a7099;
  --white:     #ffffff;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Barlow', sans-serif;
  min-height: 100vh;
  background-image:
    radial-gradient(ellipse 70% 35% at 20% 0%, rgba(26,58,143,0.22) 0%, transparent 65%),
    radial-gradient(ellipse 50% 25% at 80% 0%, rgba(192,21,42,0.15) 0%, transparent 60%);
}

/* ═══════════════════════════════════════════
   HEADER
═══════════════════════════════════════════ */
header {
  background: linear-gradient(180deg, #0d1528 0%, #08111f 100%);
  border-bottom: 3px solid var(--red);
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: sticky;
  top: 0;
  z-index: 200;
  min-height: 70px;
  box-shadow: 0 4px 40px rgba(0,0,0,0.7), 0 2px 0 var(--red);
}
header::before {
  content: '';
  position: absolute;
  bottom: -1px; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.crest-wrap {
  position: relative;
  flex-shrink: 0;
}
.crest-img {
  width: 54px;
  height: 54px;
  object-fit: contain;
  filter: drop-shadow(0 0 12px rgba(192,21,42,0.6)) drop-shadow(0 2px 4px rgba(0,0,0,0.8));
}
.header-text h1 {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 28px;
  letter-spacing: 5px;
  color: var(--white);
  line-height: 1;
  text-shadow: 0 0 30px rgba(192,21,42,0.5), 0 1px 3px rgba(0,0,0,0.8);
}
.header-text p {
  color: var(--muted);
  font-size: 11px;
  margin-top: 3px;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-family: 'Barlow Condensed', sans-serif;
}
.header-right {
  margin-left: auto;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}
.gold-star-row { color: var(--gold2); font-size: 18px; letter-spacing: 2px; }
.season-pill {
  background: var(--red);
  color: var(--white);
  font-family: 'Bebas Neue', sans-serif;
  font-size: 12px;
  letter-spacing: 2px;
  padding: 2px 10px;
  border-radius: 20px;
}

/* ═══════════════════════════════════════════
   TABS
═══════════════════════════════════════════ */
.tabs-wrapper {
  background: linear-gradient(180deg, #09122a, #05080f);
  border-bottom: 1px solid var(--border);
  padding: 0 12px;
  display: flex;
  overflow-x: auto;
  scrollbar-width: none;
  position: sticky;
  top: 70px;
  z-index: 100;
}
.tabs-wrapper::-webkit-scrollbar { display: none; }
.tab {
  padding: 12px 18px;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 15px;
  letter-spacing: 2px;
  color: var(--muted);
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all .2s;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 7px;
}
.tab:hover { color: var(--text); background: rgba(26,58,143,0.12); }
.tab.active { color: var(--gold2); border-bottom-color: var(--red); background: rgba(26,58,143,0.18); }
.tab-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.tab.general-tab.active { color: var(--gold2); border-bottom-color: var(--gold); }

/* ═══════════════════════════════════════════
   MAIN LAYOUT
═══════════════════════════════════════════ */
.main { padding: 20px; max-width: 1500px; margin: 0 auto; }
.cat-panel { display: none; }
.cat-panel.active { display: block; animation: fadeIn .25s ease; }
@keyframes fadeIn { from { opacity:0; transform:translateY(5px); } to { opacity:1; transform:none; } }

/* ═══════════════════════════════════════════
   SECTION TITLES
═══════════════════════════════════════════ */
.section-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 17px;
  letter-spacing: 3px;
  color: var(--gold2);
  margin: 20px 0 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.section-title .st-bar {
  width: 4px; height: 18px;
  background: linear-gradient(180deg, var(--red2), var(--blue2));
  border-radius: 2px;
  flex-shrink: 0;
}
.section-title::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--border), transparent);
}

/* ═══════════════════════════════════════════
   RESULTS TABLE
═══════════════════════════════════════════ */
.results-table-wrap {
  overflow-x: auto;
  margin-bottom: 28px;
  border-radius: 10px;
  border: 1px solid var(--border);
  box-shadow: 0 4px 24px rgba(0,0,0,0.5);
}
table.results { width: 100%; border-collapse: collapse; font-size: 12px; }

table.results thead tr:first-child th {
  background: linear-gradient(180deg, var(--red) 0%, #8a0f1e 100%);
  color: var(--white);
  font-family: 'Bebas Neue', sans-serif;
  font-size: 13px;
  letter-spacing: 2px;
  padding: 8px 10px;
  text-align: center;
  white-space: nowrap;
  border-right: 1px solid rgba(255,255,255,0.1);
}
table.results thead tr:first-child th:last-child { border-right: none; }

table.results thead tr.subhead th {
  background: linear-gradient(180deg, #0d1a3a, #08111f);
  color: var(--gold);
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 6px 8px;
  text-align: center;
  border-bottom: 1px solid var(--border2);
  border-right: 1px solid var(--border);
  white-space: nowrap;
}
table.results thead tr.subhead th:last-child { border-right: none; }

table.results td {
  padding: 5px 6px;
  border-bottom: 1px solid rgba(26,45,90,0.5);
  border-right: 1px solid rgba(26,45,90,0.3);
  text-align: center;
  vertical-align: middle;
}
table.results td:last-child { border-right: none; }
table.results tr:nth-child(even) td { background: rgba(10,15,30,0.5); }
table.results tr:hover td { background: rgba(26,58,143,0.18); }

/* DIVIDER */
.divider-block td {
  background: linear-gradient(90deg, rgba(192,21,42,0.15), rgba(26,58,143,0.08)) !important;
  font-family: 'Bebas Neue', sans-serif;
  letter-spacing: 2px;
  font-size: 11px;
  color: var(--red2) !important;
  text-align: left !important;
  padding: 6px 14px !important;
  border-left: 3px solid var(--red) !important;
}

/* CELLS */
.fecha-num {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 16px;
  color: var(--muted);
  width: 32px;
  min-width: 32px;
}
.rival-name {
  text-align: left !important;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 600;
  font-size: 13px;
  min-width: 145px;
  letter-spacing: .3px;
}
.cond-badge {
  display: inline-block;
  padding: 2px 7px;
  border-radius: 3px;
  font-size: 10px;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
  letter-spacing: 1px;
}
.cond-L { background: rgba(26,58,143,0.4); color: #93c5fd; border: 1px solid rgba(36,80,192,0.5); }
.cond-V { background: rgba(192,21,42,0.3); color: #fca5a5; border: 1px solid rgba(192,21,42,0.5); }

/* SCORE */
.score-cell { display: flex; align-items: center; justify-content: center; gap: 4px; }
.score-input {
  width: 34px;
  background: rgba(5,8,15,0.9);
  border: 1px solid var(--border2);
  border-radius: 4px;
  color: var(--white);
  font-size: 15px;
  font-weight: 700;
  text-align: center;
  padding: 3px 2px;
  transition: all .2s;
  font-family: 'Barlow Condensed', sans-serif;
}
.score-input:focus {
  outline: none;
  border-color: var(--gold);
  background: rgba(26,58,143,0.3);
  box-shadow: 0 0 8px rgba(201,162,39,0.3);
}
.score-sep { color: var(--muted); font-weight: 900; font-size: 14px; }

/* RESULT BADGE */
.result-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px; height: 22px;
  border-radius: 4px;
  font-weight: 800;
  font-size: 10px;
  font-family: 'Barlow Condensed', sans-serif;
}
.result-W { background: rgba(34,197,94,.2); color: var(--win); border: 1px solid rgba(34,197,94,.4); }
.result-D { background: rgba(245,158,11,.2); color: var(--draw); border: 1px solid rgba(245,158,11,.4); }
.result-L { background: rgba(239,68,68,.2); color: var(--loss); border: 1px solid rgba(239,68,68,.4); }

/* ═══════════════════════════════════════════
   LINK CELLS
═══════════════════════════════════════════ */
.link-group-header {
  background: linear-gradient(180deg, #0a1a3a, #06101f) !important;
  color: var(--blue2) !important;
  border-top: 2px solid var(--blue2) !important;
}
.link-cell { min-width: 90px; max-width: 130px; }
.link-wrap { display: flex; gap: 3px; align-items: center; }
.link-input {
  flex: 1;
  min-width: 0;
  background: rgba(5,8,15,0.7);
  border: 1px solid rgba(26,45,90,0.6);
  border-radius: 4px;
  color: #93c5fd;
  font-size: 10px;
  padding: 4px 6px;
  transition: all .2s;
  font-family: 'Barlow', sans-serif;
}
.link-input:focus {
  outline: none;
  border-color: var(--gold);
  background: rgba(26,58,143,0.25);
  box-shadow: 0 0 6px rgba(201,162,39,0.2);
}
.link-input::placeholder { color: rgba(90,112,153,0.5); font-style: italic; }
.link-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px; height: 22px;
  flex-shrink: 0;
  background: rgba(26,58,143,0.35);
  border: 1px solid var(--border2);
  border-radius: 4px;
  color: #93c5fd;
  font-size: 11px;
  cursor: pointer;
  text-decoration: none;
  transition: all .2s;
}
.link-btn:hover { background: var(--red); border-color: var(--red); color: white; }
.link-btn.empty { opacity: 0.25; pointer-events: none; }

/* ═══════════════════════════════════════════
   STATS GRID
═══════════════════════════════════════════ */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(105px, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}
.stat-card {
  background: linear-gradient(135deg, var(--surface2), var(--surface));
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 10px;
  text-align: center;
  transition: all .2s;
  position: relative;
  overflow: hidden;
}
.stat-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  border-radius: 10px 10px 0 0;
}
.stat-card.pts::before { background: var(--gold); }
.stat-card.win::before { background: var(--win); }
.stat-card.draw::before { background: var(--draw); }
.stat-card.loss::before { background: var(--loss); }
.stat-card.gf::before { background: var(--blue2); }
.stat-card.gc::before { background: var(--red2); }
.stat-card.dg::before { background: #a78bfa; }
.stat-card.pj::before { background: var(--muted); }
.stat-card:hover {
  transform: translateY(-2px);
  border-color: var(--border2);
  box-shadow: 0 6px 20px rgba(0,0,0,0.4);
}
.stat-card .val {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 36px;
  line-height: 1;
  margin-bottom: 4px;
}
.stat-card .lbl {
  font-size: 9px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-family: 'Barlow Condensed', sans-serif;
}
.stat-card.pts .val { color: var(--gold2); }
.stat-card.win .val { color: var(--win); }
.stat-card.draw .val { color: var(--draw); }
.stat-card.loss .val { color: var(--loss); }
.stat-card.gf .val { color: #60a5fa; }
.stat-card.gc .val { color: #f87171; }
.stat-card.dg .val { color: #c4b5fd; }
.stat-card.pj .val { color: var(--text); }

/* ═══════════════════════════════════════════
   PERIOD TABS
═══════════════════════════════════════════ */
.periodo-tabs { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.ptab {
  padding: 5px 13px;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  cursor: pointer;
  transition: all .2s;
  font-family: 'Barlow Condensed', sans-serif;
  letter-spacing: .5px;
}
.ptab:hover { color: var(--text); border-color: var(--red); }
.ptab.active { background: var(--red); color: white; border-color: var(--red); box-shadow: 0 2px 10px var(--red-glow); }

/* ═══════════════════════════════════════════
   CHARTS
═══════════════════════════════════════════ */
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px; }
.chart-card {
  background: linear-gradient(135deg, var(--surface2), var(--surface));
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px;
}
.chart-card h3 {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 13px;
  letter-spacing: 2px;
  color: var(--gold);
  margin-bottom: 14px;
}
canvas { width: 100% !important; }

/* PIES */
.pies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 12px;
  margin-bottom: 28px;
}
.pie-mini-card {
  background: linear-gradient(135deg, var(--surface2), var(--surface));
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
}
.pie-mini-card h4 {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 13px;
  letter-spacing: 1.5px;
  color: var(--gold);
  margin-bottom: 10px;
  text-align: center;
}
.pie-stat-row {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 8px;
  font-size: 11px;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 600;
}

/* ═══════════════════════════════════════════
   GENERAL TABLE
═══════════════════════════════════════════ */
.gen-table-wrap {
  overflow-x: auto;
  margin-bottom: 28px;
  border-radius: 10px;
  border: 1px solid var(--border);
}
table.gen-table { width: 100%; border-collapse: collapse; font-size: 13px; }
table.gen-table th {
  background: linear-gradient(180deg, var(--red) 0%, #8a0f1e 100%);
  color: white;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 13px;
  letter-spacing: 1.5px;
  padding: 10px 12px;
  text-align: center;
  border-right: 1px solid rgba(255,255,255,0.1);
  white-space: nowrap;
}
table.gen-table th:last-child { border-right: none; }
table.gen-table td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  border-right: 1px solid rgba(26,45,90,0.3);
  text-align: center;
}
table.gen-table td:last-child { border-right: none; }
table.gen-table tr:nth-child(even) td { background: rgba(10,15,30,0.5); }
table.gen-table tr:hover td { background: rgba(26,58,143,0.15); }
.cat-cell {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 16px;
  letter-spacing: 1px;
  text-align: left !important;
}
.dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 7px; }

/* ═══════════════════════════════════════════
   PWA GUIDE
═══════════════════════════════════════════ */
.guide-wrap {
  background: linear-gradient(135deg, var(--surface2), var(--surface));
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 32px;
  max-width: 820px;
  margin: 0 auto 32px;
}
.guide-wrap h2 {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 24px;
  letter-spacing: 3px;
  color: var(--gold2);
  margin-bottom: 28px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--border2);
  padding-bottom: 16px;
}
.step-block {
  display: flex;
  gap: 16px;
  margin-bottom: 22px;
  align-items: flex-start;
}
.step-num {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--red), var(--red2));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 18px;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 2px 10px var(--red-glow);
}
.step-body h3 {
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
  font-size: 16px;
  color: var(--gold2);
  margin-bottom: 6px;
  letter-spacing: .5px;
}
.step-body p {
  font-size: 13px;
  color: var(--text);
  line-height: 1.65;
  margin-bottom: 6px;
}
.step-body strong { color: var(--gold2); }
code {
  background: rgba(5,8,15,0.8);
  border: 1px solid var(--border2);
  border-radius: 4px;
  padding: 2px 7px;
  font-size: 12px;
  color: #93c5fd;
  font-family: monospace;
}
.code-block {
  background: rgba(3,5,12,0.95);
  border: 1px solid var(--border2);
  border-left: 3px solid var(--blue2);
  border-radius: 8px;
  padding: 14px 16px;
  margin: 8px 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #93c5fd;
  overflow-x: auto;
  white-space: pre;
  line-height: 1.7;
}
.tip-box {
  background: rgba(26,58,143,0.15);
  border: 1px solid var(--blue2);
  border-left: 4px solid var(--blue2);
  border-radius: 8px;
  padding: 14px 18px;
  margin-top: 20px;
  font-size: 13px;
  color: var(--text);
  line-height: 1.7;
}
.tip-box strong { color: var(--gold2); }

/* ═══════════════════════════════════════════
   MISC
═══════════════════════════════════════════ */
.scroll-top {
  position: fixed;
  bottom: 22px; right: 22px;
  width: 42px; height: 42px;
  background: linear-gradient(135deg, var(--red), var(--blue));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  font-size: 18px;
  font-weight: 800;
  box-shadow: 0 4px 20px rgba(192,21,42,0.5);
  z-index: 99;
  transition: transform .2s;
}
.scroll-top:hover { transform: scale(1.1); }

@media (max-width: 750px) {
  .charts-row { grid-template-columns: 1fr; }
  .pies-grid  { grid-template-columns: repeat(auto-fill, minmax(150px,1fr)); }
  .stats-grid { grid-template-columns: repeat(4, 1fr); }
  .stat-card .val { font-size: 28px; }
  .main { padding: 8px; }
  header { padding: 8px 12px; min-height: 56px; gap: 10px; }
  .crest-img { width: 38px; height: 38px; }
  .header-text h1 { font-size: 20px; letter-spacing: 3px; }
  .header-text p { display: none; }
  .header-right { display: none; }
  .tabs-wrapper { top: 56px; }
  .tab { padding: 10px 12px; font-size: 13px; letter-spacing: 1px; }
  /* Link columns: stack input + btn vertically, narrow */
  .link-cell { min-width: 70px; max-width: 90px; }
  .link-input { font-size: 9px; padding: 3px 4px; }
  .link-btn   { width: 20px; height: 20px; font-size: 10px; }
  .results-table-wrap { font-size: 11px; }
  .rival-name { min-width: 100px; font-size: 11px; }
  .score-input { width: 28px; font-size: 13px; }
  .section-title { font-size: 14px; }
  .guide-wrap { padding: 16px; }
  .chart-card { padding: 12px; }
}
@media (max-width: 400px) {
  .stats-grid { grid-template-columns: repeat(4, 1fr); gap: 6px; }
  .stat-card { padding: 10px 6px; }
  .stat-card .val { font-size: 24px; }
  .stat-card .lbl { font-size: 8px; }
}
</style>
</head>
<body>
<header>
  <div class="crest-wrap">
    <img class="crest-img" id="escudoImg" alt="Escudo Club Atlético Tigre">
  </div>
  <div class="header-text">
    <h1>TIGRE 2026</h1>
    <p>Divisiones Inferiores · 4TA a 9NA</p>
  </div>
  <div class="header-right">
    <div class="gold-star-row">★</div>
    <div class="season-pill">TEMPORADA 2026</div>
    <button onclick="clearData()" title="Borrar todos los datos guardados"
      style="margin-top:4px;background:rgba(192,21,42,0.2);border:1px solid rgba(192,21,42,0.4);
      border-radius:4px;color:rgba(255,100,100,0.7);font-size:9px;padding:2px 6px;cursor:pointer;
      font-family:Barlow Condensed,sans-serif;letter-spacing:1px;">🗑 RESET</button>
  </div>
</header>

<div class="tabs-wrapper" id="mainTabs"></div>
<div class="main" id="mainContent"></div>
<div class="scroll-top" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
// ============================================================
//  ESCUDO (embedded base64)
// ============================================================
const ESCUDO_B64 = '/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAoHCRIDASIAAhEBAxEB/8QAHQABAAIDAQEBAQAAAAAAAAAAAAcIBAUGCQIDAf/EAFwQAQAABAICBhIOCQMDBQABBQABAgMEBQYHEQghN3Wz0hIXGDEzNTZBUVVWYXJzlJWxtBMUFRYiUlRxdoGSw9HTMkJTYnSCkaGyI6LBQ5PCCSQ0Y/Alo0SD4fH/xAAcAQEAAgMBAQEAAAAAAAAAAAAABAUDBgcCCAH/xABDEQEAAQICAwoMBgICAwEAAwAAAQIDBAURNFEGEzFBcXKRobHREhUWISIyMzVSU4HwFBdhssHSguFCYiOSovEHJEP/2gAMAwEAAhEDEQA/AKZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGRhlnXxHErXD7WWE1xdVpKNKWMdUIzTRhCENfW24gxxN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxjmWdMfaOw840eMCERN3Ms6Y+0dh5xo8Y5lnTH2jsPONHjAhETdzLOmPtHYecaPGOZZ0x9o7DzjR4wIRE3cyzpj7R2HnGjxmDmDY26V8CwHEMbxHB7KnZYfa1Lq4nlv6U0ZadOWM80YQhHXHahHaBD4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHIabtxjPH0dxD1ao69yGm7cYzx9HcQ9WqA8swAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG80fdXuXt9LbhZWjbzR91e5e30tuFlB6vgAgbZI5zzflvNWHWmXcw3GF29Wx9kqU6VvQqQmm5OaGvXUpzR50Ic6KLOWtpP7ub/wAis/yXbbLTq1wre6HCToZQbtyqK5iJdUyHKMDfy+1cuWomqYnz6P1l2HLW0n93N/5FZ/knLW0n93N/5FZ/kuPGLfa9q38Q5d8mnodhy1tJ/dzf+RWf5Jy1tJ/dzf8AkVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/AMis/wAlx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/wAis/yTlraT+7m/8is/yXHhvte08Q5d8mnodhy1tJ/dzf8AkVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/AMis/wAk5a2k/u5v/IrP8lx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/wAis/yXHhvte08Q5d8mnodhy1tJ/dzf+RWf5Jy1tJ/dzf8AkVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/AMis/wAlx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/wAis/yTlraT+7m/8is/yXHhvte08Q5d8mnodhy1tJ/dzf8AkVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/AMis/wAk5a2k/u5v/IrP8lx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/wAis/yXHhvte08Q5d8mnodhy1tJ/dzf+RWf5Jy1tJ/dzf8AkVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/AMis/wAlx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/wAis/yTlraT+7m/8is/yXHhvte08Q5d8mnodhy1tJ/dzf8AkVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/AMis/wAk5a2k/u5v/IrP8lx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/wAis/yXHhvte08Q5d8mnodhy1tJ/dzf+RWf5Jy1tJ/dzf8AkVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/AMis/wAlx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/wAis/yTlraT+7m/8is/yXHhvte08Q5d8mnodhy1tJ/dzf8AkVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/AMis/wAk5a2k/u5v/IrP8lx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/wAis/yXHhvte08Q5d8mnodhy1tJ/dzf+RWf5Jy1tJ/dzf8AkVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/AMis/wAlx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/wAis/yTlraT+7m/8is/yXHhvte08Q5d8mnodhy1tJ/dzf8AkVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/AMis/wAk5a2k/u5v/IrP8lx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/wAis/yXHhvte08Q5d8mnodhy1tJ/dzf+RWf5Jy1tJ/dzf8AkVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/AMis/wAlx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/wAis/yTlraT+7m/8is/yXHhvte08Q5d8mnodhy1tJ/dzf8AkVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/AMis/wAk5a2k/u5v/IrP8lx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/wAis/yXHhvte08Q5d8mnodhy1tJ/dzf+RWf5Jy1tJ/dzf8AkVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/AMis/wAlx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/wAis/yTlraT+7m/8is/yXHhvte08Q5d8mnodhy1tJ/dzf8AkVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/AMis/wAk5a2k/u5v/IrP8lx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/wAis/yXHhvte08Q5d8mnodhy1tJ/dzf+RWf5Jy1tJ/dzf8AkVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/AMis/wAlx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/wAis/yTlraT+7m/8is/yXHhvte08Q5d8mnodhy1tJ/dzf8AkVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/AMis/wAk5a2k/u5v/IrP8lx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/wAis/yXHhvte08Q5d8mnodhy1tJ/dzf+RWf5Jy1tJ/dzf8AkVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/AMis/wAlx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/wAis/yTlraT+7m/8is/yXHhvte08Q5d8mnodhy1tJ/dzf8AkVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/AMis/wAk5a2k/u5v/IrP8lx4b7XtPEOXfJp6HYctbSf3c3/kVn+SctbSf3c3/kVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JOWtpP7ub/wAis/yXHhvte08Q5d8mnodhy1tJ/dzf+RWf5Jy1tJ/dzf8AkVn+S48N9r2niHLvk09DsOWtpP7ub/yKz/JWE2O2P45mPIle/wAwYpVxK7lxCpSlrVKVOSMJISSRhLqpyyw58Y9bXtqlrRbFTc2ud86vB02exXVVVomWubqcrweGwPh2bcUzpjzx9UtOQ03bjGePo7iHq1R17kNN24xnj6O4h6tUTHN3lmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3mj7q9y9vpbcLK0beaPur3L2+ltwsoPV8AFadlp1a4VvdDhJ0Mpm2WnVrhW90OEnQyrr3ry7Nub912eSe2QBiXgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAtFsVNza53zq8HTVdWi2Km5tc751eDps+G9dqm7L3d/lH8pachpu3GM8fR3EPVqjr3IabtxjPH0dxD1aonuUPLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AK07LTq1wre6HCToZTNstOrXCt7ocJOhlXXvXl2bc37rs8k9sgDEvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABaLYqbm1zvnV4Omq6tFsVNza53zq8HTZ8N67VN2Xu7/ACj+UtOQ03bjGePo7iHq1R17kNN24xnj6O4h6tUT3KHlmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3mj7q9y9vpbcLK0beaPur3L2+ltwsoPV8AFadlp1a4VvdDhJ0Mpm2WnVrhW90OEnQyrr3ry7Nub912eSe2QBiXgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABLLGaaEssIxjHnQhDngDY22A47c7dvguJVvF2s83ogyYZRzXGXkoZYxvV2faFXimiWKb9qOGqOlpRsrjL2P28vJXGB4nRh2Z7SeX0wa6pJPTnjJPLNLNDnwmhqjA0PVNdNXqzpfwAewAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABaLYqbm1zvnV4Omq6tFsVNza53zq8HTZ8N67VN2Xu7/KP5S05DTduMZ4+juIerVHXuQ03bjGePo7iHq1RPcoeWYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAVp2WnVrhW90OEnQymbZadWuFb3Q4SdDKuvevLs25v3XZ5J7ZAGJeAAAAAAAAO20K5PsM8Z3kwLErm5t6EbapV5O3jLCfXLq1Q+FCMNW2nPmacodvMd+3S4iMNifut0/4Gv/AMLfpdi3TVTpmHOt1ObYzCY7e7NyaY8GJ0dKD+Zpyh28x37dLiHM05Q7eY79ulxE4DNvNGxrnlFmfzp6u5B/M05Q7eY79ulxDmacodvMd+3S4icA3mjYeUWZ/Onq7kH8zTlDt5jv26XEOZpyh28x37dLiJwDeaNh5RZn86eruQfzNOUO3mO/bpcQ5mnKHbzHft0uInAN5o2HlFmfzp6u5B/M05Q7eY79ulxDmacodvMd+3S4icA3mjYeUWZ/Onq7kH8zTlDt5jv26XEOZpyh28x37dLiJwDeaNh5RZn86eruQfzNOUO3mO/bpcQ5mnKHbzHft0uInAN5o2HlFmfzp6u5B/M05Q7eY79ulxDmacodvMd+3S4icA3mjYeUWZ/Onq7kH8zTlDt5jv26XERzp50T4Ho/y/YYjheIYjdVLm69hmluZpIwhDkIza4cjLDb2ltkF7MnqKwXfGPBzPF21RFEzELXI87x+Ix9q3cuzNMz5482yVWgEF1MAAAAdzoRybh+es6RwPErm6tqELWpW5O3jLCbXLGWEIfChGGrbcMl7Yk7q0291b/KR7txE1REq3N71dnA3bludExE6JSXzNOUO3mO/bpcQ5mnKHbzHft0uInATt5o2OU+UWZ/Onq7kH8zTlDt5jv26XEOZpyh28x37dLiJwDeaNh5RZn86eruQfzNOUO3mO/bpcQ5mnKHbzHft0uInAN5o2HlFmfzp6u5WbSxoOy3lDR/ieYrDFcWr3NpClGSnWmpxkjyVWSSOvVJCPOmj11f11dkluK5g8G39YpKVImIpimrRDoG5PG38Zg6q79XhTFUx9NEADC2gAAAAAAAAAAB929GtcV5KFvSnrVak0JZJJJYzTTRjzoQhDnxH5M6Hw+qNKrXqy0aNOerUnjqlkkljGM0exCEOem3Rxse8bxiWlf5ruJsGs5tUYW0kITXM8O/r2qf1649mEFhcl5Eyrk+hCTAcHoW9XkdU1xNDk60/Z1zx2/qhqh3mejD1VcPmatmW6zB4SZotenV+nB092lVfKOg/P2YJZK1XDpMItptv2TEJo05tXi4QjP/AFhBK2W9jXl+2hLUx7HL7EJ4bcadvJLQk+aOvkpo/VGCdxJpw9ENMxe6zMcROimrwI/Tvnz9jicF0T6O8JlhC2ypYVZofrXUsbiMY9n/AFIxdZYYdh9hJCSxsLW1lhDVCFGjLJD+0GUMsUxHBChvYq/fnTdrmrlmZAH6wDHvrCxvpOQvbO3upPi1qUs8P7wZAP2JmJ0w4zGtFejzF4Te2sqYdJNNz5raSNvHX2f9OMqPsx7GzLd1CafAsaxDDqkduEleWWvTh3ofozQ/rFOg8Tboq4YWWHzrH4b2d2frOmOidMKa5v0F5+wGE9a3saeM20u37JYTcnPq79OMITa/mhFGdxRrW9eehcUqlGrJHkZ5J5YyzSx7EYR5z0Wc7nLJGVs328aWPYPb3M+rVJXhDkK0nzTw2/q16u8wV4aP+MtowO7a5TMU4qjTG2PNPRwT1KECbtJex9xvBpauIZTrT4zZS65o200IQuZId6ENqp9WqPeihOtTqUas9KrTmp1JJoyzSTQ1RljDnwjDrRRaqJpnRLesDmOGx1Hh2KtMdccsPkB5TQAAAAAAAAABP2iPQhlzOOj/AA7MV/iuK0Lm6jVhPToTU4SQ5CrPJDVrljHnSw66AV0djNuKYF89z6xUZsPTFVWiWsbq8bfweDprsVeDPhRH00S5fmacodvMd+3S4hzNOUO3mO/bpcROAl7zRsc+8osz+dPV3IP5mnKHbzHft0uIczTlDt5jv26XETgG80bDyizP509Xcg/macodvMd+3S4hzNOUO3mO/bpcROAbzRsPKLM/nT1dyD47GnKOraxzHIR781LiPzn2NGV4w+BmDGZY9+FOP/inQN5o2HlFmfzp6u5AFfYyYRHoGar6Tw7WSb0Rg1l5sYrmXXG0zjSqdiFWwjL/AHhUj6Fkg3i3sZaN1GaU/wD+vVT3Kn4jsbs60IRmtMSwW7hDnS+y1JJo/VGTV/dy2L6GdJOGwjNUy1WuJIfrWtWStr+qWMZv7LsjxOGolOtbs8wo9eKavp3S88sUwrFMKrew4pht5Y1PiXNCanH+k0IMN6KXVtb3dCahdUKVelNtTU6kkJpY/PCLgc0aGNHuPQnmnwOTDq83/Ww+b2GMP5YfA/rKx1YWeKV3hd3FmrzX7cx+sTp7v5UpE6502OGO2Ms9xlfE6OK0obcLevqo1vmhH9Gb64yoXxvCMUwS/nsMXw+5sbqTn0q9OMk2rsw18+HfhtI9VFVPDDasFmmEx0abFcT+nH0cLCAeVgAAAAAAAAAAO10L5QsM754p4FiNzc29Ce3qVYz28ZYT65YbX6UIwcUljYpbrtD+Cr+iD1biJqiJV2bXa7OCu3KJ0TFMzCUeZpyh28x37dLiHM05Q7eY79ulxE4CfvNGxyjyizP509Xcg/macodvMd+3S4hzNOUO3mO/bpcROAbzRsPKLM/nT1dyD+Zpyh28x37dLiHM05Q7eY79ulxE4BvNGw8osz+dPV3IP5mnKHbzHft0uIczTlDt5jv26XETgG80bDyizP509Xcg/macodvMd+3S4hzNOUO3mO/bpcROAbzRsPKLM/nT1dyD+Zpyh28x37dLiHM05Q7eY79ulxE4BvNGw8osz+dPV3IP5mnKHbzHft0uIczTlDt5jv26XETgG80bDyizP509Xcg/macodvMd+3S4hzNOUO3mO/bpcROAbzRsPKLM/nT1dyD+Zpyh28x37dLiKyZisqeG5gxHDqM009O1uqtGSabnxhLPGWEY9/aehbz+zx1a47vjccJMj4iimmI0Q2/cjmWKxly7F+uatERo62nARm8gAAAAAAAC0WxU3NrnfOrwdNV1aLYqbm1zvnV4Omz4b12qbsvd3+UfylpyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqie5Q8swAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG80fdXuXt9LbhZWjbzR91e5e30tuFlB6vgArTstOrXCt7ocJOhlM2y06tcK3uhwk6GVde9eXZtzfuuzyT2yAMS8AAAAAAAAS1sT91un/A1/8Ahb9UDYn7rdP+Br/8Lfp2G9Ryndn7xjmx/IAkNTAAAAAAAAAAAAAAEF7MnqKwXfGPBzJ0QXsyeorBd8Y8HMxXvUld7nPednl/iVWgFc7OAAAAJe2JO6tNvdW/ykRCl7Yk7q0291b/ACke7Xrwqc993XubK3YCzcTAAAAR3sktxXMHg2/rFJSpdXZJbiuYPBt/WKSlSDifWh1HcTqFfPnspAEduIAAAAAAAACUtCWiPEM83EuJ4l7LZZfpz6pqsIap7mMOfLT19bszc6HW1x537TTNU6IRcZjLODtTevVaIj7836uY0b6P8w57xONtg9vyNtTjD2xeVdcKVGHfj15uxLDb+rbW10Y6Lss5Et5allQ9uYpGXVVv68sI1I9mEkOdJL3obfZjF1eA4PhmA4VQwvCLKlZ2dCXVTpU4aoQ78evGMevGO3FnJ9uzFHn43K853SYjMZmij0bezby93AAMzWwAAAAAAAAAAABH2lTRPlzPdCe4qU4YfjEJf9O+oyQ1zdiFSX9eH94daKQR+VUxVGiUjDYq9hbkXbNXg1QoRn7JeP5JxiOHY5aRp8lrjRrybdKvLDryTdf5o7cOvBzr0EzXl3B804LWwjG7KS6tavWjtTSTdaaWPPlmh2YKe6Y9FuLZAxH2aXk73BK0+q3vIS/ox+JU1c6b+0efDrwhBu2Zo88cDqGQ7pbeYaLN70bnVPJ+v6dCPQGBtQAAAAAAAAujsZtxTAvnufWKily6Oxm3FMC+e59YqJGG9dp27bUKOfHZUkgBOcuAAAAAAAAAAAAGozVlrAs0YbNh+PYZb31COvkfZJfhSR7Ms0NuWPfhGDbhMaXui5VbqiqidExxwqdpc0EYplySti+V5q2K4VLrmqUIw13FCHZ1Q/Tlh2YbcOvDajFC70ZQVp40K0MZp3GZMo20tHFIa6lzZSQ1SXXXjNJDrVO9zpvn58S7h+Olv+RbrJqmLGNnkq7+/p2qtj+1JJ6dSanUkmknljGWaWaGqMIw58IwfxEb+AD9AAAAAAEsbFLddofwVf0QROljYpbrtD+Cr+iD3a9eFVnfu69zZ7FwQFm4kAAAAAAAAAAAAAAPP7PHVrju+Nxwkz0Bef2eOrXHd8bjhJkXFcEN73De1vckdstOAhujgAAAAAAAC0WxU3NrnfOrwdNV1aLYqbm1zvnV4Omz4b12qbsvd3+UfylpyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqie5Q8swAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG80fdXuXt9LbhZWjbzR91e5e30tuFlB6vgArTstOrXCt7ocJOhlM2y06tcK3uhwk6GVde9eXZtzfuuzyT2yAMS8AAAAAAAAS1sT91un/AANf/hb9UDYn7rdP+Br/APC36dhvUcp3Z+8Y5sfyAJDUwAAAAAAAAAAAAABBezJ6isF3xjwcydEF7MnqKwXfGPBzMV71JXe5z3nZ5f4lVoBXOzgAAACXtiTurTb3Vv8AKREKXtiTurTb3Vv8pHu168KnPfd17myt2As3EwAAAEd7JLcVzB4Nv6xSUqXV2SW4rmDwbf1ikpUg4n1odR3E6hXz57KQBHbiAAAAAAA73Qpo8us/5mhRqQqUcItIwnvriXsdanLH402r6oa496P7TTNU6IYMTibeFtVXrs6KYbzQHonrZ1vpcZxmnUo5ft59UefLNdzw/Ulj1pYfrTfVDb1xhbuztreytKVpaUKdC3oyQkpUqcsJZZJYQ1QhCEOdB8YZY2eGYfb4fh9vTtrW3pwp0qVOGqWSWHOhBkLG3biiHHM5zi7md7w6vNTHBGz/AHtAGRTgAAAAAAAAAAAAAAADFxfDrHF8NuMNxO1pXVncSRkq0qkNcs0P/wB1+sygftNU0zpjhUy046LLzIeJ+3bGFS5wC5n1UK0duajNH/pz9/sR6/z60ZvQ7GsMsMZwq5wvE7WndWdzJGnVpTw2poR9EevCPPhHbUu00aOL7R/mD2OX2S4we6mjNZXMYdbr05+xPD+8NuHXhCDes+D544HUtzW6H8bTGHxE/wDkjgn4o7//ANcEAjtvAAAAAAF0djNuKYF89z6xUUuXR2M24pgXz3PrFRIw3rtO3bahRz47KkkAJzlwAAAAAAAAAAAAAAACveye0XyXFvXzxgFtqr04clidCnD9OX9tCHZh+t2YbfWjrrU9GKkklSnNTqSyzyTQjCaWaGuEYR60VJtPGSPeRnqvbWtOMMLvYRubGPWlljHbp/yx2vm5GPXQsRb0elDpO5DOZvU/g70+ePV5Nn04v05HAAIzeQAAAAABLGxS3XaH8FX9EETpY2KW67Q/gq/og92vXhVZ37uvc2excEBZuJAAAAAAAAAAAAAADz+zx1a47vjccJM9AXn9njq1x3fG44SZFxXBDe9w3tb3JHbLTgIbo4AAAAAAAAtFsVNza53zq8HTVdWi2Km5tc751eDps+G9dqm7L3d/lH8pachpu3GM8fR3EPVqjr3IabtxjPH0dxD1aonuUPLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AK07LTq1wre6HCToZTNstOrXCt7ocJOhlXXvXl2bc37rs8k9sgDEvAAAAAAAAEtbE/dbp/wADX/4W/ef2UMzYzlPGIYvgV1C1vIU5qcJ40pZ/gzc+GqaEYdZ2fL10nd0FLyGhxEmzepop0S0jdBucxWY4vfrVVMRoiPPM/r+krnCmPL10nd0FLyGhxDl66Tu6Cl5DQ4jL+JoUnkVmHxUdM/1XOFMeXrpO7oKXkNDiHL10nd0FLyGhxD8TQeRWYfFR0z/Vc4QLsbNI2bs5ZqxKxzDicl3b0LH2anLC3p09U3sksNeuWWEedGKemaiuK40w13Mcvu5ffmxdmJmNnB5+gAekEAABH+n/ADLjGVNHdXF8CuoW15Lc0qcKkacs/wAGaMdcNU0IwflU+DGmWfC4erE3qbNHDVOiNKQBTHl66Tu6Cl5DQ4hy9dJ3dBS8hocRg/E0Np8isw+Kjpn+q5wpjy9dJ3dBS8hocQ5euk7ugpeQ0OIfiaDyKzD4qOmf6rnIL2ZPUVgu+MeDmRLy9dJ3dBS8hocRoM7aRc3ZysaFlmLE5LuhQq+y05YW9Onqm1Rhr1yywjzoxeLl+mqmYhY5TuVxmDxlu/cqp0UzxTOng5HJgIjoIAAAAl7Yk7q0291b/KREKXtiTurTb3Vv8pHu168KnPfd17myt2As3EwAAAEd7JLcVzB4Nv6xSUqXV2SW4rmDwbf1ikpUg4n1odR3E6hXz57KQBHbiAAAAAA2GW8Hv8wY7Z4LhlGNW7u6sKdOXrbfPjHsQhDXGMetCEV6NHeU8OyVlS1wLD4QmhThyVetq1TVqsf0p4/P1odaEIQ6yJ9ibkaFhg9XOmIUYe2r6EaVjCaG3JRhH4U/zzRhq+aH7yeU7D2/Bjwpct3W5vOJv/hbc+hRw/rV/rg5dIAkNPAAAAAclpC0iZWyPbcljV9ruppeSpWdDVPXqd/ketDvzRhB+TMRGmWWxYuX64t2qZmZ4oda/K7urazoRr3dxRt6UvPnqzwllh9cVT877ITNuMTz0MAp0cCtI7UJpIQq15od+eaGqH1QhGHZRPi+LYpi9zG5xXEbu/rR/wCpcVpqk39YxR6sTTHA2/B7isTdjwsRXFH6cM93XK8GIaTMgWE0ZbjN2ERmhz4UriFWMPsa2sm00aMoTcjHNVHX3ratGH+Ckwx/iqti5p3EYOI9K5V1d0rz2GlPR3fTQlo5uwuWMed7NU9h/wA4QdVYX1liFCFxYXlvd0Y86pQqwnlj9cI6nncysLxLEcLuoXWGX91ZV5edVt6s1OaH1wjCL9jFTxwwX9w1qY/8N2Yn9YiezQ9DxUrIuyCzZg09O3zBJTx2zhtRmn1U7iWHenhDVN/NCMY9mCxmj/P2Wc8WUa+B30Jq8kuutaVYchXpfPL14d+GuHfSKLtNfA1PMsgxmXelcp007Y88f6+rqQGRSgAAADUZwy5hWa8v3OCYxQhVta8vPh+lTm608setND/9ta23Qpp80x0ssyVst5ZrSVcbmhyNxcS6ppbOEetDs1O91uvt7TxXVFMaak/LcJicViKaMN63Dp2frpVv0g5Zr5PzdfZfuLqhdTW0/wAGrSmhGE0sYa5Yxh+rNqjDXLHnf0i0L7r1atxXqV69WerVqTRnnnnmjGaaaMdcYxjHnxfCsnRp8zt9qmum3TFc6Z0eeeDTIAMgAAAAujsZtxTAvnufWKily6Oxm3FMC+e59YqJGG9dp27bUKOfHZUkgBOcuAAAAAcJp4zFi2VdG95jOCXMtve0q1GWSeanLPCEJp4QjtTQjDnRflU+DGlnw2HqxN6mzRw1TER9Xdindtp/0j0ptdS+sK8OxUs5If46m/wnZLZmozSwxTAMKvJIc/2CaejNH64xmh/ZhjEUNjubjsyojzRTPJPfoWlERZO2QOSsaqyW2KQucCuJtrXcwhPR19j2SXnfPNCEEtW9ajcUJK9vVp1qNSWE0lSSaE0s0I86MIw2owZaa6auCVBi8BicHV4N+iaeX+J4JfYD0iAAAACK9k9leXH9Glxf0qfJXmDze26cYQ2/Y+dVh83I/C/kglR+N9bUb2yr2dxJCejXpzUqksevLNDVGH9IvNVPhRMJWBxVWExFF+n/AIzp7+mHnYMzHLCphWNX2F1ui2dzUt59rryTRlj6GGq3dqaoqiKo4JAB6AAAAEsbFLddofwVf0QROljYpbrtD+Cr+iD3a9eFVnfu69zZ7FwQFm4kAAAADkNMuN4ll3RpjONYRXhQvraSnGlUjJLPyMY1JJY7U0IwjtRirBy9dJ3dBS8hocRirvU0Tole5XuexWZ2pu2ZpiInR55n9J4onaucKY8vXSd3QUvIaHEOXrpO7oKXkNDiPH4mhZ+RWYfFR0z/AFXOFMeXrpO7oKXkNDiHL10nd0FLyGhxD8TQeRWYfFR0z/Vc4Ux5euk7ugpeQ0OIcvXSd3QUvIaHEPxNB5FZh8VHTP8AVc4Ux5euk7ugpeQ0OIcvXSd3QUvIaHEPxNB5FZh8VHTP9Vznn9njq1x3fG44SZ2fL10nd0FLyGhxEdX91Xvr64vbmfk69xVmq1ZtUIa5poxjGOqG1DbiwXrsVxGhsu5vIsRlddyq9MT4URwTP8xD8QGBtoAAAAAAAAtFsVNza53zq8HTVdWi2Km5tc751eDps+G9dqm7L3d/lH8pachpu3GM8fR3EPVqjr3IabtxjPH0dxD1aonuUPLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AK07LTq1wre6HCToZTNstOrXCt7ocJOhlXXvXl2bc37rs8k9sgDEvAAAAAAAAAAAAAAE5bDbq6xjez72RadVjYbdXWMb2feyLTp+H9RyPdd7zq5I7ABnayAAIn2Vu5FX/AI2h6YpYRPsrdyKv/G0PTFju+pK0yT3jZ50dqnwCtduAAAAAAAAAAEvbEndWm3urf5SIhS9sSd1abe6t/lI92vXhU577uvc2VuwFm4mAAAAjvZJbiuYPBt/WKSlS6uyS3FcweDb+sUlKkHE+tDqO4nUK+fPZSAI7cQAAABv9HWW6+bs6YZgFHkoQuq0IVp5f1KUNueb6pYR+vU0CyOw5yzCW3xbN1xT+FPH2jaxjDnQhqmqR+uPIQ196L3ao8KqIVWdY/wDAYKu9HDwRyzwd6wVhaW9hY0LGzpS0ba3py0qVOXnSSSw1QhD5oQfsCzcTmZmdMgA/AAAEE7JHSxPgklTKGW7nkcSqSar66px27aWMP0JY9aeMOfH9WHfjtea64ojTKdl+X3sffizajzz1Rtl96ctN1LAalfLuUalOvikuuS4vNqanbR68ssOdNPDr9aHfjrhCsGIXl3iF7Vvb65rXNzWmjPUq1Z4zTzx7MYx578I7cdcRXXLk1z53YMryjD5ba8C1Hn4545/1+gA8LQAAAAZWFYjfYTiFHEMNu61pd0ZuSp1qU8ZZpY/PBig81UxVGieBbPQdpots1xo4BmSalaY5q5GjWh8Gnd/N8Wfvc6PW7CZnnPJNNJPLPJNGWaWOuWaEdUYR7K1+x10se+m2kyzmG4h7t0JP9CtNH/5kkIdf/wCyEOf2YbfWimWb2n0anN90m5qMPE4rCx6PHGz9Y/Ts5OCaQEpo4Cv2yA00QsfbGVcn3UI3e3Tvb+nHao9aNOnH43Zm63Oht7cPFdcURplPy7Lr+YXotWY5Z4ojbLL0/wCmaTBIV8r5TuZZ8Ujrku72SOuFr2ZJI9ep2Y/q/Pzqu1J56k81SpNNPPNGMZppo64xjHrxfyMYxjGMYxjGO3GMRX3Lk1zpl2DKsqsZbZ3u1Hn4545n74IAHhZgAAAAAC6Oxm3FMC+e59YqKXLo7GbcUwL57n1iokYb12nbttQo58dlSSAE5y4AAAARdspdxzEf4i34SCUUXbKXccxH+It+Eg8XPUlZ5N7wsc6ntU3AVjt4mbYx6Qb7Bc1W2VL64nq4RiVT2KjJPNr9r14/oxl7EJo7UYdmMI9nXDLb5Jnmp5zwSeSMYTy4jbxljDs+ySvVFU01RMIGZ4S3i8LXauRpiYn6TxS9AgFo4YAAAAAAo9p8s4WOmDMdGWGqE11Ct/3JJZ//ACcOkrZNwhDTTjerryW+v/sU0aqu560u55VVNeBs1Tx009kADyngAAACWNiluu0P4Kv6IInSxsUt12h/BV/RB7tevCqzv3de5s9i4ICzcSAAAAR/sidxnMXiqXDU1Jl2dkTuM5i8VS4ampMg4r1odQ3EajXzp7IAEduQAAAAAAAAAAAAAAAAAAtFsVNza53zq8HTVdWi2Km5tc751eDps+G9dqm7L3d/lH8pachpu3GM8fR3EPVqjr3IabtxjPH0dxD1aonuUPLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AK07LTq1wre6HCToZTNstOrXCt7ocJOhlXXvXl2bc37rs8k9sgDEvAAAAAAAAAAAAAAE5bDbq6xjez72RadVjYbdXWMb2feyLTp+H9RyPdd7zq5I7ABnayAAIn2Vu5FX/AI2h6YpYRPsrdyKv/G0PTFju+pK0yT3jZ50dqnwCtduAAAAAAAAAAEvbEndWm3urf5SIhS9sSd1abe6t/lI92vXhU577uvc2VuwFm4mAAAAjvZJbiuYPBt/WKSlS6uyS3FcweDb+sUlKkHE+tDqO4nUK+fPZSAI7cQAAABfDRJgMMt6OMDwmMnIVadrLUrw6/ss/w5/900YfUpdo5wmGO58wPCZpeSp3N9SlqQ/+vkoRn/2wiv0l4Wnhlz/dxip0WsPH61T2R/IAluegAAAOK0z53pZFyTcYnJGSbEK8fYLGnNt66sYfpRh2JYa4x+aEOupBeXNe8u613dVp61etPGpVqTx1zTzRjrjGMezGKT9k7mubMWkevh1GpyVjg0I2tOEI7Uav/Vm+fkvg/wAkEVq+/X4VWjY67uXyyMFg4rqj06/PPJxR98YAwtlAAAAAAAAH74feXWH31C+sa89vc29SFSlVkjqmkmhHXCMH4A/JiJjRK72hXSBbZ+yrLczxkp4ra6qd/Ql2tU3Wnlh8WbVGMOxHXDrO7UK0b5vxHJGarbHMPjGaEseQuKEY6pa9KP6UkfTCPWjCEUq6btOUMcw+GA5Nq16FnXpQjeXc0sZKk8JobdKWHPhCGvVNHr86G1txm0YiPB9Lhc0zHcle/HRRho/8dXn08VO2J/jb9JbTZAaaP/kZUydd9mne4jSm/rTpRh/eaHzQ7KuQIldc1zplveW5ZYy6zFq1HLPHM/qAPKxAAAAAAAAF0djNuKYF89z6xUUuXR2M24pgXz3PrFRIw3rtO3bahRz47KkkAJzlwAAAAi7ZS7jmI/xFvwkEoou2Uu45iP8AEW/CQeLnqSs8m94WOdT2qbg+7ejWuK0tG3pVK1WeOqWSSWM00Y96EFY7dM6Hw7nQRl24zHpQwahSpxmoWdeW9uZtW1LTpxhNt/PGEsv8zPyToVz1mWrTnq4bPg9lNH4Vxfyxpx1d6n+lHvbUId9aPRho/wAEyBg01lhks1a5rao3V3UhD2StNDnfNLDb1Sw53fjriz2rNVU6Z4GrZ9uiw2GsVWrVUVXJjR5vPo08cz/DrgE9ycAAAAB8XFanb0KletPCSlTljPPNHnQhCGuMQiNKkuyDu5b3THmKtLHXCWvJS+uSnJJH+8rg2wzLiU+M5ixLF6muE17d1biMI9bk54zav7teqqp0zMu84OzvGHt2p/4xEdEaAB+JIAAAAljYpbrtD+Cr+iCJ0sbFLddofwVf0Qe7Xrwqs793XubPYuCAs3EgAAAGBmDB8Nx/B7jCMXtoXVjcQhCrSjNNLyUIRhNDbljCPPhDruM5SujHuWpeV1+OkIeZppnhhJs43E2KfBtXKqY/SZjsR7yldGPctS8rr8c5SujHuWpeV1+OkIfm907GbxrjvnV/+096PeUrox7lqXldfjnKV0Y9y1Lyuvx0hBvdOw8a4751f/tPej3lK6Me5al5XX45yldGPctS8rr8dIQb3TsPGuO+dX/7T3o95SujHuWpeV1+OcpXRj3LUvK6/HSEG907DxrjvnV/+096ENMeivIOBaM8bxbCsvU7a9tqMs1GrC4rTcjGM8sOdNPGHOjHrKqrvbIHcczH/Dy8JIpCiYiIiqNDou47EXr+Erqu1zVPhcczPFG0AR23AAAAAAAAC0WxU3NrnfOrwdNV1aLYqbm1zvnV4Omz4b12qbsvd3+UfylpyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqie5Q8swAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG80fdXuXt9LbhZWjbzR91e5e30tuFlB6vgArTstOrXCt7ocJOhlM2y06tcK3uhwk6GVde9eXZtzfuuzyT2yAMS8AAAAAAAAAAAAAATlsNurrGN7PvZFp1WNht1dYxvZ97ItOn4f1HI913vOrkjsAGdrIAAifZW7kVf8AjaHpilhE+yt3Iq/8bQ9MWO76krTJPeNnnR2qfAK124AAAAAAAAAAS9sSd1abe6t/lIiFL2xJ3Vpt7q3+Uj3a9eFTnvu69zZW7AWbiYAAACO9kluK5g8G39YpKVLq7JLcVzB4Nv6xSUqQcT60Oo7idQr589lIAjtxAAAASlsWbCF7pfsq0Ya4WVtXuP8AZyEP7zrjqs7Da3hPnbGbvVt0sN9jhHwqksf/AAWmT8PHoOT7sbnh5lNOymI/n+QBnaqAANbmvFZMCyzieM1NUZbG0qV9UevGWWMYQ+uMNTZI22TF/NY6HMXhJHVPczUaEI96NSWMf9sIvNU6KZlLwFj8Ribdqf8AlVEdMqZ3Narc3NW4rzxqVas8Z55o8+aaMdcY/wBX5gq3dojR5oAB+gACSKWg3SZVpSVZMApxknlhNLH29Q24R/nRu9EML6WWviZP8YM1m3FenS1fdLnWIyuLc2YifC06dOni0bJjap1yitJ3c/S8uocc5RWk7ufpeXUOOucJH4ahqvlrmHw0dE/2Ux5RWk7ufpeXUOOcorSd3P0vLqHHXOD8NQeWuYfDR0T/AGUx5RWk7ufpeXUOOcorSd3P0vLqHHXOD8NQeWuYfDR0T/ZTHlFaTu5+l5dQ45yitJ3c/S8uocdc4Pw1B5a5h8NHRP8AZTHlFaTu5+l5dQ45yitJ3c/S8uocdc4Pw1B5a5h8NHRP9lMeUVpO7n6Xl1DjnKK0ndz9Ly6hx1zg/DUHlrmHw0dE/wBlJ8X0M6RMKwq7xS+wSnStbSjPXrTwvKM3IySwjNNHVCbXHahHnI+X00q7mOad57rgplC0e9biiY0Nu3N5vfzO1XXeiImJ0ebT/MyAMLZAAAABdHYzbimBfPc+sVFLl0djNuKYF89z6xUSMN67Tt22oUc+OypJACc5cAAAANfmHBMKzBhk+GYzZU7yznmlmmpT69UYwjrhzu+2AcL1RXVRVFVM6JhyVpoz0f2s0JqWT8GmjD9pay1P8tbosNwvDMMp+x4bh1nZSc7kbehLTh/SWEGWPyKYjgZbmJvXfaVzPLMyAP1gAAAAAAEbbJDM0uXNF9/Sp1ORu8U/9jQhr29U8P8AUj9UkJtvsxgklTPZG53lzhnqehY1vZMKwuE1vbRlj8GpNr/1KkPnjCEIdmEsI9dhvV+DS2Dc1l043HU6Y9Gjzz9OCPrPVpRkAr3YgAAAAABLGxS3XaH8FX9EETpY2KW67Q/gq/og92vXhVZ37uvc2excEBZuJAAAAAAAAAAAAAAOE2QO45mP+Hl4SRSFd7ZA7jmY/wCHl4SRSFCxXrQ6duI1K5zv4gARm6AAAAAAAAC0WxU3NrnfOrwdNV1aLYqbm1zvnV4Omz4b12qbsvd3+UfylpyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqie5Q8swAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG80fdXuXt9LbhZWjbzR91e5e30tuFlB6vgArTstOrXCt7ocJOhlM2y06tcK3uhwk6GVde9eXZtzfuuzyT2yAMS8AAAAAAAAAAAAAATlsNurrGN7PvZFp1WNht1dYxvZ97ItOn4f1HI913vOrkjsAGdrIAAifZW7kVf+NoemKWET7K3cir/AMbQ9MWO76krTJPeNnnR2qfAK124AAAAAAAAAAS9sSd1abe6t/lIiFL2xJ3Vpt7q3+Uj3a9eFTnvu69zZW7AWbiYAAACO9kluK5g8G39YpKVLq7JLcVzB4Nv6xSUqQcT60Oo7idQr589lIAjtxAAAAWD2F8uvFcyz6udQt4f1mn/AAWWVn2F88IYxmSnr25rehNq+aaf8VmFhh/Zw5Bur96XP8f2wAMzXAABDmy8qRk0WW8sI9ExSjLH7FSP/CY0P7LijGroqpzw51HEqM8fszy/+THd9SVtkOjxlZ0/FCowCtdsAAAAHohhfSy18TJ/jB53vRDC+llr4mT/ABglYXjaBu69Wx/l/DJATHPAAAAAAAAAAHNaVdzHNO891wUyha+eleMIaMM0xj2ouof/ANKZQxCxXDDpO4fV7vLHYAIzeQAAABdHYzbimBfPc+sVFLl0djNuKYF89z6xUSMN67Tt22oUc+OypJACc5cAAAAAAAAAAAAAAAi3ThpasMj2U+F4ZPSu8w1ZPgUufLbQjzp6nf68Jevz47XP81VRTGmUnB4O9jLsWbMaZn70z+jTbJjSZJl7CamVMGuIe697T1XNSSO3a0ZodnrTzQ53Yhrjta4Kov3xG9u8Rv69/fXFS4urieNSrVqTa5p5o7cYxi/BXXLk1zpdkyfKreWYeLVPnmfPM7Z7tgA8LUAAAAAASxsUt12h/BV/RBE6WNiluu0P4Kv6IPdr14VWd+7r3NnsXBAWbiQAAAAAAAAAAAAADhNkDuOZj/h5eEkUhXe2QO45mP8Ah5eEkUhQsV60OnbiNSuc7+IAEZugAAAAAAAAtFsVNza53zq8HTVdWi2Km5tc751eDps+G9dqm7L3d/lH8pachpu3GM8fR3EPVqjr3IabtxjPH0dxD1aonuUPLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AK07LTq1wre6HCToZTNstOrXCt7ocJOhlXXvXl2bc37rs8k9sgDEvAAAAAAAAAAAAAAE5bDbq6xjez72RadVjYbdXWMb2feyLTp+H9RyPdd7zq5I7ABnayAAIn2Vu5FX/jaHpilhE+yt3Iq/wDG0PTFju+pK0yT3jZ50dqnwCtduAAAAAAAAAAEvbEndWm3urf5SIhS9sSd1abe6t/lI92vXhU577uvc2VuwFm4mAAAAjvZJbiuYPBt/WKSlS6uyS3FcweDb+sUlKkHE+tDqO4nUK+fPZSAI7cQAAAE37Dm6hTz9itpGOr2bDIzw78Zakn/ABNFapTHYy4h7Q0xYVJNNyMl3JWt5o/PTjGH+6WVc5Ow06aHKN2VrwMx8L4qYntj+ABIaoAAOB2QuGzYnofx+lJLrno0ZbmXvQpzyzzR+zCZ3zHxKzoYhh1zYXMvJULmjPRqS9mWaEYRh/SL8qjTEwkYS/8Ah79F34ZieiXncM7MWF3OB49f4Pdw1V7K4noT7XPjLNGGuHejq1sFVO8U1RXTFVPBIAPQAA9EML6WWviZP8YPO96IYX0stfEyf4wSsLxtA3derY/y/hkgJjngAAAAAAAAADkNNNX2HRRmaeMdWvDqsn2ocj/yoqupskrqFroZx2OvVNVhRpS9/kq0mv8AtrUrQsVPpQ6duIo0YO5Vtq/iABGboAAAALo7GbcUwL57n1iopcujsZtxTAvnufWKiRhvXadu21Cjnx2VJIATnLgAAAAAAAAAAAB+V3cW9pbVLm6r0qFClLGapUqTwllkhDnxjGO1CDSaRMZxjL+Ub3F8EweGLXdvLyfteNSMvwevNDVCMZtXP5GGqMYa9tTHPukPNedq8Y43iU0baE3JSWdH4FCT+Xrx782uPfYrl6KGwZLufu5ppriqKaInzzwz0d+hNGl3T/RpSVsHyLNCrVjrkqYnNL8GTxUsefH96O12IR56uF1cV7q5qXN1WqV69WaM9SpUmjNNPNHbjGMY7cYvzEGu5VXOmXUMtyrDZdb8CzHLPHPL96AB4WQAAAAAAAAljYpbrtD+Cr+iCJ0sbFLddofwVf0Qe7Xrwqs793XubPYuCAs3EgAAAAcLp9urqy0RY9dWVzWtrinTpRkq0Z4yTy/60kNqMNuG0p177s190+NeX1eMw3L0UTo0Nkybc5czSzN2muKdE6OD9In+V/xQD33Zr7p8a8vq8Y992a+6fGvL6vGY/wAVGxb+Q1750dE96/4oB77s190+NeX1eMe+7NfdPjXl9XjH4qNh5DXvnR0T3r/igHvuzX3T415fV4x77s190+NeX1eMfio2HkNe+dHRPev+KAe+7NfdPjXl9XjHvuzX3T415fV4x+KjYeQ1750dE964myB3HMx/w8vCSKQtpeZkzFe209reY/itzQqQ1T0qt5Unkmh34Rjqi1bBdub5OlteQ5RVldiq1VV4WmdPVEfwAMS8AAAAAAAAFotipubXO+dXg6arq0WxU3NrnfOrwdNnw3rtU3Ze7v8AKP5S05DTduMZ4+juIerVHXuQ03bjGePo7iHq1RPcoeWYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAVp2WnVrhW90OEnQymbZadWuFb3Q4SdDKuvevLs25v3XZ5J7ZAGJeAAAAAAAAAAAAAAJy2G3V1jG9n3si06rGw26usY3s+9kWnT8P6jke673nVyR2ADO1kAARPsrdyKv/ABtD0xSwifZW7kVf+NoemLHd9SVpknvGzzo7VPgFa7cAAAAAAAAAAJe2JO6tNvdW/wApEQpe2JO6tNvdW/yke7Xrwqc993XubK3YCzcTAAAAR3sktxXMHg2/rFJSpdXZJbiuYPBt/WKSlSDifWh1HcTqFfPnspAEduIAAADaZQxWOB5qwrGIRj/7K8pV46uvCWeEYw+uEIwegdOeSpTlqU5oTSTQhNLNCO1GEeu86F39AuPwzForwa6mn5KvbUvadfb24TUvgw19+MsJZvrSsLV55hoW7jCzNu1iI4pmJ+vnjsl3QCY50AAAAq/sucmzWWO22crOl/7a/hCheRhD9GtLD4M0fClhq+eTvoGegubMBw/M2Xb3AsUp8na3dOMk2rnyx58Jod+EYQjDvwUYz9lXE8m5nusCxST/AFKUddKrCGqWtTj+jPL3o/2jrh1kHEW/BnwodS3JZtGJw/4WufTo4P1p/wBcHQ0ICO3AAAeiGF9LLXxMn+MHnetFZ7JLKtC0o0ZsCxqMadOWWMYQpdaGr4yRh66adOlpu67LsTjYtbxR4WjwtP10J3EG80tlTtDjX9KXHOaWyp2hxr+lLjpO/UbWk+TuZ/Jnq705CDeaWyp2hxr+lLjnNLZU7Q41/SlxzfqNp5O5n8mervTkIgyrp6wPMuYrLA8My7jU91eVYU5NcKeqWHPjNH4XOhDXGPegl97pqirgQMXgcRg6opv0+DMgD0iAAAAIX2X9/wC19HFlYyzap7vEZNcOzJJJPNH+/IqnJ92ZeKwq5gwHBJZv/jWtS5nhDs1JoSw1/wDbj/VASvvzprl1/cpY3rLKJn/lpnr7oAGFsYAAAAujsZtxTAvnufWKily6Oxm3FMC+e59YqJGG9dp27bUKOfHZUkgBOcuAAAAAAAAAAAAFXtknoo9yK9bOOXLbVh1Wbkr+2py7VvPGPRJYfEjHnw60e9HatC+K9KlXoVKFenJVpVJYyTyTy65ZpYw1RhGEefCLxcoiuNErPKc0u5bfi7b4OONsffA86RKuyA0XVck4tHFsJpTz5fvKn+n142s8dv2OaPY+LH6o7cNcYqVtVM0zol2XB4y1jLNN61OmJ+9E/qAPxKAAAAAAAAEsbFLddofwVf0QROljYpbrtD+Cr+iD3a9eFVnfu69zZ7FwQFm4kAAAAj/ZE7jOYvFUuGpqTLs7IncZzF4qlw1NSZBxXrQ6huI1GvnT2QAI7cgAAAAAAAAAAAAAAAAABaLYqbm1zvnV4Omq6tFsVNza53zq8HTZ8N67VN2Xu7/KP5S05DTduMZ4+juIerVHXuQ03bjGePo7iHq1RPcoeWYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAVp2WnVrhW90OEnQymbZadWuFb3Q4SdDKuvevLs25v3XZ5J7ZAGJeAAAAAAAAAAAAAAJy2G3V1jG9n3si06rGw26usY3s+9kWnT8P6jke673nVyR2ADO1kAARPsrdyKv8AxtD0xSwifZW7kVf+NoemLHd9SVpknvGzzo7VPgFa7cAAAAAAAAAAJe2JO6tNvdW/ykRCl7Yk7q0291b/ACke7Xrwqc993XubK3YCzcTAAAAR3sktxXMHg2/rFJSpdXZJbiuYPBt/WKSlSDifWh1HcTqFfPnspAEduIAAAAnvYfZohaY9iOU7mrqp30ntm1hGO17LJD4cId+Mm3/IgRsMtYvd4Bj9jjVhNyNzZV5a1PXzoxhHnR70YbUe9F6t1eDVEq/NcDGOwldieGY83Lxdb0JGtyvjVnmLLtjjmHz8lbXtGWrJt7cuvnyx78I64R78ItktInS4fXRVRVNNUaJgAHkAAcXpb0e4XpAy/wC07nkbfEKEIzWV3CXXGlNHrR7MsdrXD6+fB2g/JiJjRLNh8Rcw9yLtqdFUcEvPzN2XMYyrjlbB8btJra6pR2uvLUl608sevLHs/wDLUr6aQskYBnjB44fjVtrmk1xoXNPVCrQmj15Y+mEdqKpGlHRVmXItxPWuKMb/AAnkv9O/oSR5DV1oTw58kfn2uxGKBdszR544HVsk3SWMwpi3c9G5s4p5O7h5XBAMLZgAAAB/ZJZp54SSSxmmmjqhCENcYxZOE4df4tiFHD8Ms615d1puRp0aMkZppo/NBafQdoVt8rT0cwZmlpXeNQ1TUaENU1O0j2dfOmn7/Oh1tfPe7dua58ypzXOMPllvwrk6ap4I45/1+r99jhoxnyjhc2P43Q5HG76nqlpzQ27WlHb5HvTx2ox7G1Ds65hBY00xTGiHHsdjbuOv1X7s+eer9IAHpEAAActpXzNJlHIGK43ycJa9OjGnbQ7Naf4Mnz6ox1x70IvyZ0RpllsWar9ym3Rw1Toj6qjadsdhmDSrjl5Tn5OhRr+1aMYR1w5GlDkNcO9GMIx+txBNGM00ZpoxjGMdcYx64q6p0zpd2w1inD2aLVPBTER0AD8ZwAAABdHYzbimBfPc+sVFLl0djNuKYF89z6xUSMN67Tt22oUc+OypJACc5cAAAAA5XSnmubJWU5swe1oXNOjc0ZK1PXqjNTmnhLNq7+qOuHfg/JnRGmWWxZrv3KbdEaZmdEOqGDgOLYfjuD2uL4XcyXNndU4VKVSXrw7EexGEdqMOtGEYM5+vFVM0TNNUaJgAHkAAABh43hdhjWE3OFYnbSXNnc0406tKeG1NCPoj14R58Iw1qV6Y9Hl/o/zHG2m5OvhdzGM1jdRh+lL15Jv35ev2dqPXXgaTO+WMKzfly5wPF6PJ0K0Nck8P06U8P0Z5Y9aMPxhHajFiu2orj9V9kOd15Ze8/nt1cMfzH69qgI6LSHlDFck5lr4LismuMvwqFeWGqSvTjzp5f+YdaOuDnVdMTE6JdgtXaL1EXLc6YngkAGQAAAAAASxsUt12h/BV/RBE6WNiluu0P4Kv6IPdr14VWd+7r3NnsXBAWbiQAAACP9kTuM5i8VS4ampMuzsidxnMXiqXDU1JkHFetDqG4jUa+dPZAAjtyAAAAAAAAAAAAAAAAAAFotipubXO+dXg6arq0WxU3NrnfOrwdNnw3rtU3Ze7v8o/lLTkNN24xnj6O4h6tUde5DTduMZ4+juIerVE9yh5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABWnZadWuFb3Q4SdDKZtlp1a4VvdDhJ0Mq6968uzbm/ddnkntkAYl4AAAAAAAAAAAAAAnLYbdXWMb2feyLTqsbDbq6xjez72RadPw/qOR7rvedXJHYAM7WQABE+yt3Iq/wDG0PTFLCJ9lbuRV/42h6Ysd31JWmSe8bPOjtU+AVrtwAAAAAAAAAAl7Yk7q0291b/KREKXtiTurTb3Vv8AKR7tevCpz33de5srdgLNxMAAABHeyS3FcweDb+sUlKl1dkluK5g8G39YpKVIOJ9aHUdxOoV8+eykAR24gAAAAAJ+2JufJbK/q5IxKtqoXc0a2HzTR2paur4VP+aENcO/CPXmWbedVrcV7W6pXVtVno16M8KlOpJHVNJNCOuEYR7MIrsaEdIFvn3KclerPJJi9pCFO/ow2vhdapCHxZtWvvR1w6yZh7mmPBlzbdfk827n421Ho1et+k7fr28rvQEpowAAAA+atOSrTmpVZJZ5J4RlmlmhrhNCPPhGD6ARDn3QFlHH56l3g80+AXk23H2CSE1CaPfpx1av5Ywh3kMZm0CaQMJnmms7O2xihDnT2laEJtXfkn1R196GtcUYarFFTYsDuozDCRFPheFGyrz9fD1qA4jlDNeHTRlvstYxb6uvUsqkIf11aosGTCMVnn5CTDL2absQoTRj6HoYMf4WNq6p3c3NHpWY08v+lD8H0dZ6xeeWWxypi00JudPUt5qUn2p9Uv8AdJ2Tdjfjt3PJWzTilvhtDnzULaPstaPe1/oy/PDkvmWiHqnDUxwoOK3Z467Hg2oijrnr83U5rIuRss5Ls42+A4bJRqTQ1Vbif4dar4U8dvV3oaod50oM8REeaGq3b1y9XNdyqZmeOQB+sYAAAAqxstc5y4pmK3ylZVuStcMj7JdcjHamuJobUP5ZY/1mmh1k7aYM7W2RcmXGKTTSTX1WEaNjRj+vVjDajq+LLz4/Nq58YKOXlzXvLutd3VWetcV6k1SrUnjrmnmmjrjGPfjGKLibmiPBhvO43KpuXZxlyPNT5qeXjn6dvI/IBDdJAAAAAAF0djNuKYF89z6xUUuXR2M24pgXz3PrFRIw3rtO3bahRz47KkkAJzlwAAAAi7ZS7jmI/wARb8JBKKLtlLuOYj/EW/CQeLnqSs8m94WOdT2oN2Pmk+pkrGPcnFq002AXtSHsmvb9q1I7XskO98aHY2+tqjcGlUp1aUlWlPLUpzywmknljrhNCPOjCPXg86Fg9jLpT9q1KGSMw3P+hPHkcMuKk3Q5o/8ARmj2I/q9iO114aoti7o9GW67qsg36JxmHj0o9aNsbeWOPb22WATXNwAAAAAHIaV8h4bn7LU+G3fI0bylrnsrrVrjRqf8yx2oRh/zCCk2ZcExLLuOXWDYvbTW95bT8hUkjzo9iMI9eEYbcI9eEXoQjXTtoyts+YJ7aspadHHrOSPtWrHahWl5/sU8exHrR60e9GKPeteFGmOFtm5rP5wNe8Xp/wDHP/zPdt6VMB+t7a3NjeVrO8oVKFxQnjTq0qkuqaSaEdUYRh1ovyQXVYmJjTAAP0AAAASxsUt12h/BV/RBE6WNiluu0P4Kv6IPdr14VWd+7r3NnsXBAWbiQAAADQ6Qsty5uydiGXZ7uazlvJZZY1oU+TjJyM8s3O1w1/o6uehfmYrTuyr+b4fmLDDxVbpqnTMLPBZxjcDRNvD1+DEzp4Inz/WJV55mK07sq/m+H5hzMVp3ZV/N8PzFhh53i3sTPKjNfm9VPcrzzMVp3ZV/N8PzDmYrTuyr+b4fmLDBvFvYeVGa/N6qe5XnmYrTuyr+b4fmHMxWndlX83w/MWGDeLew8qM1+b1U9yvPMxWndlX83w/MOZitO7Kv5vh+YsMG8W9h5UZr83qp7leeZitO7Kv5vh+Yrxj1jDDMcv8ADYVI1YWlzUoQnjDVyXITRl16utr1PQ15/Z46tcd3xuOEmR8RbpoiNENt3J5ti8fcuRiK/C0RGjzRHZENOAjN2AAAAAAAAFotipubXO+dXg6arq0WxU3NrnfOrwdNnw3rtU3Ze7v8o/lLTkNN24xnj6O4h6tUde5DTduMZ4+juIerVE9yh5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABWnZadWuFb3Q4SdDKZtlp1a4VvdDhJ0Mq6968uzbm/ddnkntkAYl4AAAAAAAAAAAAAAnLYbdXWMb2feyLTqsbDbq6xjez72RadPw/qOR7rvedXJHYAM7WQABE+yt3Iq/8bQ9MUsIn2Vu5FX/jaHpix3fUlaZJ7xs86O1T4BWu3AAAAAAAAAACXtiTurTb3Vv8pEQpe2JO6tNvdW/yke7Xrwqc993XubK3YCzcTAAAAR3sktxXMHg2/rFJSpdXZJbiuYPBt/WKSlSDifWh1HcTqFfPnspAEduIAAAAAA6HR7m7E8lZnt8cwubXNJ8GtRjHVLXpx/Skm+frR60YQj1nPBEzE6YY7tqi9RNuuNMT5phf/JOZ8Kzfl22xzCK3slCtDVNJH9OlPD9KSaHWmh+EYbUYN0o1ok0hYpo/x/23bclcYfXjCW9s4zaoVZezDsTw60fq50V0Mp5hwnNOB0MZwW6luLStDnw2ppJuvLNDrTQ68FjauxXH6uQ59kVzLLumnz254J/if17W1AZWvgAAAAAAAAAAAAAAADFxfEbLCMMucTxK5ktrS2pxqVas8dUJZYf/ALndd+11XoWttVubmtTo0KUkZ6lSpNCWWSWENcYxjHnQgqJsgNK1TOt/HBcGqT08v21TXCO3CN3PD9eaHxYfqw+uO3qhDHcuRRGlcZNk93M7/gU+amOGdkd88TmNMOfLzP2bKmIz8nSw+hrpWNvGPQ6evnx/em58fqhzoQcYCumZmdMuyYfD28PaptW40Ux5oAH4zAAAAAAC6Oxm3FMC+e59YqKXLo7GbcUwL57n1iokYb12nbttQo58dlSSAE5y4AAAARdspdxzEf4i34SCUUXbKXccxH+It+Eg8XPUlZ5N7wsc6ntU3IRjCMIwjqjAFY7etlscdKcM0YfJlnHbiHu3a0/9GrPHbu6UIc/vzyw5/Zht9lM7zuwy+u8NxChiFhcVLe6t6kKlKrJHVNJNCOuEYLpaE9I1pn/LkJ6kadHGbSEJb23hta49apLD4s39o7XYjGbYu+F6M8LmG6jIPwtc4qxHoTwxsnunqn6O/ASWmAAAAAAIV2RuimGZbOpmjL9vD3at5NdxRkht3dOEOtDr1IQ53ZhtdaCqEYRhGMIwjCMOfCL0ZVv2S+ijkI3Gd8t23wI658TtacvO7NaWHY+ND+bsol+z/wAob7uW3QeBMYPET5v+M/xP8dCuwCI6KAAAAJY2KW67Q/gq/ogidLGxS3XaH8FX9EHu168KrO/d17mz2LggLNxIAAAAAAAAAAAAAAef2eOrXHd8bjhJnoC8/s8dWuO743HCTIuK4Ib3uG9re5I7ZacBDdHAAAAAAAAFotipubXO+dXg6arq0WxU3NrnfOrwdNnw3rtU3Ze7v8o/lLTkNN24xnj6O4h6tUde5DTduMZ4+juIerVE9yh5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABWnZadWuFb3Q4SdDKZtlp1a4VvdDhJ0Mq6968uzbm/ddnkntkAYl4AAAAAAAAAAAAAAnLYbdXWMb2feyLTqsbDbq6xjez72RadPw/qOR7rvedXJHYAM7WQABE+yt3Iq/wDG0PTFLCJ9lbuRV/42h6Ysd31JWmSe8bPOjtU+AVrtwAAAAAAAAAAl7Yk7q0291b/KREKXtiTurTb3Vv8AKR7tevCpz33de5srdgLNxMAAABHeyS3FcweDb+sUlKl1dkluK5g8G39YpKVIOJ9aHUdxOoV8+eykAR24gAAAAAAADrNGWfscyFjUL7C6nsttUjCF1ZzzR9jry9/sTQ600NuHfhrhHkwiZidMMN+xbv25t3Y00zwwvjo6z1gGesHhf4NcaqskIQuLWpGEKtCbsTQ7HYmhtR/rB1Dz2y9jeK5exWjimDX1ayvKUfg1KcdW114Rhzowj14R2orPaKdPeD47LSwzNnsOEYlHVLLc69VtWj88ehx+fa7/AFk63firzVcLmedblL2FmbuG9KjZxx3x9ztTWP5JNLPJLPJNCaWaGuEYR1wjDsv6kNPAAAAAAAAAAAAGLi+JWGEYbXxLE7ulaWlCXk6tarNqllh/+63XctpJ0lZYyLax907r2e/ml10rGhGE1WfsRj8WXvx+rXzlTNJ+kjMOfr/2TEavtewpza7expTR9jp9+Pxpv3o9/VqhtMNy9FHK2LJtzuIzGYrq9G3t28m3l4HTactMF5nWtPg2DRq2mX5JtuEfgz3cYR2pp+xL2Jfrjt6oQiYECqqap0y6rgsFZwVmLNmNER96Z/UAfiWAAAAAAAALo7GbcUwL57n1iopcujsZtxTAvnufWKiRhvXadu21Cjnx2VJIATnLgAAABF2yl3HMR/iLfhIJRRdspdxzEf4i34SDxc9SVnk3vCxzqe1TcBWO3jc5KzLimUcx22OYRW9juKEfhSx/RqyR/Skmh15Y/wD+4bcINMETo88PFy3TcomiuNMTwr8aPc3YXnXLNvjeFz6pZ/g1qMY656FSH6Uk3zdaPXhGEeu6FRrRBn+/yBmaW+pcnWw6vqkvrWEdqpJ2YfvS7cYR+eHOjFdjA8UsMbwi2xbC7mS5s7qnCpSqS86MI+iMOdGHWjCMFjau+HH6uQboMkqyy9pp89urgn+J/Xt6WaAytfAAAAH8mllmljLNCE0sYaowjDXCMH9AVL2RWiqbKt9PmTAbeMcCuZ/9WlJD/wCHUjHneBGPO7Edrsa4aeiWIWdriFjXsb63p3FtcSRp1aVSGuWeWMNUYRgplpx0aXWQcd9ltoVK2B3c8Y2leO3GSPP9inj8aHWj14bfZhCDfs+D6UcDp25fdB+KpjC4ifTjgnbHfHWjoBHboAAJY2KW67Q/gq/ogidLGxS3XaH8FX9EHu168KrO/d17mz2LggLNxIAAAAAAAAAAAAAAef2eOrXHd8bjhJnoC8/s8dWuO743HCTIuK4Ib3uG9re5I7ZacBDdHAAAAAAAAFotipubXO+dXg6arq0WxU3NrnfOrwdNnw3rtU3Ze7v8o/lLTkNN24xnj6O4h6tUde5DTduMZ4+juIerVE9yh5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABWnZadWuFb3Q4SdDKZtlp1a4VvdDhJ0Mq6968uzbm/ddnkntkAYl4AAAAAAAAAAAAAAnLYbdXWMb2feyLTqG6Os8Y1kTFLjEcEktJq1xR9gn9sU4zw5HkoTbUIRht64QdzzRef/2OC+Sz8dKtXqaKdEtBz/c5jMfjZvWtGiYjhnZC3IqNzRef/wBjgvks/HOaLz/+xwXyWfjsv4mhTeR2Y/8AXp/0tyKjc0Xn/wDY4L5LPxzmi8//ALHBfJZ+OfiaDyOzH/r0/wCluUT7K3cir/xtD0xQ9zRef/2OC+Sz8doc+aX82Zzy/PgmL08NltZqktSMaFCaWbXLztuM0Xiu/RVTMQm5buVx+Gxdu9Xo0UzEz5/9I9AQ3SgAAAAAAAAABL2xJ3Vpt7q3+UiIXQZAzfiuScejjWDS201zGjNR1V5IzS8jNGEY7UIw29qD1RMU1RMoGaYevE4O5Zo4aomIX5FRuaLz/wDscF8ln45zRef/ANjgvks/HTfxNDm/kdmP/Xp/0tyKjc0Xn/8AY4L5LPxzmi8//scF8ln45+JoPI7Mf+vT/pbkVG5ovP8A+xwXyWfjnNF5/wD2OC+Sz8c/E0HkdmP/AF6f9J12SW4rmDwbf1ikpUknOWmnOGa8tXeAYpSwuWzu4SQqRo280s/wZ5Z4aoxmj15YdZGyLeriurTDdtzWWX8uwtVq9o0zVM+bkiP4AGJsIAAAAAAAAAAADutHelbN2SoyULG99uYdLHbsbrXPThD92PPk+qOrswisNkXT1kzH5ZKGK1J8AvY7UZbqOujGPeqw2oQ8KEqn4y0XqqFFmO53BY+Zqqp8GrbHmn68U9r0VtbihdW8lxa16VejUhrkqU54TSzQ7MIw2ov0efuW8z5hy5X9mwLGb3D5teuaWjVjCSbwpedN9cIpPy5sjM6WEstPFrTDsXkhz55qcaNWP1yfB/2pFOJpnhabi9xWLtzpsVRXHRPd1rZiCsH2S2Wq0JYYtgGKWU0efGhPJXlh9cYyx/s6mw07aNLqEPZMbrWs0f1a1nV9MssYf3ZYu0TxqK7kOY2vWs1fSNPZpSYOIo6WtHFWWEZc24fCEfj8lL6YP0m0qaO5YbebsL+qpr/4evDp2os5di4829Vf+s9zsxH93po0Z20I8nmmjPGHWpW9afX/AEki5/FNkTkG1lj7Up4tfzdb2K2hJCP1zzQj/Z+TcojjZ7eTZhc9WzV0THamAVqx7ZNXs8JpMCyxb0exUvK8amv+WWEv+SNM06W8/wCYpZ6V5mCvbW83PoWcIUJdXYjGX4UYfPGLHViKI4Fxhdx2YXp/8miiP1nTPRGnthbbOmkTJ+UJJoY1jVCS4hDataUfZK0f5JduHzx1Q76ANImyGxzFpatllS2jg1rNte2Z4wnuZod79WT6tcexGCD5oxmmjNNGMYxjrjGPXEevEVVcHmbdl25PBYSYquenV+vB0d+l+l1cXF3c1Lm6r1a9epNGapUqTxmmnjHrxjHbjF+YMDaIjR5oAB+gAAAAAAAAAC6Oxm3FMC+e59YqKXJIyVpnzflLLVrl/CqWFzWdryfsca1Caaf4U8Z464wmh15o9Zls1xRVplr26TLb+Y4Wm1Z0aYqifPyTH8roio3NF5//AGOC+Sz8c5ovP/7HBfJZ+OlfiaGk+R2Y/wDXp/0tyKjc0Xn/APY4L5LPxzmi8/8A7HBfJZ+OfiaDyOzH/r0/6W5FRuaLz/8AscF8ln45zRef/wBjgvks/HPxNB5HZj/16f8AS3KLtlLuOYj/ABFvwkEL80Xn/wDY4L5LPx2jzzpjzbnHLtbAsWp4ZLaVp5J5o0KE0s+uWMIw24zR68Hmu/RNMxCZl25XH4fF27tejRTVEz59k8iOwEJ0sAASzsetKE+TMXhg2L1ppsAvanwox2/atSO17JD92P60Pr62qMTD9pqmmdMImNwdrG2arN2NMT96Y/V6L0p5KtOWpTnlnknhCaWaWOuE0I86MIvpS7J2mrO2V8AoYJZVbK5tbfXCjG6oxnnkl+LCMJofBh1uxzudqbjmi8//ALHBfJZ+OmxiaHNrm4zHxXMUTTMcU6VuRUbmi8//ALHBfJZ+Oc0Xn/8AY4L5LPx37+JoePI7Mf8Ar0/6W5FRuaLz/wDscF8ln45zRef/ANjgvks/HPxNB5HZj/16f9Lcio3NF5//AGOC+Sz8c5ovP/7HBfJZ+OfiaDyOzH/r0/6W5azNOA4ZmbAbrBcXt4V7S5k5GaHXlj1ppY9aaEduEVWeaLz/APscF8ln45zRef8A9jgvks/Hfk4iiXqjcjmdFUVUzETH6/6cXpSyNieQ8zVMLvoRq20+uezuoS6pa9PXz+9NDnRh1o96MIx5NIGfNLeY864J7k47Y4PUpQnhUp1KdvNLUpTQ68s3JR1a4bUe9FH6HX4On0eB0jATid4iMVEeHHDo4J/UAeU0SxsUt12h/BV/RBE7fZDzXimTMwSY3hEtvNdS05qcIV5IzS6puftQjB6onRVEyg5lh68ThLlmjhqiYhfsVG5ovP8A+xwXyWfjnNF5/wD2OC+Sz8dN/E0ObeR2Y/8AXp/0tyKjc0Xn/wDY4L5LPxzmi8//ALHBfJZ+OfiaDyOzH/r0/wCluRUbmi8//scF8ln45zRef/2OC+Sz8c/E0HkdmP8A16f9Lcio3NF5/wD2OC+Sz8c5ovP/AOxwXyWfjn4mg8jsx/69P+luRUbmi8//ALHBfJZ+Oc0Xn/8AY4L5LPxz8TQeR2Y/9en/AEtyKjc0Xn/9jgvks/HOaLz/APscF8ln45+JoPI7Mf8Ar0/6W5FRuaLz/wDscF8ln45zRef/ANjgvks/HPxNB5HZj/16f9Lcio3NF5//AGOC+Sz8c5ovP/7HBfJZ+OfiaDyOzH/r0/6W5ef2eOrXHd8bjhJkkc0Xn/8AY4L5LPx0T4neVsRxK6xC4hLCtc1p61TkYaoclNNGMdXe1xYL92muI0Nn3M5JistuXKr+j0ojRonSxwEduAAAAAAAAAtFsVNza53zq8HTVdWi2Km5tc751eDps+G9dqm7L3d/lH8pachpu3GM8fR3EPVqjr3IabtxjPH0dxD1aonuUPLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AK07LTq1wre6HCToZTNstOrXCt7ocJOhlXXvXl2bc37rs8k9sgDEvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABaLYqbm1zvnV4Omq6tFsVNza53zq8HTZ8N67VN2Xu7/KP5S05DTduMZ4+juIerVHXuQ03bjGePo7iHq1RPcoeWYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAVp2WnVrhW90OEnQymbZadWuFb3Q4SdDKuvevLs25v3XZ5J7ZAGJeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC0WxU3NrnfOrwdNV1aLYqbm1zvnV4Omz4b12qbsvd3+UfylpyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqie5Q8swAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG80fdXuXt9LbhZWjbzR91e5e30tuFlB6vgArTstOrXCt7ocJOhlM2y06tcK3uhwk6GVde9eXZtzfuuzyT2yAMS8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFotipubXO+dXg6arq0WxU3NrnfOrwdNnw3rtU3Ze7v8AKP5S05DTduMZ4+juIerVHXuQ03bjGePo7iHq1RPcoeWYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAVp2WnVrhW90OEnQykrZrX11a5+waS3q8hLHC4RjDkYR2/ZZ+ygX3YxH5TH7Ev4MtOTX8RG+UzGieXubllu7nL8uwtGFu0VzVTw6Ip0cOnjqh2A4/3YxH5TH7Ev4HuxiPymP2JfwevJ/E/FT19yd+ZOV/LudFP9nYDj/djEflMfsS/ge7GI/KY/Yl/A8n8T8VPX3H5k5X8u50U/2dgOP92MR+Ux+xL+B7sYj8pj9iX8DyfxPxU9fcfmTlfy7nRT/Z2A4/3YxH5TH7Ev4HuxiPymP2JfwPJ/E/FT19x+ZOV/LudFP9nYDj/djEflMfsS/ge7GI/KY/Yl/A8n8T8VPX3H5k5X8u50U/2dgOP92MR+Ux+xL+B7sYj8pj9iX8DyfxPxU9fcfmTlfy7nRT/Z2A4/3YxH5TH7Ev4HuxiPymP2JfwPJ/E/FT19x+ZOV/LudFP9nYDj/djEflMfsS/ge7GI/KY/Yl/A8n8T8VPX3H5k5X8u50U/2dgOP92MR+Ux+xL+B7sYj8pj9iX8DyfxPxU9fcfmTlfy7nRT/Z2A4/3YxH5TH7Ev4HuxiPymP2JfwPJ/E/FT19x+ZOV/LudFP9nYDj/djEflMfsS/ge7GI/KY/Yl/A8n8T8VPX3H5k5X8u50U/2dgOP92MR+Ux+xL+B7sYj8pj9iX8DyfxPxU9fcfmTlfy7nRT/Z2A4/3YxH5TH7Ev4HuxiPymP2JfwPJ/E/FT19x+ZOV/LudFP9nYDj/djEflMfsS/ge7GI/KY/Yl/A8n8T8VPX3H5k5X8u50U/2dgOP92MR+Ux+xL+B7sYj8pj9iX8DyfxPxU9fcfmTlfy7nRT/Z2A4/3YxH5TH7Ev4HuxiPymP2JfwPJ/E/FT19x+ZOV/LudFP9nYDj/djEflMfsS/ge7GI/KY/Yl/A8n8T8VPX3H5k5X8u50U/2dgOP92MR+Ux+xL+B7sYj8pj9iX8DyfxPxU9fcfmTlfy7nRT/Z2A4/3YxH5TH7Ev4HuxiPymP2JfwPJ/E/FT19x+ZOV/LudFP9nYDj/djEflMfsS/ge7GI/KY/Yl/A8n8T8VPX3H5k5X8u50U/2dgOP92MR+Ux+xL+B7sYj8pj9iX8DyfxPxU9fcfmTlfy7nRT/Z2A4/3YxH5TH7Ev4HuxiPymP2JfwPJ/E/FT19x+ZOV/LudFP9nYDj/djEflMfsS/ge7GI/KY/Yl/A8n8T8VPX3H5k5X8u50U/2dgOP92MR+Ux+xL+B7sYj8pj9iX8DyfxPxU9fcfmTlfy7nRT/Z2A4/3YxH5TH7Ev4HuxiPymP2JfwPJ/E/FT19x+ZOV/LudFP9nYDj/djEflMfsS/ge7GI/KY/Yl/A8n8T8VPX3H5k5X8u50U/2dgMfDak9Wwo1Kk3JTzSQjGPZZCkrpmiqaZ4m+2LsXrdNyngqiJ6QB5ZQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAActiGKX9K+r06dxGWSWeMIQ5GG1D+j8PdjEflMfsS/gureRYi5RFcVR5/Px9zQ8R//ACHluHvVWqrdemmZjgp4p0fE7Acf7sYj8pj9iX8D3YxH5TH7Ev4Pfk/ifip6+5h/MnK/l3Oin+zsBx/uxiPymP2JfwPdjEflMfsS/geT+J+Knr7j8ycr+Xc6Kf7OwHH+7GI/KY/Yl/A92MR+Ux+xL+B5P4n4qevuPzJyv5dzop/s7Acf7sYj8pj9iX8D3YxH5TH7Ev4Hk/ifip6+4/MnK/l3Oin+zsBx/uxiPymP2JfwPdjEflMfsS/geT+J+Knr7j8ycr+Xc6Kf7OwHH+7GI/KY/Yl/A92MR+Ux+xL+B5P4n4qevuPzJyv5dzop/s7Acf7sYj8pj9iX8D3YxH5TH7Ev4Hk/ifip6+4/MnK/l3Oin+zsBx/uxiPymP2JfwPdjEflMfsS/geT+J+Knr7j8ycr+Xc6Kf7OwHH+7GI/KY/Yl/A92MR+Ux+xL+B5P4n4qevuPzJyv5dzop/s7Acf7sYj8pj9iX8D3YxH5TH7Ev4Hk/ifip6+4/MnK/l3Oin+zsBx/uxiPymP2JfwPdjEflMfsS/geT+J+Knr7j8ycr+Xc6Kf7OwHH+7GI/KY/Yl/A92MR+Ux+xL+B5P4n4qevuPzJyv5dzop/s7Acf7sYj8pj9iX8D3YxH5TH7Ev4Hk/ifip6+4/MnK/l3Oin+zsBx/uxiPymP2JfwPdjEflMfsS/geT+J+Knr7j8ycr+Xc6Kf7OwHH+7GI/KY/Yl/A92MR+Ux+xL+B5P4n4qevuPzJyv5dzop/s7Acf7sYj8pj9iX8D3YxH5TH7Ev4Hk/ifip6+4/MnK/l3Oin+zsBx/uxiPymP2JfwPdjEflMfsS/geT+J+Knr7j8ycr+Xc6Kf7OwHH+7GI/KY/Yl/A92MR+Ux+xL+B5P4n4qevuPzJyv5dzop/s7Acf7sYj8pj9iX8D3YxH5TH7Ev4Hk/ifip6+4/MnK/l3Oin+zsBx/uxiPymP2JfwPdjEflMfsS/geT+J+Knr7j8ycr+Xc6Kf7OwHH+7GI/KY/Yl/A92MR+Ux+xL+B5P4n4qevuPzJyv5dzop/s7Acf7sYj8pj9iX8D3YxH5TH7Ev4Hk/ifip6+4/MnK/l3Oin+zsBx/uxiPymP2JfwPdjEflMfsS/geT+J+Knr7j8ycr+Xc6Kf7OwHH+7GI/KY/Yl/A92MR+Ux+xL+B5P4n4qevuPzJyv5dzop/s7Acf7sYj8pj9iX8D3YxH5TH7Ev4Hk/ifip6+4/MnK/l3Oin+zsFotipubXO+dXg6alvuxiPymP2JfwXB2GlzWutFF3Urz8nNDF60NeqENr2Ol2HmrKb2FjfK5jR+mnuVWcbscFm+G/DWKKoq0xPniNHm5KpTW5DTduMZ4+juIerVHXuQ03bjGePo7iHq1Riao8swAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG80fdXuXt9LbhZWjbzR91e5e30tuFlB6vgAqZs2KEtXPuCzRmjD/+L1f/ANWdAftST48ywOzS6u8F3s+9nQO3XLKKZwtEzH3panmFdUYmqI+/Mxvaknx5j2pJ8eZkidvdOxD3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxvaknx5j2pJ8eZkhvdOw3yraxZ7WWWSabko7UNbEbOr0KfwYtYwXaYpnzM1qqZjzu0wjpZb+Lgy2JhHSy38XBluZX/a1csvqfLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfNvQlqyRmjNGGqOp9Yt0zufGTel92HQo+E6TgIibVETsjsfLmdTMY2/MfHV2y/ntST48x7Uk+PMyRYb3TsVG+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMe1JPjzMkN7p2G+VbWN7Uk+PMuHsM6cKWie7lhGMdeL1o7fi6Soq32w53KrrfatwdJU51RTGG0xthZZTXM4jz7E0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUak2Z5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wwkWeCXaYR0st/FwZbEwjpZb+Lgy3Mb/ALWrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/z6v3SyAFkpQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABb7Yc7lV1vtW4OkqCt9sOdyq632rcHSVGd6t9YWeUax9JTQ5DTduMZ4+juIerVHXuQ03bjGePo7iHq1RqDaHlmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3mj7q9y9vpbcLK0beaPur3L2+ltwsoPV8AFUdml1d4LvZ97OgdPGzS6u8F3s+9nQO3fK9Uo++NqOY6zX98QAnoQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD5q9Cn8GLWNnV6FP4MWsRr/DCRZ4JdphHSy38XBlsTCOllv4uDLcxv+1q5ZfVGW6na5tPZAAxJoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADisW6Z3PjJvS+7DoUfCfGLdM7nxk3pfdh0KPhOlZf7KjkjsfLmd65f59X7pZACyUoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt9sOdyq632rcHSVBW+2HO5Vdb7VuDpKjO9W+sLPKNY+kpochpu3GM8fR3EPVqjr3IabtxjPH0dxD1ao1BtDyzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbzR91e5e30tuFlaNvNH3V7l7fS24WUHq+ACqOzS6u8F3s+9nQOnjZpdXeC72fezoHbvleqUffG1HMdZr++IAT0IAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB81ehT+DFrGzq9Cn8GLWI1/hhIs8Eu0wjpZb+Lgy2JhHSy38XBluY3/a1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv8AZUckdj5czvXL/Pq/dLIAWSlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFvthzuVXW+1bg6SoK32w53KrrfatwdJUZ3q31hZ5RrH0lNDkNN24xnj6O4h6tUde5DTduMZ4+juIerVGoNoeWYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAVR2aXV3gu9n3s6B08bNLq7wXez72dA7d8r1Sj742o5jrNf3xACehAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPmr0KfwYtY2dXoU/gxaxGv8MJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/wA+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wAMJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf8Aa1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv9lRyR2PlzO9cv8+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wwkWeCXaYR0st/FwZbEwjpZb+Lgy3Mb/ALWrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/z6v3SyAFkpQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABb7Yc7lV1vtW4OkqCt9sOdyq632rcHSVGd6t9YWeUax9JTQ5DTduMZ4+juIerVHXuQ03bjGePo7iHq1RqDaHlmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3mj7q9y9vpbcLK0beaPur3L2+ltwsoPV8AFUdml1d4LvZ97OgdPGzS6u8F3s+9nQO3fK9Uo++NqOY6zX98QAnoQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD5q9Cn8GLWNnV6FP4MWsRr/DCRZ4JdphHSy38XBlsTCOllv4uDLcxv+1q5ZfVGW6na5tPZAAxJoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADisW6Z3PjJvS+7DoUfCfGLdM7nxk3pfdh0KPhOlZf7KjkjsfLmd65f59X7pZACyUoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt9sOdyq632rcHSVBW+2HO5Vdb7VuDpKjO9W+sLPKNY+kpochpu3GM8fR3EPVqjr3IabtxjPH0dxD1ao1BtDyzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbzR91e5e30tuFlaNvNH3V7l7fS24WUHq+ACqOzS6u8F3s+9nQOnjZpdXeC72fezoHbvleqUffG1HMdZr++IAT0IAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB81ehT+DFrGzq9Cn8GLWI1/hhIs8Eu0wjpZb+Lgy2JhHSy38XBluY3/a1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv8AZUckdj5czvXL/Pq/dLIAWSlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFvthzuVXW+1bg6SoK32w53KrrfatwdJUZ3q31hZ5RrH0lNDkNN24xnj6O4h6tUde5DTduMZ4+juIerVGoNoeWYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAVR2aXV3gu9n3s6B08bNLq7wXez72dA7d8r1Sj742o5jrNf3xACehAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPmr0KfwYtY2dXoU/gxaxGv8MJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/wA+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wAMJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf8Aa1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv9lRyR2PlzO9cv8+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wwkWeCXaYR0st/FwZbEwjpZb+Lgy3Mb/ALWrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/z6v3SyAFkpQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABb7Yc7lV1vtW4OkqCt9sOdyq632rcHSVGd6t9YWeUax9JTQ5DTduMZ4+juIerVHXuQ03bjGePo7iHq1RqDaHlmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3mj7q9y9vpbcLK0beaPur3L2+ltwsoPV8AFUdml1d4LvZ97OgdPGzS6u8F3s+9nQO3fK9Uo++NqOY6zX98QAnoQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD5q9Cn8GLWNnV6FP4MWsRr/DCRZ4JdphHSy38XBlsTCOllv4uDLcxv+1q5ZfVGW6na5tPZAAxJoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADisW6Z3PjJvS+7DoUfCfGLdM7nxk3pfdh0KPhOlZf7KjkjsfLmd65f59X7pZACyUoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt9sOdyq632rcHSVBW+2HO5Vdb7VuDpKjO9W+sLPKNY+kpochpu3GM8fR3EPVqjr3IabtxjPH0dxD1ao1BtDyzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbzR91e5e30tuFlaNvNH3V7l7fS24WUHq+ACqOzS6u8F3s+9nQOnjZpdXeC72fezoHbvleqUffG1HMdZr++IAT0IAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB81ehT+DFrGzq9Cn8GLWI1/hhIs8Eu0wjpZb+Lgy2JhHSy38XBluY3/a1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv8AZUckdj5czvXL/Pq/dLIAWSlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFvthzuVXW+1bg6SoK32w53KrrfatwdJUZ3q31hZ5RrH0lNDkNN24xnj6O4h6tUde5DTduMZ4+juIerVGoNoeWYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAVR2aXV3gu9n3s6B08bNLq7wXez72dA7d8r1Sj742o5jrNf3xACehAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPmr0KfwYtY2dXoU/gxaxGv8MJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/wA+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wAMJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf8Aa1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv9lRyR2PlzO9cv8+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wwkWeCXaYR0st/FwZbEwjpZb+Lgy3Mb/ALWrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/z6v3SyAFkpQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABb7Yc7lV1vtW4OkqCt9sOdyq632rcHSVGd6t9YWeUax9JTQ5DTduMZ4+juIerVHXuQ03bjGePo7iHq1RqDaHlmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3mj7q9y9vpbcLK0beaPur3L2+ltwsoPV8AFUdml1d4LvZ97OgdPGzS6u8F3s+9nQO3fK9Uo++NqOY6zX98QAnoQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD5q9Cn8GLWNnV6FP4MWsRr/DCRZ4JdphHSy38XBlsTCOllv4uDLcxv+1q5ZfVGW6na5tPZAAxJoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADisW6Z3PjJvS+7DoUfCfGLdM7nxk3pfdh0KPhOlZf7KjkjsfLmd65f59X7pZACyUoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt9sOdyq632rcHSVBW+2HO5Vdb7VuDpKjO9W+sLPKNY+kpochpu3GM8fR3EPVqjr3IabtxjPH0dxD1ao1BtDyzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbzR91e5e30tuFlaNvNH3V7l7fS24WUHq+ACqOzS6u8F3s+9nQOnjZpdXeC72fezoHbvleqUffG1HMdZr++IAT0IAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB81ehT+DFrGzq9Cn8GLWI1/hhIs8Eu0wjpZb+Lgy2JhHSy38XBluY3/a1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv8AZUckdj5czvXL/Pq/dLIAWSlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFvthzuVXW+1bg6SoK32w53KrrfatwdJUZ3q31hZ5RrH0lNDkNN24xnj6O4h6tUde5DTduMZ4+juIerVGoNoeWYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAVR2aXV3gu9n3s6B08bNLq7wXez72dA7d8r1Sj742o5jrNf3xACehAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPmr0KfwYtY2dXoU/gxaxGv8MJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/wA+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wAMJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf8Aa1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv9lRyR2PlzO9cv8+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wwkWeCXaYR0st/FwZbEwjpZb+Lgy3Mb/ALWrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/z6v3SyAFkpQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABb7Yc7lV1vtW4OkqCt9sOdyq632rcHSVGd6t9YWeUax9JTQ5DTduMZ4+juIerVHXuQ03bjGePo7iHq1RqDaHlmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3mj7q9y9vpbcLK0beaPur3L2+ltwsoPV8AFUdml1d4LvZ97OgdPGzS6u8F3s+9nQO3fK9Uo++NqOY6zX98QAnoQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD5q9Cn8GLWNnV6FP4MWsRr/DCRZ4JdphHSy38XBlsTCOllv4uDLcxv+1q5ZfVGW6na5tPZAAxJoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADisW6Z3PjJvS+7DoUfCfGLdM7nxk3pfdh0KPhOlZf7KjkjsfLmd65f59X7pZACyUoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt9sOdyq632rcHSVBW+2HO5Vdb7VuDpKjO9W+sLPKNY+kpochpu3GM8fR3EPVqjr3IabtxjPH0dxD1ao1BtDyzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbzR91e5e30tuFlaNvNH3V7l7fS24WUHq+ACqOzS6u8F3s+9nQOnjZpdXeC72fezoHbvleqUffG1HMdZr++IAT0IAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB81ehT+DFrGzq9Cn8GLWI1/hhIs8Eu0wjpZb+Lgy2JhHSy38XBluY3/a1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv8AZUckdj5czvXL/Pq/dLIAWSlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFvthzuVXW+1bg6SoK32w53KrrfatwdJUZ3q31hZ5RrH0lNDkNN24xnj6O4h6tUde5DTduMZ4+juIerVGoNoeWYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAVR2aXV3gu9n3s6B08bNLq7wXez72dA7d8r1Sj742o5jrNf3xACehAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPmr0KfwYtY2dXoU/gxaxGv8MJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/wA+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wAMJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf8Aa1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv9lRyR2PlzO9cv8+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wwkWeCXaYR0st/FwZbEwjpZb+Lgy3Mb/ALWrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/z6v3SyAFkpQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABb7Yc7lV1vtW4OkqCt9sOdyq632rcHSVGd6t9YWeUax9JTQ5DTduMZ4+juIerVHXuQ03bjGePo7iHq1RqDaHlmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3mj7q9y9vpbcLK0beaPur3L2+ltwsoPV8AFUdml1d4LvZ97OgdPGzS6u8F3s+9nQO3fK9Uo++NqOY6zX98QAnoQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD5q9Cn8GLWNnV6FP4MWsRr/DCRZ4JdphHSy38XBlsTCOllv4uDLcxv+1q5ZfVGW6na5tPZAAxJoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADisW6Z3PjJvS+7DoUfCfGLdM7nxk3pfdh0KPhOlZf7KjkjsfLmd65f59X7pZACyUoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAt9sOdyq632rcHSVBW+2HO5Vdb7VuDpKjO9W+sLPKNY+kpochpu3GM8fR3EPVqjr3IabtxjPH0dxD1ao1BtDyzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbzR91e5e30tuFlaNvNH3V7l7fS24WUHq+ACqOzS6u8F3s+9nQOnjZpdXeC72fezoHbvleqUffG1HMdZr++IAT0IAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB81ehT+DFrGzq9Cn8GLWI1/hhIs8Eu0wjpZb+Lgy2JhHSy38XBluY3/a1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv8AZUckdj5czvXL/Pq/dLIAWSlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFvthzuVXW+1bg6SoK32w53KrrfatwdJUZ3q31hZ5RrH0lNDkNN24xnj6O4h6tUde5DTduMZ4+juIerVGoNoeWYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADeaPur3L2+ltwsrRt5o+6vcvb6W3Cyg9XwAVR2aXV3gu9n3s6B08bNLq7wXez72dA7d8r1Sj742o5jrNf3xACehAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPmr0KfwYtY2dXoU/gxaxGv8MJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/wA+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wAMJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo280fdXuXt9LbhZQer4AKo7NLq7wXez72dA6eNml1d4LvZ97Ogdu+V6pR98bUcx1mv74gBPQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf8Aa1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv9lRyR2PlzO9cv8+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW+2HO5Vdb7VuDpKgrfbDncqut9q3B0lRnerfWFnlGsfSU0OQ03bjGePo7iHq1R17kNN24xnj6O4h6tUag2h5ZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN5o+6vcvb6W3CytG3mj7q9y9vpbcLKD1fABVHZpdXeC72fezoHTxs0urvBd7PvZ0Dt3yvVKPvjajmOs1/fEAJ6EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wwkWeCXaYR0st/FwZbEwjpZb+Lgy3Mb/ALWrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC32w53KrrfatwdJUFb7Yc7lV1vtW4OkqM71b6ws8o1j6SmhyGm7cYzx9HcQ9WqOvchpu3GM8fR3EPVqjUG0PLMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABvNH3V7l7fS24WVo24yPUhSzrgdWMdUJMRt5tfzVJQesYAKo7NLq7wXez72dA6wWzWt4y5my9datqpZ1acI+DPCP/mr63fKp04Sj745ajmMaMTX98QAnoQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD5q9Cn8GLWNnV6FP4MWsRr/AAwkWeCXaYR0st/FwZbEwjpZb+Lgy3Mb/tauWX1Rlup2ubT2QAMSaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4rFumdz4yb0vuw6FHwnxi3TO58ZN6X3YdCj4TpWX+yo5I7Hy5neuX+fV+6WQAslKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALfbDncqut9q3B0lQVx9iLQjR0RS1Iw1ez4hXqQ7/wCjL/4qfPJ0Yb6x/K0yiP8A+x9EvuQ03bjGePo7iHq1R17itPNaFDQnnaeMdWvAbyT7VGaX/lqLZ3lyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAyMOuPauIW11D/o1Zan9IwixwHr1LNLNLCaWMIyxhrhGHXg/rnNF+J+7WjXLOL8lyUbzCbWtNH96alLGMP663Rgr1s2LOafAst4hCX4NG6rUYx7EZ5ZYw4OKry52ywwyN/oeu7iWXXGwu6Fz/u9jj/aopi3DJa/CwujZM9/8tXzajwcRp2xHcALZWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPmr0KfwYtY2dXoU/gxaxGv8MJFngl2mEdLLfxcGWxMI6WW/i4MtzG/7Wrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC8uxzs42OhfLtKMvIzT0alaPf5OrPPCP9IwUbhCMYwhCEYxjzoQeiOUMN9x8p4RhMZYSxsrGjbxhDsySQlj6FDn9ei3RRtnT0f8A6uslo011Vfp99jaIw2Vl7Cw2Peb68Y6uTtJKP/cqyU//ACSegPZ44n7R0EzWfJao4jilvb6uzCXkqv3cGrthUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB6MbDPGoYxsfcCkmn5Oth89eyq97kak0ZYfYmkTGqX/AOnZmCE+GZpyrUn1RpVqWIUZdfPhNL7HUj9XIU/6raA0WkPB/d/IuOYNCTk57uxq06cP/s5GPIf7tTz2jtR1RekygumDAve3pMx7CZafIUqd3NUoy9ilP8OT/bNCDYsgu+eu39VHnVvzU1/RyYDZFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+avQp/Bi1jZ1ehT+DFrEa/wwkWeCXaYR0st/FwZbEwjpZb+Lgy3Mb/ALWrll9UZbqdrm09kADEmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOKxbpnc+Mm9L7sOhR8J8Yt0zufGTel92HQo+E6Vl/sqOSOx8uZ3rl/n1fulkALJSgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOn0UYP7vaScv4VGSM8la+pxqwh16cseTn/2yxX/AFSthxgUb7P99jlSSMaWF2cYSTdirVjyMP8AbCotq1LPLvhYiKNkdrZsot+DYmrbIqH/AOotjUORyjl2nPt67i9rS/Ykpx4Rbx547NnMEMd09YjbU5+To4RbUbCSMI7WuEPZJ/6T1JofUplqhIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEx7DjM8MtaeMHkq1OQtsXlnwyrt8+NTVGnD/uS04fW9GHkZh15c4diFtiFnVjSubarLWo1Ic+WeWMIyx+qMIPVjIOYrbNuSsGzLacjCliVnTuORhHXyE00sOSk+eWbXD6gbtV7Zn5djQxzB800aeqndUY2deMIfryR5KSMe/GWaMP5FoXDadsrxzboxxXDqNPk7ujJ7btIQhrjGrT29UO/NDkpf5kzL7+8YimueDj+qLjbO/WKqY4VEgG9NOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfNXoU/gxaxs6vQp/Bi1iNf4YSLPBLtMI6WW/i4MtiYR0st/FwZbmN/2tXLL6oy3U7XNp7IAGJNAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcVi3TO58ZN6X3YdCj4T4xbpnc+Mm9L7sOhR8J0rL/AGVHJHY+XM71y/z6v3SyAFkpQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG1yjglzmTM+G4FZw/1r64kowjq18jCMduaPehDXGPzPyqqKYmqeCH7TTNUxELabE/LscF0W08RrU+RuMXrzXMYxht+xw+BJD5tUIzQ8NLrHwqxt8Mwy1w2zk5C2taMlClL8WSWWEsIf0gyGgYi7N67Vcnjlutm3Fq3FEcTGxe/tsKwq7xO9qex2tnQnr1p/iySSxmmj/SEXlBmvGLnMOZ8Ux68/8AkYjeVbqpDXzpqk8Zow/uv3s1c3e9nQjfWNCryF5jtWXD6cIR2/Y465qsfm5CWMsfDg88WFlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF3f8A0/s6wxLJWKZIuq2u4wit7ZtJYx2429WPwoQ8GprjHxkFInf7H3PM2jzSvg+YalSaWx9k9rYhCH61vU2p46uvyO1PCHZkgD08HzSqSVactWlPLPJPCE0s0sdcJoR50YR7D6BRrZA5Q95+kq/taFLkLC9j7cs9UNqEk8Y65YeDNyUPmhDso+XP2T2SY5ryBPiFnS5PE8G5K5pQhDbnpav9ST+kITQ78urrqYN1yvFfiLEaeGPNLUsxw+83p0cE+eABYoIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD5q9Cn8GLWNnV6FP4MWsRr/DCRZ4JdphHSy38XBlsTCOllv4uDLcxv8AtauWX1Rlup2ubT2QAMSaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4rFumdz4yb0vuw6FHwnxi3TO58ZN6X3YdCj4TpWX+yo5I7Hy5neuX+fV+6WQAslKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALDbDfKHtnFr/Od3S/07SEbSyjGHPqTQ/1JofNLGEP549hAmDYdeYvi1pheH0Y1ru7rS0aMkP1ppo6oL+6P8tWmUMn4dl6z1TS2lKEKlSENXslSO3PP9c0Yx/sps6xW9Wd7jhq7FrlOH3y7vk8FPa3wOZ0p5vs8iaP8YzVexljLY28ZqVOMei1Y/BpyfzTRlh9etqTZlLdnVnWGYtLFPLtrW5Oyy9Q9gjCEdcI3FTVNVj9UISS/PJFXxk4pfXeKYndYlf1pq93d1p69erNz5555ozTTR+eMYxYwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPQLYU6RYZw0YSZevq/JYvl2EttNCaPwqltHoM/1QhGSPgwj108vL7QVpBu9GukjD8yUeTntIR9gxCjL/1reaMOTh88NUJod+WD05wu/s8Uwy1xLD7inc2d1SlrUK0kdctSSaEIyzQ70YRgDIUm2RWQI5JztUrWVHkcGxOM1ezjCHwacdfw6X8sY7X7sYd9dly+lHJtjnrJ91gV5yMlSaHslrX1a40a0P0Zvm58Iw68IxT8uxk4W94U8E8KHjsL+ItaI4Y4FARn5hwjEMAxq7wfFbea3vLSpGnVkj1ow68OzCMNuEevCMIsBu0TFUaYajMTE6JAH6/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/2VHJHY+XM71y/z6v3SyAFkpQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHaaHch3mf84UcLpQnp2FHVVv7iEOhUtfOhH403Oh/XnQi8XLlNqia6p80Pdu3VcqimnhlL2xDyBHkqmfcToaoQ5Khhks0Of1qlWH95Ifzd5ZRj4ZY2mGYdb4dYUJLe1tqctKjSkhtSSyw1QhBkNFxeJqxN2bk/cNxw1iLFuKIFLNnzpFhiOPWWjvDa/JW+Gxhd4lGWO1NXml/05I+DJGMY9+eHXgtBppz7YaN9HmI5nvOQnrU5fYrKhNHo9xNCPISfNz4x7Ess0XmFjOJXuMYveYtiVxPc3t5Wnr3FWfnzzzRjGaMfrijM7EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAW/2CulqHIcq/HrnVGHJVcFq1Jufz5p7fX/AFml/mh2IKgP3w+8usPvre/sbipb3VvUlq0atObkZqc8sdcs0I9aMIwhEHroIo2NGlyz0p5LlnuZ6VLMWHyy08Tt4bXJR61aSHxJtX1R1w7EYyuCHtkhorhnPCfd7BKEPd+yp6uQlh/8ulDb5Dwofqx+rsaqdzyTU55pJ5YyzSx1TSxhqjCPYi9JUAbI3Q1HGfZ835Ttf/5KEIz31lTl/wDk9mpJD9p2Yfrc/n/pX2U5lvf/AIbs+binZ/pTZlgN8/8ALbjz8cbVWB/ZoRlmjLNCMIwjqjCPWfxtDXQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHzV6FP4MWsbOr0KfwYtYjX+GEizwS7TCOllv4uDLYmEdLLfxcGW5jf9rVyy+qMt1O1zaeyABiTQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHFYt0zufGTel92HQo+E+MW6Z3PjJvS+7DoUfCdKy/wBlRyR2PlzO9cv8+r90sgBZKUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABm4FhOI45i1vhWE2lW7vbmfkKVKnDXGMf+IQ58Yx2oQ235MxEaZfsRMzoh+uWMCxPMmO2uC4PbTXF5dT8hTkhzodmaMetLCG3GPWhBefRRkXDsg5Uo4RZ8jVuZ9VS8udWqNerq2496WHOhDrQ78YxjptB2i+w0e4LGpW9juscupIe27mENqSHP8AY5OxLCPPj+tHbj1oQkZqOaZj+Jq8Cj1Y62z5dgd4p8Ov1p6h/J55ack0880JZJYa5pox1QhDsxf1VbZs6Z5cMsK2jTLN3/7+6k1YxcU5ugUow6BCPxpofpdiWOr9aOqoWaFNljpYjpJz5G0wuvGbLmDzTUbHVH4NefXqnr/zatUv7sIc6MYoYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHSaNc6Y5kDN9nmbALj2O6t5tU9ObX7HXpx/Spzw68sf7R1RhqjCEXpRoj0hYDpKyfb5hwOrq16pLq1mmhGpa1dW3JN6YR68NUXlm7XQ7pJzBoxzZTxzA6vJ0p9Ul7ZzzRhSuqWv9GbsRh1pufCPe1wiHqMOT0V6QMuaR8q0cfy7dcnJHVLcW88YQq21TVtyTw60exHnRhtwdYCD9PGhC3zPGvmLKtOla41HXPXttqWneR7PYlqd/nR6+qO2qhiNld4dfVrG/tqtrdUJ4yVaNWSMs8k0OtGEec9H3CaVtFuXNIFnGa9p+08Ukl5GhiFGWHJy9iE0P15e9H6owXeX5tVZ0W7vnp64/0qcblkXfTt+ae1RQdlpJ0bZoyHeRkxezjUspptVG+oQjNRqdiGv9Wb92OqPzw23Gtot3KLtPhUTphrtduq3V4NUaJAHt4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfNXoU/gxaxs6vQp/Bi1iNf4YSLPBLtMI6WW/i4MtiYR0st/FwZbmN/2tXLL6oy3U7XNp7IAGJNAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcVi3TO58ZN6X3YdCj4T4xbpnc+Mm9L7sOhR8J0rL/AGVHJHY+XM71y/z6v3SyAFkpQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEr6JdCGY85TUsQxOWpg2CTapvZ6sn+rXl/+uSPWj8aO12NfOYr1+3Yp8K5OiGW1ZrvVeDRGmXCZKypjmccbp4RgNlPc15tuebnU6UvXmnm/Vh//AMhrjtLl6HdF2DaPML10uRvMYryarq+ml1Rj+5JD9WT+8efHrQh0eSsp4Dk7BpMKwCxktaMNUak3PqVZvjTzc+aPo62qDeNTx+Z14n0afNT28rZcFl9OH9Krz1dnIAh/ZH6b8I0WYNNZWcaN/mi6p67Sz165aMI86rV1c6XsQ580edqhrjCqWLE2UWmy00ZZfjhWEVaVfNd/Sj7WpbU0LSSO17NPD/GEefHvQi89b66ub69r3t7cVbi5uKk1WtVqTRmnqTzR1xmjGPPjGMdetlZjxrFcxY5d43jd7VvsQvKkalevVjrmmmj6IQhtQhDahCEIQ2mvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB1WjDP+ZdHOZ6WPZavI0asNUtehPrjRuaevbkqS9eH94c+EYRehGg3THlfSpg8J8OqwssZoyQjeYZWnh7JT7M0kf15Nf60O9rhCLzNZuCYriWB4rb4rg99cWN9bTwno3FCeMk8k3ejD/8ARB63CrmgXZVYbjEtvgOkmajhmI7UlPFpZeRtq8f/ALYQ6FN3/wBHn/orQUKtKvQkr0KslWlUlhNJPJNCaWaWO3CMIw58AfN7a219aVbS9t6Nzb1ZeRqUqskJ5J4diMI7UYIJ0k7HHCMSmq3+TbuXCbmO3GzrxjNbzR/dm25pP90O9BPYz2MTdw9Wm3OhhvYe3ejRXGl595zyRmnJ917BmDB7m0ljHVJW1clSn8GeGuWPza9bnXpFdW9vd29S2uqFKvQqQ5GenUkhNLNDsRhHaiirOegDIePxnr2FvWwK6m1x5Kym/wBKMe/Tm1w1d6XkV/h89pnzXqdH6wpb+TVR57U6f0lTITXmrY351w2aepgl1Y43Rh+jLLP7BWjDvyz/AAf90UX5hyjmjL00YY3gGJWEsP161vNCSPzTatUfqiuLOMsXvUqifvYq7uFvWvXpmGkASGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB81ehT+DFrGzq9Cn8GLWI1/hhIs8Eu0wjpZb+Lgy2JhHSy38XBluY3/a1csvqjLdTtc2nsgAYk0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxWLdM7nxk3pfdh0KPhPjFumdz4yb0vuw6FHwnSsv9lRyR2PlzO9cv8APq/dLIAWSlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIQjGMIQhGMY86EAB1mW9G+eswxkjhWWMRqU5/0a1Wl7FSj/ADz6pf7pUynsZcbuYyVszY5a4fTjtxo2ksa1T5ozR1Swj34ckiXsdh7PrVx2pNrB37vq0yr+7zR/olzrnOanWsMMmtLCb/8AvbzXTpauzLta5/5YR+pavJWh7IWVIyVrTBpL28k24XV/H2afX2YQjDkZY9+EsIu/U+Iz3is0/We5a2Mm47s/SO9FGjPQVlLKUad7iEkMdxSXVGFa5pw9ipx/cp7cPrm1x7GpK4KG7euXqvCuTplc2rVFqnwaI0QDW5nx/Bcs4NXxnMGJ22G2FCGupXrzwllh2IQ7MY9aENcY9ZTDT9spMUzJLcZf0exuMIwmbXJWxGb4N1cw53wP2UsftR/d24MTIlzZI7I7C8i07nLeUKlDE8z6oyVasNU9Cwj1+S609SHxOdCP6XO5GNFcaxTEcaxa5xbFr2ve311UjUr1608Zp55o9eMWJGMYxjGMYxjHnxi/gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACT9DmnHPOjOrJbYbewxDBuS1z4XeRjNS78acefTjz/wBHa18+EUYAPRzRJsh9H2f5aNnNfQwHGZ9UI2F/PCXk5uxTqfoz96G1NH4qX3kIlTRhp90k5BlpWtjjMcTwynqhCwxKEa1OWXsSTa4TyQ70s0Id6IPScVx0ebLnIuNS07bNdjeZau47U1XVG4tox8KWHJw+uXVDsp5y1mTL+ZrKF7l7GsPxW32tdS0uJasJe9HkY7Ue9HbBtSMIRhqjDXCIA5rG8gZJxrko4llXCK883Pqe1ZZKkf55YQm/u47Fdj7o0vYxjQw69w+Mfk15PH/PkkrDPRib1v1a5j6sNeHtV+tTE/RAuIbGHK9SMY2GYsYt4ditLTq+iErUXGxakjrjb52mh3p8M1/3hV/4WREinNMXTwV9jBOXYaeGjtVgn2LmJwj8DN9nGHfspof+T8+Zexrurw/yaf8AFaMe/G+L+PqjuefFmF+HrnvVc5l7Gu6vD/Jp/wATmXsa7q8P8mn/ABWjDxvi/i6o7jxZhfh6571XOZexrurw/wAmn/E5l7Gu6vD/ACaf8Vow8b4v4uqO48WYX4eue9VzmXsa7q8P8mn/ABOZexrurw/yaf8AFaMPG+L+LqjuPFmF+HrnvVc5l7Gu6vD/ACaf8TmXsa7q8P8AJp/xWjDxvi/i6o7jxZhfh6571XOZexrurw/yaf8AE5l7Gu6vD/Jp/wAVow8b4v4uqO48WYX4eue9VzmXsa7q8P8AJp/xOZexrurw/wAmn/FaMPG+L+LqjuPFmF+HrnvVc5l7Gu6vD/Jp/wATmXsa7q8P8mn/ABWjDxvi/i6o7jxZhfh6571XOZexrurw/wAmn/E5l7Gu6vD/ACaf8Vow8b4v4uqO48WYX4eue9VzmXsa7q8P8mn/ABOZexrurw/yaf8AFaMPG+L+LqjuPFmF+HrnvVc5l7Gu6vD/ACaf8TmXsa7q8P8AJp/xWjDxvi/i6o7jxZhfh6571XOZexrurw/yaf8AE5l7Gu6vD/Jp/wAVow8b4v4uqO48WYX4eue9VzmXsa7q8P8AJp/xOZexrurw/wAmn/FaMPG+L+LqjuPFmF+HrnvVc5l7Gu6vD/Jp/wATmXsa7q8P8mn/ABWjDxvi/i6o7jxZhfh6571XOZexrurw/wAmn/E5l7Gu6vD/ACaf8Vow8b4v4uqO48WYX4eue9VzmXsa7q8P8mn/ABOZexrurw/yaf8AFaMPG+L+LqjuPFmF+HrnvVc5l7Gu6vD/ACaf8TmXsa7q8P8AJp/xWjDxvi/i6o7jxZhfh6571W59i7jU0k0vvrw/bhq/+NP+LE5lLHO67DvJp/xWvHmrNMVVw1dUdz1Tl2Hp4KeuVbLPY34zb2tKjHMthNGSWENfsE+3/d+3M64z3SWH/YnWNFXVZoqmZmOFtlrdNmdqiKKbnmiNEeani+iuXM64z3SWH/YnOZ1xnuksP+xOsaPO8W9j35V5r83/AOae5XLmdcZ7pLD/ALE5zOuM90lh/wBidY0N4t7DyrzX5v8A809yuXM64z3SWH/YnfnW2O2Pwh/o5gwyeP78k8vohFZEN4t7CN1ea/M/+ae5VjEdAuebaGu3mwu+71G5jLH/AHyyuYxfRnnzC4ze2csX88JYa4zW8kK8NXZ104xXOHmcNRPAm2d2mPon04pq+kx2T/Cg1ejWt6saVelUpVJefLPLGWMPqi+F8MVwnC8Wo+w4ph1pfU+tLcUZakIf1gjzMug7JOKyzT2NG5wivGG1NbVIzSa+/JNrhq70NTFVhp4pXeF3b4evzX7c0/rHnj+J7VUhK2btBWbcJhPXwmehjVvLrjqpf6daEO/JNHVH5oRjFF99aXdhdT2t7bVra4px1T0q0kZJpY9+EduDBVRVTww2vB5jhcbGmxXFXb0cL8QHlNAAAAAAAAAAAAAABscBwLGMeu/amDYbdX1bry0acZoS9+MedCHfilrKmx9xm6hLWzHilDDpI7caFvD2ar80Y7UsPq5J7pt1VcEK3G5tg8D7e5ETs4Z6I86FGVhuG4jiVeFDDrC6vKsY6oSUKM1Sb+kILa5b0QZDwTkZ4YRDEK0v/VvpvZdf8u1J/tdxaW1taUJbe0t6VvRl/Rp0pISyw+aENpnpws8ctWxW7i1T5rFqZ/WZ0dUae2FQMK0S6QcRl5Knl2vQk7NzUko6vqmjCP8AZ0ljsf8AOdeSE1xe4Pa/uzVp5pofZk1f3WgGSMNRCku7sswr9XwaeSO+ZVwk2O2ORh8PMWHSx71KeP4PrmdcZ7pLD/sTrGj1vFvYi+Vea/M/+ae5XLmdcZ7pLD/sTnM64z3SWH/YnWNDeLew8q81+b/809yuXM64z3SWH/YnOZ1xnuksP+xOsaG8W9h5V5r83/5p7lcuZ1xnuksP+xOczrjPdJYf9idY0N4t7DyrzX5v/wA09yq15sWMcr3VWtDNmHSwnmjNq9rT7X931b7FnG6UkZY5sw6OuOv/AONP+K04tLeY4i3ERTVwfpDVL+EtX66rlyNM1TpnllVzmXsa7q8P8mn/ABOZexrurw/yaf8AFaMZPG+L+LqjuYfFmF+HrnvVc5l7Gu6vD/Jp/wATmXsa7q8P8mn/ABWjDxvi/i6o7jxZhfh6571XOZexrurw/wAmn/E5l7Gu6vD/ACaf8Vow8b4v4uqO48WYX4eue9VzmXsa7q8P8mn/ABOZexrurw/yaf8AFaMPG+L+LqjuPFmF+HrnvVc5l7Gu6vD/ACaf8TmXsa7q8P8AJp/xWjDxvi/i6o7jxZhfh6571XOZexrurw/yaf8AE5l7Gu6vD/Jp/wAVow8b4v4uqO48WYX4eue9VzmXsa7q8P8AJp/xOZexrurw/wAmn/FaMPG+L+LqjuPFmF+HrnvVc5l7Gu6vD/Jp/wATmXsa7q8P8mn/ABWjDxvi/i6o7jxZhfh6571XOZexrurw/wAmn/E5l7Gu6vD/ACaf8Vow8b4v4uqO48WYX4eue9VzmXsa7q8P8mn/ABOZexrurw/yaf8AFaMPG+L+LqjuPFmF+HrnvVc5l7Gu6vD/ACaf8TmXsa7q8P8AJp/xWjDxvi/i6o7jxZhfh6571XOZexrurw/yaf8AE5l7Gu6vD/Jp/wAVow8b4v4uqO48WYX4eue9VzmXsa7q8P8AJp/xOZexrurw/wAmn/FaMPG+L+LqjuPFmF+HrnvVc5l7Gu6vD/Jp/wATmXsa7q8P8mn/ABWjDxvi/i6o7jxZhfh6571XOZexrurw/wAmn/E5l7Gu6vD/ACaf8Vow8b4v4uqO48WYX4eue9VzmXsa7q8P8mn/ABOZexrurw/yaf8AFaMPG+L+LqjuPFmF+HrnvVdhsXsZ17ea7CEO9bT/AIv2pbFzEIx/1c42skP3bGab/wA4LOB43xfx9Udx4swvw9c96uVtsWraXV7YzrWqdn2PDoS+mpFusP2MuTaWqN7jWOXM3Yknp05Y/VyEY/3TmPFWZ4urhr7HunL8NTwUIzwnQRoysNUZsBnvJ4fr3N1Um/tCaEv9naYJlbLWB8jHB8Awuwml509vaySTfXNCGuLcCLXfu3PXqmfqkUWbdHq0xH0AGJkBy2d9IuR8lUpp8z5nw3Dp5Ya/YJ6vJV5od6lLrnj9UFedI2zGw23hUtchZeq3tXbhC9xP/TpQj2YUpY8lND55pfmBaq8ubaztal1eXFK3t6UsZqlWrPCSSSWHPjGMdqEFd9L2yuylluWth2SqUuZcThrl9sa4y2dKPZ5Ln1Pml1Qj8ZULSNpPzzpAuPZM05gurujCbkpLSSPsdvT7GqnLql19+MIx77jgdVpH0g5u0hYv7pZqxitezSxj7DQh8GjQhHrSSQ2pfn58dW3GLlQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZWF4jiGFXkl7hd9dWN1J+hWtq01OeX5ppYwjBigJjyfsl9LmXYSU58wU8at5OdSxShCtr+epDkakftJbyxs0NqWnmbJG3+tWw689FOeH/mqCA9B8A2VmiHEoS+3L/FcHmj1rywmm1R+elybucI0x6K8VhCNpn/L0Izc6Wvey0Jo/VU5GLy/AetWH49geI6o4fjOHXmvnewXUlTX/AEi2LyEZVriWI2sNVrf3VCHYp1ppfREHriPJ2nmvNFOGqnmTGZIdiW+qQ/8AJ+sM55whDVDNeOwhvjV4wPV0eUXv0zj3WY95xq8Y9+mce6zHvONXjA9XR5Re/TOPdZj3nGrxj36Zx7rMe841eMD1dHlF79M491mPecavGPfpnHusx7zjV4wPV0eUXv0zj3WY95xq8Y9+mce6zHvONXjA9XR5Re/TOPdZj3nGrxj36Zx7rMe841eMD1dHlF79M491mPecavGPfpnHusx7zjV4wPV0eUXv0zj3WY95xq8Y9+mce6zHvONXjA9XR5Re/TOPdZj3nGrxj36Zx7rMe841eMD1dHlF79M491mPecavGPfpnHusx7zjV4wPV0eUXv0zj3WY95xq8Y9+mce6zHvONXjA9XR5Re/TOPdZj3nGrxj36Zx7rMe841eMD1dHlF79M491mPecavGPfpnHusx7zjV4wPV0eUXv0zj3WY95xq8Y9+mce6zHvONXjA9XR5Re/TOPdZj3nGrxj36Zx7rMe841eMD1dHlF79M491mPecavGPfpnHusx7zjV4wPV0eUXv0zj3WY95xq8Y9+mce6zHvONXjA9XR5Re/TOPdZj3nGrxj36Zx7rMe841eMD1dHlF79M491mPecavGPfpnHusx7zjV4wPV0eUXv0zj3WY95xq8Y9+mce6zHvONXjA9XR5Re/TOPdZj3nGrxj36Zx7rMe841eMD1dHlF79M491mPecavGfrbZ9zzbT8nbZzzHRmh+tTxStLH+0wPVgeZmDaddLuExhG1z7i9TV8rnlueFhMkHLOy80lYfGWTGLHBMapQ/SmnoTUKsfmmkjCWH2YgvkK2ZL2YORcTmko5mwbFMAqzc+rJquqEvzxlhCf+kkU6ZOzplPONp7ayxmHDsVkhDXNLb1oRnk8KT9KX64QBv2mzTlbAMz2ntbHMLt7yWENUk80uqpJ4M8PhQ+qLchMaXu3cqt1RVROiY44Vu0haBsRw+FS+ylcTYjbw+FG0rRhCvLD92O1Cf5tqPzoYureva3FS2uqNShWpzRlnp1JYyzSxh1owjtwivw4/SJo7y9nW1j7foe17+WXVSvaMsIVJexCb48vej9UYI1zDxPnpbplO7C7amLeM9Knbxxy7e3lUzHU6Q8iY7knEfa+J0fZLapH/AELunCMaVWHz9absyx2/nhtuWQ5iYnRLouHxFrEW4uWqtNM8cAD8ZgAAAAAAEk6KdE2L5xmp4jfRnw7BdfR4y/6leHYpwj1v3o7Xz6tT9ppmqdEImMxtjBWpu36tEffBtcNgGC4rj+IyYdg9hWvbmfnSU5deqHZjHnQh347SecgaArO3lp3ucLr21V2pvaNvNGWnL3p5+fN80NXzxS3lPLOCZWwyXD8EsKdrS2uTmhtz1Yw6883Pmj/+hqbhNt4emnz1edzbNd12JxUzRhvQp/8AqfrxfTpYmE4Zh2EWUllhdlb2dtJ+jTo04SS/PtdfvssEhqUzNU6Z4QaDOWdcpZOtPbOaMw4dhUkYa5JbitCE88P3ZP0pvqhFBWdNmDkbDJp6OWcGxTH6svOqz6rWhN80ZoRn/rJAfiygoZmbZeaSsRmmkweywTBKUf0YyUI16sPnmqRjLH7MEeY1py0uYvNNNdZ+xqnyXPhaVYWsP6UoSg9Nh5S1s852rVI1K2cMw1J48+afEq0Y/wB5nx79M491mPecavGB6ujyi9+mce6zHvONXjHv0zj3WY95xq8YHq6PKL36Zx7rMe841eMe/TOPdZj3nGrxgero8ovfpnHusx7zjV4x79M491mPecavGB6ujyi9+mce6zHvONXjHv0zj3WY95xq8YHq6PKL36Zx7rMe841eMe/TOPdZj3nGrxgero8ovfpnHusx7zjV4x79M491mPecavGB6ujyi9+mce6zHvONXjHv0zj3WY95xq8YHq6PKL36Zx7rMe841eMe/TOPdZj3nGrxgero8ovfpnHusx7zjV4x79M491mPecavGB6ujyi9+mce6zHvONXjHv0zj3WY95xq8YHq6PKL36Zx7rMe841eMe/TOPdZj3nGrxgero8ovfpnHusx7zjV4x79M491mPecavGB6ujyi9+mce6zHvONXjHv0zj3WY95xq8YHq6PKL36Zx7rMe841eMe/TOPdZj3nGrxgero8ovfpnHusx7zjV4x79M491mPecavGB6ujyi9+mce6zHvONXjHv0zj3WY95xq8YHq6PKL36Zx7rMe841eMe/TOPdZj3nGrxgero8ovfpnHusx7zjV4x79M491mPecavGB6ujyi9+mce6zHvONXjHv0zj3WY95xq8YHq6PKL36Zx7rMe841eMe/TOPdZj3nGrxgero8oZs5ZvmhqmzVjsYd/EKvGfjWzPmWtDVWzDi9Twr2pH/AJB6xzTSyyxmmjCWEOfGMdqDTYlm3KuGQjHEszYLZQhz43F/Sp6vtTQeUlzd3VzHkrm5rVo9mpPGb0vxB6aYzp10RYTCMbrPuD1NXySea54KEzgsw7LrRfh8JpcMt8dxieH6MaNrClJH541JpYw+zFQgBarNOzNx6vCanlnJ2HWMOdCrf3E9xH5+Rk5CEI/XFEGctO+lbNUJ6WIZwvra3n2vYLDVayauxH2OEJpoeFGKNAH1Unnq1JqlSeaeeaOuaaaOuMY9mMXyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADIw6+vcNvaV9h15cWd1SjyVOvQqxp1JI9mE0IwjBjgLD6K9ldnjLc1KyzZTkzRhsuqEalSMKd3JDvVIQ1T/zQjGPxoLeaLNK2SdJNj7NlnFpZ7qSXkq1hX1U7mj88mvbh+9LGMvfeXjKwrEL/AArEaGI4ZeXFleW88J6NehUjJUpzQ68JobcIg9cRUvY/bKqndz2+XdJ9SnRrRjCnQxqWWEsk0etCvLDal8OG12YQ25lsqNSnWpSVqNSSpTnlhNJPLHXCaEduEYR68AYuN4Vh2NYZWwzFbSld2laXkZ6dSG1Hvw7EYdaMNuCqmmLRhfZJu431nGpd4HWn1Uq0Ya5qMY86Spq/tNzo96O0tu/DEbO1xGxrWN9b07i2ryRkq0qkNcs0setFjuW4rhc5PnV/LLvhU+emeGNvdP6qFCQdNGjm5yRi8Li1hPWwW6nj7Wqx24048/2OePZh1o9eHfhFHyuqpmmdEuv4PF2sZZpvWp00yAPxKAAATlsfdFst/Gjm3MdvyVrCPJWFrUhtVYw/6k0Pi9iHX5/O1a/VFE1zohX5lmVnLrE3rv0jjmdj+6EtD3t+ShmPNtvGFrHVPa2E8NUasOtPUh1pexL1+vtbUbEU5JKdOWnTklkklhCWWWWGqEIQ50IQf0WNFEURohx7Mszv5je329PJHFHID8b+7tbCyrXt9c0bW1oSRqVq1aeEklOWENcZpox2oQh2VQNPmysr1p7jL+jCeNGjDXJWxqpJ8Ofs+wSx/Rh+/NDX2IQ2ovauWI0raXcjaNbWMcxYrLG+ml5Klh1tCFS5qdj4Ov4MI/GmjCHfVF0pbKzPeZZqtnlaWTK2Gza4Qmox9kup4d+pGHwf5IQjDsxQFfXd1f3lW9vrmtdXNaeM9WtWnjPPPNHnxmmjtxj34vwBkYhe3mI3lS9xC7uLy6qx5KpWr1I1J549mM0duLHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABYDYxbIO/wAgXVDLOaa1a9yrUmhLJPHXNUw+MY/pSdeNPsydbny7euE1fwHrph95aYjYUL+wuaVza3FOWrRrUpoTSVJJoa4TQjDnwjB+6imw904T5PxajkfNF5GOXb2ryNpXqzbVhWmj2etTmjHb60sY69qEZl6wa7MuCYfmLA7rB8Uowq2tzJyM0OvLHrTQj1owjtwipln7K1/k/M1zgt9CM3IR5KjV1aoVqcf0Z4f89iMIw6y7yO9PGSJc35Snr2dGE2L4fCNW2jCHwqkv61P64Q1w78IdmLDft+HGmOFs25nOZy/Eb3cn/wAdXD+k7e/9ORUcIwjCOqO1EV7rgDOy/hV7jmNWmEYfS9kurqrCnTh1tvrx7EIQ1xjHsQIjS8V100UzVVOiIdzoJ0fxzlmCN5iFKb3FsZoTXEed7NPz4UoemPe7GuC2lOSSlTlp05JZJJIQllllhqhCEOdCEGnyVl2xyrlq0wSwlh7HQk+HU1ao1Z4/pTx78Y/02odZuVlat+BTocZzzNq8zxM1/wDCPNTH6beWf9cQ1uZ8ewjLOA3eO47fUrHDrOn7JWrVI6oSw60IdeMYx1QhCG3GMYQhtsvEby0w6wuL+/uKVtaW1OarWrVJuRkpySw1xmjGPOhCEHndsnNNF9pRzJGyw+pVt8rWFSMLK3jrljXmhtez1IfGjt6oR/RhHsxjryKZ9bIvTvjmlDEamG2M1bDMrUZ/9CyhNqnuNUdqpW1c+PXhLzpe/HbjDQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL47CnS1NnDKs2S8cueTxzBaMPa9SebXNc2sNUIR780kdUsezCMsduOtQ50OjjNmJZGztheacKmj7YsK8J4ya9UKskdqenHvTSxjCPzg9Whrcq45h+Zct4dmDCqvstjiFvJcUZuvyM0NeqPYjDnRh1owi2QKnbIjKEMtZ2mvrSlyGH4ryVxShCGqElTX/qSQ+uMI/NNCHWRouDp1yzDM2jy9p0qfJ3ljD23baobeuSEeSl+uXkoauzqU+V9+jwauV13ctmM43BRTVPpUeaeTino830FhNivlCFO3uc43lL4dTXb2PJQ50sOiTw+ePwYR703ZQPgeHXOMYzZ4VZy8lcXdaSjTh1tc0dW33l4svYVa4HgdlhFlLyNvaUZaUm1qjHVDnx78Y7ce/F6w1GmfC2IO7LMZsYaMNRPnr4eSO+f5ZwOA2QGkKjo10ZYjmGE0kcQnh7Ww6lN+vcTwjyO114SwhGeMOxLGHXTnMFddnLpdmur2bRjl+61W1CMs+NVac3RKnPloa+xLtTTd/VD9WKpr9r26uL28r3l3WqV7mvUmq1qs82uaeeaOuaaMevGMYxi/EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF1P8A0/c9TX+W8VyDe1uSrYZN7dsYTR2/YJ5tVSWHelnjCP8A/lWneZGxwzdHJWmbL2MT1fY7SpcwtLzXHa9hq/AmjHvS64Tfywem4ClOlPAPezn7FsJkl5GhJWjUt4f/AFT/AApYfVCOr6l1ledlrg0KeIYNj9OXo1Oe0rRhDryx5KT64wmm/owYinTRp2Nr3H4zeMfvU8FcaPrHnj+Y+rUbFnAIYhnS5xytJro4XQ+BH/7amuWH+2E/9lnUZbGnBoYXozoXk0sIVsSrz3E0dW3yMI8hLD+kuv8AmSa9WafBohA3R4z8VmNyrip9GPp/vTIoRs58+TZl0oS5Xs63JYdl2SNKaEsdqe5n1RqR/lhyMnejLN2V28/5itso5JxnM11qjSw2zqXHIxj+nNLLHkZPnmm1Q+t5U4pfXWJ4ndYlfVZq11d1p69epNz5555ozTRj88YxZVGxgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHqboYzHHNuinLWYZ6nsla7w+nGvNr59aWHIVP98szyyX42A+MT4hoSrYdUm1xwvFa1CnDXzpJ5ZKsP8AdPOCwaPNkRhE2L6MLz2KSM9e0r0rilLCHPjyXIR/2zzJDfFxRpXFGajXpy1Kc8NU0s0NcIvyqPCjQkYTEVYa/Rep4aZiehiZew6nhGA4fhVLVyFnbU6EIwhz+RlhDX/ZnA/WCqqapmZ4ZV02fWZY4Voks8v0anI1cbv5ZZ5df6VGj/qTf7/YlD1lP/UFx2N9pRwjApJoxpYXhkJ5odipWnjGb/bJTVrH4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALLbAjPdtgWeMRydiNeWlQx6SSa0mmjqhC5p69Une5OWaPzxllh11aX6W1eta3NK5tq1SjXpTwnp1Kc0ZZpJoR1wjCMNuEYR64PXcVb0C7KnBsRw+3wPSVW9zsTpywpyYrCSMaFz1oRqQhDXTn7MdXIx24/B5yyuC43g2N2st1g2LWGJUJoa4VLS4kqyxh88sYgz34393bWFjXvr2vTt7a3pzVa1WpNqlpySw1zTRj1oQhCMWgzjn/JWULWe4zJmfDMOhJDX7HUrwjVm8GnDXPNHvQhFTDZMbIy50gW1XK2U6Vxh+W4zf+4rVPg1r7VHXCEYQ/Qp69vkefHa16ucCKtNmcff7pSx7NMsJoW93c6rWWaGqMKEkISU9cOtHkZYRj34xcaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/2Q==';
document.getElementById('escudoImg').src = 'data:image/png;base64,' + ESCUDO_B64;

// ============================================================
//  DATA
// ============================================================
const CATEGORIES = ['4TA','5TA','6TA','7MA','8VA','9NA'];
const LINK_CATS  = ['4TA','5TA','6TA'];
const CAT_COLORS = {
  '4TA':'#f0c040','5TA':'#60a5fa','6TA':'#f87171',
  '7MA':'#f472b6','8VA':'#a78bfa','9NA':'#34d399'
};
const LINK_TYPES = [
  { key:'cit', label:'Citaciones',       icon:'📋' },
  { key:'par', label:'Partido',          icon:'▶'  },
  { key:'res', label:'Resumen Goles',    icon:'⚽'  },
  { key:'ana', label:'Análisis Propio',  icon:'📊'  },
  { key:'prx', label:'Próximo Rival',    icon:'🔍'  },
];

const RIVALS = [
  {f:1, r:'IND. RIVADAVIA',    c:'L'},{f:2, r:'FERRO',              c:'V'},
  {f:3, r:'LANÚS',             c:'L'},{f:4, r:'INDEPENDIENTE',      c:'V'},
  {f:5, r:'NEWELLS',           c:'L'},{f:6, r:'SAN MARTIN SJ',      c:'V'},
  {f:7, r:'ARGENTINOS JRS',    c:'L'},{f:8, r:'INSTITUTO',          c:'V'},
  {f:9, r:'TALLERES',          c:'L'},{f:10,r:'ESTUDIANTES RC',     c:'V'},
  {f:11,r:'BARRACAS CENTRAL',  c:'L'},{f:12,r:'QUILMES',            c:'V'},
  {f:13,r:'RIVER PLATE',       c:'L'},{f:14,r:'UNIÓN',              c:'V'},
  {f:15,r:'SAN LORENZO',       c:'L'},{f:16,r:'GIMNASIA LP',        c:'V'},
  {f:17,r:'CENTRAL CÓRDOBA',   c:'L'},{f:18,r:'GIMNASIA MENDOZA',   c:'V'},
  {f:19,r:'VÉLEZ SARSFIELD',   c:'L'},{f:20,r:'BANFIELD',           c:'V'},
  {f:21,r:'RACING',            c:'L'},{f:22,r:'ROSARIO CENTRAL',    c:'V'},
  {f:23,r:'GODOY CRUZ',        c:'L'},{f:24,r:'PLATENSE',           c:'V'},
  {f:25,r:'SARMIENTO',         c:'L'},{f:26,r:'BELGRANO',           c:'V'},
  {f:27,r:'ATL. DE RAFAELA',   c:'L'},{f:28,r:'DEP. RIESTRA',       c:'V'},
  {f:29,r:'ALDOSIVI',          c:'L'},{f:30,r:'BOCA JUNIORS',       c:'V'},
  {f:31,r:'COLÓN',             c:'L'},{f:32,r:'HURACÁN',            c:'V'},
  {f:33,r:'ESTUDIANTES LP',    c:'L'},{f:34,r:'DEFENSA Y JUSTICIA', c:'V'},
  {f:35,r:'ATL. TUCUMÁN',      c:'V'},
];

const PREFILLED = {
  '4TA':{1:[1,0],2:[0,1],3:[2,4],4:[2,3],5:[2,0],6:[4,0],7:[0,1],8:[0,2],9:[2,0]},
  '5TA':{1:[2,0],2:[0,0],3:[0,3],4:[0,0],5:[1,1],6:[4,0],7:[1,2],8:[2,0],9:[2,2],10:[2,2]},
  '6TA':{1:[3,1],2:[1,1],3:[0,7],4:[1,3],5:[3,1],6:[4,4],7:[1,2],8:[2,1],9:[1,2],10:[1,1]},
};

const results = {};
const links   = {};
CATEGORIES.forEach(cat => {
  results[cat] = {};
  links[cat]   = {};
  RIVALS.forEach(r => {
    results[cat][r.f] = (PREFILLED[cat] && PREFILLED[cat][r.f]) ? [...PREFILLED[cat][r.f]] : null;
    links[cat][r.f]   = {};
    LINK_TYPES.forEach(lt => { links[cat][r.f][lt.key] = ''; });
  });
});

// ============================================================
//  HELPERS
// ============================================================
function getResult(gf, gc) {
  if (gf === null || gc === null) return null;
  return gf > gc ? 'W' : gf === gc ? 'D' : 'L';
}
function calcStats(cat, from, to) {
  let pj=0,pg=0,pe=0,pp=0,gf=0,gc=0;
  for (let f=from; f<=to; f++) {
    const r = results[cat][f];
    if (r) {
      pj++; gf+=r[0]; gc+=r[1];
      const x = getResult(r[0],r[1]);
      if(x==='W')pg++; else if(x==='D')pe++; else pp++;
    }
  }
  return {pj,pg,pe,pp,gf,gc,dg:gf-gc,pts:pg*3+pe};
}
function calcStatsAll(from, to) {
  let pj=0,pg=0,pe=0,pp=0,gf=0,gc=0;
  CATEGORIES.forEach(cat => {
    const s=calcStats(cat,from,to);
    pj+=s.pj;pg+=s.pg;pe+=s.pe;pp+=s.pp;gf+=s.gf;gc+=s.gc;
  });
  return {pj,pg,pe,pp,gf,gc,dg:gf-gc,pts:pg*3+pe};
}
function getPeriodos() {
  const p=[{label:'TOTAL',from:1,to:35}];
  for(let s=1;s<=35;s+=5) p.push({label:`F${s}–F${Math.min(s+4,35)}`,from:s,to:Math.min(s+4,35)});
  return p;
}
function getBlocks() {
  const b=[];
  for(let s=1;s<=35;s+=5) b.push({label:`F${s}–F${Math.min(s+4,35)}`,from:s,to:Math.min(s+4,35)});
  return b;
}
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function chartDef() {
  return {
    responsive:true, animation:{duration:300},
    plugins:{legend:{labels:{color:'#5a7099',font:{family:'Barlow Condensed',size:11}}}},
    scales:{
      x:{ticks:{color:'#5a7099',font:{family:'Barlow Condensed'}},grid:{color:'rgba(26,45,90,0.4)'}},
      y:{ticks:{color:'#5a7099',font:{family:'Barlow Condensed'}},grid:{color:'rgba(26,45,90,0.4)'}}
    }
  };
}
function killChart(id){ const c=Chart.getChart(id); if(c) c.destroy(); }
function ST(text, extra='') {
  return `<div class="section-title" style="${extra}"><div class="st-bar"></div>${text}</div>`;
}
function statsHTML(s) {
  const dgColor = s.dg>0?'var(--win)':s.dg<0?'var(--loss)':'var(--muted)';
  const dgSign  = s.dg>0?'+':'';
  return `<div class="stats-grid">
    <div class="stat-card pts"><div class="val">${s.pts}</div><div class="lbl">Puntos</div></div>
    <div class="stat-card pj"><div class="val">${s.pj}</div><div class="lbl">Jugados</div></div>
    <div class="stat-card win"><div class="val">${s.pg}</div><div class="lbl">Ganados</div></div>
    <div class="stat-card draw"><div class="val">${s.pe}</div><div class="lbl">Empates</div></div>
    <div class="stat-card loss"><div class="val">${s.pp}</div><div class="lbl">Perdidos</div></div>
    <div class="stat-card gf"><div class="val">${s.gf}</div><div class="lbl">Goles a Favor</div></div>
    <div class="stat-card gc"><div class="val">${s.gc}</div><div class="lbl">Goles en Contra</div></div>
    <div class="stat-card dg"><div class="val" style="color:${dgColor}">${dgSign}${s.dg}</div><div class="lbl">Dif. Gol</div></div>
  </div>`;
}
function pieMiniHTML(id, s, label) {
  return `<div class="pie-mini-card">
    <h4>${label}</h4>
    <canvas id="${id}" height="155"></canvas>
    <div class="pie-stat-row">
      <span style="color:var(--win)">▲${s.pg}G</span>
      <span style="color:var(--draw)">${s.pe}E</span>
      <span style="color:var(--loss)">▼${s.pp}P</span>
      <span style="color:var(--gold2)">${s.pts}pts</span>
    </div>
  </div>`;
}
function drawPie(id, s) {
  if(s.pj===0) return;
  killChart(id);
  new Chart(document.getElementById(id).getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Ganados','Empates','Perdidos'],
      datasets: [{
        data: [s.pg, s.pe, s.pp],
        backgroundColor: ['rgba(34,197,94,.82)','rgba(245,158,11,.82)','rgba(192,21,42,.75)'],
        borderColor: ['#22c55e','#f59e0b','#c0152a'],
        borderWidth: 2,
      }]
    },
    options: { responsive:true, plugins:{ legend:{display:false} } }
  });
}
function ptabsHTML(id, periods, activeIdx=0) {
  return periods.map((p,i) =>
    `<div class="ptab${i===activeIdx?' active':''}" data-ptid="${id}" data-idx="${i}">${p.label}</div>`
  ).join('');
}

// ============================================================
//  TABS
// ============================================================
function buildTabs() {
  const wrap = document.getElementById('mainTabs');
  const addTab = (tab, label, cls='', dotColor='') => {
    const t = document.createElement('div');
    t.className = 'tab ' + cls;
    t.dataset.tab = tab;
    t.innerHTML = (dotColor ? `<span class="tab-dot" style="background:${dotColor}"></span>` : '') + label;
    t.addEventListener('click', () => switchTab(tab));
    wrap.appendChild(t);
  };
  addTab('GENERAL','⬡ GENERAL','general-tab');
  CATEGORIES.forEach((cat,i) => addTab(cat, cat, i===0?'active':'', CAT_COLORS[cat]));
}
function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab===tab));
  document.querySelectorAll('.cat-panel').forEach(p => p.classList.toggle('active', p.dataset.tab===tab));
  if (tab==='GENERAL') renderGeneral();
}

// ============================================================
//  BUILD ALL PANELS
// ============================================================
function buildAllPanels() {
  const content = document.getElementById('mainContent');
  // GENERAL
  const gp = document.createElement('div');
  gp.className='cat-panel'; gp.dataset.tab='GENERAL'; gp.id='panel-GENERAL';
  content.appendChild(gp);
  // Categories
  CATEGORIES.forEach((cat,idx) => {
    const panel = document.createElement('div');
    panel.className = 'cat-panel' + (idx===0?' active':'');
    panel.dataset.tab = cat;
    panel.innerHTML = buildCatHTML(cat);
    content.appendChild(panel);
    attachCatEvents(cat);
    renderCatStats(cat);
    renderCatCharts(cat);
  });
}

// ============================================================
//  CATEGORY HTML
// ============================================================
function buildCatHTML(cat) {
  const isLink = LINK_CATS.includes(cat);
  const periods = getPeriodos();
  const col = CAT_COLORS[cat];

  // Table rows
  let rows = '';
  RIVALS.forEach(r => {
    if ((r.f-1)%5===0 && r.f>1) {
      const pE = Math.min(r.f+4,35);
      const span = 6 + (isLink ? LINK_TYPES.length : 0);
      rows += `<tr class="divider-block"><td colspan="${span}">── BLOQUE F${r.f}–F${pE}</td></tr>`;
    }
    const stored = results[cat][r.f];
    const gf = stored ? stored[0] : '';
    const gc = stored ? stored[1] : '';
    const res = stored ? getResult(stored[0], stored[1]) : null;
    const rb  = res ? `<span class="result-badge result-${res}">${res}</span>` : '—';
    const pts = res==='W'?3 : res==='D'?1 : res==='L'?0 : '—';
    const ptC = res==='W'?'var(--win)':res==='D'?'var(--draw)':res==='L'?'var(--loss)':'var(--muted)';

    let linkCols = '';
    if (isLink) {
      LINK_TYPES.forEach(lt => {
        const val = links[cat][r.f][lt.key] || '';
        const has = val.trim() !== '';
        linkCols += `<td class="link-cell">
          <div class="link-wrap">
            <input class="link-input" type="url" value="${esc(val)}"
              placeholder="${lt.label}…"
              data-cat="${cat}" data-fecha="${r.f}" data-lkey="${lt.key}"
              title="${lt.label}">
            <a class="link-btn${has?'':' empty'}" href="${has?esc(val):'#'}"
              target="_blank" rel="noopener" title="${lt.label}">${lt.icon}</a>
          </div>
        </td>`;
      });
    }

    rows += `<tr>
      <td class="fecha-num">${r.f}</td>
      <td class="rival-name">${r.r}</td>
      <td><span class="cond-badge cond-${r.c}">${r.c==='L'?'LOCAL':'VISIT.'}</span></td>
      <td><div class="score-cell">
        <input class="score-input" type="number" min="0" max="99" value="${gf}"
          data-cat="${cat}" data-fecha="${r.f}" data-side="0" placeholder="—">
        <span class="score-sep">-</span>
        <input class="score-input" type="number" min="0" max="99" value="${gc}"
          data-cat="${cat}" data-fecha="${r.f}" data-side="1" placeholder="—">
      </div></td>
      <td>${rb}</td>
      <td style="font-weight:700;color:${ptC}">${pts}</td>
      ${linkCols}
    </tr>`;
  });

  // Link column headers (split: group header + individual)
  let groupHeader = '';
  let subHeaders = '<th>#</th><th>RIVAL</th><th>COND.</th><th>RESULTADO</th><th>RES</th><th>PTS</th>';
  if (isLink) {
    groupHeader = `<tr><th colspan="6" style="background:linear-gradient(135deg,#0a0f1e,#08111f);color:var(--muted);font-size:10px;letter-spacing:2px;">DATOS DEL PARTIDO</th>
      <th colspan="${LINK_TYPES.length}" class="link-group-header" style="background:linear-gradient(135deg,#0d1a3a,#08111f);color:var(--blue2);font-size:12px;letter-spacing:2px;border-top:2px solid var(--blue2);">🔗 LINKS</th></tr>`;
    LINK_TYPES.forEach(lt => { subHeaders += `<th title="${lt.label}">${lt.icon} ${lt.label}</th>`; });
  } else {
    groupHeader = `<tr><th colspan="6" style="background:linear-gradient(135deg,#0a0f1e,#08111f);color:var(--muted);font-size:10px;letter-spacing:2px;">DATOS DEL PARTIDO</th></tr>`;
  }

  return `
    ${ST(`RESULTADOS · <span style="color:${col}">${cat}</span>${isLink?' <span style="font-size:12px;color:var(--muted);font-family:Barlow Condensed,sans-serif">· CITACIONES Y LINKS</span>':''}`)}
    <div class="results-table-wrap">
      <table class="results">
        <thead>
          ${groupHeader}
          <tr class="subhead">${subHeaders}</tr>
        </thead>
        <tbody id="tbody-${cat}">${rows}</tbody>
      </table>
    </div>

    ${ST(`ESTADÍSTICAS · ${cat}`)}
    <div class="periodo-tabs" id="ptabs-${cat}">
      ${ptabsHTML(cat, periods)}
    </div>
    <div id="stats-area-${cat}"></div>

    ${ST(`GRÁFICOS · ${cat}`)}
    <div class="charts-row">
      <div class="chart-card"><h3>Puntos por Bloque</h3><canvas id="cpts-${cat}" height="200"></canvas></div>
      <div class="chart-card"><h3>Goles a Favor / En Contra</h3><canvas id="cgls-${cat}" height="200"></canvas></div>
    </div>
    <div class="charts-row">
      <div class="chart-card"><h3>Diferencia de Gol Acumulada</h3><canvas id="cdg-${cat}" height="200"></canvas></div>
      <div class="chart-card"><h3>Resultados Totales</h3><canvas id="cpie-${cat}" height="200"></canvas></div>
    </div>

    ${ST(`TORTAS POR BLOQUE · ${cat}`)}
    <div class="pies-grid" id="piesgrid-${cat}"></div>
  `;
}

// ============================================================
//  EVENTS
// ============================================================
function attachCatEvents(cat) {
  document.getElementById(`tbody-${cat}`).addEventListener('change', e => {
    const el = e.target;
    if (el.classList.contains('score-input')) {
      const f = parseInt(el.dataset.fecha);
      const s = parseInt(el.dataset.side);
      const v = el.value==='' ? null : parseInt(el.value);
      if (!results[cat][f]) results[cat][f] = [null,null];
      results[cat][f][s] = v;
      if (results[cat][f][0]===null && results[cat][f][1]===null) results[cat][f]=null;
      rebuildRow(cat,f);
      renderCatStats(cat);
      renderCatCharts(cat);
      if (document.getElementById('panel-GENERAL').classList.contains('active')) renderGeneral();
      saveData(); showSaved();
      saveData(); showSaved();
    }
    if (el.classList.contains('link-input')) {
      const f   = parseInt(el.dataset.fecha);
      const key = el.dataset.lkey;
      const val = el.value.trim();
      links[cat][f][key] = val;
      const btn = el.nextElementSibling;
      if (btn) {
        if (val) { btn.href = val; btn.classList.remove('empty'); }
        else     { btn.href = '#'; btn.classList.add('empty'); }
      saveData(); showSaved();
      }
    }
  });

  document.getElementById(`ptabs-${cat}`).addEventListener('click', e => {
    if (!e.target.classList.contains('ptab')) return;
    document.getElementById(`ptabs-${cat}`)
      .querySelectorAll('.ptab').forEach(t => t.classList.remove('active'));
    e.target.classList.add('active');
    renderCatStats(cat);
  });
}

function rebuildRow(cat, fecha) {
  document.getElementById(`tbody-${cat}`).querySelectorAll('tr').forEach(tr => {
    const inp = tr.querySelectorAll('.score-input');
    if (!inp.length || parseInt(inp[0].dataset.fecha)!==fecha) return;
    const r   = results[cat][fecha];
    const res = r ? getResult(r[0],r[1]) : null;
    tr.children[4].innerHTML = res ? `<span class="result-badge result-${res}">${res}</span>` : '—';
    const pts = res==='W'?3:res==='D'?1:res==='L'?0:'—';
    tr.children[5].textContent = pts;
    tr.children[5].style.color = res==='W'?'var(--win)':res==='D'?'var(--draw)':res==='L'?'var(--loss)':'var(--muted)';
    tr.children[5].style.fontWeight = '700';
  });
}

// ============================================================
//  CAT STATS
// ============================================================
function renderCatStats(cat) {
  const idx = parseInt(document.getElementById(`ptabs-${cat}`).querySelector('.ptab.active').dataset.idx);
  const p   = getPeriodos()[idx];
  document.getElementById(`stats-area-${cat}`).innerHTML = statsHTML(calcStats(cat, p.from, p.to));
  renderCatCharts(cat);
}

// ============================================================
//  CAT CHARTS
// ============================================================
function renderCatCharts(cat) {
  const blocks = getBlocks();
  const labels = blocks.map(b=>b.label);
  const col    = CAT_COLORS[cat];
  const def    = chartDef();
  const tot    = calcStats(cat,1,35);

  // Puntos bar
  killChart(`cpts-${cat}`);
  new Chart(document.getElementById(`cpts-${cat}`).getContext('2d'), {
    type: 'bar',
    data: { labels, datasets: [{ label:'Puntos',
      data: blocks.map(b=>calcStats(cat,b.from,b.to).pts),
      backgroundColor: blocks.map(b=>{const v=calcStats(cat,b.from,b.to).pts; return v>=9?'rgba(34,197,94,.75)':v>=5?'rgba(201,162,39,.75)':'rgba(192,21,42,.65)';}),
      borderRadius:5, borderSkipped:false }]},
    options: def
  });

  // GF/GC bar
  killChart(`cgls-${cat}`);
  new Chart(document.getElementById(`cgls-${cat}`).getContext('2d'), {
    type:'bar',
    data:{ labels, datasets:[
      { label:'GF', data:blocks.map(b=>calcStats(cat,b.from,b.to).gf), backgroundColor:'rgba(36,80,192,.7)', borderRadius:4 },
      { label:'GC', data:blocks.map(b=>calcStats(cat,b.from,b.to).gc), backgroundColor:'rgba(192,21,42,.55)', borderRadius:4 }
    ]},
    options: def
  });

  // DG line
  let dgAcc=[], acc=0, dgL=[];
  RIVALS.forEach(r => { const x=results[cat][r.f]; if(x){acc+=(x[0]-x[1]); dgAcc.push(acc); dgL.push('F'+r.f);} });
  killChart(`cdg-${cat}`);
  new Chart(document.getElementById(`cdg-${cat}`).getContext('2d'), {
    type:'line',
    data:{ labels:dgL, datasets:[{ label:'DG Acum.',data:dgAcc,
      borderColor:col, backgroundColor:col+'22', fill:true, tension:.3,
      pointRadius:3, pointBackgroundColor:dgAcc.map(v=>v>=0?'#22c55e':'#ef4444') }]},
    options:{...def, scales:{...def.scales, y:{...def.scales.y, grid:{color:ctx=>ctx.tick.value===0?'#5a7099':'rgba(26,45,90,0.4)'}}}}
  });

  // Pie total
  killChart(`cpie-${cat}`);
  new Chart(document.getElementById(`cpie-${cat}`).getContext('2d'), {
    type:'doughnut',
    data:{ labels:['Ganados','Empates','Perdidos'], datasets:[{
      data:[tot.pg,tot.pe,tot.pp],
      backgroundColor:['rgba(34,197,94,.82)','rgba(245,158,11,.82)','rgba(192,21,42,.75)'],
      borderColor:['#22c55e','#f59e0b','#c0152a'], borderWidth:2 }]},
    options:{responsive:true, plugins:{legend:{position:'bottom',labels:{color:'#5a7099',font:{family:'Barlow Condensed'}}}}}
  });

  // Block pies grid
  const grid = document.getElementById(`piesgrid-${cat}`);
  grid.innerHTML = '';
  blocks.forEach(b => {
    const s = calcStats(cat, b.from, b.to);
    const id = `pb-${cat}-${b.from}`;
    grid.insertAdjacentHTML('beforeend', pieMiniHTML(id, s, b.label));
    drawPie(id, s);
  });
}

// ============================================================
//  GENERAL
// ============================================================
function renderGeneral() {
  const panel  = document.getElementById('panel-GENERAL');
  const blocks = getBlocks();
  const periods= getPeriodos();

  const ptHTML = ptabsHTML('GEN', periods);

  let tableRows = CATEGORIES.map(cat => {
    const s = calcStats(cat,1,35);
    const dgC = s.dg>0?'var(--win)':s.dg<0?'var(--loss)':'var(--muted)';
    const pct = s.pj>0?Math.round(s.pts/(s.pj*3)*100):0;
    return `<tr>
      <td class="cat-cell"><span class="dot" style="background:${CAT_COLORS[cat]}"></span>${cat}</td>
      <td style="color:var(--gold2);font-weight:700;font-size:15px">${s.pts}</td>
      <td>${s.pj}</td>
      <td style="color:var(--win)">${s.pg}</td>
      <td style="color:var(--draw)">${s.pe}</td>
      <td style="color:var(--loss)">${s.pp}</td>
      <td style="color:#60a5fa">${s.gf}</td>
      <td style="color:#f87171">${s.gc}</td>
      <td style="color:${dgC};font-weight:700">${s.dg>0?'+':''}${s.dg}</td>
      <td style="color:var(--muted)">${pct}%</td>
    </tr>`;
  }).join('');

  const tot = calcStatsAll(1,35);
  const tDgC = tot.dg>0?'var(--win)':tot.dg<0?'var(--loss)':'var(--muted)';
  const tPct = tot.pj>0?Math.round(tot.pts/(tot.pj*3)*100):0;
  tableRows += `<tr style="background:rgba(192,21,42,0.12);">
    <td class="cat-cell" style="color:var(--gold2)">TOTAL</td>
    <td style="color:var(--gold2);font-size:15px;font-weight:700">${tot.pts}</td>
    <td>${tot.pj}</td>
    <td style="color:var(--win)">${tot.pg}</td>
    <td style="color:var(--draw)">${tot.pe}</td>
    <td style="color:var(--loss)">${tot.pp}</td>
    <td style="color:#60a5fa">${tot.gf}</td>
    <td style="color:#f87171">${tot.gc}</td>
    <td style="color:${tDgC};font-weight:700">${tot.dg>0?'+':''}${tot.dg}</td>
    <td style="color:var(--muted)">${tPct}%</td>
  </tr>`;

  panel.innerHTML = `
    ${ST('RESUMEN GENERAL · TODAS LAS CATEGORÍAS')}
    <div class="periodo-tabs" id="ptabs-GEN">${ptHTML}</div>
    <div id="gen-stats-area"></div>

    <div class="gen-table-wrap">
      <table class="gen-table">
        <thead><tr>
          <th>CAT.</th><th>PTS</th><th>PJ</th><th>PG</th><th>PE</th>
          <th>PP</th><th>GF</th><th>GC</th><th>DG</th><th>%</th>
        </tr></thead>
        <tbody>${tableRows}</tbody>
      </table>
    </div>

    ${ST('PUNTOS POR CATEGORÍA · CADA BLOQUE')}
    <div class="chart-card" style="margin-bottom:20px">
      <h3>Puntos — Todas las Categorías por Bloque</h3>
      <canvas id="cgen-pts" height="220"></canvas>
    </div>
    <div class="charts-row">
      <div class="chart-card"><h3>Goles a Favor — Comparativo</h3><canvas id="cgen-gf" height="200"></canvas></div>
      <div class="chart-card"><h3>Goles en Contra — Comparativo</h3><canvas id="cgen-gc" height="200"></canvas></div>
    </div>

    ${ST('TORTAS POR CATEGORÍA (TEMPORADA COMPLETA)')}
    <div class="pies-grid" id="gen-pies-cat"></div>

    ${ST('TORTAS GENERALES POR BLOQUE (TODAS LAS CATEGORÍAS)')}
    <div class="pies-grid" id="gen-pies-blk"></div>
  `;

  document.getElementById('ptabs-GEN').addEventListener('click', e => {
    if (!e.target.classList.contains('ptab')) return;
    document.getElementById('ptabs-GEN').querySelectorAll('.ptab').forEach(t=>t.classList.remove('active'));
    e.target.classList.add('active');
    renderGenStats();
  });

  renderGenStats();
  renderGenCharts(blocks);
  renderGenPiesCat();
  renderGenPiesBlocks(blocks);
}

function renderGenStats() {
  const idx = parseInt(document.getElementById('ptabs-GEN').querySelector('.ptab.active').dataset.idx);
  const p   = getPeriodos()[idx];
  document.getElementById('gen-stats-area').innerHTML = statsHTML(calcStatsAll(p.from,p.to));
}

function renderGenCharts(blocks) {
  const labels = blocks.map(b=>b.label);
  const def    = chartDef();
  const mkDs   = (cat,field) => ({
    label:cat,
    data: blocks.map(b=>calcStats(cat,b.from,b.to)[field]),
    backgroundColor: CAT_COLORS[cat]+'bb',
    borderColor: CAT_COLORS[cat],
    borderWidth:1, borderRadius:4, borderSkipped:false
  });

  ['cgen-pts','cgen-gf','cgen-gc'].forEach(id=>killChart(id));

  new Chart(document.getElementById('cgen-pts').getContext('2d'),{type:'bar',
    data:{labels,datasets:CATEGORIES.map(c=>mkDs(c,'pts'))},
    options:{...def,plugins:{...def.plugins,legend:{labels:{color:'#5a7099',font:{family:'Barlow Condensed'}}}}}});

  new Chart(document.getElementById('cgen-gf').getContext('2d'),{type:'bar',
    data:{labels,datasets:CATEGORIES.map(c=>mkDs(c,'gf'))},
    options:{...def,plugins:{...def.plugins,legend:{labels:{color:'#5a7099'}}}}});

  new Chart(document.getElementById('cgen-gc').getContext('2d'),{type:'bar',
    data:{labels,datasets:CATEGORIES.map(c=>({...mkDs(c,'gc'),backgroundColor:CAT_COLORS[c]+'66'}))},
    options:{...def,plugins:{...def.plugins,legend:{labels:{color:'#5a7099'}}}}});
}

function renderGenPiesCat() {
  const grid = document.getElementById('gen-pies-cat');
  grid.innerHTML='';
  CATEGORIES.forEach(cat => {
    const s  = calcStats(cat,1,35);
    const id = `gpc-${cat}`;
    grid.insertAdjacentHTML('beforeend', pieMiniHTML(id, s,
      `<span class="dot" style="background:${CAT_COLORS[cat]}"></span>${cat}`));
    drawPie(id, s);
  });
}
function renderGenPiesBlocks(blocks) {
  const grid = document.getElementById('gen-pies-blk');
  grid.innerHTML='';
  blocks.forEach(b => {
    const s  = calcStatsAll(b.from,b.to);
    const id = `gpb-${b.from}`;
    grid.insertAdjacentHTML('beforeend', pieMiniHTML(id, s, b.label+' — TODAS'));
    drawPie(id, s);
  });
}


// ============================================================
//  PERSISTENCE — localStorage
// ============================================================
const STORAGE_KEY = 'tigre2026_data_v1';

function saveData() {
  try {
    const payload = { results: {}, links: {} };
    CATEGORIES.forEach(cat => {
      payload.results[cat] = {};
      payload.links[cat]   = {};
      RIVALS.forEach(r => {
        payload.results[cat][r.f] = results[cat][r.f];
        payload.links[cat][r.f]   = links[cat][r.f];
      });
    });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch(e) { console.warn('No se pudo guardar:', e); }
}

function loadData() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const payload = JSON.parse(raw);
    CATEGORIES.forEach(cat => {
      if (!payload.results?.[cat]) return;
      RIVALS.forEach(r => {
        const res = payload.results[cat][r.f];
        if (res) results[cat][r.f] = res;
        const lnk = payload.links?.[cat]?.[r.f];
        if (lnk) {
          LINK_TYPES.forEach(lt => {
            if (lnk[lt.key] !== undefined) links[cat][r.f][lt.key] = lnk[lt.key];
          });
        }
      });
    });
  } catch(e) { console.warn('No se pudo cargar:', e); }
}

function clearData() {
  if (!confirm('\u26a0\ufe0f \u00bfSeguro que quer\u00e9s borrar TODOS los resultados y links guardados?')) return;
  localStorage.removeItem(STORAGE_KEY);
  location.reload();
}

function showSaved() {
  let el = document.getElementById('save-toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'save-toast';
    el.style.cssText = 'position:fixed;bottom:72px;right:22px;background:linear-gradient(135deg,#1a3a8f,#0d1528);' +
      'border:1px solid #22c55e;border-radius:8px;padding:8px 14px;font-family:Barlow Condensed,sans-serif;' +
      'font-size:13px;letter-spacing:1px;color:#22c55e;z-index:999;' +
      'box-shadow:0 4px 16px rgba(0,0,0,0.5);transition:opacity .4s;pointer-events:none;';
    document.body.appendChild(el);
  }
  el.textContent = '\u2713 GUARDADO';
  el.style.opacity = '1';
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.style.opacity = '0'; }, 1800);
}

// ============================================================
//  INIT
// ============================================================
loadData();   // restore saved data before building UI
buildTabs();
buildAllPanels();

</script></body></html>
