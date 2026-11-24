"""Builds the 4 game pages (index hub, rarely, squarely, quickly) from shared header/footer."""
import os, json
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BASE = "https://sheihab.github.io/rarely/"
VERIFY = ""   # paste Google/Bing verification <meta> tags here if needed
def head(title, desc, canon, og, ld):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{BASE}{canon}">
<meta name="theme-color" content="#14121F">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icon-180.png">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{BASE}{canon}"><meta property="og:type" content="website">
<meta property="og:image" content="{BASE}{og}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{VERIFY}
<script type="application/ld+json">{json.dumps(ld)}</script>
<link rel="stylesheet" href="app.css">
</head>
<body>'''
def nav(active):
    tabs = "".join(f'<a href="{h}"{" class=\"on\"" if n == active else ""}>{n}</a>' for n, h in [("Rarely", "rarely.html"), ("Squarely", "squarely.html"), ("Quickly", "quickly.html")])
    stats = '<button class="icon-btn" id="statsBtn" aria-label="Stats"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 20V11M12 20V4M19 20v-6"/></svg></button>' if active else '<span style="width:44px"></span>'
    return f'''<header><div class="bar">
<a class="icon-btn" href="./" aria-label="All games"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/></svg></a>
<nav class="games">{tabs}</nav>{stats}</div></header>'''
FOOT = '''<footer><a href="./">All games</a> · <a href="how-to-play.html">How to play</a> · <a href="answers.html">Answers</a> · <a href="lists.html">Lists</a> · <a href="word-lists.html">Word lists</a> · <a href="privacy.html">Privacy</a></footer>
<div class="modal-bg" id="modal" role="dialog" aria-modal="true"><div class="modal" id="modalBody"></div></div>
<div class="toast" id="toast"></div>
<script src="common.js"></script>'''
def app(name, url, genre, desc):
    return {"@context": "https://schema.org", "@type": "WebApplication", "name": name, "url": BASE + url, "applicationCategory": "GameApplication", "genre": genre,
            "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "AUD"}, "description": desc}
GAMES = [
 ("Rarely", "rarely.html", "Rarely: Daily Trivia Game Where Rare Answers Win", "Free daily trivia game. 7 'Name a…' prompts, 25 seconds each. Obvious answers barely score; rare answers win. Plus unlimited mode.", "og-image.png", "Trivia"),
 ("Squarely", "squarely.html", "Squarely: Daily 5-Letter Word Game + Unlimited", "Guess the hidden 5-letter word in 6 tries. Green = right spot, gold = wrong spot. New word daily, plus unlimited play. Free.", "og-squarely.png", "Word game"),
 ("Quickly", "quickly.html", "Quickly: Unscramble Words Game (60-Second Challenge)", "Unscramble as many words as you can in 60 seconds. Free daily word scramble, plus unlimited mode.", "og-quickly.png", "Word game"),
]
for name, url, title, desc, og, genre in GAMES:
    html = head(title, desc, url, og, app(name, url, genre, desc)) + "\n" + nav(name) + f'''
<main class="wrap"><div id="game"><div class="loading">Loading…</div></div><div class="ad-slot" data-slot="game"></div></main>
{FOOT}
<script src="js/{name.lower()}.js"></script>
</body></html>
'''
    open(os.path.join(ROOT, url), "w").write(html)
hub_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Rarely games", "url": BASE, "description": "Free daily word games: Rarely, Squarely and Quickly."}
CARD = lambda href, name, line, bg, icon: f'<a class="gcard" href="{href}"><div class="ic" style="background:{bg}">{icon}</div><div><b>{name}</b><span>{line}</span></div><span class="arrow">›</span></a>'
GEM = '<svg width="30" height="30" viewBox="0 0 24 24"><path d="M6 3h12l4 6-10 12L2 9z" fill="#14121F"/></svg>'
GRID = '<svg width="30" height="30" viewBox="0 0 24 24" fill="#fff"><rect x="2" y="2" width="9" height="9" rx="2"/><rect x="13" y="2" width="9" height="9" rx="2" opacity=".55"/><rect x="2" y="13" width="9" height="9" rx="2" opacity=".55"/><rect x="13" y="13" width="9" height="9" rx="2"/></svg>'
BOLT = '<svg width="30" height="30" viewBox="0 0 24 24"><path d="M13 2 4 14h7l-1 8 9-12h-7z" fill="#fff"/></svg>'
html = head("Free Daily Word Games: Rarely, Squarely & Quickly", "Three free daily word games. Name rare answers in Rarely, guess the 5-letter word in Squarely, unscramble words fast in Quickly. New puzzles daily, plus unlimited play.", "", "og-image.png", hub_ld) + "\n" + nav("") + f'''
<main class="wrap">
<div class="hub-title"><h1>Daily word games</h1><p>New puzzles every day. Unlimited anytime.</p></div>
<div class="hub">
{CARD("rarely.html", "Rarely", "Name something rare · 25s per prompt", "var(--legend)", GEM)}
{CARD("squarely.html", "Squarely", "Guess the 5-letter word · 6 tries", "var(--sq-hit)", GRID)}
{CARD("quickly.html", "Quickly", "Unscramble words · 60 seconds", "var(--epic)", BOLT)}
</div>
<div class="ad-slot" data-slot="hub"></div>
</main>
{FOOT}
<script>Common.setupAds();</script>
</body></html>
'''
open(os.path.join(ROOT, "index.html"), "w").write(html)
print("built 4 pages")
