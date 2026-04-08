"""
PGI Dashboard Refresher — thefor app edition
=============================================
Reads your thefor habit export JSON + optional PGI Excel history,
computes per-habit streaks, and regenerates the dashboard.

Workflow:
  1. Export from thefor  →  habits-DD-M-YYYY.json
  2. Drop in same folder as this script
  3. Run:   python refresh_dashboard.py
  4. Open:  PGI_Dashboard.html

Rename these in thefor to preserve streaks:
  3 Hours of study       →  Trading Study
  30 minutes of reading  →  Deep Learning
  Journal                →  Trading Journal
  Visualization          →  Clarity Practice
  No shit                →  Shit
  Morning Routine        →  Morning Routine  (already correct)

Archive: Wake up early, Sunday Spirituality Study, Guitar Practice
"""

import json, os, sys
from pathlib import Path
from datetime import datetime, date, timedelta
from collections import defaultdict
from contextlib import contextmanager

# ══════════════════════════════════════════════════════════════════════════════
#  HABIT CONFIG  —  exact titles as they appear in thefor, case-sensitive
# ══════════════════════════════════════════════════════════════════════════════
#  (title, type, points, color)
#  type "positive" = checked when DONE
#  type "negative" = checked when you SLIPPED (not used currently)
#  "Shit" is checked when CLEAN — so it's type "positive"
HABITS = [
    ("Trading Study",    "growth",   +4, "#0f6e56"),
    ("Trading Journal",  "growth",   +2, "#085041"),
    ("Morning Routine",  "positive", +2, "#185fa5"),
    ("Deep Learning",    "positive", +2, "#534ab7"),
    ("Clarity Practice", "positive", +1, "#ba7517"),
    ("Shit",             "positive", +2, "#1d9e75"),   # checked = clean day
]

HABIT_CONFIG = {h[0]: {"type": h[1], "points": h[2], "color": h[3]} for h in HABITS}
HABIT_NAMES  = [h[0] for h in HABITS]
MAX_PTS      = sum(h[2] for h in HABITS if h[2] > 0)

SCRIPT_DIR  = Path(__file__).parent
EXCEL_FILE  = SCRIPT_DIR / "PGI_v3.xlsx"
OUTPUT_HTML   = SCRIPT_DIR / "PGI_Dashboard.html"
OUTPUT_DETAIL = SCRIPT_DIR / "habit_detail.html"
DATA_DIR      = SCRIPT_DIR / "data"
LATEST_JSON   = DATA_DIR / "latest.json"
LOCK_FILE     = SCRIPT_DIR / ".refresh_dashboard.lock"

DETAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Habit Detail</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
:root{--bg:#fff;--bg2:#f8f8f6;--bg3:#f2f1ed;--text:#1a1a1a;--text2:#6b6a65;--text3:#9b9a94;
  --bdr:rgba(0,0,0,0.1);--teal:#0f6e56;--teal-l:#e1f5ee;--blue:#185fa5;--blue-l:#e6f1fb;
  --red:#a32d2d;--red-l:#fcebeb;--amber:#ba7517;--amber-l:#faeeda;--r:12px;--rs:8px}
@media(prefers-color-scheme:dark){:root{--bg:#1a1a1e;--bg2:#222226;--bg3:#2a2a2e;
  --text:#e8e7e2;--text2:#9b9a94;--text3:#6b6a65;--bdr:rgba(255,255,255,0.1);
  --teal-l:#04342c;--blue-l:#042c53;--red-l:#501313;--amber-l:#412402}}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
     background:var(--bg3);color:var(--text);font-size:14px}
.app{max-width:980px;margin:0 auto;padding:20px 16px 48px}

/* Nav */
.nav{display:flex;align-items:center;gap:10px;margin-bottom:20px;flex-wrap:wrap}
.back{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--text2);
      cursor:pointer;padding:6px 12px;border-radius:var(--rs);border:.5px solid var(--bdr);
      background:var(--bg);transition:all .15s}
.back:hover{background:var(--bg2)}
.habit-pills{display:flex;gap:6px;flex-wrap:wrap;margin-left:4px}
.hpill{padding:5px 12px;border-radius:20px;font-size:12px;font-weight:500;cursor:pointer;
       border:.5px solid transparent;transition:all .15s;color:#fff;opacity:.55}
.hpill.active{opacity:1;box-shadow:0 1px 4px rgba(0,0,0,.15)}
.hpill:hover{opacity:.85}

/* Header */
.hdr{display:flex;align-items:flex-start;justify-content:space-between;
     margin-bottom:20px;flex-wrap:wrap;gap:12px}
.hdr-left h2{font-size:22px;font-weight:600;margin-bottom:4px}
.hdr-left .sub{font-size:13px;color:var(--text2)}
.pts-big{display:inline-flex;align-items:center;justify-content:center;
         padding:6px 16px;border-radius:var(--rs);font-size:15px;font-weight:700;color:#fff}

/* Summary cards */
.g5{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-bottom:14px}
.mc{background:var(--bg);border-radius:var(--rs);padding:12px 14px;border:.5px solid var(--bdr)}
.ml{font-size:10px;color:var(--text2);font-weight:500;text-transform:uppercase;
    letter-spacing:.05em;margin-bottom:5px}
.mv{font-size:22px;font-weight:700;line-height:1}
.ms{font-size:11px;color:var(--text3);margin-top:3px}

/* Cards */
.card{background:var(--bg);border-radius:var(--r);border:.5px solid var(--bdr);
      padding:18px 20px;margin-bottom:14px}
.ch{display:flex;align-items:center;justify-content:space-between;
    margin-bottom:14px;flex-wrap:wrap;gap:8px}
.ct{font-size:14px;font-weight:600}
.cs{font-size:12px;color:var(--text2);margin-top:2px}
.tabs{display:flex;gap:3px;background:var(--bg2);padding:3px;
      border-radius:var(--rs);border:.5px solid var(--bdr)}
.tab{padding:5px 12px;font-size:12px;font-weight:500;border-radius:6px;cursor:pointer;
     border:none;background:transparent;color:var(--text2);transition:all .15s}
.tab.active{background:var(--bg);color:var(--text);box-shadow:0 1px 3px rgba(0,0,0,.08)}

/* Calendar heatmap */
.cal-wrap{overflow-x:auto;padding-bottom:4px}
.cal{display:flex;gap:3px}
.cal-col{display:flex;flex-direction:column;gap:3px}
.cal-cell{width:13px;height:13px;border-radius:2px;flex-shrink:0}
.cal-month-labels{display:flex;gap:3px;margin-bottom:4px;font-size:10px;color:var(--text3)}
.cal-day-labels{display:flex;flex-direction:column;gap:3px;margin-right:6px;
                font-size:9px;color:var(--text3);padding-top:1px}

/* Streak list */
.streak-list{display:flex;flex-direction:column;gap:6px;max-height:320px;overflow-y:auto}
.streak-row{display:flex;align-items:center;gap:8px;padding:7px 10px;
            background:var(--bg2);border-radius:var(--rs)}
.streak-rank{font-size:11px;color:var(--text3);width:20px;text-align:center;flex-shrink:0}
.streak-bar-wrap{flex:1;height:6px;background:var(--bg3);border-radius:3px;overflow:hidden}
.streak-bar{height:100%;border-radius:3px}
.streak-val{font-size:12px;font-weight:600;min-width:40px;text-align:right}

/* Monthly rate table */
.dt{width:100%;font-size:12px;border-collapse:collapse}
.dt th{padding:6px 8px;text-align:left;color:var(--text2);
       border-bottom:.5px solid var(--bdr);font-weight:500}
.dt td{padding:6px 8px;border-bottom:.5px solid var(--bdr)}
.dt tr:last-child td{border-bottom:none}
.dt tr:hover td{background:var(--bg2)}
.rate-bar{display:inline-flex;height:6px;border-radius:3px;vertical-align:middle;margin-right:6px}

/* Day streak dots */
.dot-row{display:flex;flex-wrap:wrap;gap:3px;margin-top:4px}
.dot{width:8px;height:8px;border-radius:50%}

@media(max-width:640px){
  .g5{grid-template-columns:repeat(3,1fr)}
  /* Stack streak + dow chart vertically on mobile */
  .two-detail{grid-template-columns:1fr !important}
  /* Make month table font smaller */
  .dt{font-size:11px}
  .dt th,.dt td{padding:5px 5px}
  /* Shrink nav pills */
  .hpill{padding:4px 9px;font-size:11px}
}
@media(max-width:400px){
  .g5{grid-template-columns:repeat(2,1fr)}
}
</style>
</head>
<body>
<div class="app">

<!-- Nav bar with habit pills -->
<div class="nav">
  <div class="back" onclick="goBack()">← Dashboard</div>
  <div class="habit-pills" id="habit-pills"></div>
</div>

<!-- Habit header -->
<div class="hdr">
  <div class="hdr-left">
    <h2 id="h-name">—</h2>
    <div class="sub" id="h-sub">—</div>
  </div>
  <div class="pts-big" id="h-pts-badge">—</div>
</div>

<!-- Summary metrics -->
<div class="g5" id="summary-cards"></div>

<!-- Rate over time -->
<div class="card">
  <div class="ch">
    <div><div class="ct">Completion rate over time</div>
      <div class="cs" id="rate-sub"></div></div>
    <div class="tabs">
      <button class="tab active" onclick="setRateView('monthly',this)">Monthly</button>
      <button class="tab" onclick="setRateView('weekly',this)">Weekly</button>
    </div>
  </div>
  <div style="position:relative;height:200px"><canvas id="rate-chart"></canvas></div>
</div>

<!-- Streak history + calendar heatmap -->
<div class="two-detail" style="display:grid;grid-template-columns:1fr 1.4fr;gap:14px;margin-bottom:14px">

  <!-- Top streaks -->
  <div class="card" style="margin-bottom:0">
    <div class="ch"><div class="ct">Top streaks</div>
      <div class="cs">longest consecutive runs</div></div>
    <div class="streak-list" id="streak-list"></div>
  </div>

  <!-- Day of week breakdown -->
  <div class="card" style="margin-bottom:0">
    <div class="ch"><div class="ct">Day of week pattern</div>
      <div class="cs">which days you're most consistent</div></div>
    <div style="position:relative;height:200px"><canvas id="dow-chart"></canvas></div>
  </div>

</div>

<!-- Full calendar heatmap -->
<div class="card">
  <div class="ch"><div class="ct">Activity calendar</div>
    <div class="cs" id="cal-sub">all time · green = done, red = missed</div></div>
  <div class="cal-wrap">
    <div id="cal-container"></div>
  </div>
  <div style="display:flex;gap:12px;margin-top:10px;font-size:11px;color:var(--text3)">
    <span style="display:flex;align-items:center;gap:4px">
      <span id="done-swatch" style="width:10px;height:10px;border-radius:2px;display:inline-block"></span>Done</span>
    <span style="display:flex;align-items:center;gap:4px">
      <span style="width:10px;height:10px;border-radius:2px;background:rgba(163,45,45,0.2);display:inline-block"></span>Missed</span>
    <span style="display:flex;align-items:center;gap:4px">
      <span style="width:10px;height:10px;border-radius:2px;background:var(--bg2);display:inline-block"></span>No data</span>
  </div>
</div>

<!-- Monthly breakdown table -->
<div class="card">
  <div class="ch"><div class="ct">Monthly breakdown</div></div>
  <div style="overflow-x:auto"><table class="dt" id="month-table"></table></div>
</div>

</div>

<script>
// Data injected by refresh_dashboard.py
const INJECTED_DATA = %%DETAIL_DATA%%;

// ── State ────────────────────────────────────────────────────────────────────
let D = null;
let currentHabit = null;
let rateChart = null, dowChart = null;

function loadData() {
  // Data is injected at build time by refresh_dashboard.py
  if (typeof INJECTED_DATA !== 'undefined') {
    D = INJECTED_DATA;
    init();
  } else {
    document.querySelector('.app').innerHTML =
      '<div style="padding:40px;text-align:center;color:var(--text2)">' +
      '<div style="font-size:16px;font-weight:500;margin-bottom:8px">No data found</div>' +
      '<div style="font-size:13px">Run refresh_dashboard.py to regenerate this file.</div>' +
      '</div>';
  }
}

function init() {
  // Build habit pills
  const pillsEl = document.getElementById('habit-pills');
  D.streaks.forEach(s => {
    const pill = document.createElement('div');
    pill.className = 'hpill';
    pill.textContent = s.name;
    pill.style.background = s.color;
    pill.onclick = () => showHabit(s.name);
    pillsEl.appendChild(pill);
  });

  // Show habit from URL param or first habit
  const params = new URLSearchParams(window.location.search);
  const h = params.get('habit') || D.streaks[0].name;
  showHabit(h);
}

function goBack() {
  if (history.length > 1) { history.back(); }
  else { window.location.href = "PGI_Dashboard.html"; }
}

function showHabit(name) {
  currentHabit = name;

  // Update URL
  const url = new URL(window.location);
  url.searchParams.set('habit', name);
  window.history.replaceState({}, '', url);

  // Update pills
  document.querySelectorAll('.hpill').forEach(p => {
    p.classList.toggle('active', p.textContent === name);
  });

  const s = D.streaks.find(x => x.name === name);
  const color = s.color;

  // Header
  document.getElementById('h-name').textContent = name;
  document.getElementById('done-swatch').style.background = color;

  const typeMap = {
    'Trading Study':   'Growth habit · +4 pts · your highest value habit',
    'Trading Journal': 'Growth habit · +2 pts · separates traders from gamblers',
    'Morning Routine': 'Positive habit · +2 pts · sets up every other habit',
    'Deep Learning':   'Positive habit · +2 pts · compound knowledge',
    'Clarity Practice':'Positive habit · +1 pt · mental reset',
    'Shit':            'Clean habit · +2 pts · checked on clean days',
  };
  document.getElementById('h-sub').textContent = typeMap[name] || '';

  const badge = document.getElementById('h-pts-badge');
  badge.textContent = `+${s.points} pts`;
  badge.style.background = color;

  // Build daily presence for this habit
  const dailyDone = D.daily.map(d => ({
    date: d.date,
    done: d.habits[name] || 0,
    source: d.source,
  }));

  // Summary cards
  buildSummaryCards(s, dailyDone, color);

  // Rate chart
  buildRateChart('monthly', color);

  // Streak analysis
  buildStreakList(dailyDone, color);

  // Day of week
  buildDowChart(dailyDone, color);

  // Calendar
  buildCalendar(dailyDone, color);

  // Month table
  buildMonthTable(name, color);
}

// ── Summary cards ─────────────────────────────────────────────────────────────
function buildSummaryCards(s, dailyDone, color) {
  const theforDays = dailyDone.filter(d => d.source === 'thefor');
  const theforDone = theforDays.filter(d => d.done).length;
  const theforRate = theforDays.length ? Math.round(theforDone/theforDays.length*100) : 0;

  // Current streak run length
  const curStreakColor = s.cur >= 14 ? '#0f6e56' : s.cur >= 7 ? '#ba7517' : s.cur >= 3 ? '#185fa5' : 'var(--text2)';

  // Longest miss streak
  let maxMiss = 0, curMiss = 0;
  dailyDone.forEach(d => {
    if (d.source !== 'thefor') return;
    if (!d.done) { curMiss++; maxMiss = Math.max(maxMiss, curMiss); }
    else curMiss = 0;
  });

  // Last 30 days rate
  const l30 = dailyDone.filter(d=>d.source==='thefor').slice(-30);
  const l30rate = l30.length ? Math.round(l30.filter(d=>d.done).length/l30.length*100) : 0;

  document.getElementById('summary-cards').innerHTML = `
    <div class="mc"><div class="ml">Current streak</div>
      <div class="mv" style="color:${curStreakColor}">${s.cur}</div>
      <div class="ms">days in a row</div></div>
    <div class="mc"><div class="ml">Best ever</div>
      <div class="mv" style="color:${color}">${s.best}</div>
      <div class="ms">consecutive days</div></div>
    <div class="mc"><div class="ml">All-time rate</div>
      <div class="mv" style="color:${s.rate>=60?'#0f6e56':s.rate>=40?'#ba7517':'#a32d2d'}">${s.rate}%</div>
      <div class="ms">${s.done} of ${s.total} days</div></div>
    <div class="mc"><div class="ml">Last 30 days</div>
      <div class="mv" style="color:${l30rate>=60?'#0f6e56':l30rate>=40?'#ba7517':'#a32d2d'}">${l30rate}%</div>
      <div class="ms">recent trend</div></div>
    <div class="mc"><div class="ml">Longest miss</div>
      <div class="mv" style="color:${maxMiss>=14?'#a32d2d':maxMiss>=7?'#ba7517':'var(--text2)'}">${maxMiss}</div>
      <div class="ms">consecutive misses</div></div>`;
}

// ── Rate chart ────────────────────────────────────────────────────────────────
function buildRateChart(view, color) {
  color = color || D.streaks.find(s=>s.name===currentHabit)?.color;
  document.getElementById('rate-sub').textContent =
    view === 'monthly' ? 'completion % per month' : 'completion % per week';

  let labels, rates;
  if (view === 'monthly') {
    labels = D.monthly.map(m => m.label.slice(2).replace('-','/'));
    rates  = D.monthly.map(m => (m.rates||{})[currentHabit] || 0);
  } else {
    labels = D.weekly.map(w => w.label.slice(5));
    rates  = D.weekly.map(w => (w.rates||{})[currentHabit] || 0);
  }

  if (rateChart) rateChart.destroy();
  rateChart = new Chart(document.getElementById('rate-chart'), {
    type: 'bar',
    data: { labels, datasets: [{
      data: rates,
      backgroundColor: rates.map(r =>
        r >= 80 ? color+'cc' : r >= 50 ? color+'88' : r >= 20 ? color+'44' : 'rgba(163,45,45,0.2)'
      ),
      borderRadius: 3,
    }]},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false },
        tooltip: { callbacks: { label: i => ` ${i.raw}%` }}},
      scales: {
        x: { ticks: { color: '#888', font: { size: 10 }, autoSkip: true,
                       maxTicksLimit: view==='weekly'?20:17, maxRotation: 45 },
             grid: { display: false } },
        y: { min: 0, max: 100, ticks: { color: '#888', font: { size: 10 },
               callback: v => v+'%' }, grid: { color: 'rgba(128,128,128,0.07)' } }
      }
    }
  });
}

function setRateView(v, btn) {
  btn.closest('.card').querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  buildRateChart(v);
}

// ── Streak list ───────────────────────────────────────────────────────────────
function buildStreakList(dailyDone, color) {
  // Find all streaks
  const thefor = dailyDone.filter(d => d.source === 'thefor');
  const streaks = [];
  let cur = 0, startDate = '';

  thefor.forEach((d, i) => {
    if (d.done) {
      if (cur === 0) startDate = d.date;
      cur++;
    } else {
      if (cur > 0) {
        streaks.push({ len: cur, start: startDate, end: thefor[i-1].date });
        cur = 0;
      }
    }
  });
  if (cur > 0) streaks.push({ len: cur, start: startDate, end: thefor[thefor.length-1].date });

  streaks.sort((a,b) => b.len - a.len);
  const top = streaks.slice(0, 6);
  const maxLen = top[0]?.len || 1;

  document.getElementById('streak-list').innerHTML = top.length
    ? top.map((s, i) => `
        <div class="streak-row">
          <div class="streak-rank">#${i+1}</div>
          <div style="flex:1">
            <div class="streak-bar-wrap">
              <div class="streak-bar" style="width:${Math.round(s.len/maxLen*100)}%;background:${color}"></div>
            </div>
            <div style="font-size:10px;color:var(--text3);margin-top:3px">${s.start} → ${s.end}</div>
          </div>
          <div class="streak-val" style="color:${color}">${s.len}d</div>
        </div>`).join('')
    : '<div style="color:var(--text3);font-size:13px;padding:12px 0">No streaks recorded yet</div>';
}

// ── Day of week chart ─────────────────────────────────────────────────────────
function buildDowChart(dailyDone, color) {
  const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  const counts = Array(7).fill(0);
  const totals = Array(7).fill(0);

  dailyDone.filter(d=>d.source==='thefor').forEach(d => {
    const dow = (new Date(d.date).getDay() + 6) % 7; // Mon=0
    totals[dow]++;
    if (d.done) counts[dow]++;
  });

  const rates = days.map((_,i) => totals[i] ? Math.round(counts[i]/totals[i]*100) : 0);

  if (dowChart) dowChart.destroy();
  dowChart = new Chart(document.getElementById('dow-chart'), {
    type: 'bar',
    data: { labels: days, datasets: [{
      data: rates,
      backgroundColor: rates.map(r =>
        r >= 70 ? color+'dd' : r >= 40 ? color+'88' : 'rgba(163,45,45,0.25)'
      ),
      borderRadius: 4,
    }]},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false },
        tooltip: { callbacks: {
          label: (i) => ` ${i.raw}% (${counts[i.dataIndex]}/${totals[i.dataIndex]} days)`
        }}},
      scales: {
        x: { ticks: { color: '#888', font: { size: 11 } }, grid: { display: false } },
        y: { min: 0, max: 100, ticks: { color: '#888', font: { size: 10 },
               callback: v => v+'%' }, grid: { color: 'rgba(128,128,128,0.07)' } }
      }
    }
  });
}

// ── Calendar heatmap ──────────────────────────────────────────────────────────
function buildCalendar(dailyDone, color) {
  const dateMap = {};
  dailyDone.forEach(d => { dateMap[d.date] = { done: d.done, source: d.source }; });

  const dates = dailyDone.map(d => new Date(d.date));
  const minDate = new Date(Math.min(...dates));
  const maxDate = new Date(Math.max(...dates));

  // Start from Monday of minDate's week
  const start = new Date(minDate);
  start.setDate(start.getDate() - ((start.getDay() + 6) % 7));
  const end = new Date(maxDate);
  end.setDate(end.getDate() + (6 - (end.getDay() + 6) % 7));

  // Build columns (weeks)
  const cols = [];
  let cur = new Date(start);
  while (cur <= end) {
    const col = [];
    for (let d = 0; d < 7; d++) {
      col.push(new Date(cur));
      cur.setDate(cur.getDate() + 1);
    }
    cols.push(col);
  }

  // Month labels
  let lastMonth = -1;
  const monthLabels = cols.map(col => {
    const m = col[0].getMonth();
    if (m !== lastMonth) { lastMonth = m; return col[0].toLocaleString('default',{month:'short'}); }
    return '';
  });

  const container = document.getElementById('cal-container');
  container.innerHTML = '';

  // Month label row
  const mlRow = document.createElement('div');
  mlRow.style.cssText = 'display:flex;gap:3px;margin-bottom:4px;padding-left:24px';
  monthLabels.forEach(lbl => {
    const el = document.createElement('div');
    el.style.cssText = `width:13px;font-size:9px;color:var(--text3);white-space:nowrap;
                        overflow:visible;min-width:13px`;
    el.textContent = lbl;
    mlRow.appendChild(el);
  });
  container.appendChild(mlRow);

  // Grid row with day labels
  const row = document.createElement('div');
  row.style.cssText = 'display:flex;gap:3px';

  // Day labels
  const dayLbls = document.createElement('div');
  dayLbls.style.cssText = 'display:flex;flex-direction:column;gap:3px;margin-right:4px;padding-top:0';
  ['M','','W','','F','','S'].forEach(l => {
    const el = document.createElement('div');
    el.style.cssText = 'width:12px;height:13px;font-size:9px;color:var(--text3);line-height:13px';
    el.textContent = l;
    dayLbls.appendChild(el);
  });
  row.appendChild(dayLbls);

  // Cells
  cols.forEach(col => {
    const colEl = document.createElement('div');
    colEl.style.cssText = 'display:flex;flex-direction:column;gap:3px';
    col.forEach(date => {
      const ds = date.toISOString().slice(0,10);
      const info = dateMap[ds];
      const cell = document.createElement('div');
      cell.className = 'cal-cell';
      cell.title = ds + (info ? (info.done ? ' ✓' : ' ✗') : '');
      if (!info) {
        cell.style.background = 'var(--bg2)';
      } else if (info.source === 'excel') {
        cell.style.background = info.done ? color+'66' : 'var(--bg2)';
      } else if (info.done) {
        cell.style.background = color;
      } else {
        cell.style.background = 'rgba(163,45,45,0.2)';
      }
      colEl.appendChild(cell);
    });
    row.appendChild(colEl);
  });
  container.appendChild(row);

  document.getElementById('cal-sub').textContent =
    `${dailyDone.length} days · green = done · red = missed`;

  // Auto-scroll to most recent data (right end)
  const wrap = container.closest('.cal-wrap');
  if (wrap) wrap.scrollLeft = wrap.scrollWidth;
}

// ── Month table ───────────────────────────────────────────────────────────────
function buildMonthTable(name, color) {
  const rows = [...D.monthly].reverse();
  const isMobile = window.innerWidth < 640;
  let h = `<thead><tr>
    <th>Month</th><th>Rate</th><th>${isMobile?'Done':'Days done'}</th>
    <th>${isMobile?'Miss':'Days missed'}</th><th>${isMobile?'Trend':'vs prev month'}</th>
  </tr></thead><tbody>`;

  let prevRate = null;
  const fwdRows = [...D.monthly];
  fwdRows.forEach((m, i) => {
    const rate = (m.rates||{})[name] || 0;
    fwdRows[i]._rate = rate;
  });

  rows.forEach((m) => {
    const rate  = (m.rates||{})[name] || 0;
    const done  = Math.round(rate/100 * m.days);
    const missed = m.days - done;
    const rateC = rate>=60?'#0f6e56':rate>=40?'#ba7517':'#a32d2d';
    const lbl   = m.label.slice(2).replace('-','/');

    // Find previous month rate
    const idx = fwdRows.findIndex(x => x.label === m.label);
    const prev = idx > 0 ? fwdRows[idx-1]._rate : null;
    let trend = '—';
    let trendC = 'var(--text3)';
    if (prev !== null) {
      const diff = rate - prev;
      trend = (diff >= 0 ? '+' : '') + diff + '%';
      trendC = diff > 0 ? '#0f6e56' : diff < 0 ? '#a32d2d' : 'var(--text3)';
    }

    h += `<tr>
      <td style="font-weight:500">${lbl}</td>
      <td>
        <span style="display:inline-flex;align-items:center;gap:6px">
          <span style="width:${rate}px;max-width:100px;height:6px;border-radius:3px;
                background:${color};display:inline-block;opacity:.8"></span>
          <span style="color:${rateC};font-weight:600">${rate}%</span>
        </span>
      </td>
      <td style="color:#0f6e56">${done}</td>
      <td style="color:${missed>0?'#a32d2d':'var(--text3)'}">${missed}</td>
      <td style="color:${trendC};font-weight:500">${trend}</td>
    </tr>`;
  });
  h += '</tbody>';
  document.getElementById('month-table').innerHTML = h;
}

// ── Boot ──────────────────────────────────────────────────────────────────────
loadData();
</script>
</body>
</html>
"""
USE_EXCEL   = True   # ← set to False to use thefor data only (clean sample)

# ── Todoist config ────────────────────────────────────────────────────────────
TODOIST_TOKEN      = os.getenv("TODOIST_TOKEN", "")
TODOIST_PTS_ONTIME  = 2   # completed on or before due date
TODOIST_PTS_OVERDUE = 1   # completed after due date
TODOIST_PTS_NODUE   = 1   # completed with no due date


HABIT_ALIASES = {
    "3 Hours of study": "Trading Study",
    "30 minutes of reading": "Deep Learning",
    "Journal": "Trading Journal",
    "Visualization": "Clarity Practice",
    "No shit": "Shit",
}

# ── Find newest thefor export ─────────────────────────────────────────────────
def find_json():
    files = sorted(SCRIPT_DIR.glob("habits-*.json"), key=lambda p: p.stat().st_mtime)
    if not files:
        return None
    if len(files) > 1:
        print(f"  Multiple exports — using newest: {files[-1].name}")
    return files[-1]

@contextmanager
def run_lock():
    try:
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        print(f"ERROR: Lock file exists: {LOCK_FILE.name}. Another refresh may be running.")
        sys.exit(1)
    try:
        os.write(fd, str(os.getpid()).encode("utf-8"))
        yield
    finally:
        os.close(fd)
        try:
            LOCK_FILE.unlink()
        except FileNotFoundError:
            pass

def load_latest_payload():
    if not LATEST_JSON.exists():
        return None
    try:
        with open(LATEST_JSON, encoding="utf-8") as f:
            payload = json.load(f)
        if not isinstance(payload, dict):
            return None
        if not payload.get("daily"):
            return None
        return payload
    except Exception:
        return None

def write_json_atomic(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    tmp.replace(path)

# ── Parse thefor JSON → {date_str: {habit: 1/0}} ────────────────────────────
def parse_thefor(json_path, run_report=None):
    run_report = run_report if run_report is not None else {}
    run_report.setdefault("unmatched_habits", [])
    run_report.setdefault("skipped_checked_days", 0)

    with open(json_path) as f:
        raw = json.load(f)
    if isinstance(raw, dict):
        raw = raw.get("habits", [])
    if not isinstance(raw, list):
        run_report["raw_format_error"] = True
        return {}

    day_map = defaultdict(lambda: {h: 0 for h in HABIT_NAMES})

    for habit in raw:
        title = habit.get("title", "").strip()
        title = HABIT_ALIASES.get(title, title)
        if title not in HABIT_CONFIG:
            if title and title not in run_report["unmatched_habits"]:
                run_report["unmatched_habits"].append(title)
            continue

        archived = habit.get("archiveTime", "null")
        archive_date = None
        if archived and archived != "null":
            try:
                archive_date = datetime.fromisoformat(archived.replace("Z", "")).date()
            except Exception:
                pass

        for entry in habit.get("checkedDays", []):
            try:
                d = datetime.fromisoformat(entry["day"].replace("Z", "")).date()
            except Exception:
                run_report["skipped_checked_days"] += 1
                continue
            if archive_date and d > archive_date:
                continue
            day_map[d.isoformat()][title] = 1

    return day_map

# ── Load Excel history (rows before thefor coverage starts) ───────────────────
def load_excel(cutoff):
    if not EXCEL_FILE.exists():
        return []
    try:
        import pandas as pd, numpy as np
    except ImportError:
        print("  pandas not installed — skipping Excel history.")
        return []

    # Auto-detect header row — handles both original PGI_Index.xlsx and new PGI_v3.xlsx
    df = None
    for header_row in [0, 1, 2, 3]:
        try:
            test = pd.read_excel(EXCEL_FILE, sheet_name="Daily Tracker", header=header_row, nrows=1)
            cols = [str(c).strip().lower() for c in test.columns]
            if any("date" in c for c in cols):
                df = pd.read_excel(EXCEL_FILE, sheet_name="Daily Tracker", header=header_row)
                print(f"  Excel: using header row {header_row}")
                break
        except Exception:
            continue
    if df is None:
        print("  Could not find header row in Excel — skipping.")
        return []
    # Map actual column names from PGI_v3.xlsx
    CMAP_EXACT = {
        "Date":                 "Date",
        "PGI Index":            "PGI",
        "Growth Habits":        "Growth",
        "Mildly +VE":           "MildlyPos",
        "Mindly -VE":           "MildlyNeg",
        "Back Stabbing Habits": "BackStab",
        "Aggregate":            "Agg",
        "Momen. (W)":           "MomenW",
        "Momen. (M)":           "MomenM",
    }
    cmap = {}
    for c in df.columns:
        if c in CMAP_EXACT:
            cmap[c] = CMAP_EXACT[c]
        else:
            s = str(c).strip().lower()
            if "date" in s:                          cmap[c] = "Date"
            elif "pgi" in s:                         cmap[c] = "PGI"
            elif "growth" in s or "study" in s:      cmap[c] = "Growth"
            elif "read" in s:                        cmap[c] = "Read"
            elif "mildly" in s and "+" in s:         cmap[c] = "MildlyPos"
            elif "mindly" in s or ("mildly" in s and "-" in s): cmap[c] = "MildlyNeg"
            elif "back" in s or "stab" in s:         cmap[c] = "BackStab"
            elif "aggregate" in s and "atft" not in s: cmap[c] = "Agg"
            elif "momen" in s and "w" in s:          cmap[c] = "MomenW"
            elif "momen" in s and "m" in s:          cmap[c] = "MomenM"

    df = df.rename(columns=cmap)

    # Safety net — if Date column still missing, force-rename first column
    if "Date" not in df.columns:
        print(f"  WARNING: columns found: {list(df.columns)}")
        df = df.rename(columns={df.columns[0]: "Date"})

    df = df[df["Date"].astype(str).str.match(r"\d{4}-\d{2}-\d{2}")].copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[df["Date"].dt.date < cutoff].sort_values("Date")

    def g(row, col):
        v = row.get(col)
        if v is None:
            return None
        try:
            fv = float(v)
            if np.isnan(fv):
                return None
            return fv
        except Exception:
            return None

    rows = []
    for _, r in df.iterrows():
        pgi    = g(r, "PGI")
        growth = g(r, "Growth") or 0
        read_v = g(r, "Read") or 0
        hab    = {h: 0 for h in HABIT_NAMES}
        hab["Trading Study"]   = 1 if growth >= 2 else 0
        hab["Trading Journal"] = 1 if growth >= 1 else 0
        hab["Deep Learning"]   = 1 if read_v >= 1 else 0
        rows.append({
            "date":         r["Date"].strftime("%Y-%m-%d"),
            "source":       "excel",
            "pgi_override": float(pgi) if pgi is not None else None,
            "habits":       hab,
        })
    return rows


# ── Fetch Todoist completed tasks → {date_str: {on_time: N, overdue: N, no_due: N}} ──
def fetch_todoist():
    import urllib.request, urllib.error
    if not TODOIST_TOKEN:
        return {}

    print("  Fetching Todoist completed tasks...")
    task_map = defaultdict(lambda: {"on_time": 0, "overdue": 0, "no_due": 0, "total": 0})

    try:
        # Sync API to get completed items (supports full history)
        url = "https://api.todoist.com/sync/v9/items/completed/get_all"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {TODOIST_TOKEN}"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())

        items = data.get("items", [])
        print(f"    Found {len(items)} completed tasks")

        for item in items:
            # completed_at is like "2025-06-15T14:23:00.000000Z"
            completed_raw = item.get("completed_at") or item.get("date_completed", "")
            if not completed_raw:
                continue
            try:
                completed_date = datetime.fromisoformat(
                    completed_raw.replace("Z","").split("T")[0]
                ).date()
            except Exception:
                continue

            ds = str(completed_date)

            # Check if it had a due date and whether it was on time
            due = item.get("due")
            if not due:
                task_map[ds]["no_due"]  += 1
            else:
                due_str = due.get("date","")[:10] if isinstance(due, dict) else str(due)[:10]
                try:
                    due_date = date.fromisoformat(due_str)
                    if completed_date <= due_date:
                        task_map[ds]["on_time"]  += 1
                    else:
                        task_map[ds]["overdue"] += 1
                except Exception:
                    task_map[ds]["no_due"] += 1

            task_map[ds]["total"] += 1

        return dict(task_map)

    except urllib.error.URLError as e:
        print(f"    Todoist unavailable: {e} — skipping tasks")
        return {}
    except Exception as e:
        print(f"    Todoist error: {e} — skipping tasks")
        return {}

# ── Merge excel history + thefor rows ────────────────────────────────────────
def merge(excel_rows, day_map, task_map=None):
    task_map = task_map or {}
    by_date = {r["date"]: r for r in excel_rows}
    for ds in sorted(day_map.keys()):
        by_date[ds] = {
            "date":   ds,
            "source": "thefor",
            "habits": dict(day_map[ds]),
            "tasks":  task_map.get(ds, {"on_time":0,"overdue":0,"no_due":0,"total":0}),
        }
    # Add task data to excel rows too
    for r in by_date.values():
        if "tasks" not in r:
            r["tasks"] = task_map.get(r["date"], {"on_time":0,"overdue":0,"no_due":0,"total":0})
    return [by_date[d] for d in sorted(by_date)]

# ── Running PGI, momentum, per-habit rolling streaks ─────────────────────────
def calc_metrics(rows):
    pgi      = 0
    agg_hist = []
    streaks  = {h: 0 for h in HABIT_NAMES}
    out      = []

    for r in rows:
        hab = r.get("habits", {h: 0 for h in HABIT_NAMES})

        if r["source"] == "excel" and r.get("pgi_override") is not None:
            agg = r["pgi_override"] - pgi
            pgi = r["pgi_override"]
        else:
            # Penalty scoring: complete = +points, miss = -1
            agg = sum(HABIT_CONFIG[h]["points"] if hab.get(h, 0) else -1 for h in HABIT_NAMES)
            # Add task completion points
            tasks = r.get("tasks", {})
            agg += tasks.get("on_time", 0)  * TODOIST_PTS_ONTIME
            agg += tasks.get("overdue", 0)  * TODOIST_PTS_OVERDUE
            agg += tasks.get("no_due", 0)   * TODOIST_PTS_NODUE
            pgi += agg

        agg_hist.append(agg)
        streaks = {h: streaks[h] + 1 if hab.get(h, 0) else 0 for h in HABIT_NAMES}

        mw = round(sum(agg_hist[-7:])  / len(agg_hist[-7:]),  3)
        mm = round(sum(agg_hist[-30:]) / len(agg_hist[-30:]), 3)

        out.append({
            "date":    r["date"],
            "source":  r["source"],
            "pgi":     round(pgi, 1),
            "habits":  {h: hab.get(h, 0) for h in HABIT_NAMES},
            "tasks":   r.get("tasks", {"on_time":0,"overdue":0,"no_due":0,"total":0}),
            "agg":     round(agg, 1),
            "mw":      mw,
            "mm":      mm,
            "streaks": dict(streaks),
        })
    return out

# ── Per-habit streak summary for streak cards ─────────────────────────────────
def streak_summary(daily):
    if not daily:
        return []
    last_day = daily[-1]
    result   = []
    for h in HABIT_NAMES:
        cfg        = HABIT_CONFIG[h]
        done_days  = sum(1 for d in daily if d["habits"].get(h, 0))
        total_days = len(daily)
        rate       = round(done_days / total_days * 100) if total_days else 0
        cur        = last_day["streaks"].get(h, 0)
        best       = max(d["streaks"].get(h, 0) for d in daily)
        grid_90    = [d["habits"].get(h, 0) for d in daily[-90:]]
        result.append({
            "name":   h,
            "color":  cfg["color"],
            "points": cfg["points"],
            "cur":    cur,
            "best":   best,
            "rate":   rate,
            "done":   done_days,
            "total":  total_days,
            "grid":   grid_90,
        })
    return result

# ── Weekly / monthly aggregates ───────────────────────────────────────────────
def aggregates(daily):
    def w_key(ds):
        dt = datetime.strptime(ds, "%Y-%m-%d").date()
        return (dt - timedelta(days=dt.weekday())).isoformat()
    def m_key(ds): return ds[:7]

    def build(key_fn):
        g = defaultdict(list)
        for r in daily: g[key_fn(r["date"])].append(r)
        out = []
        for lbl in sorted(g):
            rows = g[lbl]; n = len(rows)
            out.append({
                "label": lbl,
                "pgi":   rows[-1]["pgi"],
                "net":   round(sum(r["agg"] for r in rows), 1),
                "mw":    rows[-1]["mw"],
                "pd":    sum(1 for r in rows if r["agg"] > 0),
                "nd":    sum(1 for r in rows if r["agg"] < 0),
                "days":  n,
                "rates": {h: round(sum(r["habits"].get(h,0) for r in rows)/n*100) for h in HABIT_NAMES},
            })
        return out

    return build(w_key), build(m_key)

# ══════════════════════════════════════════════════════════════════════════════
#  HTML TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PGI Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
:root{--bg:#fff;--bg2:#f8f8f6;--bg3:#f2f1ed;--text:#1a1a1a;--text2:#6b6a65;--text3:#9b9a94;
  --bdr:rgba(0,0,0,0.1);--teal:#0f6e56;--teal-l:#e1f5ee;--blue:#185fa5;
  --red:#a32d2d;--red-l:#fcebeb;--amber:#ba7517;--amber-l:#faeeda;--r:12px;--rs:8px}
@media(prefers-color-scheme:dark){:root{--bg:#1a1a1e;--bg2:#222226;--bg3:#2a2a2e;
  --text:#e8e7e2;--text2:#9b9a94;--text3:#6b6a65;--bdr:rgba(255,255,255,0.1);
  --teal-l:#04342c;--red-l:#501313;--amber-l:#412402}}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg3);color:var(--text);font-size:14px}
.app{max-width:980px;margin:0 auto;padding:20px 16px 48px}
.hrow{display:flex;align-items:baseline;gap:10px;margin-bottom:18px;flex-wrap:wrap}
.hrow h1{font-size:20px;font-weight:600}.meta{font-size:12px;color:var(--text3)}
.g4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:14px}
.mc{background:var(--bg);border-radius:var(--rs);padding:14px 16px;border:.5px solid var(--bdr)}
.ml{font-size:11px;color:var(--text2);font-weight:500;text-transform:uppercase;letter-spacing:.05em;margin-bottom:5px}
.mv{font-size:26px;font-weight:600;line-height:1}.ms{font-size:11px;color:var(--text3);margin-top:4px}
.teal{color:var(--teal)}.blue{color:#185fa5}.amber{color:var(--amber)}.red{color:var(--red)}
.card{background:var(--bg);border-radius:var(--r);border:.5px solid var(--bdr);padding:18px 20px;margin-bottom:14px}
.ch{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:8px}
.ct{font-size:14px;font-weight:600}.cs{font-size:12px;color:var(--text2);margin-top:2px}
.tabs{display:flex;gap:3px;background:var(--bg2);padding:3px;border-radius:var(--rs);border:.5px solid var(--bdr)}
.tab{padding:5px 12px;font-size:12px;font-weight:500;border-radius:6px;cursor:pointer;
     border:none;background:transparent;color:var(--text2);transition:all .15s}
.tab.active{background:var(--bg);color:var(--text);box-shadow:0 1px 3px rgba(0,0,0,.08)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}

/* ── Streak cards ─────────────────────────────────────────────── */
.sgrid-wrap{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.scard{background:var(--bg);border:.5px solid var(--bdr);border-radius:var(--r);padding:15px 16px}
.scard-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.scard-name{font-size:13px;font-weight:500}
.pts-badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:20px;color:#fff}
.scard-nums{display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;margin-bottom:10px}
.snum{text-align:center;padding:6px 4px;background:var(--bg2);border-radius:var(--rs)}
.snum-v{font-size:18px;font-weight:700;line-height:1}
.snum-l{font-size:10px;color:var(--text3);margin-top:3px;text-transform:uppercase;letter-spacing:.04em}
.cells{display:flex;flex-wrap:wrap;gap:2px}
.cell{width:10px;height:10px;border-radius:2px;flex-shrink:0}
@media(max-width:640px){.cell{width:8px;height:8px;gap:1px}}

/* ── Completion bars ──────────────────────────────────────────── */
.hbr{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.hn{font-size:12px;color:var(--text2);width:130px;flex-shrink:0}
.ht{flex:1;height:7px;background:var(--bg2);border-radius:3px;overflow:hidden}
.hf{height:100%;border-radius:3px;transition:width .4s}
.hv{font-size:12px;font-weight:500;min-width:34px;text-align:right}

/* ── Table ───────────────────────────────────────────────────── */
.dt{width:100%;font-size:12px;border-collapse:collapse}
.dt th{padding:7px 8px;text-align:left;color:var(--text2);border-bottom:.5px solid var(--bdr);font-weight:500;white-space:nowrap}
.dt td{padding:6px 8px;border-bottom:.5px solid var(--bdr)}
.dt tr:last-child td{border-bottom:none}.dt tr:hover td{background:var(--bg2)}
.wb{display:flex;height:6px;border-radius:3px;overflow:hidden;width:52px}
.wb .w{background:var(--teal)}.wb .l{background:var(--red-l)}
.pill{display:inline-flex;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:500}
.pp{background:var(--teal-l);color:var(--teal)}.np{background:var(--red-l);color:var(--red)}
.rk{display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;
    border-radius:5px;font-size:11px;font-weight:700;color:#fff;margin-right:4px;flex-shrink:0}

@media(max-width:640px){
  .g4{grid-template-columns:repeat(2,1fr)}
  div[style*="repeat(5"]{grid-template-columns:repeat(2,1fr) !important}
  .two{grid-template-columns:1fr}
  .sgrid-wrap{grid-template-columns:repeat(2,1fr)}
  .dt{font-size:11px}
  .dt th,.dt td{padding:5px 5px;white-space:nowrap}
  .dt .hide-mobile{display:none}
}
@media(max-width:400px){.sgrid-wrap{grid-template-columns:1fr}}
</style>
</head>
<body><div class="app">

<div class="hrow">
  <h1>PGI Dashboard</h1>
  <span class="meta" id="dr"></span>
  <span class="meta" style="margin-left:auto">Updated %%GEN%%</span><span class="meta" style="background:rgba(163,45,45,0.12);color:#a32d2d;padding:2px 8px;border-radius:20px;font-weight:500;margin-left:6px">−1 per missed habit</span>
</div>

<div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-bottom:14px">
  <div class="mc"><div class="ml">Current PGI</div><div class="mv blue" id="m1">—</div><div class="ms" id="m1s"></div></div>
  <div class="mc"><div class="ml">Days tracked</div><div class="mv teal" id="m2">—</div><div class="ms" id="m2s"></div></div>
  <div class="mc"><div class="ml">Win rate</div><div class="mv" id="m3">—</div><div class="ms" id="m3s"></div></div>
  <div class="mc"><div class="ml">7-day momentum</div><div class="mv" id="m4">—</div><div class="ms">avg daily aggregate</div></div>
  <div class="mc"><div class="ml">Tasks (all time)</div><div class="mv amber" id="m5">—</div><div class="ms" id="m5s"></div></div>
</div>

<!-- Main chart -->
<div class="card">
  <div class="ch">
    <div><div class="ct">PGI score + momentum</div><div class="cs" id="mcs"></div></div>
    <div class="tabs">
      <button class="tab active" onclick="sv('weekly',this)">Weekly</button>
      <button class="tab" onclick="sv('monthly',this)">Monthly</button>
      <button class="tab" onclick="sv('daily',this)">Daily</button>
    </div>
  </div>
  <div style="position:relative;height:260px"><canvas id="mc2"></canvas></div>
</div>

<!-- Per-habit streak cards -->
<div class="card">
  <div class="ch">
    <div><div class="ct">Habit streaks</div>
      <div class="cs">Current streak · best ever · completion rate · last 90 days · <span style="color:#185fa5;cursor:pointer">tap any card for detail ↗</span></div></div>
    <div class="tabs">
      <button class="tab active" onclick="setGrid(90,this)">90 days</button>
      <button class="tab" onclick="setGrid(30,this)">30 days</button>
      <button class="tab" onclick="setGrid(0,this)">All time</button>
    </div>
  </div>
  <div class="sgrid-wrap" id="streak-wrap"></div>
</div>

<!-- Completion rates + monthly bar -->
<div class="two">
  <div class="card" style="margin-bottom:0">
    <div class="ch"><div class="ct">Completion rates</div>
      <div class="tabs">
        <button class="tab active" onclick="sh('all',this)">All time</button>
        <button class="tab" onclick="sh('3m',this)">3 months</button>
        <button class="tab" onclick="sh('1m',this)">1 month</button>
      </div>
    </div>
    <div id="hb"></div>
  </div>
  <div class="card" style="margin-bottom:0">
    <div class="ch"><div class="ct">Monthly net gain</div></div>
    <div style="position:relative;height:210px"><canvas id="bc2"></canvas></div>
  </div>
</div>

<!-- Month table -->
<div class="card" style="margin-top:14px">
  <div class="ch"><div class="ct">Month-by-month breakdown</div></div>
  <div style="overflow-x:auto"><table class="dt" id="mt"></table></div>
</div>

</div>
<script>
const D=%%DATA%%;
const sign=n=>n>0?'+':'', fmt=(n,d=0)=>n==null?'—':Number(n).toFixed(d);
function rk(p){
  if(p==null)return{r:'?',c:'#888'};if(p<0)return{r:'F',c:'#e24b4a'};
  if(p<100)return{r:'E',c:'#888780'};if(p<300)return{r:'D',c:'#5f5e5a'};
  if(p<600)return{r:'C',c:'#ba7517'};if(p<1000)return{r:'B',c:'#0f6e56'};
  if(p<2000)return{r:'A',c:'#185fa5'};if(p<5000)return{r:'S',c:'#534ab7'};
  return{r:'SS',c:'#d85a30'};
}
const daily=D.daily, monthly=D.monthly, weekly=D.weekly;
const streaks=D.streaks;
const last=daily[daily.length-1];

// ── Summary cards ─────────────────────────────────────────────────────────────
const r2=rk(last.pgi);
document.getElementById('m1').textContent=fmt(last.pgi);
document.getElementById('m1s').innerHTML=`<span class="rk" style="background:${r2.c}">${r2.r}</span>Rank ${r2.r}`;
document.getElementById('dr').textContent=daily[0].date+' → '+last.date;
document.getElementById('m2').textContent=daily.length;
document.getElementById('m2s').textContent='since '+daily[0].date;
const pos=daily.filter(d=>(d.agg||0)>0).length, neg=daily.filter(d=>(d.agg||0)<0).length;
const wr=(pos+neg)>0?Math.round(pos/(pos+neg)*100):0;
const we=document.getElementById('m3');
we.textContent=wr+'%'; we.className='mv '+(wr>=55?'teal':wr>=45?'amber':'red');
document.getElementById('m3s').textContent=`${pos} wins · ${neg} losses`;
const me=document.getElementById('m4');
me.textContent=last.mw!=null?(last.mw>0?'+':'')+fmt(last.mw,2):'—';
me.className='mv '+(last.mw>0?'teal':last.mw<0?'red':'');

// ── Tasks summary ─────────────────────────────────────────────────────────────
const totalTasks  = daily.reduce((s,d)=>s+(d.tasks&&d.tasks.total||0),0);
const onTimeTasks = daily.reduce((s,d)=>s+(d.tasks&&d.tasks.on_time||0),0);
const onTimeRate  = totalTasks ? Math.round(onTimeTasks/totalTasks*100) : 0;
const t5=document.getElementById('m5');
if(t5){
  t5.textContent = totalTasks || '—';
  t5.className = 'mv amber';
  const t5s=document.getElementById('m5s');
  if(t5s) t5s.textContent = totalTasks ? onTimeRate+'% on time' : 'connect Todoist';
}

// ── Main chart ────────────────────────────────────────────────────────────────
let mc3, cv='weekly';
function buildMain(v){
  cv=v;
  let lbl, pd, md, sub;
  if(v==='daily'){
    lbl=daily.map(d=>d.date); pd=daily.map(d=>d.pgi); md=daily.map(d=>d.mw);
    sub=daily.length+' days';
  } else if(v==='weekly'){
    lbl=weekly.map(w=>w.label); pd=weekly.map(w=>w.pgi); md=weekly.map(w=>w.mw);
    sub=weekly.length+' weeks';
  } else {
    lbl=monthly.map(m=>m.label); pd=monthly.map(m=>m.pgi); md=monthly.map(m=>m.net);
    sub=monthly.length+' months';
  }
  document.getElementById('mcs').textContent=sub+' · PGI line + momentum bars';
  if(mc3) mc3.destroy();
  mc3=new Chart(document.getElementById('mc2'),{
    data:{labels:lbl, datasets:[
      {type:'line',label:'PGI',data:pd,borderColor:'#185fa5',borderWidth:2,
       pointRadius:v==='monthly'?4:v==='weekly'?2:0,pointHoverRadius:5,tension:0.35,
       yAxisID:'y',fill:{target:'origin',above:'rgba(24,95,165,0.06)',below:'rgba(163,45,45,0.06)'}},
      {type:'bar',label:v==='monthly'?'Net':'Mom.',data:md,yAxisID:'y2',borderRadius:3,
       backgroundColor:md.map(x=>(x||0)>=0?'rgba(15,110,86,0.4)':'rgba(163,45,45,0.4)')}
    ]},
    options:{responsive:true,maintainAspectRatio:false,
      interaction:{mode:'index',intersect:false},
      plugins:{legend:{display:false},tooltip:{callbacks:{
        title:i=>i[0].label,
        label:i=>i.datasetIndex===0?` PGI: ${fmt(i.raw)}`:` ${cv==='monthly'?'Net':'Mom.'}: ${sign(i.raw)}${fmt(i.raw,1)}`
      }}},
      scales:{
        x:{ticks:{maxTicksLimit:16,color:'#888',font:{size:11},autoSkip:true,maxRotation:40},
           grid:{color:'rgba(128,128,128,0.08)'}},
        y:{position:'left',ticks:{color:'#185fa5',font:{size:11}},grid:{color:'rgba(128,128,128,0.08)'},
           title:{display:true,text:'PGI',color:'#185fa5',font:{size:11}}},
        y2:{position:'right',ticks:{color:'#0f6e56',font:{size:11}},grid:{display:false},
            title:{display:true,text:cv==='monthly'?'Net gain':'Momentum',color:'#0f6e56',font:{size:11}}}
      }
    }
  });
}
function sv(v,btn){
  document.querySelectorAll('#mc2').forEach(()=>{});
  btn.closest('.card').querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active'); buildMain(v);
}
buildMain('weekly');

// ── Bar chart ─────────────────────────────────────────────────────────────────
let bc3;
(function(){
  const lbl=monthly.map(m=>m.label.slice(2).replace('-','/'));
  const nets=monthly.map(m=>m.net);
  bc3=new Chart(document.getElementById('bc2'),{type:'bar',
    data:{labels:lbl,datasets:[{data:nets,borderRadius:3,
      backgroundColor:nets.map(v=>(v||0)>=0?'rgba(15,110,86,0.7)':'rgba(163,45,45,0.7)')}]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:i=>` ${sign(i.raw)}${fmt(i.raw)} pts`}}},
      scales:{x:{ticks:{color:'#888',font:{size:10},autoSkip:false,maxRotation:50},grid:{display:false}},
              y:{ticks:{color:'#888',font:{size:10}},grid:{color:'rgba(128,128,128,0.08)'}}}}
  });
})();

// ── Streak cards ──────────────────────────────────────────────────────────────
let gridDays=90;
function setGrid(days, btn){
  gridDays=days;
  btn.closest('.card').querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  buildStreakCards();
}

function buildStreakCards(){
  const wrap=document.getElementById('streak-wrap');
  wrap.innerHTML=streaks.map(h=>{
    const grid = days => {
      const slice = days===0 ? h.grid : h.grid.slice(-days);
      return slice.map(v=>
        `<div class="cell" style="background:${v?h.color:'rgba(128,128,128,0.15)'}"
              title="${v?'Done':'Missed'}"></div>`
      ).join('');
    };
    const streakColor = h.cur>=14?'#0f6e56':h.cur>=7?'#ba7517':h.cur>=3?'#185fa5':'#888';
    const fire = h.cur>=14?' 🔥':h.cur>=7?' ⚡':'';
    return `<div class="scard" style="border-top:3px solid ${h.color};cursor:pointer" onclick="openHabit('${h.name}')">
      <div class="scard-head">
        <div class="scard-name">${h.name}${fire}</div>
        <div class="pts-badge" style="background:${h.color}">${h.points>0?'+':''}${h.points}</div>
      </div>
      <div class="scard-nums">
        <div class="snum">
          <div class="snum-v" style="color:${streakColor}">${h.cur}</div>
          <div class="snum-l">Current</div>
        </div>
        <div class="snum">
          <div class="snum-v" style="color:${h.color}">${h.best}</div>
          <div class="snum-l">Best</div>
        </div>
        <div class="snum">
          <div class="snum-v" style="color:${h.rate>=60?'#0f6e56':h.rate>=40?'#ba7517':'#a32d2d'}">${h.rate}%</div>
          <div class="snum-l">Rate</div>
        </div>
      </div>
      <div class="cells">${grid(gridDays)}</div>
      <div style="font-size:10px;color:var(--text3);margin-top:5px">${h.done} of ${h.total} days</div>
    </div>`;
  }).join('');
}
buildStreakCards();

function openHabit(name){
  window.location.href='habit_detail.html?habit='+encodeURIComponent(name);
}

// ── Completion rates bars ─────────────────────────────────────────────────────
function buildRates(period){
  const ld=new Date(last.date);
  let sl=daily;
  if(period==='3m'){const c=new Date(ld);c.setMonth(c.getMonth()-3);sl=daily.filter(d=>new Date(d.date)>=c);}
  else if(period==='1m'){const c=new Date(ld);c.setMonth(c.getMonth()-1);sl=daily.filter(d=>new Date(d.date)>=c);}
  const n=sl.length||1;
  document.getElementById('hb').innerHTML=streaks.map(h=>{
    const rate=Math.round(sl.reduce((s,d)=>s+(d.habits[h.name]||0),0)/n*100);
    return `<div class="hbr">
      <div class="hn" style="color:var(--text2)">${h.name}</div>
      <div class="ht"><div class="hf" style="width:${rate}%;background:${h.color}"></div></div>
      <div class="hv" style="color:${h.color}">${rate}%</div>
    </div>`;
  }).join('');
}
function sh(p,btn){
  btn.closest('.card').querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active'); buildRates(p);
}
buildRates('all');

// ── Month table ───────────────────────────────────────────────────────────────
(function(){
  const rows=[...monthly].reverse();
  const mob = window.innerWidth < 640;
  let h=`<thead><tr><th>Month</th><th>PGI</th><th>Net</th><th>W/L</th>${mob?'':'<th>Momentum</th>'}`;
  streaks.forEach(s=>{ h+=`<th>${s.name.split(' ')[0]}</th>`; });
  h+=`</tr></thead><tbody>`;
  rows.forEach(m=>{
    const rk2=rk(m.pgi);
    const wp=Math.round(m.pd/(m.pd+m.nd||1)*100);
    const lbl=m.label.length>=7?m.label.slice(2).replace('-','/'):m.label;
    const nc=(m.net||0)>=0?'var(--teal)':'var(--red)';
    h+=`<tr>
      <td style="font-weight:500">${lbl}</td>
      <td><span class="rk" style="background:${rk2.c}">${rk2.r}</span>${fmt(m.pgi)}</td>
      <td style="color:${nc};font-weight:500">${sign(m.net)}${fmt(m.net)}</td>
      <td><div style="display:flex;align-items:center;gap:5px">
        <div class="wb"><div class="w" style="width:${wp}%"></div><div class="l" style="width:${100-wp}%"></div></div>
        <span style="font-size:11px;color:var(--text2)">${m.pd}W ${m.nd}L</span></div></td>
      <td><span class="pill ${(m.net||0)>=0?'pp':'np'}">${sign(m.net)}${fmt(m.net)}</span></td>`;
    streaks.forEach(s=>{
      const r=(m.rates||{})[s.name]||0;
      const c=r>=60?s.color:r>=40?'var(--amber)':'var(--red)';
      h+=`<td style="color:${c};font-weight:500">${r}%</td>`;
    });
    h+=`</tr>`;
  });
  h+=`</tbody>`;
  document.getElementById('mt').innerHTML=h;
})();
</script></body></html>"""

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    with run_lock():
        json_path = find_json()
        run_report = {
            "unmatched_habits": [],
            "skipped_checked_days": 0,
        }

        if json_path is None:
            print("  No habits-*.json found. Trying fallback data/latest.json ...")
            payload = load_latest_payload()
            if payload is None:
                print("ERROR: No habits export and no fallback payload found.")
                sys.exit(1)
            print("  Using fallback payload from data/latest.json")
        else:
            print(f"Reading {json_path.name}...")
            day_map = parse_thefor(json_path, run_report=run_report)
            if not day_map:
                print("  No matching habits found in export. Trying fallback data/latest.json ...")
                payload = load_latest_payload()
                if payload is None:
                    print("ERROR: No matching habits and no fallback payload found.")
                    sys.exit(1)
                print("  Using fallback payload from data/latest.json")
            else:
                thefor_start = date.fromisoformat(min(day_map.keys()))
                print(f"  thefor: {min(day_map.keys())} → {max(day_map.keys())}  ({len(day_map)} active days)")

                excel_rows = []
                if USE_EXCEL and EXCEL_FILE.exists():
                    print(f"  Merging Excel history before {thefor_start}...")
                    excel_rows = load_excel(thefor_start)
                    print(f"  Excel rows: {len(excel_rows)}")
                elif not USE_EXCEL:
                    print("  Excel disabled — thefor only (clean sample mode).")
                else:
                    print("  No PGI_v3.xlsx — using thefor data only.")

                task_map = fetch_todoist()
                if task_map:
                    total_tasks = sum(v["total"] for v in task_map.values())
                    print(f"  Todoist: {total_tasks} completed tasks across {len(task_map)} days")

                all_rows = merge(excel_rows, day_map, task_map)
                daily    = calc_metrics(all_rows)
                weekly, monthly = aggregates(daily)
                streaks  = streak_summary(daily)

                payload = {
                    "daily":    daily,
                    "weekly":   weekly,
                    "monthly":  monthly,
                    "streaks":  streaks,
                    "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }

        html = HTML.replace("%%DATA%%", json.dumps(payload, separators=(',',':')))
        html = html.replace("%%GEN%%", payload.get("generated", datetime.now().strftime("%Y-%m-%d %H:%M")))
        OUTPUT_HTML.write_text(html, encoding="utf-8")

        detail_data = json.dumps(payload, separators=(',',':'))
        detail_html = DETAIL_TEMPLATE.replace("%%DETAIL_DATA%%", detail_data)
        OUTPUT_DETAIL.write_text(detail_html, encoding="utf-8")
        write_json_atomic(LATEST_JSON, payload)

        daily = payload.get("daily", [])
        weekly = payload.get("weekly", [])
        monthly = payload.get("monthly", [])
        streaks = payload.get("streaks", [])

        print(f"\nDone! → {OUTPUT_HTML.name} + {OUTPUT_DETAIL.name}")
        print(f"  {len(daily)} days  ·  {len(weekly)} weeks  ·  {len(monthly)} months")
        if daily:
            print(f"  Current PGI: {daily[-1]['pgi']}")
        print(f"  Parse report: unmatched={len(run_report['unmatched_habits'])}, skipped_checked_days={run_report['skipped_checked_days']}")
        print(f"\n  Habit streaks:")
        for s in streaks:
            bar = "█" * min(s["cur"], 20)
            print(f"    {s['name']:20}  streak={s['cur']:3}  best={s['best']:3}  rate={s['rate']:3}%  {bar}")
        print(f"\nOpen PGI_Dashboard.html in your browser.")

if __name__ == "__main__":
    main()
