# Rarely: the daily word game where rare answers win

**▶ Play: [sheihab.github.io/rarely](https://sheihab.github.io/rarely/)**

Every day there are 7 word prompts, the same for everyone ("Starts with QU", "Contains Z", "5 letters, starts with R"…). Type one real English word for each. Common words barely score; rare words score up to 100. A perfect day is 700.

- 🗓️ New puzzle every day at midnight · 🔥 streaks and stats · 📤 share your score grid
- ♾️ Unlimited mode · 🗂️ Archive of every past puzzle
- 📚 [319 word lists](https://sheihab.github.io/rarely/word-lists.html) (words that start with, end with, contain…) · 💡 [Daily answers](https://sheihab.github.io/rarely/answers.html)

No sign-up, works on phones and laptops, installable as an app.

---
### How it runs (developer notes)
- `index.html`: the whole game. `data/words.json` holds ~57k words with rarity points; `data/puzzles.json` holds the prompts and 800 days of daily puzzles.
- `tools/build_data.py` rebuilds the word list and puzzles (word frequencies from the open-source [wordfreq](https://github.com/rspeer/wordfreq) project).
- `tools/build_pages.py` builds the word-list pages, how-to-play and privacy.
- `tools/build_daily.py` builds the daily answers page, sitemap and robots.txt. **It runs automatically every night** via `.github/workflows/daily.yml`, which also pings Bing/IndexNow.
- **Ads:** paste your AdSense publisher ID into `CONFIG.ADSENSE_CLIENT` in `index.html` (ad slots stay hidden until then).

Built by Shehab Fadalalla.
