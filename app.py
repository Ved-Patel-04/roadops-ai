import json
import html
from pathlib import Path

import streamlit as st

from agent.orchestrator import run_roadops


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
BENCHMARK_PATH = BASE_DIR / "data" / "benchmark_frozen_v1.json"

st.set_page_config(
    page_title="RoadOps AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# GLOBAL STYLE
# =========================================================

st.html(r"""
<style>
:root {
  --bg: #06101b;
  --bg-deep: #040a12;
  --panel: rgba(9, 23, 39, 0.76);
  --panel-strong: rgba(12, 30, 50, 0.92);
  --border: rgba(148, 163, 184, 0.13);
  --border-blue: rgba(77, 163, 255, 0.26);
  --text: #f5f9ff;
  --muted: #8395ad;
  --muted2: #60748d;
  --blue: #55a8ff;
  --cyan: #70e6ff;
  --green: #58e5a5;
  --amber: #ffd166;
  --orange: #ff9f57;
  --red: #ff667a;
}

html, body, [class*="css"] {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* Hide Streamlit's top chrome so it never overlaps the product UI. */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
}

/* Keep sidebar reopen control visible */
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;

    position: fixed !important;
    top: 16px !important;
    left: 16px !important;

    z-index: 999999 !important;
}

[data-testid="stSidebarCollapsedControl"] button {
    background: rgba(8, 21, 36, 0.92) !important;
    border: 1px solid rgba(85,168,255,.22) !important;
    border-radius: 10px !important;
    color: #d7edff !important;

    box-shadow: 0 8px 28px rgba(0,0,0,.25) !important;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.stApp {
  background:
    radial-gradient(circle at 82% -5%, rgba(34, 112, 255, .16), transparent 31%),
    radial-gradient(circle at 10% 18%, rgba(33, 213, 255, .055), transparent 26%),
    linear-gradient(180deg, #071421 0%, #040a12 100%);
  color: var(--text);
}

[data-testid="stMainBlockContainer"] {
  max-width: 1480px;
  padding-top: 1.6rem !important;
  padding-bottom: 5rem;
  animation: pageEnter .55s cubic-bezier(.22,.61,.36,1);
}

@keyframes pageEnter {
  from { opacity: 0; transform: translateY(12px); filter: blur(5px); }
  to   { opacity: 1; transform: translateY(0); filter: blur(0); }
}

/* ---------------------------------------------------------
   MODE CHANGE WIPE
--------------------------------------------------------- */
.mode-wipe {
  position: fixed;
  inset: 0;
  z-index: 999999;
  pointer-events: none;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at 50% 50%, rgba(64, 154, 255, .16), transparent 36%),
    rgba(3, 9, 16, .94);
  animation: wipeOut .72s cubic-bezier(.22,.61,.36,1) forwards;
}

.mode-wipe::before {
  content: "";
  position: absolute;
  width: 140vw;
  height: 2px;
  background: linear-gradient(90deg, transparent, #67dfff, #55a8ff, transparent);
  box-shadow: 0 0 45px rgba(85,168,255,.65);
  animation: scanWipe .55s ease-out forwards;
}

.mode-wipe-label {
  position: relative;
  z-index: 2;
  font-size: .75rem;
  font-weight: 900;
  letter-spacing: .22em;
  color: #c8e5ff;
  text-transform: uppercase;
  animation: modeLabel .58s ease-out forwards;
}

@keyframes scanWipe {
  from { transform: translateY(-52vh); opacity: 0; }
  20% { opacity: 1; }
  to { transform: translateY(52vh); opacity: 0; }
}

@keyframes modeLabel {
  0% { opacity: 0; transform: scale(.92); letter-spacing: .38em; }
  36% { opacity: 1; transform: scale(1); }
  100% { opacity: 0; transform: scale(1.035); letter-spacing: .22em; }
}

@keyframes wipeOut {
  0%, 48% { opacity: 1; }
  100% { opacity: 0; visibility: hidden; }
}

/* ---------------------------------------------------------
   SIDEBAR
--------------------------------------------------------- */
[data-testid="stSidebar"] {
  background:
    radial-gradient(circle at 15% 0%, rgba(54,137,255,.13), transparent 24%),
    linear-gradient(180deg, rgba(8, 21, 36, .995), rgba(4, 11, 20, .995));
  border-right: 1px solid rgba(148,163,184,.11);
  box-shadow: 24px 0 70px rgba(0,0,0,.18);
}

[data-testid="stSidebar"] > div:first-child {
  padding-top: 1.3rem;
}

.sidebar-shell {
  position: relative;
  padding: .35rem 0 .25rem;
}

.sidebar-shell::before {
  content: "";
  position: absolute;
  left: 0;
  top: -.9rem;
  width: 72px;
  height: 2px;
  background: linear-gradient(90deg, #58aaff, transparent);
  box-shadow: 0 0 18px rgba(88,170,255,.55);
}

.side-brand {
  display: flex;
  align-items: center;
  gap: .78rem;
}

.side-logo {
  width: 40px;
  height: 40px;
  border-radius: 13px;
  border: 1px solid rgba(255,159,87,.24);
  background:
    radial-gradient(circle at 50% 34%, rgba(255,159,87,.16), transparent 58%),
    linear-gradient(145deg, rgba(15,33,51,.98), rgba(7,18,30,.98));
  position: relative;
  display: grid;
  place-items: center;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.03), 0 10px 26px rgba(0,0,0,.20);
  animation: coneFloatSmall 4.2s ease-in-out infinite;
}

.side-logo svg {
  width: 24px;
  height: 24px;
  filter: drop-shadow(0 5px 10px rgba(255,126,54,.20));
}

@keyframes coneFloatSmall {
  0%,100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

.side-name {
  color: #f5f9ff;
  font-size: 1.07rem;
  font-weight: 900;
  letter-spacing: -.025em;
}

.side-sub {
  color: #667c96;
  font-size: .7rem;
  margin-top: .11rem;
}

.side-section {
  margin-top: 1.1rem;
  color: #5f7590;
  font-size: .63rem;
  font-weight: 900;
  letter-spacing: .16em;
  text-transform: uppercase;
}

.side-helper {
  margin-top: .3rem;
  color: #9aabc0;
  font-size: .76rem;
  line-height: 1.55;
}

[data-testid="stSidebar"] hr {
  border-color: rgba(148,163,184,.095);
  margin: 1.05rem 0;
}

/* segmented mode selector */
[data-testid="stSegmentedControl"] {
  padding: 4px;
  border: 1px solid rgba(148,163,184,.12);
  border-radius: 13px;
  background: rgba(2,10,18,.72);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.02);
}

[data-testid="stSegmentedControl"] button {
  border-radius: 9px !important;
  transition: transform .22s ease, background .22s ease, color .22s ease, box-shadow .22s ease !important;
  font-weight: 800 !important;
}

[data-testid="stSegmentedControl"] button:hover {
  transform: translateY(-1px);
}

[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
  background: linear-gradient(135deg, rgba(55,135,255,.27), rgba(64,205,255,.11)) !important;
  color: #d7edff !important;
  box-shadow: 0 0 0 1px rgba(85,168,255,.23), 0 10px 30px rgba(21,100,210,.13) !important;
  transform: scale(1.02);
}

/* Sidebar fields */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  color: #a8b7c9;
}

[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] input {
  border-radius: 12px !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
  border-radius: 12px !important;
  background: rgba(3, 12, 22, .76) !important;
  border-color: rgba(148,163,184,.12) !important;
}

[data-testid="stSidebar"] [data-testid="stTextArea"] textarea,
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
  background: rgba(3, 12, 22, .76) !important;
  border: 1px solid rgba(148,163,184,.12) !important;
}

[data-testid="stSidebar"] .stButton button[kind="primary"] {
  min-height: 3.15rem;
  border: 0 !important;
  border-radius: 13px !important;
  color: #06111f !important;
  font-weight: 900 !important;
  letter-spacing: -.01em;
  background: linear-gradient(100deg, #58aaff, #72e4ff) !important;
  box-shadow: 0 15px 36px rgba(54,146,255,.20);
  transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
}

[data-testid="stSidebar"] .stButton button[kind="primary"] p,
[data-testid="stSidebar"] .stButton button[kind="primary"] span {
  color: #06111f !important;
  font-weight: 900 !important;
  opacity: 1 !important;
}

[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
  transform: translateY(-2px);
  box-shadow: 0 19px 45px rgba(54,146,255,.28);
  filter: brightness(1.04);
}

/* ---------------------------------------------------------
   TOP PRODUCT BAR
--------------------------------------------------------- */
.product-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.product-lockup {
  display: flex;
  align-items: center;
  gap: .82rem;
}

.product-mark {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(255,159,87,.26);
  background:
    radial-gradient(circle at 50% 32%, rgba(255,159,87,.18), transparent 58%),
    linear-gradient(145deg, rgba(15,33,51,.98), rgba(7,18,30,.98));
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.04),
    0 14px 38px rgba(0,0,0,.22),
    0 0 30px rgba(255,126,54,.06);
  animation: coneFloat 4.4s ease-in-out infinite;
}

.product-mark svg {
  width: 31px;
  height: 31px;
  filter: drop-shadow(0 6px 12px rgba(255,126,54,.24));
}

@keyframes coneFloat {
  0%,100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-3px) rotate(-1deg); }
}

.product-name {
  color: #f7fbff;
  font-size: 1.82rem;
  line-height: 1;
  font-weight: 950;
  letter-spacing: -.052em;
}

.product-tagline {
  color: #7489a2;
  font-size: .79rem;
  margin-top: .33rem;
}

.ready-pill {
  display: inline-flex;
  align-items: center;
  gap: .52rem;
  padding: .46rem .72rem;
  border: 1px solid rgba(88,229,165,.2);
  border-radius: 999px;
  background: rgba(88,229,165,.06);
  color: #8ef0bd;
  font-size: .67rem;
  font-weight: 900;
  letter-spacing: .11em;
  text-transform: uppercase;
}

.ready-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #58e5a5;
  animation: readyPulse 1.8s infinite;
}

@keyframes readyPulse {
  0% { box-shadow: 0 0 0 0 rgba(88,229,165,.42); }
  70% { box-shadow: 0 0 0 9px rgba(88,229,165,0); }
  100% { box-shadow: 0 0 0 0 rgba(88,229,165,0); }
}

.mode-pill {
  display: inline-flex;
  align-items: center;
  margin-top: .12rem;
  padding: .38rem .68rem;
  border-radius: 999px;
  border: 1px solid rgba(85,168,255,.2);
  background: rgba(85,168,255,.07);
  color: #94c9ff;
  font-size: .65rem;
  font-weight: 900;
  letter-spacing: .11em;
  text-transform: uppercase;
  animation: modePill .48s cubic-bezier(.22,.61,.36,1);
}

@keyframes modePill {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

/* ---------------------------------------------------------
   LANDING EXPERIENCE
--------------------------------------------------------- */
.landing {
  position: relative;
  overflow: hidden;
  min-height: 650px;
  border: 1px solid rgba(148,163,184,.11);
  border-radius: 30px;
  background:
    linear-gradient(145deg, rgba(10,26,43,.86), rgba(5,15,26,.78));
  box-shadow: 0 38px 120px rgba(0,0,0,.24);
}

.landing::before {
  content: "";
  position: absolute;
  width: 760px;
  height: 760px;
  right: -300px;
  top: -420px;
  background: radial-gradient(circle, rgba(38,130,255,.22), transparent 64%);
  pointer-events: none;
}

.landing::after {
  content: "";
  position: absolute;
  width: 560px;
  height: 560px;
  left: -270px;
  bottom: -360px;
  background: radial-gradient(circle, rgba(53,219,255,.075), transparent 66%);
  pointer-events: none;
}

.grid-field {
  position: absolute;
  inset: 0;
  opacity: .13;
  background-image:
    linear-gradient(rgba(112,163,210,.15) 1px, transparent 1px),
    linear-gradient(90deg, rgba(112,163,210,.15) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: linear-gradient(to bottom, rgba(0,0,0,.9), transparent 92%);
}

.landing-inner {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 1.02fr .98fr;
  gap: 4.1rem;
  align-items: center;
  min-height: 650px;
  padding: 4rem 4.35rem;
}

.landing-kicker {
  color: #82baff;
  font-size: .69rem;
  font-weight: 900;
  letter-spacing: .17em;
  text-transform: uppercase;
}

.landing-title {
  max-width: 780px;
  margin-top: .82rem;
  color: #f8fbff;
  font-size: clamp(3.1rem, 4.8vw, 5.15rem);
  line-height: .94;
  font-weight: 950;
  letter-spacing: -.078em;
}

.landing-title .accent {
  background: linear-gradient(90deg, #83c0ff, #77e3ff);
  -webkit-background-clip: text;
  color: transparent;
}

.landing-copy {
  max-width: 690px;
  margin-top: 1.42rem;
  color: #93a5bb;
  font-size: 1.06rem;
  line-height: 1.78;
}

.landing-copy strong { color: #d9eaff; font-weight: 760; }

.landing-points {
  display: flex;
  flex-wrap: wrap;
  gap: .66rem;
  margin-top: 1.6rem;
}

.landing-point {
  padding: .44rem .72rem;
  border-radius: 999px;
  border: 1px solid rgba(148,163,184,.13);
  background: rgba(255,255,255,.024);
  color: #a6b7ca;
  font-size: .71rem;
  font-weight: 760;
}

.landing-cta {
  margin-top: 2rem;
  color: #70859e;
  font-size: .82rem;
}
.landing-cta b { color: #d8e8fa; }

/* visual on landing */
.visual-stage {
  position: relative;
  min-height: 430px;
  display: grid;
  place-items: center;
}

.radar-ring {
  position: absolute;
  border: 1px solid rgba(85,168,255,.13);
  border-radius: 50%;
  animation: ringBreath 3.5s ease-in-out infinite;
}
.radar-ring.r1 { width: 360px; height: 360px; }
.radar-ring.r2 { width: 270px; height: 270px; animation-delay: .45s; }
.radar-ring.r3 { width: 180px; height: 180px; animation-delay: .9s; }

@keyframes ringBreath {
  0%,100% { opacity: .38; transform: scale(1); }
  50% { opacity: .92; transform: scale(1.035); }
}

.radar-sweep {
  position: absolute;
  width: 350px;
  height: 350px;
  border-radius: 50%;
  overflow: hidden;
}
.radar-sweep::before {
  content: "";
  position: absolute;
  left: 50%;
  top: 50%;
  width: 200px;
  height: 200px;
  transform-origin: 0 0;
  background: conic-gradient(from 0deg, rgba(85,168,255,.23), transparent 34deg);
  animation: radar 4.2s linear infinite;
}
@keyframes radar { to { transform: rotate(360deg); } }

.road-perspective {
  position: relative;
  width: 230px;
  height: 300px;
  transform: perspective(650px) rotateX(58deg);
  border-radius: 34px;
  overflow: hidden;
  box-shadow: 0 0 70px rgba(48,142,255,.09);
}

.road-surface {
  position: absolute;
  inset: 0 47px;
  border-left: 1px solid rgba(150,190,230,.17);
  border-right: 1px solid rgba(150,190,230,.17);
  background: linear-gradient(180deg, rgba(16,36,59,.97), rgba(4,16,28,.99));
}

.road-surface::before {
  content: "";
  position: absolute;
  left: 50%;
  top: -100px;
  width: 2px;
  height: 500px;
  transform: translateX(-50%);
  background: repeating-linear-gradient(to bottom, rgba(128,200,255,.86) 0 14px, transparent 14px 33px);
  animation: laneMove 1.08s linear infinite;
}

@keyframes laneMove { to { background-position: 0 33px; } }

.signal-node {
  position: absolute;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #70e6ff;
  box-shadow: 0 0 0 5px rgba(112,230,255,.07), 0 0 22px rgba(112,230,255,.57);
  animation: nodePulse 1.9s ease-in-out infinite;
}
.signal-node.n1 { top: 90px; left: 58px; }
.signal-node.n2 { top: 165px; right: 50px; animation-delay: .45s; }
.signal-node.n3 { bottom: 72px; left: 66px; animation-delay: .9s; }

@keyframes nodePulse {
  0%,100% { transform: scale(.8); opacity: .65; }
  50% { transform: scale(1.25); opacity: 1; }
}

.visual-label {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  color: #60758f;
  font-size: .64rem;
  font-weight: 850;
  letter-spacing: .16em;
  text-transform: uppercase;
  white-space: nowrap;
}

/* ---------------------------------------------------------
   HEADINGS
--------------------------------------------------------- */
.section-head {
  margin-top: 2rem;
  margin-bottom: .95rem;
}

.section-kicker {
  color: #60758f;
  font-size: .65rem;
  font-weight: 900;
  letter-spacing: .17em;
  text-transform: uppercase;
  margin-bottom: .32rem;
}

.section-title {
  color: #f5f9ff;
  font-size: 1.62rem;
  line-height: 1.12;
  font-weight: 920;
  letter-spacing: -.038em;
}

.section-copy {
  color: #71869f;
  font-size: .86rem;
  line-height: 1.55;
  margin-top: .34rem;
}

/* ---------------------------------------------------------
   INCIDENT HERO / PRIORITY
--------------------------------------------------------- */
.incident-hero {
  position: relative;
  overflow: hidden;
  min-height: 205px;
  padding: 1.7rem 1.8rem;
  border-radius: 23px;
  border: 1px solid rgba(148,163,184,.13);
  background: linear-gradient(135deg, rgba(12,31,52,.96), rgba(7,19,33,.91));
  box-shadow: 0 25px 72px rgba(0,0,0,.18);
}

.incident-hero::after {
  content: "";
  position: absolute;
  width: 390px;
  height: 390px;
  right: -170px;
  top: -210px;
  background: radial-gradient(circle, rgba(72,152,255,.17), transparent 66%);
}

.incident-id {
  color: #68809b;
  font-size: .66rem;
  font-weight: 900;
  letter-spacing: .17em;
  text-transform: uppercase;
}

.incident-report {
  position: relative;
  z-index: 2;
  max-width: 900px;
  margin-top: .85rem;
  color: #eef6ff;
  font-size: 1.34rem;
  font-weight: 640;
  line-height: 1.58;
}

.priority-panel {
  min-height: 205px;
  padding: 1.45rem 1.5rem;
  border-radius: 23px;
  border: 1px solid rgba(148,163,184,.13);
  background: linear-gradient(145deg, rgba(11,27,46,.96), rgba(6,17,30,.88));
}

.priority-kicker {
  color: #657b94;
  font-size: .65rem;
  font-weight: 900;
  letter-spacing: .16em;
  text-transform: uppercase;
}

.priority-value {
  margin-top: .55rem;
  font-size: 2.25rem;
  line-height: 1;
  font-weight: 950;
  letter-spacing: -.05em;
}
.priority-low { color: var(--green); }
.priority-medium { color: var(--amber); }
.priority-high { color: var(--orange); }
.priority-critical { color: var(--red); text-shadow: 0 0 28px rgba(255,102,122,.19); }
.priority-insufficient { color: var(--blue); }

.conf-label {
  margin-top: 1.25rem;
  color: #61758e;
  font-size: .62rem;
  font-weight: 900;
  letter-spacing: .14em;
  text-transform: uppercase;
}

.conf-big {
  margin-top: .2rem;
  color: #f8fbff;
  font-size: 1.88rem;
  font-weight: 940;
}

.conf-track {
  height: 4px;
  margin-top: .54rem;
  border-radius: 99px;
  overflow: hidden;
  background: rgba(148,163,184,.11);
}

.conf-fill {
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, #55a8ff, #70e6ff);
  animation: confGrow .82s ease-out;
}
@keyframes confGrow { from { width: 0 !important; } }

/* ---------------------------------------------------------
   FLIP CONTEXT CARDS
--------------------------------------------------------- */
.context-onboarding {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: .48rem;
  margin: -.2rem 0 .85rem;
  padding: .42rem .66rem;
  border-radius: 999px;
  border: 1px solid rgba(85,168,255,.16);
  background: rgba(85,168,255,.055);
  color: #83a9cf;
  font-size: .68rem;
  font-weight: 760;
  animation: hintAppear 5.7s ease forwards;
}
.context-onboarding::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #6fdfff;
  box-shadow: 0 0 14px rgba(111,223,255,.55);
}
@keyframes hintAppear {
  0% { opacity: 0; transform: translateY(5px); }
  10%, 78% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-3px); }
}

.flip-toggle {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.flip-card {
  display: block;
  position: relative;
  height: 165px;
  perspective: 900px;
  cursor: pointer;
  animation: floatCard 5s ease-in-out infinite;
}

.flip-card.delay-1 { animation-delay: .35s; }
.flip-card.delay-2 { animation-delay: .7s; }
.flip-card.delay-3 { animation-delay: 1.05s; }
.flip-card.delay-4 { animation-delay: 1.4s; }

@keyframes floatCard {
  0%,100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.flip-inner {
  width: 100%;
  height: 100%;
  position: relative;
  transform-style: preserve-3d;
  transition: transform .62s cubic-bezier(.2,.75,.25,1);
}

.flip-toggle:checked + .flip-card .flip-inner {
  transform: rotateY(180deg);
}

.flip-card:hover .flip-inner {
  transform: rotateY(180deg);
}

.flip-toggle:checked + .flip-card:hover .flip-inner {
  transform: rotateY(180deg);
}

.flip-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  border-radius: 19px;
  overflow: hidden;
  border: 1px solid rgba(148,163,184,.12);
  background: linear-gradient(145deg, rgba(12,29,48,.86), rgba(7,18,31,.72));
  box-shadow: 0 18px 44px rgba(0,0,0,.14);
}

.flip-front {
  display: grid;
  place-items: center;
}

.flip-front::before {
  content: "";
  position: absolute;
  width: 130px;
  height: 130px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(70,155,255,.12), transparent 68%);
}

.flip-front::after {
  content: "";
  position: absolute;
  width: 46px;
  height: 1px;
  bottom: 27px;
  background: linear-gradient(90deg, transparent, rgba(112,230,255,.48), transparent);
}

.flip-title {
  position: relative;
  z-index: 2;
  color: #eaf4ff;
  font-size: 1.1rem;
  font-weight: 900;
  letter-spacing: -.025em;
}

.flip-back {
  padding: 1rem 1.04rem;
  transform: rotateY(180deg);
  background: linear-gradient(145deg, rgba(14,35,58,.97), rgba(7,21,37,.94));
  border-color: rgba(85,168,255,.22);
}

.flip-back-title {
  color: #7890aa;
  font-size: .61rem;
  font-weight: 900;
  letter-spacing: .15em;
  text-transform: uppercase;
}

.flip-main {
  margin-top: .42rem;
  color: #f6faff;
  font-size: 1.2rem;
  font-weight: 920;
  letter-spacing: -.03em;
}

.flip-detail {
  margin-top: .3rem;
  color: #8ea2b9;
  font-size: .72rem;
  line-height: 1.45;
}

/* First-card hover direction. Once that card is clicked, this disappears. */
.flip-card.first-hint::after {
  content: "Click to keep this card open";
  position: absolute;
  z-index: 12;
  left: 50%;
  top: -42px;
  transform: translateX(-50%) translateY(5px);
  width: max-content;
  max-width: 200px;
  opacity: 0;
  pointer-events: none;
  padding: .4rem .57rem;
  border-radius: 9px;
  border: 1px solid rgba(112,230,255,.17);
  background: rgba(5,16,28,.96);
  color: #9ec6e8;
  font-size: .63rem;
  font-weight: 760;
  box-shadow: 0 12px 28px rgba(0,0,0,.25);
  transition: .18s ease;
}
.flip-card.first-hint:hover::after {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
.flip-toggle:checked + .flip-card.first-hint::after { display: none; }

/* ---------------------------------------------------------
   OPERATOR CONTENT
--------------------------------------------------------- */
.operator-summary {
  padding: 1.2rem 1.25rem;
  border-radius: 17px;
  border: 1px solid rgba(148,163,184,.105);
  background: rgba(9,23,39,.48);
}

.operator-summary-title {
  color: #eff6ff;
  font-size: .93rem;
  font-weight: 880;
}

.operator-summary-text {
  color: #93a6bc;
  font-size: .84rem;
  line-height: 1.72;
  margin-top: .55rem;
}

.action-card {
  display: flex;
  gap: .78rem;
  padding: .92rem .98rem;
  margin-bottom: .6rem;
  border-radius: 15px;
  border: 1px solid rgba(148,163,184,.10);
  background: rgba(9,23,39,.52);
  color: #dce9f8;
  font-size: .84rem;
  line-height: 1.52;
  transition: transform .18s ease, border-color .18s ease, background .18s ease;
}
.action-card:hover {
  transform: translateX(4px);
  border-color: rgba(85,168,255,.20);
  background: rgba(12,30,50,.72);
}
.action-number {
  flex: 0 0 auto;
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  border: 1px solid rgba(85,168,255,.18);
  background: rgba(85,168,255,.09);
  color: #8bc6ff;
  font-size: .67rem;
  font-weight: 920;
}

[data-testid="stVerticalBlockBorderWrapper"] {
  border-color: rgba(148,163,184,.10) !important;
  border-radius: 17px !important;
  background: rgba(8,22,37,.42) !important;
}

.review-banner {
  margin-top: 1.4rem;
  padding: .92rem 1rem;
  border: 1px solid rgba(85,168,255,.16);
  border-radius: 14px;
  background: linear-gradient(90deg, rgba(85,168,255,.045), rgba(85,168,255,.10), rgba(85,168,255,.045));
  color: #a8cff5;
  text-align: center;
  font-size: .7rem;
  font-weight: 900;
  letter-spacing: .11em;
  text-transform: uppercase;
}

/* ---------------------------------------------------------
   DEVELOPER SYSTEM BRIEFING
--------------------------------------------------------- */
.briefing-shell {
  position: relative;
  overflow: hidden;
  margin-top: 1.35rem;
  padding: 3.15rem 3.25rem 2.35rem;
  border: 1px solid rgba(112,230,255,.13);
  border-radius: 28px;
  background:
    radial-gradient(circle at 50% -14%, rgba(67,145,255,.16), transparent 34%),
    radial-gradient(circle at 100% 100%, rgba(88,229,165,.055), transparent 28%),
    linear-gradient(145deg, rgba(9,24,41,.96), rgba(4,13,24,.96));
  box-shadow: 0 38px 110px rgba(0,0,0,.25);
  isolation: isolate;
}

.briefing-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -2;
  opacity: .16;
  background-image:
    linear-gradient(rgba(111,167,216,.18) 1px, transparent 1px),
    linear-gradient(90deg, rgba(111,167,216,.18) 1px, transparent 1px);
  background-size: 36px 36px;
  mask-image: linear-gradient(to bottom, #000 0%, rgba(0,0,0,.5) 68%, transparent 100%);
}

.briefing-shell::after {
  content: "";
  position: absolute;
  z-index: -1;
  width: 620px;
  height: 620px;
  border-radius: 50%;
  left: 50%;
  top: 42%;
  transform: translate(-50%, -50%);
  border: 1px solid rgba(85,168,255,.06);
  box-shadow:
    0 0 0 95px rgba(85,168,255,.018),
    0 0 0 190px rgba(85,168,255,.012);
  pointer-events: none;
}

.briefing-kicker {
  text-align: center;
  color: #76b9ff;
  font-size: .67rem;
  font-weight: 950;
  letter-spacing: .2em;
  text-transform: uppercase;
}

.briefing-title {
  max-width: 920px;
  margin: .72rem auto 0;
  text-align: center;
  color: #f8fbff;
  font-size: clamp(2.35rem, 4vw, 4.1rem);
  line-height: 1.02;
  font-weight: 950;
  letter-spacing: -.062em;
}

.briefing-title span {
  background: linear-gradient(90deg, #83c0ff, #79e4ff);
  -webkit-background-clip: text;
  color: transparent;
}

.briefing-copy {
  max-width: 820px;
  margin: 1rem auto 0;
  text-align: center;
  color: #8ea2ba;
  font-size: .94rem;
  line-height: 1.72;
}

.briefing-legend {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: .55rem;
  margin-top: 1.35rem;
}

.briefing-chip {
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  padding: .38rem .62rem;
  border: 1px solid rgba(148,163,184,.12);
  border-radius: 999px;
  background: rgba(255,255,255,.022);
  color: #8ea3bb;
  font-size: .64rem;
  font-weight: 820;
  letter-spacing: .035em;
}

.briefing-chip::before {
  content: "";
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #67c9ff;
  box-shadow: 0 0 12px rgba(103,201,255,.45);
}

.architecture-map {
  max-width: 1160px;
  margin: 2.7rem auto 0;
}

.arch-step {
  position: relative;
  min-width: 0;
  padding: .92rem 1rem;
  border: 1px solid rgba(148,163,184,.12);
  border-radius: 16px;
  background: linear-gradient(145deg, rgba(13,31,51,.92), rgba(7,19,33,.82));
  box-shadow: inset 0 1px 0 rgba(255,255,255,.025), 0 18px 44px rgba(0,0,0,.12);
}

.arch-step.primary {
  border-color: rgba(85,168,255,.25);
  background: linear-gradient(145deg, rgba(17,42,70,.96), rgba(8,24,42,.9));
}

.arch-step.assessor {
  border-color: rgba(112,230,255,.24);
  background: linear-gradient(145deg, rgba(14,42,64,.96), rgba(7,25,41,.92));
}

.arch-step.human {
  border-color: rgba(88,229,165,.22);
  background: linear-gradient(145deg, rgba(12,42,38,.62), rgba(7,25,30,.84));
}

.arch-eyebrow {
  color: #607b98;
  font-size: .56rem;
  font-weight: 950;
  letter-spacing: .16em;
  text-transform: uppercase;
}

.arch-name {
  margin-top: .32rem;
  color: #edf6ff;
  font-size: .92rem;
  font-weight: 900;
  letter-spacing: -.018em;
}

.arch-desc {
  margin-top: .3rem;
  color: #7f94ad;
  font-size: .66rem;
  line-height: 1.48;
}

.arch-node-dot {
  position: absolute;
  right: 12px;
  top: 12px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #62cfff;
  box-shadow: 0 0 0 5px rgba(98,207,255,.055), 0 0 18px rgba(98,207,255,.42);
  animation: archPulse 2.1s ease-in-out infinite;
}

.arch-step.human .arch-node-dot {
  background: #58e5a5;
  box-shadow: 0 0 0 5px rgba(88,229,165,.055), 0 0 18px rgba(88,229,165,.38);
}

@keyframes archPulse {
  0%,100% { opacity: .58; transform: scale(.86); }
  50% { opacity: 1; transform: scale(1.16); }
}

.arch-top {
  display: grid;
  grid-template-columns: minmax(180px, .8fr) 64px minmax(220px, 1fr) 64px minmax(220px, 1fr);
  align-items: center;
  gap: .4rem;
}

.arch-entry {
  width: min(410px, 100%);
  margin: 0 auto;
  text-align: center;
}

.arch-down {
  position: relative;
  width: 2px;
  height: 34px;
  margin: .35rem auto .25rem;
  background: linear-gradient(to bottom, rgba(112,230,255,.7), rgba(85,168,255,.12));
}

.arch-down::after {
  content: "";
  position: absolute;
  left: 50%;
  bottom: -1px;
  width: 7px;
  height: 7px;
  border-right: 2px solid #70dfff;
  border-bottom: 2px solid #70dfff;
  transform: translateX(-50%) rotate(45deg);
}

.arch-parallel {
  position: relative;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  max-width: 790px;
  margin: 0 auto;
}

.arch-parallel::before {
  content: "";
  position: absolute;
  left: 16%;
  right: 16%;
  top: -17px;
  height: 1px;
  background: linear-gradient(90deg, rgba(112,230,255,.12), rgba(112,230,255,.45), rgba(112,230,255,.12));
}

.arch-parallel .arch-step::before {
  content: "";
  position: absolute;
  left: 50%;
  top: -17px;
  width: 1px;
  height: 17px;
  background: rgba(112,230,255,.28);
}

.arch-arrow {
  position: relative;
  height: 2px;
  background: linear-gradient(90deg, rgba(85,168,255,.16), rgba(112,230,255,.7));
  overflow: visible;
}

.arch-arrow::before {
  content: "";
  position: absolute;
  width: 34%;
  height: 100%;
  left: -34%;
  background: linear-gradient(90deg, transparent, #8bdfff, transparent);
  filter: drop-shadow(0 0 5px rgba(112,230,255,.58));
  animation: dataMove 2.5s linear infinite;
}

.arch-arrow::after {
  content: "";
  position: absolute;
  right: -1px;
  top: 50%;
  width: 7px;
  height: 7px;
  border-top: 2px solid #70dfff;
  border-right: 2px solid #70dfff;
  transform: translateY(-50%) rotate(45deg);
}

@keyframes dataMove {
  from { left: -34%; opacity: 0; }
  12% { opacity: 1; }
  88% { opacity: 1; }
  to { left: 100%; opacity: 0; }
}

.arch-split-label {
  margin: 1.2rem 0 .55rem;
  text-align: center;
  color: #58718d;
  font-size: .57rem;
  font-weight: 930;
  letter-spacing: .16em;
  text-transform: uppercase;
}

.arch-tool-zone {
  position: relative;
  margin-top: 2rem;
  padding-top: 1.15rem;
}

.arch-tool-zone::before {
  content: "";
  position: absolute;
  top: 0;
  left: 10%;
  right: 10%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(85,168,255,.25), rgba(112,230,255,.52), rgba(85,168,255,.25), transparent);
}

.arch-tool-zone::after {
  content: "";
  position: absolute;
  top: -20px;
  left: 50%;
  width: 1px;
  height: 20px;
  background: rgba(112,230,255,.35);
}

.arch-tool-grid {
  display: grid;
  grid-template-columns: 1.08fr repeat(4, minmax(0, 1fr));
  gap: .72rem;
}

.arch-tool {
  position: relative;
  min-width: 0;
  padding: .78rem .82rem;
  border: 1px solid rgba(148,163,184,.105);
  border-radius: 13px;
  background: rgba(7,20,34,.72);
}

.arch-tool.reported {
  border-color: rgba(112,230,255,.17);
  background: rgba(10,31,47,.76);
}

.arch-tool-label {
  color: #536e8a;
  font-size: .52rem;
  font-weight: 950;
  letter-spacing: .14em;
  text-transform: uppercase;
}

.arch-tool-name {
  margin-top: .28rem;
  color: #dcecff;
  font-size: .78rem;
  font-weight: 880;
}

.arch-tool-detail {
  margin-top: .24rem;
  color: #71859d;
  font-size: .6rem;
  line-height: 1.4;
}

.arch-merge {
  position: relative;
  display: flex;
  justify-content: center;
  margin-top: 1.45rem;
  padding-top: 1.45rem;
}

.arch-merge::before {
  content: "";
  position: absolute;
  left: 10%;
  right: 10%;
  top: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(112,230,255,.22), rgba(112,230,255,.55), rgba(112,230,255,.22), transparent);
}

.arch-merge::after {
  content: "";
  position: absolute;
  left: 50%;
  top: 0;
  width: 1px;
  height: 1.45rem;
  background: linear-gradient(to bottom, rgba(112,230,255,.5), rgba(112,230,255,.14));
}

.arch-evidence {
  width: min(410px, 100%);
  text-align: center;
}

.arch-bypass {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: .58rem;
  margin: .85rem auto;
  color: #607993;
  font-size: .61rem;
  font-weight: 780;
}

.arch-bypass::before,
.arch-bypass::after {
  content: "";
  width: 74px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(148,163,184,.24));
}

.arch-bypass::after { transform: rotate(180deg); }

.arch-bottom {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) 64px minmax(220px, 1fr) 64px minmax(190px, .85fr);
  align-items: center;
  gap: .4rem;
}

.arch-output-points {
  margin-top: .36rem;
  color: #7790aa;
  font-size: .61rem;
  line-height: 1.46;
}

.briefing-principle {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 1rem;
  max-width: 1160px;
  margin: 2rem auto 0;
  padding: .92rem 1rem;
  border: 1px solid rgba(88,229,165,.13);
  border-radius: 14px;
  background: linear-gradient(90deg, rgba(88,229,165,.035), rgba(7,21,35,.58));
}

.briefing-principle-title {
  color: #cfeee0;
  font-size: .78rem;
  font-weight: 900;
}

.briefing-principle-copy {
  margin-top: .2rem;
  color: #748c9f;
  font-size: .66rem;
  line-height: 1.5;
}

.briefing-principle-tag {
  padding: .38rem .6rem;
  border: 1px solid rgba(88,229,165,.16);
  border-radius: 999px;
  color: #81ddb0;
  font-size: .57rem;
  font-weight: 930;
  letter-spacing: .12em;
  text-transform: uppercase;
  white-space: nowrap;
}

.briefing-action-copy {
  margin: 1.3rem 0 .75rem;
  text-align: center;
  color: #617991;
  font-size: .7rem;
}

[data-testid="stMainBlockContainer"] .stButton button[kind="primary"] {
  min-height: 3.15rem;
  border: 1px solid rgba(88,229,165,.26) !important;
  border-radius: 13px !important;
  background: linear-gradient(100deg, #55dda0, #7af1bd) !important;
  color: #05150f !important;
  font-weight: 950 !important;
  letter-spacing: -.01em;
  box-shadow: 0 15px 38px rgba(55,205,141,.16);
  transition: transform .18s ease, box-shadow .18s ease, filter .18s ease;
}

[data-testid="stMainBlockContainer"] .stButton button[kind="primary"] p,
[data-testid="stMainBlockContainer"] .stButton button[kind="primary"] span {
  color: #05150f !important;
  font-weight: 950 !important;
  opacity: 1 !important;
}

[data-testid="stMainBlockContainer"] .stButton button[kind="primary"]:hover {
  transform: translateY(-2px);
  filter: brightness(1.035);
  box-shadow: 0 19px 46px rgba(55,205,141,.23);
}

.dev-architecture-note {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin: .5rem 0 1rem;
  padding: .72rem .82rem;
  border: 1px solid rgba(85,168,255,.11);
  border-radius: 12px;
  background: rgba(85,168,255,.035);
  color: #738ba3;
  font-size: .67rem;
  line-height: 1.45;
}

@media (max-width: 980px) {
  .briefing-shell { padding: 2.4rem 1.4rem 1.8rem; }
  .arch-top,
  .arch-bottom {
    grid-template-columns: 1fr;
    gap: .65rem;
  }
  .arch-arrow {
    width: 2px;
    height: 30px;
    margin: 0 auto;
    background: linear-gradient(to bottom, rgba(85,168,255,.16), rgba(112,230,255,.7));
  }
  .arch-arrow::before { display: none; }
  .arch-arrow::after {
    right: auto;
    left: 50%;
    top: auto;
    bottom: -1px;
    transform: translateX(-50%) rotate(135deg);
  }
  .arch-tool-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .arch-tool.reported { grid-column: 1 / -1; }
  .briefing-principle { grid-template-columns: 1fr; }
  .briefing-principle-tag { width: max-content; }
}

@media (max-width: 620px) {
  .briefing-title { font-size: 2.35rem; }
  .arch-parallel { grid-template-columns: 1fr; }
  .arch-parallel::before,
  .arch-parallel .arch-step::before { display: none; }
  .arch-tool-grid { grid-template-columns: 1fr; }
  .arch-tool.reported { grid-column: auto; }
}

/* ---------------------------------------------------------
   DEVELOPER CONSOLE
--------------------------------------------------------- */
.dev-divider {
  height: 1px;
  margin: 2.2rem 0 1.8rem;
  background: linear-gradient(90deg, transparent, rgba(85,168,255,.18), transparent);
}

.dev-card {
  min-height: 142px;
  padding: .95rem 1rem;
  border-radius: 16px;
  border: 1px solid rgba(148,163,184,.11);
  background: rgba(8,21,36,.52);
}

.dev-card-title {
  color: #e6f1ff;
  font-size: .83rem;
  font-weight: 860;
}

.dev-status {
  display: inline-flex;
  margin-top: .55rem;
  padding: .28rem .52rem;
  border-radius: 999px;
  border: 1px solid rgba(88,229,165,.17);
  background: rgba(88,229,165,.055);
  color: #8ceabd;
  font-size: .61rem;
  font-weight: 900;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.dev-reason {
  margin-top: .57rem;
  color: #71869f;
  font-size: .7rem;
  line-height: 1.48;
}

[data-testid="stExpander"] {
  border: 1px solid rgba(148,163,184,.11);
  border-radius: 14px;
  background: rgba(7,20,34,.52);
}

[data-testid="stMetric"] {
  padding: 1rem;
  border: 1px solid rgba(148,163,184,.11);
  border-radius: 16px;
  background: rgba(8,22,37,.52);
}

@media (max-width: 1050px) {
  .landing-inner { grid-template-columns: 1fr; padding: 3rem 2.4rem; }
  .visual-stage { min-height: 340px; }
  .landing-title { font-size: 3.5rem; }
}
</style>
""")


# =========================================================
# HELPERS
# =========================================================

def ui(content: str) -> None:
    st.html(content)


def esc(value) -> str:
    return html.escape(str(value))


def pretty(value) -> str:
    if value is None:
        return "Unknown"
    text = str(value)
    if text.lower() == "unknown":
        return "Unknown"
    return html.escape(text.replace("_", " ").title())


def load_benchmark():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def display_incident_name(case):
    num = case["id"][1:].zfill(3)
    report = case["initial_report"]
    if len(report) > 46:
        report = report[:43] + "..."
    return f"INC-{num} — {report}"


def operator_id(incident_id):
    if incident_id.startswith("A") and incident_id[1:].isdigit():
        return "INC-" + incident_id[1:].zfill(3)
    return incident_id


def priority_css(priority):
    return {
        "LOW": "priority-low",
        "MEDIUM": "priority-medium",
        "HIGH": "priority-high",
        "CRITICAL": "priority-critical",
        "INSUFFICIENT_INFORMATION": "priority-insufficient",
    }.get(priority, "priority-insufficient")


def priority_text(priority):
    return priority.replace("_", " ")


def get_context(result):
    context = result["context"]

    traffic = (
        (context.get("traffic") or {}).get("data")
        or {}
    )

    weather = (
        (context.get("weather") or {}).get("data")
        or {}
    )

    details = (
        (context.get("incident_details") or {}).get("data")
        or {}
    )

    reported = (
        context.get("reported_context")
        or {}
    )

    sop = (
        context.get("sop")
        or {}
    )

    return traffic, weather, details, reported, sop


def section(kicker: str, title: str, copy: str = ""):
    copy_html = f'<div class="section-copy">{esc(copy)}</div>' if copy else ""
    ui(
        f'<div class="section-head">'
        f'<div class="section-kicker">{esc(kicker)}</div>'
        f'<div class="section-title">{esc(title)}</div>'
        f'{copy_html}'
        f'</div>'
    )


def flip_card(card_id, title, main, details, delay="", first_hint=False):
    detail_markup = "".join(f'<div class="flip-detail">{esc(d)}</div>' for d in details if d)
    hint_class = " first-hint" if first_hint else ""
    return f'''
      <input class="flip-toggle" type="checkbox" id="{esc(card_id)}">
      <label class="flip-card {delay}{hint_class}" for="{esc(card_id)}">
        <div class="flip-inner">
          <div class="flip-face flip-front">
            <div class="flip-title">{esc(title)}</div>
          </div>
          <div class="flip-face flip-back">
            <div class="flip-back-title">{esc(title)}</div>
            <div class="flip-main">{esc(main)}</div>
            {detail_markup}
          </div>
        </div>
      </label>
    '''


def render_developer_briefing():
    ui(r'''
    <div class="briefing-shell">
      <div class="briefing-kicker">Developer orientation · System architecture</div>
      <div class="briefing-title">Understand the system <span>before you inspect it.</span></div>
      <div class="briefing-copy">
        RoadOps AI separates incident intake, planning, contextual retrieval, policy grounding,
        and final assessment into distinct stages. Follow the evidence path first, then enter the
        developer console to inspect the exact planner decisions, tool outputs, structured context,
        and frozen evaluation results behind the interface.
      </div>

      <div class="briefing-legend">
        <span class="briefing-chip">Structured outputs</span>
        <span class="briefing-chip">Tool-orchestrated</span>
        <span class="briefing-chip">Policy-grounded</span>
        <span class="briefing-chip">Human-in-the-loop</span>
      </div>

      <div class="architecture-map">
        <div class="arch-step primary arch-entry">
          <span class="arch-node-dot"></span>
          <div class="arch-eyebrow">01 · Input</div>
          <div class="arch-name">Incident Report</div>
          <div class="arch-desc">The operator's original report remains preserved as first-party incident evidence.</div>
        </div>

        <div class="arch-down"></div>
        <div class="arch-split-label">The same report starts two parallel paths</div>

        <div class="arch-parallel">
          <div class="arch-step">
            <span class="arch-node-dot"></span>
            <div class="arch-eyebrow">02A · Intake path</div>
            <div class="arch-name">Reported Context Extraction</div>
            <div class="arch-desc">Explicitly stated roadway, lane, traffic, weather, visibility, and duration facts are structured without inventing missing fields.</div>
          </div>

          <div class="arch-step primary">
            <span class="arch-node-dot"></span>
            <div class="arch-eyebrow">02B · Agent path</div>
            <div class="arch-name">Agent Planner</div>
            <div class="arch-desc">The planner reads the original report and decides which contextual sources could meaningfully improve the assessment.</div>
          </div>
        </div>

        <div class="arch-split-label">Structured and retrieved evidence</div>

        <div class="arch-tool-zone">
          <div class="arch-tool-grid">
            <div class="arch-tool reported">
              <div class="arch-tool-label">Extracted context</div>
              <div class="arch-tool-name">Reported Context</div>
              <div class="arch-tool-detail">Facts explicitly present in the initial incident report.</div>
            </div>
            <div class="arch-tool">
              <div class="arch-tool-label">Tool</div>
              <div class="arch-tool-name">Traffic Context</div>
              <div class="arch-tool-detail">Traffic level, queue state, observed speed, normal speed.</div>
            </div>
            <div class="arch-tool">
              <div class="arch-tool-label">Tool</div>
              <div class="arch-tool-name">Weather Context</div>
              <div class="arch-tool-detail">Weather and visibility conditions when available.</div>
            </div>
            <div class="arch-tool">
              <div class="arch-tool-label">Tool</div>
              <div class="arch-tool-name">Incident Details</div>
              <div class="arch-tool-detail">Blocked lanes, roadway position, incident type, duration.</div>
            </div>
            <div class="arch-tool">
              <div class="arch-tool-label">Tool</div>
              <div class="arch-tool-name">SOP / Policy</div>
              <div class="arch-tool-detail">Priority framework plus incident-relevant operating guidance.</div>
            </div>
          </div>
        </div>

        <div class="arch-merge">
          <div class="arch-step arch-evidence primary">
            <span class="arch-node-dot"></span>
            <div class="arch-eyebrow">03 · Evidence merge</div>
            <div class="arch-name">Gathered Context</div>
            <div class="arch-desc">Operator-reported facts and available external tool evidence are retained with their source semantics.</div>
          </div>
        </div>

        <div class="arch-bypass">Original report is also passed directly to the assessor</div>

        <div class="arch-bottom">
          <div class="arch-step assessor">
            <span class="arch-node-dot"></span>
            <div class="arch-eyebrow">04 · Reasoning</div>
            <div class="arch-name">Assessment Agent</div>
            <div class="arch-desc">Uses the original report, gathered evidence, and retrieved policy. Missing information lowers confidence but is never silently invented.</div>
          </div>

          <div class="arch-arrow"></div>

          <div class="arch-step primary">
            <span class="arch-node-dot"></span>
            <div class="arch-eyebrow">05 · Structured output</div>
            <div class="arch-name">Reviewable Assessment</div>
            <div class="arch-output-points">Priority · Confidence · Identified factors · Recommended actions · Missing information · Reasoning summary</div>
          </div>

          <div class="arch-arrow"></div>

          <div class="arch-step human">
            <span class="arch-node-dot"></span>
            <div class="arch-eyebrow">06 · Authority</div>
            <div class="arch-name">Human Review</div>
            <div class="arch-desc">RoadOps supports operational decisions; it does not autonomously dispatch responders or control roadway infrastructure.</div>
          </div>
        </div>
      </div>

      <div class="briefing-principle">
        <div>
          <div class="briefing-principle-title">Decision support by design</div>
          <div class="briefing-principle-copy">The interface can stay simple because the complexity is handled inside a traceable pipeline: evidence is acquired, structured, grounded, assessed, and surfaced for human review.</div>
        </div>
        <div class="briefing-principle-tag">Human authority retained</div>
      </div>
    </div>
    ''')


# =========================================================
# SESSION STATE / DATA
# =========================================================

for key, default in {
    "roadops_result": None,
    "roadops_incident_id": None,
    "roadops_report": None,
    "developer_briefing_seen": False,
    "developer_enter_animation": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

benchmark = load_benchmark()
demo_cases = {
    item["id"]: item
    for item in benchmark
    if isinstance(item, dict) and item.get("id", "").startswith("A")
}


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    ui('''
    <div class="sidebar-shell">
      <div class="side-brand">
        <div class="side-logo">
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M32 8L20 43H44L32 8Z" fill="#FF8A3D"/>
            <path d="M25 28H39" stroke="#F8FAFC" stroke-width="5" stroke-linecap="round"/>
            <path d="M21 40H43" stroke="#F8FAFC" stroke-width="5" stroke-linecap="round"/>
            <rect x="15" y="46" width="34" height="7" rx="3.5" fill="#FF8A3D"/>
          </svg>
        </div>
        <div>
          <div class="side-name">RoadOps AI</div>
          <div class="side-sub">Roadway incident decision support</div>
        </div>
      </div>
    </div>
    ''')

    st.divider()
    ui('<div class="side-section">Experience</div><div class="side-helper">Choose the view that matches how you want to use RoadOps.</div>')

    try:
        view_mode = st.segmented_control(
            "Interface mode",
            options=["Operator", "Developer"],
            default="Operator",
            label_visibility="collapsed",
        )
    except Exception:
        view_mode = st.radio(
            "Interface mode",
            ["Operator", "Developer"],
            horizontal=True,
            label_visibility="collapsed",
        )

    # Show the full-screen transition only on an actual mode change.
    if "last_view_mode" not in st.session_state:
        st.session_state.last_view_mode = view_mode
    mode_changed = st.session_state.last_view_mode != view_mode
    if mode_changed:
        st.session_state.last_view_mode = view_mode

    st.divider()
    ui('<div class="side-section">Incident</div><div class="side-helper">Start from a reproducible demo case or enter your own initial report.</div>')

    input_mode = st.radio(
        "Incident source",
        ["Benchmark", "Custom"],
        horizontal=True,
        label_visibility="visible",
    )

    if input_mode == "Benchmark":
        incident_id = st.selectbox(
            "Choose incident",
            options=list(demo_cases.keys()),
            format_func=lambda x: display_incident_name(demo_cases[x]),
        )
        report = st.text_area(
            "Initial report",
            value=demo_cases[incident_id]["initial_report"],
            height=120,
        )
    else:
        incident_id = st.text_input("Incident ID", value="DEMO-001")
        report = st.text_area(
            "Initial report",
            placeholder="Describe what was reported: roadway, direction, location, obstruction, and any known conditions.",
            height=120,
        )
        st.caption("Custom incident IDs may not have local synthetic context available to the POC tools.")

    run_clicked = st.button("Analyze Incident", type="primary", use_container_width=True)

    if st.session_state.roadops_result:
        if st.button("Clear current assessment", use_container_width=True):
            st.session_state.roadops_result = None
            st.session_state.roadops_incident_id = None
            st.session_state.roadops_report = None
            st.rerun()

    st.divider()
    ui('''
    <div style="color:#5f7590;font-size:.67rem;line-height:1.55;">
      Proof of concept<br>
      Reproducible synthetic operational context
    </div>
    ''')


# =========================================================
# MODE SWITCH ANIMATION
# =========================================================

show_developer_briefing = (
    view_mode == "Developer"
    and not st.session_state.developer_briefing_seen
)

if st.session_state.developer_enter_animation:
    ui('<div class="mode-wipe"><div class="mode-wipe-label">Entering developer console</div></div>')
    st.session_state.developer_enter_animation = False
elif mode_changed:
    if view_mode == "Operator":
        label = "Operator experience"
    elif show_developer_briefing:
        label = "System architecture"
    else:
        label = "Developer console"
    ui(f'<div class="mode-wipe"><div class="mode-wipe-label">{esc(label)}</div></div>')


# =========================================================
# TOP PRODUCT BAR
# =========================================================

if view_mode == "Operator":
    mode_label = "Operator Experience"
elif show_developer_briefing:
    mode_label = "System Briefing"
else:
    mode_label = "Developer Console"

ui(f'''
<div class="product-bar">
  <div class="product-lockup">
    <div class="product-mark">
      <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M32 7L19 44H45L32 7Z" fill="#FF8A3D"/>
        <path d="M24 27.5H40" stroke="#F8FAFC" stroke-width="5" stroke-linecap="round"/>
        <path d="M20.5 40H43.5" stroke="#F8FAFC" stroke-width="5" stroke-linecap="round"/>
        <rect x="14" y="47" width="36" height="8" rx="4" fill="#FF8A3D"/>
      </svg>
    </div>
    <div>
      <div class="product-name">RoadOps AI</div>
      <div class="product-tagline">Clearer incident decisions from the information already around you</div>
    </div>
  </div>
  <div class="ready-pill"><span class="ready-dot"></span> Ready</div>
</div>
<div class="mode-pill">{esc(mode_label)}</div>
''')


# =========================================================
# DEVELOPER BRIEFING GATE
# =========================================================

if show_developer_briefing:
    render_developer_briefing()
    ui('<div class="briefing-action-copy">Continue when the evidence path and system boundaries are clear.</div>')

    left_space, action_col, right_space = st.columns([1.15, .9, 1.15])
    with action_col:
        if st.button(
            "I UNDERSTAND — ENTER DEVELOPER MODE →",
            key="developer_briefing_continue",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.developer_briefing_seen = True
            st.session_state.developer_enter_animation = True
            st.rerun()

    st.stop()


# =========================================================
# RUN ASSESSMENT
# =========================================================

if run_clicked:
    if not report.strip():
        st.error("Enter an incident report before running the assessment.")
        st.stop()

    with st.status("Building the incident picture...", expanded=True) as status:
        st.write("Identifying the context that could change the assessment")
        st.write("Retrieving available roadway, traffic, weather, and policy context")
        st.write("Producing a reviewable priority assessment and recommended next steps")

        result = run_roadops(incident_id=incident_id, report=report)
        st.session_state.roadops_result = result
        st.session_state.roadops_incident_id = incident_id
        st.session_state.roadops_report = report

        status.update(
            label="Assessment ready for review",
            state="complete",
            expanded=False,
        )


# =========================================================
# OPENING EXPERIENCE
# =========================================================

if not st.session_state.roadops_result:
    ui('''
    <div class="landing">
      <div class="grid-field"></div>
      <div class="landing-inner">
        <div>
          <div class="landing-kicker">Incident decision support</div>
          <div class="landing-title">From incident report <span class="accent">to informed action.</span></div>
          <div class="landing-copy">
            RoadOps AI brings together <strong>traffic conditions, weather, roadway impact, incident details, and operating guidance</strong> into one clear, reviewable assessment. Operators get the information that matters most without digging through separate sources.
          </div>
          <div class="landing-points">
            <span class="landing-point">One incident picture</span>
            <span class="landing-point">Clear priority</span>
            <span class="landing-point">Recommended next steps</span>
            <span class="landing-point">Human review retained</span>
          </div>
          <div class="landing-cta"><b>To begin:</b> choose an incident in the control panel and select Analyze Incident.</div>
        </div>

        <div class="visual-stage">
          <div class="radar-ring r1"></div>
          <div class="radar-ring r2"></div>
          <div class="radar-ring r3"></div>
          <div class="radar-sweep"></div>
          <div class="road-perspective">
            <div class="road-surface"></div>
            <span class="signal-node n1"></span>
            <span class="signal-node n2"></span>
            <span class="signal-node n3"></span>
          </div>
          <div class="visual-label">Waiting for incident input</div>
        </div>
      </div>
    </div>
    ''')
    st.stop()


# =========================================================
# CURRENT RESULT
# =========================================================

result = st.session_state.roadops_result
current_id = st.session_state.roadops_incident_id
current_report = st.session_state.roadops_report
plan = result["tool_plan"]
assessment = result["assessment"]
traffic, weather, details, reported, sop = get_context(result)
sop_sections = sop.get("guidance", []) if sop else []
display_id = operator_id(current_id)

# =========================================================
# MERGE EXTERNAL TOOL DATA + INITIAL REPORT DATA
# External tool data takes priority when available.
# =========================================================

# TRAFFIC
external_traffic_level = traffic.get("traffic_level")
reported_traffic_level = reported.get("traffic_level")

traffic_level = pretty(
    external_traffic_level or reported_traffic_level
)

traffic_source = (
    "Traffic data source"
    if external_traffic_level is not None
    else (
        "Initial incident report"
        if reported_traffic_level is not None
        else "No traffic data available"
    )
)

# QUEUE
external_queue = traffic.get("queue_status")
reported_queue = reported.get("queue_status")

queue = pretty(
    external_queue or reported_queue
)

# SPEED
avg_speed = traffic.get("average_speed_mph")
normal_speed = traffic.get("normal_speed_mph")


# WEATHER
external_weather = (
    weather.get("condition")
    or weather.get("weather")
)

reported_weather = reported.get("weather")

weather_condition = (
    external_weather or reported_weather
)

weather_source = (
    "Weather data source"
    if external_weather is not None
    else (
        "Initial incident report"
        if reported_weather is not None
        else "No weather data available"
    )
)


# VISIBILITY
external_visibility = weather.get("visibility")
reported_visibility = reported.get("visibility")

visibility = pretty(
    external_visibility or reported_visibility
)


# ROADWAY / LANE IMPACT
external_lanes = details.get("blocked_active_lanes")
reported_lanes = reported.get("blocked_active_lanes")

lanes = (
    external_lanes
    if external_lanes is not None
    else reported_lanes
)

lane_source = (
    "Incident data source"
    if external_lanes is not None
    else (
        "Initial incident report"
        if reported_lanes is not None
        else "Lane impact not available"
    )
)

raw_location_status = (
    details.get("location_status")
    or reported.get("lane_impact")
)

location_status = pretty(raw_location_status)

roadway_status = pretty(
    details.get("roadway_status")
    or reported.get("roadway")
)


# DURATION
external_duration = details.get("duration_minutes")
reported_duration = reported.get("duration_minutes")

duration = (
    external_duration
    if external_duration is not None
    else reported_duration
)

duration_source = (
    "Incident data source"
    if external_duration is not None
    else (
        "Initial incident report"
        if reported_duration is not None
        else "Duration not available"
    )
)


# =========================================================
# OPERATOR EXPERIENCE
# =========================================================

section(
    "Current incident",
    "Situation at a glance",
    "The initial report is combined with available operational context before RoadOps recommends a priority.",
)

hero_left, hero_right = st.columns([1.62, .78])

with hero_left:
    ui(f'''
    <div class="incident-hero">
      <div class="incident-id">{esc(display_id)}</div>
      <div class="incident-report">{esc(current_report)}</div>
    </div>
    ''')

with hero_right:
    conf = max(0.0, min(1.0, float(assessment.confidence)))
    ui(f'''
    <div class="priority-panel">
      <div class="priority-kicker">Recommended priority</div>
      <div class="priority-value {priority_css(assessment.priority)}">{esc(priority_text(assessment.priority))}</div>
      <div class="conf-label">Confidence</div>
      <div class="conf-big">{conf*100:.0f}%</div>
      <div class="conf-track"><div class="conf-fill" style="width:{conf*100:.0f}%"></div></div>
    </div>
    ''')

section(
    "Live incident picture",
    "Explore the signals behind the assessment",
    "The front stays intentionally simple. Hover or select a tile to inspect the available context.",
)
ui('<div class="context-onboarding">Select a signal to flip the card and inspect the underlying context</div>')

context_cols = st.columns(5)

traffic_details = [
    f"Source: {traffic_source}",
    f"Queue: {queue}",
    (
        f"Observed speed: {avg_speed} mph"
        if avg_speed is not None
        else "Observed speed: Unknown"
    ),
]

if normal_speed is not None:
    traffic_details.append(
        f"Typical speed: {normal_speed} mph"
    )


cards = [
    flip_card(
        "flip-traffic",
        "Traffic",
        traffic_level,
        traffic_details,
        first_hint=True,
    ),

    flip_card(
        "flip-weather",
        "Weather",
        pretty(weather_condition),
        [
            f"Source: {weather_source}",
            f"Visibility: {visibility}",
        ],
        delay="delay-1",
    ),

    flip_card(
        "flip-roadway",
        "Roadway",
        (
            f"{lanes} blocked lane"
            if lanes == 1
            else (
                f"{lanes} blocked lanes"
                if lanes is not None
                else location_status
            )
        ),
        [
            f"Source: {lane_source}",
            (
                f"Position: {location_status}"
                if location_status != "Unknown"
                else "Exact lane position unknown"
            ),
            (
                f"Roadway: {roadway_status}"
                if roadway_status != "Unknown"
                else ""
            ),
        ],
        delay="delay-2",
    ),

    flip_card(
        "flip-duration",
        "Duration",
        (
            f"{duration} min"
            if duration is not None
            else "Unknown"
        ),
        [
            f"Source: {duration_source}",
        ],
        delay="delay-3",
    ),

    flip_card(
        "flip-guidance",
        "Guidance",
        (
            "Policy grounded"
            if sop_sections
            else "Unavailable"
        ),
        [
            (
                f"{len(sop_sections)} relevant section"
                f"{'s' if len(sop_sections) != 1 else ''} retrieved"
            ),
            "Final recommendation remains subject to human review",
        ],
        delay="delay-4",
    ),
]

for col, markup in zip(context_cols, cards):
    with col:
        ui(markup)

next_left, next_right = st.columns([1.08, .92])

with next_left:
    section("Operator actions", "Recommended next steps")
    for i, action in enumerate(assessment.recommended_actions, start=1):
        ui(f'<div class="action-card"><div class="action-number">{i}</div><div>{esc(action)}</div></div>')

with next_right:
    section("Why this priority", "What drove the recommendation")
    ui(f'''
    <div class="operator-summary">
      <div class="operator-summary-title">Assessment summary</div>
      <div class="operator-summary-text">{esc(assessment.reasoning_summary)}</div>
    </div>
    ''')

factor_col, missing_col = st.columns(2)

with factor_col:
    section("Evidence", "What RoadOps considered")
    with st.container(border=True):
        for factor in assessment.identified_factors:
            st.markdown(f"- {factor}")

with missing_col:
    section("Uncertainty", "What still needs confirmation")
    with st.container(border=True):
        if assessment.missing_information:
            for item in assessment.missing_information:
                st.markdown(f"- {item}")
        else:
            st.write("No major information gaps were identified from the available context.")

ui('<div class="review-banner">Human review required · Decision support only · No autonomous roadway control or dispatch</div>')


# =========================================================
# DEVELOPER MODE
# =========================================================

if view_mode == "Developer":
    ui('<div class="dev-divider"></div>')
    section(
        "Developer console",
        "Open the hood",
        "Inspect planner decisions, tool outputs, retrieved policy context, structured model output, and frozen evaluation results.",
    )

    ui(
        '<div class="dev-architecture-note">'
        '<span>The developer briefing explains the evidence path and system boundaries shown by this console.</span>'
        '<span>Architecture available on demand</span>'
        '</div>'
    )

    arch_button_col, _ = st.columns([.34, 1.66])
    with arch_button_col:
        if st.button("Review system architecture", key="review_system_architecture"):
            st.session_state.developer_briefing_seen = False
            st.rerun()

    tool_data = [
        ("Traffic Tool", plan.use_traffic, plan.traffic_reason),
        ("Weather Tool", plan.use_weather, plan.weather_reason),
        ("Incident Details", plan.use_incident_details, plan.incident_details_reason),
        ("SOP Retrieval", plan.use_sop, plan.sop_reason),
    ]

    dev_cols = st.columns(4)
    for col, (tool_name, used, reason) in zip(dev_cols, tool_data):
        with col:
            status_text = "Selected" if used else "Skipped"
            ui(f'''
            <div class="dev-card">
              <div class="dev-card-title">{esc(tool_name)}</div>
              <div class="dev-status">{esc(status_text)}</div>
              <div class="dev-reason">{esc(reason or 'No planner reason was returned.')}</div>
            </div>
            ''')

    execution_tab, data_tab, policy_tab, evaluation_tab = st.tabs(
        ["Execution", "Tool Data", "Policy", "Evaluation"]
    )

    with execution_tab:
        with st.expander("Planner decision object", expanded=True):
            st.json(plan.model_dump())
        with st.expander("Structured Pydantic assessment"):
            st.json(assessment.model_dump())
        with st.expander("Full raw RoadOps output"):
            st.json({
                "tool_plan": plan.model_dump(),
                "context": result["context"],
                "assessment": assessment.model_dump(),
            })

    with data_tab:
        with st.expander("Traffic tool output", expanded=True):
            st.json(result["context"].get("traffic"))
        with st.expander("Weather tool output"):
            st.json(result["context"].get("weather"))
        with st.expander("Incident Details tool output"):
            st.json(result["context"].get("incident_details"))

    with policy_tab:
        if sop_sections:
            for index, sop_section in enumerate(sop_sections, start=1):
                with st.expander(f"Retrieved policy section {index}", expanded=(index == 1)):
                    st.markdown(sop_section)
        else:
            st.info("No SOP guidance was retrieved for this run.")

    with evaluation_tab:
        section(
            "Frozen holdout",
            "Evaluation performance",
            "A5–A24 were frozen before the final RoadOps execution. These figures are preserved evaluation results, not live calculations from the selected incident.",
        )
        e1, e2, e3, e4 = st.columns(4)
        e1.metric("Priority Accuracy", "95.0%", "+90.0 pp")
        e2.metric("Factor Recall", "92.2%", "+69.0 pp")
        e3.metric("Guidance Coverage", "81.7%", "+53.4 pp")
        e4.metric("Prohibited Matches", "0")
        st.caption("RoadOps: 19/20 correct priorities · Baseline: 1/20 · Same underlying LLM used for both systems")

        with st.expander("Evaluation notes and limitations"):
            st.markdown("""
- The A5–A24 holdout set was frozen before final RoadOps evaluation.
- A15 was retained as the single RoadOps priority miss.
- The planner selected all four tools on all 20 holdout cases, indicating a completeness bias rather than optimized tool efficiency.
- Synthetic tool data is used for reproducibility.
- Prohibited-match scoring is deterministic and does not prove universal absence of hallucinations.
            """)
