# Rarely & Squarely: free daily word games

**▶ Play: [sheihab.github.io/rarely](https://sheihab.github.io/rarely/)**

- **Rarely**: 7 "Name a…" prompts a day, 25 seconds each. Obvious answers score 10; rare answers score up to 100. Unlimited mode never ends.
- **[Squarely](https://sheihab.github.io/rarely/squarely.html)**: guess the hidden 5-letter word in 6 tries. New word daily, plus unlimited.

No sign-up. Works on phones and laptops, installable as an app.
[Lists](https://sheihab.github.io/rarely/lists.html) · [Word lists](https://sheihab.github.io/rarely/word-lists.html) · [Answers](https://sheihab.github.io/rarely/answers.html)

---
### Developer notes
- `index.html` (Rarely), `squarely.html`, shared `app.css` + `common.js`.
- `tools/categories.py`: the "Name a…" answer bank. Edit, then run `python3 tools/build_v2.py` to rebuild `data/rarely.json` + `data/squarely.json`.
- `tools/build_pages.py` (word lists), `tools/build_lists.py` (category lists, how-to-play), `tools/build_daily.py` (daily answers, sitemap). **build_daily runs automatically every night** (`.github/workflows/daily.yml`) and pings Bing via IndexNow.
- **Ads:** paste your AdSense IDs into `CONFIG` at the top of `common.js`. Ad slots stay hidden until then.

Built by Shehab Fadalalla.
