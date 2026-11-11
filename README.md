# Cloudy Prompt Library

A free, static library of original prompts and agent configs for system prompts, Cursor rules, custom instructions, agent task templates, vibe coding, game dev, code review and research writing.

- `data/prompts.json` — the curated library. Every entry is original Cloudy writing, free to copy and adapt.
- `src/` — CSS, JS (search, filters, copy buttons), favicon, OG image.
- `build.py` — generates the static site into `dist/` (home, library, category pages, prompt pages, sitemap.xml, robots.txt, llms.txt, llms-full.txt, JSON-LD).

```
BASE_URL=https://<user>.github.io/prompt-library python3 build.py
```

Deployed to GitHub Pages from the `gh-pages` branch by `deploy.sh`. Built by Cloudy.
