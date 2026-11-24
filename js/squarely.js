/* Squarely: guess the 5-letter word in 6 tries. Daily or unlimited. Boards are not saved. */
(() => {
const { $, store, toast, openModal, X, dayIndex, countdown, setupAds } = Common;
const ROWS = [["q","w","e","r","t","y","u","i","o","p"],["a","s","d","f","g","h","j","k","l"],["enter","z","x","c","v","b","n","m","back"]];
let S, VALID, G = null, busy = false, tick = null;
const today = () => dayIndex(S.start, S.answers.length);

function score(guess, ans){
  const res = Array(5).fill("miss"), left = {};
  for (let i = 0; i < 5; i++){ if (guess[i] === ans[i]) res[i] = "hit"; else left[ans[i]] = (left[ans[i]] || 0) + 1; }
  for (let i = 0; i < 5; i++) if (res[i] !== "hit" && left[guess[i]]){ res[i] = "near"; left[guess[i]]--; }
  return res;
}
function startScreen(){
  G = null; clearInterval(tick);
  const st = store.get("s:stats", {played: 0, wins: 0, streak: 0, max: 0, lastDay: -1});
  $("game").innerHTML = `<div class="card start">
    <div class="logo-big">Squarely</div>
    <p class="rule">Guess the 5-letter word in 6 tries.</p>
    <p class="meta"><span class="chip" style="background:var(--sq-hit);color:#fff">Green</span> right spot · <span class="chip" style="background:var(--sq-near)">Gold</span> wrong spot</p>
    <div class="btns"><button class="go" id="bDaily">Daily #${today() + 1}</button><button class="ghost" id="bUnl">Unlimited</button></div>
    <div class="best">${st.lastDay === today() ? "✓ Played today · " : ""}Streak ${st.streak}🔥 · Wins ${st.wins}</div></div>`;
  $("bDaily").onclick = () => begin("daily"); $("bUnl").onclick = () => begin("unl");
}
function begin(mode){
  G = {mode, day: today(), ans: mode === "daily" ? S.answers[today()] : S.answers[Math.floor(Math.random() * S.answers.length)], guesses: [], cur: "", over: false, t0: Date.now(), wins: G && G.mode === "unl" ? G.wins : 0};
  $("game").innerHTML = `<div class="hud"><span class="side" id="tries">0 / 6</span><div class="clock"><span id="secs">0:00</span></div><span class="side" id="wins">${mode === "unl" ? G.wins + " won" : "#" + (G.day + 1)}</span></div>
    <div class="grid" id="grid"></div><div id="end"></div><div class="kb" id="kb"></div>`;
  clearInterval(tick); tick = setInterval(() => { if (!G || G.over) return; const s = Math.floor((Date.now() - G.t0) / 1000); $("secs").textContent = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; }, 250);
  draw();
}
function draw(){
  let g = "";
  for (let r = 0; r < 6; r++){
    const word = G.guesses[r] || (r === G.guesses.length ? G.cur : ""), res = G.guesses[r] ? score(G.guesses[r], G.ans) : null;
    g += `<div class="row" id="r${r}">` + [0,1,2,3,4].map(i => `<div class="tile ${res ? res[i] : word[i] ? "filled" : ""}" style="${res && r === G.guesses.length - 1 ? `animation-delay:${i * 90}ms` : res ? "animation:none" : ""}">${word[i] || ""}</div>`).join("") + "</div>";
  }
  $("grid").innerHTML = g;
  const ks = {}, rank = {hit: 3, near: 2, miss: 1};
  G.guesses.forEach(w => score(w, G.ans).forEach((r, i) => { if (!ks[w[i]] || rank[r] > rank[ks[w[i]]]) ks[w[i]] = r; }));
  $("kb").innerHTML = ROWS.map(row => `<div class="krow">${row.map(k => `<button data-k="${k}" class="${k.length > 1 ? "wide" : ""} ${ks[k] || ""}" aria-label="${k}">${k === "back" ? "⌫" : k}</button>`).join("")}</div>`).join("");
  $("tries").textContent = `${G.guesses.length} / 6`;
  $("kb").style.display = G.over ? "none" : "";
  $("end").innerHTML = G.over ? endHtml() : "";
  if (G.over) wireEnd();
}
function endHtml(){
  const won = G.guesses[G.guesses.length - 1] === G.ans;
  return `<div class="sq-end"><div class="ans">${G.ans}</div><div style="color:var(--muted);margin:2px 0 12px">${won ? ["Genius","Brilliant","Great","Nice","Solid","Phew"][G.guesses.length - 1] + " · " + $("secs").textContent : "Next time"}</div>
    <div class="btnrow">${G.mode === "daily" ? `<button class="go" id="shareB">Share</button><button class="ghost" id="playUnl">Unlimited</button>` : `<button class="go" id="nextB">Next word →</button><button class="ghost" id="shareB">Share</button>`}</div>
    ${G.mode === "daily" ? `<div class="count">New word in <b id="cd"></b></div>` : ""}</div>`;
}
function wireEnd(){
  const grid = G.guesses.map(w => score(w, G.ans).map(r => ({hit: "🟩", near: "🟨", miss: "⬛"})[r]).join("")).join("\n");
  const won = G.guesses[G.guesses.length - 1] === G.ans;
  $("shareB").onclick = () => Common.share(`${G.mode === "daily" ? `Squarely #${G.day + 1}` : "Squarely"} ${won ? G.guesses.length : "X"}/6\n${grid}\nsheihab.github.io/rarely/squarely.html`);
  if ($("playUnl")) $("playUnl").onclick = () => begin("unl");
  if ($("nextB")) $("nextB").onclick = () => begin("unl");
  countdown($("cd")); setupAds();
}
function press(k){
  if (!G || G.over || busy) return;
  if (k === "back"){ G.cur = G.cur.slice(0, -1); return drawRow(); }
  if (k === "enter") return submit();
  if (/^[a-z]$/.test(k) && G.cur.length < 5){ G.cur += k; drawRow(); }
}
function drawRow(){ const row = $("r" + G.guesses.length); if (row) [...row.children].forEach((t, i) => { t.textContent = G.cur[i] || ""; t.className = "tile" + (G.cur[i] ? " filled" : ""); }); }
function submit(){
  const row = $("r" + G.guesses.length);
  const bad = m => { toast(m); row.classList.remove("shake"); void row.offsetWidth; row.classList.add("shake"); };
  if (G.cur.length < 5) return bad("5 letters");
  if (!VALID.has(G.cur)) return bad("Not in word list");
  G.guesses.push(G.cur); G.cur = "";
  const won = G.guesses[G.guesses.length - 1] === G.ans;
  if (won || G.guesses.length === 6){ G.over = true; if (G.mode === "unl" && won) G.wins++; record(won); }
  busy = true; draw();
  if (G.mode === "unl") $("wins").textContent = G.wins + " won";
  setTimeout(() => { busy = false; if (won) Common.burst(); }, 600);
}
function record(won){
  if (G.mode !== "daily") return;
  const s = store.get("s:stats", {played: 0, wins: 0, streak: 0, max: 0, last: -2, lastDay: -1, dist: [0,0,0,0,0,0]});
  if (s.lastDay === G.day) return;
  s.played++; s.lastDay = G.day;
  if (won){ s.wins++; s.dist[G.guesses.length - 1]++; s.streak = s.last === G.day - 1 ? s.streak + 1 : 1; s.last = G.day; s.max = Math.max(s.max, s.streak); } else s.streak = 0;
  store.set("s:stats", s);
}
document.addEventListener("keydown", e => {
  if (e.ctrlKey || e.metaKey || e.altKey || document.querySelector(".modal-bg.on")) return;
  const k = e.key === "Enter" ? "enter" : e.key === "Backspace" ? "back" : e.key.toLowerCase();
  if (G && !G.over && (k === "enter" || k === "back" || /^[a-z]$/.test(k))){ e.preventDefault(); press(k); }
});
document.addEventListener("click", e => { const b = e.target.closest("[data-k]"); if (b) press(b.dataset.k); });
$("statsBtn").onclick = () => { const s = store.get("s:stats", {played: 0, wins: 0, streak: 0, max: 0, dist: [0,0,0,0,0,0]}), mx = Math.max(1, ...s.dist);
  openModal(`<h2>Squarely ${X}</h2><div class="stats"><div><b>${s.played}</b><span>Played</span></div><div><b>${s.played ? Math.round(100 * s.wins / s.played) : 0}</b><span>Win %</span></div><div><b>${s.streak}</b><span>Streak</span></div><div><b>${s.max}</b><span>Best</span></div></div>
  ${s.dist.map((n, i) => `<div style="display:flex;gap:8px;align-items:center;margin:4px 0;font-size:14px"><span style="width:12px">${i + 1}</span><span style="background:var(--sq-hit);padding:2px 8px;border-radius:6px;min-width:24px;width:${Math.max(8, 100 * n / mx)}%;text-align:right;font-weight:700">${n}</span></div>`).join("")}`); };
(async () => {
  S = await fetch("data/squarely.json").then(r => r.json());
  VALID = new Set(S.valid.split(" ")); S.answers.forEach(a => VALID.add(a));
  startScreen(); setupAds();
})();
window.__sq = { get G(){ return G } };
})();
