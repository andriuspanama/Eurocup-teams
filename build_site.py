"""Sugeneruoja modernų EuroCup dashboard iš site/data.json."""

import json
import pathlib
from html import escape as e


CSS = r"""
:root{
  --bg:#07111f;
  --bg2:#0b1728;
  --card:#101f33;
  --card2:#14263d;
  --border:rgba(255,255,255,.09);
  --text:#f4f7fb;
  --muted:#8fa2b8;
  --accent:#35d07f;
  --accent2:#55a8ff;
  --danger:#ff5f6d;
  --warning:#ffc857;
  --shadow:0 16px 40px rgba(0,0,0,.22);
}

*{
  box-sizing:border-box;
}

html{
  scroll-behavior:smooth;
}

body{
  margin:0;
  font-family:
    Inter,
    ui-sans-serif,
    system-ui,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
  background:
    radial-gradient(circle at top right,rgba(53,208,127,.08),transparent 30%),
    radial-gradient(circle at top left,rgba(85,168,255,.08),transparent 30%),
    var(--bg);
  color:var(--text);
  min-height:100vh;
}

button,
input,
select{
  font:inherit;
}

button{
  cursor:pointer;
}

.topbar{
  position:sticky;
  top:0;
  z-index:50;
  backdrop-filter:blur(18px);
  background:rgba(7,17,31,.82);
  border-bottom:1px solid var(--border);
}

.topbar-inner{
  max-width:1200px;
  margin:auto;
  padding:14px 18px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:16px;
}

.brand{
  display:flex;
  align-items:center;
  gap:12px;
  min-width:0;
}

.brand-logo{
  width:46px;
  height:46px;
  object-fit:contain;
  border-radius:12px;
  background:rgba(255,255,255,.05);
  padding:5px;
}

.brand-title{
  font-size:18px;
  font-weight:800;
  line-height:1.1;
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}

.brand-subtitle{
  color:var(--muted);
  font-size:12px;
  margin-top:3px;
}

.updated{
  color:var(--muted);
  font-size:11px;
  white-space:nowrap;
}

main{
  max-width:1200px;
  margin:auto;
  padding:22px 18px 50px;
}

.hero{
  display:grid;
  grid-template-columns:1.5fr 1fr;
  gap:16px;
  margin-bottom:18px;
}

.hero-main,
.hero-hot{
  background:
    linear-gradient(135deg,rgba(255,255,255,.06),rgba(255,255,255,.015));
  border:1px solid var(--border);
  border-radius:22px;
  padding:24px;
  box-shadow:var(--shadow);
}

.hero-main{
  position:relative;
  overflow:hidden;
}

.hero-main:after{
  content:"";
  position:absolute;
  width:230px;
  height:230px;
  right:-80px;
  top:-100px;
  background:rgba(53,208,127,.10);
  border-radius:50%;
  filter:blur(5px);
}

.eyebrow{
  color:var(--accent);
  text-transform:uppercase;
  font-size:11px;
  font-weight:800;
  letter-spacing:.12em;
}

.hero h1{
  font-size:34px;
  line-height:1.05;
  margin:8px 0 10px;
  max-width:650px;
}

.hero p{
  margin:0;
  color:var(--muted);
  line-height:1.5;
  max-width:650px;
}

.stats{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
  margin-top:20px;
}

.stat{
  background:rgba(255,255,255,.045);
  border:1px solid var(--border);
  border-radius:14px;
  padding:10px 14px;
  min-width:100px;
}

.stat-number{
  font-size:21px;
  font-weight:850;
}

.stat-label{
  color:var(--muted);
  font-size:11px;
  margin-top:2px;
}

.hero-hot{
  display:flex;
  flex-direction:column;
  justify-content:center;
}

.hot-title{
  color:var(--muted);
  font-size:11px;
  text-transform:uppercase;
  letter-spacing:.1em;
  font-weight:800;
  margin-bottom:12px;
}

.hot-team{
  display:flex;
  align-items:center;
  gap:12px;
}

.hot-team img{
  width:54px;
  height:54px;
  object-fit:contain;
  border-radius:14px;
  background:rgba(255,255,255,.06);
  padding:5px;
}

.hot-name{
  font-size:19px;
  font-weight:800;
}

.hot-form{
  display:flex;
  gap:4px;
  margin-top:6px;
}

.controls{
  display:grid;
  grid-template-columns:1fr auto auto;
  gap:10px;
  margin-bottom:14px;
}

.search{
  width:100%;
  background:var(--card);
  color:var(--text);
  border:1px solid var(--border);
  border-radius:14px;
  padding:13px 15px;
  outline:none;
}

.search:focus{
  border-color:rgba(53,208,127,.55);
  box-shadow:0 0 0 3px rgba(53,208,127,.08);
}

.select{
  background:var(--card);
  color:var(--text);
  border:1px solid var(--border);
  border-radius:14px;
  padding:0 13px;
  min-width:155px;
  outline:none;
}

.favorite-toggle{
  border:1px solid var(--border);
  background:var(--card);
  color:var(--text);
  border-radius:14px;
  padding:0 16px;
  font-weight:700;
}

.favorite-toggle.active{
  border-color:rgba(255,200,87,.35);
  color:var(--warning);
}

.filters{
  display:flex;
  gap:7px;
  overflow-x:auto;
  padding-bottom:5px;
  margin-bottom:18px;
  scrollbar-width:none;
}

.filters::-webkit-scrollbar{
  display:none;
}

.filter{
  flex:0 0 auto;
  border:1px solid var(--border);
  background:rgba(255,255,255,.035);
  color:var(--muted);
  padding:8px 12px;
  border-radius:999px;
  font-size:12px;
  font-weight:700;
}

.filter.active{
  background:rgba(53,208,127,.13);
  border-color:rgba(53,208,127,.35);
  color:var(--accent);
}

.league{
  margin-bottom:24px;
}

.league-header{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin:20px 0 9px;
}

.league-title{
  display:flex;
  align-items:center;
  gap:10px;
  min-width:0;
}

.league-title img{
  width:32px;
  height:32px;
  object-fit:contain;
  border-radius:9px;
  background:rgba(255,255,255,.05);
  padding:3px;
}

.league-name{
  font-size:17px;
  font-weight:850;
}

.league-count{
  color:var(--muted);
  font-size:11px;
}

.teams{
  display:grid;
  gap:7px;
}

.team{
  position:relative;
  display:grid;
  grid-template-columns:42px minmax(150px,1fr) 46px 76px 100px;
  align-items:center;
  gap:10px;
  background:linear-gradient(135deg,rgba(255,255,255,.045),rgba(255,255,255,.02));
  border:1px solid var(--border);
  border-radius:15px;
  padding:9px 11px;
  transition:.18s ease;
  cursor:pointer;
}

.team:hover{
  transform:translateY(-1px);
  border-color:rgba(255,255,255,.18);
  background:var(--card2);
}

.team-logo{
  width:38px;
  height:38px;
  object-fit:contain;
  border-radius:10px;
  background:rgba(255,255,255,.05);
  padding:4px;
}

.team-name-wrap{
  min-width:0;
}

.team-name{
  font-weight:800;
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}

.team-note{
  color:var(--warning);
  font-size:10px;
  margin-top:3px;
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}

.rank{
  font-size:16px;
  font-weight:900;
  text-align:center;
}

.record{
  color:var(--muted);
  font-size:12px;
  text-align:center;
}

.form{
  display:flex;
  justify-content:flex-end;
  gap:3px;
}

.f{
  width:20px;
  height:20px;
  border-radius:6px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  font-size:10px;
  font-weight:900;
  color:white;
}

.W{
  background:var(--accent);
  color:#062315;
}

.L{
  background:var(--danger);
}

.favorite{
  position:absolute;
  right:7px;
  top:6px;
  width:24px;
  height:24px;
  border:0;
  background:transparent;
  color:#53657b;
  font-size:17px;
  padding:0;
  z-index:2;
}

.favorite:hover{
  color:var(--warning);
}

.favorite.active{
  color:var(--warning);
}

.no-results{
  padding:35px;
  text-align:center;
  color:var(--muted);
  background:var(--card);
  border:1px solid var(--border);
  border-radius:16px;
}

.footer{
  text-align:center;
  color:var(--muted);
  font-size:11px;
  padding:20px 0 0;
}

.modal-backdrop{
  display:none;
  position:fixed;
  inset:0;
  z-index:100;
  background:rgba(0,0,0,.7);
  backdrop-filter:blur(7px);
  padding:18px;
  align-items:center;
  justify-content:center;
}

.modal-backdrop.open{
  display:flex;
}

.modal{
  width:min(620px,100%);
  max-height:90vh;
  overflow:auto;
  background:#0c1a2c;
  border:1px solid var(--border);
  border-radius:24px;
  box-shadow:0 30px 80px rgba(0,0,0,.5);
}

.modal-head{
  padding:20px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
  border-bottom:1px solid var(--border);
}

.modal-team{
  display:flex;
  align-items:center;
  gap:
