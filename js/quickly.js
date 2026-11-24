/* Quickly: unscramble as many words as you can in 60 seconds. Daily set or unlimited. Nothing saved mid-game. */
(() => {
const SECS = 60, RING = 2 * Math.PI * 28;
const { $, store, openModal, X, dayIndex, countdown, setupAds } = Common;
let Q, W, KEY = {}, G, timer = null;
const today = () => dayIndex(Q.start, 800);
const sortKey = w => [...w].sort().join("");
function seeded(n){ let x = n * 9301 + 49297; return () => (x = (x * 9301 + 49297) % 233280) / 233280; }
function scramble(w, rnd){
  let s = w;
  for (let k = 0; k < 20 && (s === w || KEY[sortKey(w)].includes(s)); k++){ const a = [...w]; for (let i = a.length - 1; i > 0; i--){ const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } s = a.join(""); }
  return s;
}
function startScreen(){
  stopTimer();
  const st = store.get("q:stats", {best: 0, bestDaily: 0, lastDay: -1, streak: 0, last: -2});
  $("game").innerHTML = `<div class="card start">
    <div class="logo-big">Quickly</div>
    <p class="rule">Unscramble as many words as you can.</p>
    <p class="meta">60 seconds · longer words score more</p>
    <div class="btns"><button class="go" id="bDaily">Daily #${today() + 1}</button><button class="ghost" id="bUnl">Unlimited</button></div>
    <div class="best">${st.lastDay === today() ? "✓ Played today · " : ""}Best ${st.best} · Streak ${st.streak}🔥</div></div>`;
  $("bDaily").onclick = () => begin("daily"); $("bUnl").onclick = () => begin("unl");
}
function begin(mode){
  const rnd = mode === "daily" ? seeded(today() + 1) : Math.random;
  const pool = Q.words, n = pool.length, list = [];
  if (mode === "daily"){ const off = (today() * 37) % n; for (let i = 0; i < 40; i++) list.push(pool[(off + i * 13) % n]); }
  G = {mode, rnd, list, i: 0, score: 0, solved: [], t0: performance.now()};
  $("game").innerHTML = `<div class="hud"><span class="side" id="cnt">0 words</span>
    <div class="clock" id="clock"><svg viewBox="0 0 64 64"><circle class="bg" cx="32" cy="32" r="28"/><circle class="fg" id="ring" cx="32" cy="32" r="28" stroke-dasharray="${RING}" stroke-dashoffset="0"/></svg><span id="secs">${SECS}</span></div>
    <span class="side" id="score">0 pts</span></div>
  <div class="card"><div class="letters" id="letters"></div>
    <form class="entry" id="f" autocomplete="off"><input id="in" autocapitalize="none" autocorrect="off" spellcheck="false" placeholder="unscramble" aria-label="Your answer" maxlength="12"><button class="go">Go</button></form>
    <div class="under"><span class="msg" id="msg"></span><button class="skip" id="skip" type="button">Skip</button></div></div>`;
  $("f").onsubmit = e => { e.preventDefault(); submit(); };
  $("skip").onclick = () => { G.solved.push({w: cur(), ok: false}); nextWord(); };
  nextWord(true); startTimer();
}
const cur = () => G.list[G.i];
function nextWord(first){
  if (!first) G.i++;
  if (G.mode === "unl" && G.i >= G.list.length) G.list.push(Q.words[Math.floor(Math.random() * Q.words.length)]);
  if (G.i >= G.list.length) return finish();
  G.shown = scramble(cur(), G.rnd);
  $("letters").className = "letters"; $("letters").innerHTML = [...G.shown].map(c => `<span>${c}</span>`).join("");
  $("in").value = ""; $("msg").textContent = ""; $("in").focus({preventScroll: true});
}
function submit(){
  const v = $("in").value.toLowerCase().replace(/[^a-z]/g, ""), w = cur(), inp = $("in");
  if (sortKey(v) === sortKey(w) && (v === w || (v in W))){
    const pts = w.length * 10; G.score += pts; G.solved.push({w: v, ok: true});
    $("score").textContent = G.score + " pts"; $("cnt").textContent = G.solved.filter(s => s.ok).length + " words";
    $("letters").className = "letters ok"; $("letters").innerHTML = [...v].map(c => `<span>${c}</span>`).join("");
    setTimeout(() => G && G.alive && nextWord(), 260);
  } else { $("msg").textContent = v.length !== w.length ? `${w.length} letters` : "Not quite"; inp.classList.remove("shake"); void inp.offsetWidth; inp.classList.add("shake"); inp.select(); }
}
function startTimer(){
  stopTimer(); G.alive = true; const t0 = performance.now();
  const step = () => {
    const ring = $("ring"); if (!ring) return;
    const left = Math.max(0, SECS - (performance.now() - t0) / 1000);
    ring.setAttribute("stroke-dashoffset", RING * (1 - left / SECS)); $("secs").textContent = Math.ceil(left); $("clock").classList.toggle("low", left < 10);
    if (left <= 0) return finish();
    timer = requestAnimationFrame(step);
  };
  timer = requestAnimationFrame(step);
}
function stopTimer(){ if (timer) cancelAnimationFrame(timer); timer = null; if (G) G.alive = false; }
function finish(){
  stopTimer();
  const ok = G.solved.filter(s => s.ok), missed = G.solved.filter(s => !s.ok);
  const st = store.get("q:stats", {best: 0, lastDay: -1, streak: 0, last: -2, played: 0});
  st.best = Math.max(st.best, G.score);
  if (G.mode === "daily" && st.lastDay !== today()){ st.played = (st.played || 0) + 1; st.streak = st.last === today() - 1 ? st.streak + 1 : 1; st.last = today(); st.lastDay = today(); }
  store.set("q:stats", st);
  $("game").innerHTML = `<div class="card result">
    <div class="big" id="cntUp">0</div><div class="sub">points · ${ok.length} word${ok.length === 1 ? "" : "s"}</div>
    <div class="solved">${ok.map(s => `<i>${s.w}</i>`).join("")}${missed.map(s => `<i class="miss">${s.w}</i>`).join("")}${G.solved.length === G.i && cur() ? `<i class="miss">${cur()}</i>` : ""}</div>
    <div class="btnrow" style="margin-top:16px"><button class="go" id="share">Share</button><button class="ghost" id="again">${G.mode === "daily" ? "Unlimited" : "Play again"}</button></div>
    ${G.mode === "daily" ? `<div class="count">New words in <b id="cd"></b></div>` : ""}</div>`;
  Common.countUp($("cntUp"), G.score); countdown($("cd"));
  $("share").onclick = () => Common.share(`${G.mode === "daily" ? `Quickly #${today() + 1}` : "Quickly"}: ${ok.length} words, ${G.score} pts in 60s ⚡\nsheihab.github.io/rarely/quickly.html`);
  $("again").onclick = () => begin("unl");
  setupAds();
}
$("statsBtn").onclick = () => { const st = store.get("q:stats", {best: 0, streak: 0, played: 0});
  openModal(`<h2>Quickly ${X}</h2><div class="stats"><div><b>${st.played || 0}</b><span>Played</span></div><div><b>${st.streak}</b><span>Streak</span></div><div><b>${st.best}</b><span>Best</span></div><div><b>60s</b><span>Time</span></div></div><ul class="rules"><li>Unscramble the letters. 10 points per letter.</li><li>Stuck? Skip.</li></ul>`); };
(async () => {
  const [q, w] = await Promise.all([fetch("data/quickly.json").then(r => r.json()), fetch("data/words.json").then(r => r.json())]);
  Q = q; W = {}; for (const p in w) for (const x of w[p].split(" ")) W[x] = +p;
  for (const x of Q.words){ const k = sortKey(x); (KEY[k] = KEY[k] || []); }
  for (const x in W){ const k = sortKey(x); if (KEY[k]) KEY[k].push(x); }
  startScreen(); setupAds();
})();
window.__qk = { get G(){ return G } };
})();
