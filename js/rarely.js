/* Rarely: name something, rarer answers score more. 7 daily prompts or unlimited. Nothing in-progress is saved. */
(() => {
const SECS = 25, RING = 2 * Math.PI * 28;
const TIERS = [
  {p:100, name:"Legendary", c:"var(--legend)", e:"🟨"}, {p:85, name:"Epic", c:"var(--epic)", e:"🟪"},
  {p:60, name:"Rare", c:"var(--rare)", e:"🟦"}, {p:30, name:"Uncommon", c:"var(--uncommon)", e:"🟩"},
  {p:10, name:"Common", c:"var(--common)", e:"⬜"}, {p:0, name:"Missed", c:"var(--line)", e:"⬛"}];
const tierOf = p => TIERS.find(t => p >= t.p);
const { $, store, openModal, X, dayIndex, setupAds, countdown } = Common;
let R, W, G, timer = null;

// ---------- checking answers
const norm = s => s.toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/&/g, " and ").replace(/'/g, "").replace(/-/g, " ").replace(/[^a-z0-9 ]/g, " ").replace(/\s+/g, " ").trim().replace(/^the /, "");
function lev(a, b){
  if (Math.abs(a.length - b.length) > 2) return 9;
  const d = Array.from({length: a.length + 1}, (_, i) => [i]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++) d[i][j] = Math.min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (a[i-1] === b[j-1] ? 0 : 1));
  return d[a.length][b.length];
}
const wordPts = p => p >= 85 ? 100 : p >= 60 ? 85 : p >= 35 ? 60 : p >= 15 ? 30 : 10;
function fitsRule(r, w){
  const a = r.arg, k = r.kind, v = "aeiou";
  if (k === "start") return w.startsWith(a);
  if (k === "end") return w.endsWith(a) && w !== a;
  if (k === "has") return w.includes(a);
  if (k === "startend") return w[0] === a[0] && w[w.length-1] === a[1];
  const f = {
    "2double": () => { const s = new Set(); for (let i = 0; i < w.length-1; i++) if (w[i] === w[i+1]) s.add(w[i]); return s.size >= 2; },
    novowel: () => !/[aeiou]/.test(w), allvowels: () => [...v].every(c => w.includes(c)), threevowelsrow: () => /[aeiou]{3}/.test(w),
    "4consonants": () => /[^aeiouy]{4}/.test(w), onevowel7: () => w.length >= 7 && new Set(w.match(/[aeiou]/g) || []).size === 1,
    zandq: () => w.includes("z") && w.includes("e") && !w.includes("a"), kx: () => w.includes("k") && w.endsWith("y"),
    doubleo_end: () => w.length > 3 && w[w.length-1] === w[w.length-2], samestartend: () => w.length >= 5 && w[0] === w[w.length-1],
    alternating: () => w.length >= 6 && [...w].slice(0, -1).every((c, i) => v.includes(c) !== v.includes(w[i+1]))
  }[a];
  return f ? f() : false;
}
function fromLetters(base, w){ const c = {}; for (const ch of base) c[ch] = (c[ch] || 0) + 1; for (const ch of w){ if (!c[ch]) return false; c[ch]--; } return true; }
function answers(pr){
  if (pr._all) return pr._all;
  const out = [];
  if (pr.type === "cat"){ for (const [a, p] of Object.entries(R.cats[pr.cat].a)) if (!pr.start || a[0] === pr.start) out.push([a, p]); }
  else if (pr.type === "word"){ for (const w in W) if (fitsRule(pr.rule, w)) out.push([w, wordPts(W[w])]); }
  else { for (const w in W) if (w.length >= 4 && w !== pr.base && fromLetters(pr.base, w)) out.push([w, wordPts(W[w])]); }
  out.sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  return (pr._all = out);
}
function check(pr, raw){
  const s = norm(raw);
  if (s.length < 2) return {err: "Type an answer"};
  if (pr.type === "cat"){
    const map = R.cats[pr.cat].a, ok = a => !pr.start || a[0] === pr.start;
    for (const t of [s, s.replace(/ies$/, "y"), s.replace(/es$/, ""), s.replace(/s$/, ""), s + "s"]) if (map[t] !== undefined && ok(t)) return {a: t, p: map[t]};
    if (s.length >= 5){ let best = null, bd = 9; for (const a of Object.keys(map)) if (ok(a)){ const d = lev(s, a); if (d < bd){ bd = d; best = a; } } if (best && bd <= (s.length >= 9 ? 2 : 1)) return {a: best, p: map[best]}; }
    if (pr.start && s[0] !== pr.start) return {err: `Must start with ${pr.start.toUpperCase()}`};
    return {err: "Not on our list"};
  }
  const w = s.replace(/ /g, "");
  if (pr.type === "word"){ if (!fitsRule(pr.rule, w)) return {err: "Doesn't fit"}; if (!(w in W)) return {err: "Not a word we know"}; return {a: w, p: wordPts(W[w])}; }
  if (w.length < 4) return {err: "4+ letters"};
  if (!fromLetters(pr.base, w)) return {err: `Only letters in ${pr.base.toUpperCase()}`};
  if (w === pr.base) return {err: "Not the word itself"};
  if (!(w in W)) return {err: "Not a word we know"};
  return {a: w, p: wordPts(W[w])};
}

// ---------- screens
const today = () => dayIndex(R.start, R.days.length);
function startScreen(){
  stopTimer();
  const st = store.get("r:stats", {best: 0, streak: 0, last: -2, lastDay: -1});
  const doneToday = st.lastDay === today();
  $("game").innerHTML = `<div class="card start">
    <div class="logo-big">Rarely</div>
    <p class="rule">Name something. <b style="color:var(--ink)">Rarer answers score more.</b></p>
    <p class="meta">25 seconds per prompt</p>
    <div class="btns"><button class="go" id="bDaily">Daily #${today() + 1} · 7 prompts</button><button class="ghost" id="bUnl">Unlimited</button></div>
    <div class="best">${doneToday ? "✓ Played today · " : ""}Best ${st.best} · Streak ${st.streak}🔥</div></div>`;
  $("bDaily").onclick = () => begin("daily"); $("bUnl").onclick = () => begin("unl");
}
const rand = () => Math.floor(Math.random() * R.prompts.length);
function begin(mode){
  G = mode === "daily" ? {mode, day: today(), list: R.days[today()].slice(), i: 0, ans: [], score: 0} : {mode, list: [rand()], i: 0, ans: [], score: 0};
  prompt();
}
function hud(left){
  return `<div class="hud"><span class="side">${left}</span>
    <div class="clock" id="clock"><svg viewBox="0 0 64 64"><circle class="bg" cx="32" cy="32" r="28"/><circle class="fg" id="ring" cx="32" cy="32" r="28" stroke-dasharray="${RING}" stroke-dashoffset="0"/></svg><span id="secs">${SECS}</span></div>
    <span class="side" id="score">${G.score} pts</span></div>`;
}
function prompt(){
  const pr = R.prompts[G.list[G.i]];
  $("game").innerHTML = hud(G.mode === "daily" ? `${G.i + 1} / 7` : `#${G.i + 1}`) + `
  <div class="card">
    <div class="prompt">${pr.t}</div>
    <form class="entry" id="f" autocomplete="off"><input id="in" autocapitalize="none" autocorrect="off" spellcheck="false" placeholder="type your answer" aria-label="Your answer" maxlength="40"><button class="go">Go</button></form>
    <div class="under"><span class="msg" id="msg"></span><button class="skip" id="skip" type="button">Skip</button></div>
    <div id="rev"></div>
  </div>
  ${G.mode === "unl" ? `<div class="hint"><button class="skip" id="quit">End game</button></div>` : ""}`;
  $("f").onsubmit = e => { e.preventDefault(); submit(); };
  $("skip").onclick = () => lock(null, "Skipped");
  if ($("quit")) $("quit").onclick = finish;
  setTimeout(() => $("in") && $("in").focus({preventScroll: true}), 30);
  startTimer();
}
function startTimer(){
  stopTimer(); const t0 = performance.now();
  const step = () => {
    const ring = $("ring"); if (!ring) return;
    const left = Math.max(0, SECS - (performance.now() - t0) / 1000);
    ring.setAttribute("stroke-dashoffset", RING * (1 - left / SECS));
    $("secs").textContent = Math.ceil(left);
    $("clock").classList.toggle("low", left < 6);
    if (left <= 0) return lock(null, "Time's up");
    timer = requestAnimationFrame(step);
  };
  timer = requestAnimationFrame(step);
}
function stopTimer(){ if (timer) cancelAnimationFrame(timer); timer = null; }
function submit(){
  const pr = R.prompts[G.list[G.i]], r = check(pr, $("in").value), inp = $("in");
  if (!r.err && G.ans.some(a => a.a === r.a)) r.err = "Already used";
  if (r.err){ $("msg").textContent = r.err; inp.classList.remove("shake"); void inp.offsetWidth; inp.classList.add("shake"); inp.select(); return; }
  lock(r);
}
function lock(r, label){
  stopTimer();
  const pr = R.prompts[G.list[G.i]], p = r ? r.p : 0, t = tierOf(p);
  G.ans.push({a: r ? r.a : null, p, q: pr.t}); G.score += p;
  $("score").textContent = G.score + " pts";
  const top = answers(pr).filter(x => x[0] !== (r && r.a) && x[1] > p).slice(0, 2);
  $("f").remove(); document.querySelector(".under").remove();
  const last = G.mode === "daily" && G.i === 6;
  $("rev").innerHTML = `<div class="inline-reveal"><span class="w" style="${r ? "" : "color:var(--muted)"}">${r ? r.a : label}</span><span class="tier" style="background:${t.c}">+${p} ${t.name}</span></div>
    <div class="reveal on" style="margin-top:6px"><div class="note">${top.length ? "Rarer: " + top.map(x => `<b>${x[0]}</b>`).join(", ") : "Top tier 🏆"}</div>
    <button class="next" id="next">${last ? "See score" : "Next →"}</button></div>`;
  if (p === 100) Common.burst();
  $("next").onclick = next; $("next").focus();
}
function next(){
  if (G.mode === "daily" && G.i === 6) return finish();
  if (G.mode === "unl") G.list.push(rand());
  G.i++; prompt();
}
function finish(){
  stopTimer();
  const s = G.score, n = G.ans.length, emoji = G.ans.map(a => tierOf(a.p).e).join("");
  if (G.mode === "daily"){
    const st = store.get("r:stats", {best: 0, streak: 0, last: -2, lastDay: -1, played: 0});
    if (st.lastDay !== G.day){ st.played = (st.played || 0) + 1; st.streak = st.last === G.day - 1 ? st.streak + 1 : 1; st.last = G.day; st.lastDay = G.day; }
    st.best = Math.max(st.best, s); store.set("r:stats", st);
  }
  const rows = G.ans.map(a => `<div class="brow"><span class="q">${a.q}</span><span class="mine" style="color:${tierOf(a.p).c}">${a.a || "—"} · ${a.p}</span></div>`).join("");
  $("game").innerHTML = `<div class="card result">
    <div class="big" id="cnt">0</div><div class="sub">${G.mode === "daily" ? "out of 700" : `points from ${n} prompt${n === 1 ? "" : "s"}`}</div>
    <div class="emoji">${emoji}</div>
    <div class="btnrow"><button class="go" id="share">Share</button><button class="ghost" id="again">${G.mode === "daily" ? "Unlimited" : "Play again"}</button></div>
    ${G.mode === "daily" ? `<div class="count">New prompts in <b id="cd"></b></div>` : ""}
    <div class="best">${rows}</div></div>`;
  Common.countUp($("cnt"), s); countdown($("cd"));
  $("share").onclick = () => Common.share(`${G.mode === "daily" ? `Rarely #${G.day + 1}: ${s}/700` : `Rarely: ${s} pts in ${n}`}\n${emoji}\nsheihab.github.io/rarely`);
  $("again").onclick = () => begin("unl");
  setupAds();
}
$("statsBtn").onclick = () => { const st = store.get("r:stats", {played: 0, streak: 0, best: 0});
  openModal(`<h2>Rarely ${X}</h2><div class="stats"><div><b>${st.played || 0}</b><span>Played</span></div><div><b>${st.streak}</b><span>Streak</span></div><div><b>${st.best}</b><span>Best</span></div><div><b>700</b><span>Max</span></div></div>
  <ul class="rules"><li>Name something that fits. 25 seconds.</li><li>Points: <span class="chip" style="background:var(--common)">10</span> <span class="chip" style="background:var(--uncommon)">30</span> <span class="chip" style="background:var(--rare)">60</span> <span class="chip" style="background:var(--epic)">85</span> <span class="chip" style="background:var(--legend)">100</span></li></ul>`); };
(async () => {
  try{
    const [r, w] = await Promise.all([fetch("data/rarely.json").then(x => x.json()), fetch("data/words.json").then(x => x.json())]);
    R = r; W = {}; for (const p in w) for (const x of w[p].split(" ")) W[x] = +p;
    startScreen(); setupAds();
  }catch(e){ $("game").innerHTML = `<div class="loading">Couldn't load. Refresh to try again.</div>`; console.error(e); }
})();
window.__rarely = { get R(){ return R }, get G(){ return G }, answers, check };
})();
