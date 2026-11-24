/* Shared helpers for Rarely + Squarely */
const Common = (() => {
  const CONFIG = { ADSENSE_CLIENT: "", ADSENSE_SLOT: "" };   // paste your AdSense IDs here when approved
  const $ = id => document.getElementById(id);
  const store = {
    get(k, d){ try{ const v = localStorage.getItem("rarely:" + k); return v ? JSON.parse(v) : d; }catch(e){ return d; } },
    set(k, v){ try{ localStorage.setItem("rarely:" + k, JSON.stringify(v)); }catch(e){} }
  };
  let tt; const toast = m => { const t = $("toast"); t.textContent = m; t.classList.add("on"); clearTimeout(tt); tt = setTimeout(() => t.classList.remove("on"), 2000); };
  const X = `<button class="icon-btn" data-close aria-label="Close">✕</button>`;
  function openModal(html){ $("modalBody").innerHTML = html; $("modal").classList.add("on"); }
  function closeModal(){ $("modal").classList.remove("on"); }
  document.addEventListener("click", e => { if (e.target.id === "modal" || e.target.closest("[data-close]")) closeModal(); });
  document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });
  function dayIndex(start, max){   // local calendar day since launch
    const s = new Date(start + "T00:00:00"), n = new Date(); n.setHours(0, 0, 0, 0);
    return Math.max(0, Math.min(max - 1, Math.round((n - s) / 864e5)));
  }
  function countUp(el, to){ const t0 = performance.now(); const f = t => { const k = Math.min(1, (t - t0) / 600); el.textContent = Math.round(to * (1 - Math.pow(1 - k, 3))); if (k < 1) requestAnimationFrame(f); }; requestAnimationFrame(f); }
  function burst(){
    for (let i = 0; i < 26; i++){
      const s = document.createElement("i"), a = Math.random() * 6.28, d = 80 + Math.random() * 140;
      s.style.cssText = `position:fixed;left:50%;top:45%;width:8px;height:8px;border-radius:2px;background:${["#FFC23D","#B66BFF","#4C9BFF","#3FCB7E"][i % 4]};z-index:50;pointer-events:none;transition:transform .9s cubic-bezier(.2,.8,.2,1),opacity .9s`;
      document.body.appendChild(s);
      requestAnimationFrame(() => { s.style.transform = `translate(${Math.cos(a) * d}px,${Math.sin(a) * d}px) rotate(${Math.random() * 360}deg)`; s.style.opacity = "0"; });
      setTimeout(() => s.remove(), 1000);
    }
  }
  function countdown(el){
    if (!el) return;
    const tick = () => { if (!el.isConnected) return; const n = new Date(), m = new Date(n); m.setHours(24, 0, 0, 0); const s = Math.floor((m - n) / 1000);
      el.textContent = [s / 3600, s % 3600 / 60, s % 60].map(x => String(Math.floor(x)).padStart(2, "0")).join(":"); setTimeout(tick, 1000); };
    tick();
  }
  async function share(text){
    try{ if (navigator.share){ await navigator.share({text}); return; } await navigator.clipboard.writeText(text); toast("Copied"); }catch(e){}
  }
  function setupAds(){
    if (!CONFIG.ADSENSE_CLIENT) return;
    if (!setupAds.done){ const s = document.createElement("script"); s.async = true; s.crossOrigin = "anonymous"; s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + CONFIG.ADSENSE_CLIENT; document.head.appendChild(s); setupAds.done = true; }
    document.querySelectorAll(".ad-slot:not(.on)").forEach(el => { el.innerHTML = `<div class="ad-label">Advertisement</div><ins class="adsbygoogle" style="display:block" data-ad-client="${CONFIG.ADSENSE_CLIENT}" data-ad-slot="${CONFIG.ADSENSE_SLOT}" data-ad-format="auto" data-full-width-responsive="true"></ins>`; el.classList.add("on"); try{ (window.adsbygoogle = window.adsbygoogle || []).push({}); }catch(e){} });
  }
  if ("serviceWorker" in navigator && location.protocol === "https:" && !location.hostname.endsWith("claude.ai") && !location.hostname.endsWith("claudeusercontent.com")) navigator.serviceWorker.register("sw.js").catch(() => {});
  return { $, store, toast, X, openModal, closeModal, dayIndex, countUp, burst, countdown, share, setupAds };
})();
