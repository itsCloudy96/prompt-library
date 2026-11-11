#!/usr/bin/env python3
"""Static site generator for Cloudy Prompt Library. Usage: BASE_URL=https://x.github.io/repo python3 build.py"""
import json, os, shutil, html, datetime
from pathlib import Path
from urllib.parse import urlparse
BASE = os.environ.get('BASE_URL', 'https://itscloudy96.github.io/prompt-library').rstrip('/')
SITE = 'Cloudy Prompt Library'
X_HANDLE = 'ItsCloudySpace'
NEWS = 'https://cloudys-newsletter.beehiiv.com/subscribe'
TOOLS_SITE = 'https://itscloudy96.github.io/ai-tool-finder/'
TODAY = datetime.date.today().isoformat()
src, out = Path('src'), Path('dist')
D = json.load(open('data/prompts.json'))
PROMPTS, CATS = D['prompts'], D['categories']
BY = {p['id']: p for p in PROMPTS}
CAT_BLURB = D['categoryBlurbs']
e = lambda s: html.escape(str(s if s is not None else ''), quote=True)
def jl(o): return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False).replace('</','<\\/') + '</script>'
ORG = {"@type":"Organization","name":"Cloudy","url":BASE+'/',"sameAs":[f"https://x.com/{X_HANDLE}","https://cloudys-newsletter.beehiiv.com",TOOLS_SITE]}

def page(path, title, desc, body, root, ld=None, ogtype='website'):
    url = BASE + '/' + path
    lds = ''.join(jl(x) for x in (ld or []))
    doc = f'''<!doctype html>
<html lang="en" data-root="{root}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#0b1020">
<meta property="og:type" content="{ogtype}"><meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}"><meta property="og:image" content="{BASE}/og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:site" content="@{X_HANDLE}">
<meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{BASE}/og.png">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<link rel="alternate" type="text/plain" title="LLM summary" href="{root}llms.txt">
<link rel="stylesheet" href="{root}css/styles.css?v={TODAY}">
{lds}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="container nav">
<a class="logo" href="{root}"><span class="logo-mark" aria-hidden="true">☁️</span>Cloudy <span class="muted" style="font-weight:600">Prompt Library</span></a>
<nav class="nav-links" aria-label="Main"><a href="{root}prompts/">Library</a><a href="{root}category/">Categories</a><a href="{e(TOOLS_SITE)}">Tool Finder</a><a href="{root}about/">About</a><a href="{NEWS}" target="_blank" rel="noopener">Newsletter</a></nav>
</div></header>
<main id="main" class="container">
{body}
</main>
<footer class="footer"><div class="container footer-grid">
<div><strong>☁️ Cloudy</strong><p>Original, copy-ready prompts and agent configs for builders, gamers and vibe coders.</p>
<form class="newsletter" action="{NEWS}" method="get" target="_blank"><input type="email" name="email" placeholder="you@example.com" aria-label="Email address" required><button class="btn btn-primary" type="submit">Get the daily AI agent changelog</button></form></div>
<div><strong>Explore</strong><br>{'<br>'.join(f'<a href="{root}category/{k}/">{e(v)}</a>' for k,v in CATS.items())}</div>
<div><strong>Cloudy</strong><br><a href="{root}about/">About &amp; disclosure</a><br><a href="{root}about/#sponsor">Sponsor Cloudy</a><br><a href="{e(TOOLS_SITE)}">AI Tool Finder</a><br><a href="https://x.com/{X_HANDLE}" target="_blank" rel="noopener">@{X_HANDLE} on X</a><br><a href="{root}llms.txt">llms.txt</a><br><a href="{root}sitemap.xml">Sitemap</a></div>
</div><div class="container disclaimer" style="margin-top:1rem">© {datetime.date.today().year} Cloudy. Prompts are original Cloudy writing, free to use and adapt. Review any model output before you ship it. Some outbound links may be affiliate links.</div></footer>
<script src="{root}js/app.js?v={TODAY}" defer></script>
</body></html>'''
    p = out / path
    if path == '' or path.endswith('/'): p = p / 'index.html'
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(doc)

def card(p, root):
    cats = f'<span class="badge">{e(CATS.get(p["category"], p["category"]))}</span>'
    tools = ''.join(f'<span class="badge">{e(w)}</span>' for w in p.get('worksWith', [])[:3])
    return (f'<article class="card tool-card" data-id="{e(p["id"])}"><h3><a href="{root}prompt/{p["id"]}/">{e(p["title"])}</a></h3><div>{cats}{tools}</div>'
            f'<p>{e(p["summary"])}</p><div class="meta"><a href="{root}prompt/{p["id"]}/">Open →</a>'
            f'<button type="button" class="btn btn-secondary btn-sm" data-copy-id="{e(p["id"])}">Copy prompt</button></div></article>')

SPONSOR = lambda root: (f'<aside class="card sponsor" aria-label="Sponsor"><div class="label">Sponsor slot</div><h3 style="margin:.3rem 0">Your AI tool here</h3>'
    f'<p class="muted" style="margin:0 0 .6rem">Reach builders, gamers and vibe coders who actually use prompts and agents.</p><a class="btn btn-secondary btn-sm" href="{root}about/#sponsor">Sponsor this spot</a></aside>')
def in_cat(c): return [p for p in PROMPTS if p['category'] == c]
def works_options():
    seen = []
    for p in PROMPTS:
        for w in p.get('worksWith', []):
            if w not in seen: seen.append(w)
    return seen

def build():
    if out.exists(): shutil.rmtree(out)
    shutil.copytree(src, out)
    (out/'data').mkdir(exist_ok=True)
    shutil.copy('data/prompts.json', out/'data/prompts.json')
    (out/'.nojekyll').write_text('')
    urls = []
    faqs = [
        ("What is the Cloudy Prompt Library?", f"A free library of {len(PROMPTS)} original, copy-ready prompts and agent configs across {len(CATS)} categories: system prompts, Cursor rules, custom instructions, agent task templates, vibe coding, game dev, review and debug, and research writing."),
        ("Can I use these prompts in my own projects?", "Yes. Every prompt is original Cloudy writing. Copy it, adapt it, ship with it. A credit is nice but not required."),
        ("Do you collect copyrighted prompt packs?", "No. We write original prompts instead of copying public prompt collections or vendor system prompts."),
        ("What is the daily AI agent changelog?", "A short Cloudy newsletter that tracks new agent tools, model updates and useful workflow changes. Subscribe free — no spam, just the brief."),
        ("How should I use a prompt?", "Open any entry for a short how-to, then hit Copy prompt and paste it into ChatGPT, Claude, Cursor, Claude Code or whatever you use. Tweak the bracketed placeholders first."),
    ]
    cats_html = ''.join(f'<a class="card" href="category/{k}/"><strong>{e(v)}</strong><div class="count">{len(in_cat(k))} prompts</div></a>' for k,v in CATS.items())
    feat = [p for p in PROMPTS if p.get('featured')][:6]
    if len(feat) < 6:
        for p in PROMPTS:
            if p not in feat:
                feat.append(p)
            if len(feat) >= 6: break
    body = f'''
<section class="hero">
<div class="pill-row"><span class="pill">🧠 System prompts</span><span class="pill">📋 Cursor rules</span><span class="pill">⚡ Vibe coding</span><span class="pill">🎮 Game dev</span></div>
<h1>Copy-ready prompts<br>for better agents.</h1>
<p>A free library of {len(PROMPTS)} original prompts and configs — system prompts, Cursor rules, custom instructions, agent task templates and more. No sign-up. Hit copy and go.</p>
<form class="search-hero" id="home-search" data-action="prompts/" role="search">
<input id="home-q" type="search" name="q" placeholder="Search prompts, e.g. “code review”, “platformer”, “changelog”" aria-label="Search prompts">
<button class="btn btn-primary" type="submit">Search the library</button>
</form>
</section>
<section class="section"><h2>Browse by category</h2><div class="cat-grid">{cats_html}</div></section>
<section class="section"><h2>Featured prompts</h2><div class="grid">{''.join(card(p,'') for p in feat)}{SPONSOR('')}</div></section>
<section class="section card"><h2>Get the daily AI agent changelog</h2><p class="muted">New agent tools, model updates and workflow changes in a 3-minute read. Free.</p>
<form class="newsletter" action="{NEWS}" method="get" target="_blank"><input type="email" name="email" placeholder="you@example.com" aria-label="Email address" required><button class="btn btn-primary" type="submit">Subscribe free</button></form></section>
<section class="section"><h2>Also from Cloudy</h2><div class="sister"><a class="card" href="{e(TOOLS_SITE)}"><strong>☁️ AI Tool Finder</strong><p class="muted" style="margin:.4rem 0 0">A 30-second quiz that matches you with the right AI tools for coding, agents, game dev and more.</p></a>
<a class="card" href="{NEWS}" target="_blank" rel="noopener"><strong>✉️ Cloudy newsletter</strong><p class="muted" style="margin:.4rem 0 0">The daily AI agent changelog, plus new prompts from this library.</p></a></div></section>
<section class="section faq"><h2>FAQ</h2>{''.join(f'<details><summary>{e(q)}</summary><p class="muted">{e(a)}</p></details>' for q,a in faqs)}</section>'''
    ld = [{"@context":"https://schema.org","@type":"WebSite","name":SITE,"url":BASE+'/',"description":"Free library of original AI agent prompts and configs.","publisher":ORG,
           "potentialAction":{"@type":"SearchAction","target":BASE+"/prompts/?q={search_term_string}","query-input":"required name=search_term_string"}},
          {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]},
          {"@context":"https://schema.org", **ORG}]
    page('', f'{SITE}: Copy-Ready AI Agent Prompts & Configs', f'A free library of {len(PROMPTS)} original prompts and agent configs for Cursor, Claude, ChatGPT and more. System prompts, rules files, vibe-coding prompts and game-dev templates.', body, '', ld); urls.append(('', '1.0'))
    # ---- library
    opts = ''.join(f'<option value="{k}">{e(v)}</option>' for k,v in CATS.items())
    tools = ''.join(f'<option value="{e(w)}">{e(w)}</option>' for w in works_options())
    body = f'''<p class="crumbs"><a href="../">Home</a> / Library</p>
<section class="hero" style="padding-top:1.5rem"><h1>All prompts</h1><p>Search and filter {len(PROMPTS)} original, copy-ready prompts and agent configs.</p></section>
<div class="filters"><input id="f-q" type="search" placeholder="Search prompts, e.g. “review”, “godot”, “changelog”" aria-label="Search">
<select id="f-cat" aria-label="Category"><option value="">All categories</option>{opts}</select>
<select id="f-tool" aria-label="Works with"><option value="">Any tool</option>{tools}</select></div>
<p class="muted" id="dir-count">{len(PROMPTS)} prompts</p>
<div class="grid" id="dir-grid">{''.join(card(p,'../') for p in PROMPTS)}</div>
<p class="empty" id="dir-empty" hidden>No prompts match those filters. Try a broader search.</p>
<div class="section">{SPONSOR('../')}</div>'''
    ld = [{"@context":"https://schema.org","@type":"ItemList","name":"AI prompt library","numberOfItems":len(PROMPTS),
           "itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{BASE}/prompt/{p['id']}/","name":p['title']} for i,p in enumerate(PROMPTS)]}]
    page('prompts/', f'AI Prompt Library ({len(PROMPTS)} prompts, 2026) | Cloudy', f'Browse {len(PROMPTS)} original prompts and agent configs. Filter by category and the tool you use.', body, '../', ld); urls.append(('prompts/','0.9'))
    # ---- categories index
    body = f'<p class="crumbs"><a href="../">Home</a> / Categories</p><section class="hero" style="padding-top:1.5rem"><h1>Prompt categories</h1><p>Pick a lane. Every prompt is original Cloudy writing, ready to copy.</p></section><div class="cat-grid">' + \
        ''.join(f'<a class="card" href="{k}/"><strong>{e(v)}</strong><div class="count">{len(in_cat(k))} prompts</div><p class="muted" style="font-size:.85rem;margin:.4rem 0 0">{e(CAT_BLURB[k])}</p></a>' for k,v in CATS.items()) + '</div>'
    page('category/', 'Prompt Categories | Cloudy Prompt Library', 'Browse original AI prompts by category: system prompts, Cursor rules, custom instructions, agent templates, vibe coding, game dev, review and research.', body, '../'); urls.append(('category/','0.8'))
    for k, v in CATS.items():
        lst = in_cat(k)
        body = f'''<p class="crumbs"><a href="../../">Home</a> / <a href="../">Categories</a> / {e(v)}</p>
<section class="hero" style="padding-top:1.5rem"><h1>{e(v)}</h1><p>{e(CAT_BLURB[k])} {len(lst)} copy-ready prompts.</p>
<div><a class="btn btn-primary" href="../../prompts/?cat={k}">Filter the full library</a></div></section>
<div class="grid">{''.join(card(p,'../../') for p in lst)}{SPONSOR('../../')}</div>'''
        ld = [{"@context":"https://schema.org","@type":"ItemList","name":v,"numberOfItems":len(lst),
               "itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{BASE}/prompt/{p['id']}/","name":p['title']} for i,p in enumerate(lst)]},
              {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":BASE+'/'},{"@type":"ListItem","position":2,"name":"Categories","item":BASE+'/category/'},{"@type":"ListItem","position":3,"name":v,"item":f"{BASE}/category/{k}/"}]}]
        page(f'category/{k}/', f'{v} Prompts (2026) | Cloudy', f'{CAT_BLURB[k]} {len(lst)} original, copy-ready prompts.', body, '../../', ld); urls.append((f'category/{k}/','0.8'))
    # ---- prompt pages
    for p in PROMPTS:
        prim = p['category']
        alts = [x for x in PROMPTS if x['id'] != p['id'] and x['category'] == prim][:4]
        catlink = f'<a class="badge" href="../../category/{prim}/">{e(CATS.get(prim, prim))}</a>'
        tools = ' '.join(f'<span class="badge">{e(w)}</span>' for w in p.get('worksWith', []))
        tags = ' '.join(f'<span class="badge">{e(t)}</span>' for t in p.get('tags', []))
        body_esc = e(p['body'])
        body = f'''<p class="crumbs"><a href="../../">Home</a> / <a href="../../category/{prim}/">{e(CATS[prim])}</a> / {e(p["title"])}</p>
<section class="hero" style="padding-top:1.5rem"><h1>{e(p["title"])}</h1><p>{e(p["summary"])}</p>
<div>{catlink} {tools}</div>
<div class="btn-row"><button type="button" class="btn btn-primary" data-copy-target="#prompt-body">Copy prompt</button>
<a class="btn btn-secondary" href="../../prompts/">Back to library</a></div></section>
<section class="section"><h2>How to use it</h2><p class="how-to">{e(p["howToUse"])}</p>
<div class="kv"><div><strong>Works with</strong><span>{e(", ".join(p.get("worksWith", [])))}</span></div>
<div><strong>Tags</strong><span>{tags or "—"}</span></div></div></section>
<section class="section"><h2>The prompt</h2>
<div class="prompt-wrap">
<button type="button" class="btn btn-secondary btn-sm copy-btn" data-copy-target="#prompt-body">Copy</button>
<pre class="prompt" id="prompt-body">{body_esc}</pre>
</div></section>
<section class="section related"><h2>Related prompts</h2><div class="grid">{''.join(card(a,'../../') for a in alts)}</div></section>
<section class="section card"><h2>Get the daily AI agent changelog</h2><p class="muted">New agent tools, model updates and a fresh prompt from this library, in a 3-minute read.</p>
<form class="newsletter" action="{NEWS}" method="get" target="_blank"><input type="email" name="email" placeholder="you@example.com" aria-label="Email address" required><button class="btn btn-primary" type="submit">Subscribe free</button></form></section>
<p class="disclaimer">Original Cloudy writing. Free to use and adapt. Review model output before you ship it.</p>'''
        ld = [{"@context":"https://schema.org","@type":"TechArticle","headline":p['title'],"name":p['title'],"url":f"{BASE}/prompt/{p['id']}/",
               "description":p['summary'],"author":{"@type":"Organization","name":"Cloudy"},"publisher":ORG,"dateModified":D.get('generatedAt', TODAY),
               "keywords":", ".join(p.get('tags', [])),"articleSection":CATS.get(prim, prim)},
              {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":BASE+'/'},{"@type":"ListItem","position":2,"name":CATS[prim],"item":f"{BASE}/category/{prim}/"},{"@type":"ListItem","position":3,"name":p['title'],"item":f"{BASE}/prompt/{p['id']}/"}]}]
        page(f'prompt/{p["id"]}/', f'{p["title"]} (Copy-Ready Prompt) | Cloudy', f'{p["title"]}: {p["summary"]}'[:300], body, '../../', ld, 'article'); urls.append((f'prompt/{p["id"]}/','0.7'))
    # ---- about
    body = f'''<p class="crumbs"><a href="../">Home</a> / About</p><section class="section prose"><h1>About Cloudy</h1>
<p>Cloudy builds free, fast tools for people into AI, AI agents, vibe coding, tech and video games. The Prompt Library is a curated set of {len(PROMPTS)} original prompts and agent configs you can copy into ChatGPT, Claude, Cursor and other tools.</p>
<p>Looking for the right product instead of a prompt? Try the <a href="{e(TOOLS_SITE)}">Cloudy AI Tool Finder</a> — a 30-second quiz and directory of real AI tools.</p>
<h2>How we write prompts</h2><ul><li>Every prompt is original Cloudy writing. We do not copy copyrighted prompt packs or vendor system prompts.</li><li>Each one is written to be useful on its own: a clear job, constraints, and a defined output.</li><li>They are starting points. Adapt the bracketed placeholders to your project.</li></ul>
<h2>Affiliate disclosure</h2><p>Some outbound links may be affiliate links, which means Cloudy may earn a commission at no extra cost to you. Affiliate links are marked with <code>rel="sponsored"</code> and never change how prompts are written or featured.</p>
<h2 id="sponsor">Sponsor Cloudy</h2><p>Want your AI tool in front of builders and vibe coders? Sponsor slots are available on the site and in the Cloudy newsletter. Send a DM to <a href="https://x.com/{X_HANDLE}" target="_blank" rel="noopener">@{X_HANDLE}</a> on X.</p>
<h2>Corrections</h2><p>Spotted a broken prompt or want to suggest a category? DM <a href="https://x.com/{X_HANDLE}" target="_blank" rel="noopener">@{X_HANDLE}</a> and we'll take a look.</p>
<h2>Newsletter</h2><p><a href="{NEWS}" target="_blank" rel="noopener">Subscribe to the Cloudy newsletter</a> for the daily AI agent changelog.</p></section>'''
    page('about/', 'About Cloudy & Disclosure | Cloudy Prompt Library', 'How Cloudy writes original prompts, affiliate disclosure and sponsorship info.', body, '../'); urls.append(('about/','0.4'))
    # ---- 404
    pre = urlparse(BASE).path.rstrip('/') + '/'
    page('404.html', 'Page not found | Cloudy Prompt Library', 'This page does not exist.', f'<section class="hero"><h1>Lost in the clouds ☁️</h1><p>That page doesn\'t exist. Try the library or pick a category.</p><div><a class="btn btn-primary" href="{pre}">Go home</a> <a class="btn btn-secondary" href="{pre}prompts/">Browse prompts</a></div></section>', pre)
    # ---- sitemap / robots / llms
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{BASE}/{u}</loc><lastmod>{TODAY}</lastmod><priority>{p}</priority></url>\n' for u,p in urls) + '</urlset>\n'
    (out/'sitemap.xml').write_text(sm)
    (out/'robots.txt').write_text(f'User-agent: *\nAllow: /\n\n# AI crawlers welcome\nUser-agent: GPTBot\nAllow: /\nUser-agent: OAI-SearchBot\nAllow: /\nUser-agent: ChatGPT-User\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\nUser-agent: Claude-SearchBot\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')
    L = [f'# {SITE}', '', f'> Free library of original, copy-ready AI agent prompts and configs. {len(PROMPTS)} prompts across {len(CATS)} categories. Run by Cloudy.', '',
         'Data is available as JSON at ' + BASE + '/data/prompts.json (fields: id, title, category, summary, howToUse, worksWith, tags, body).', '', '## Main pages',
         f'- [Home]({BASE}/): search and featured prompts', f'- [Library]({BASE}/prompts/): searchable directory', f'- [Full prompt list for LLMs]({BASE}/llms-full.txt)', f'- [About & disclosure]({BASE}/about/)', f'- [Cloudy AI Tool Finder]({TOOLS_SITE})', '', '## Categories']
    L += [f'- [{v}]({BASE}/category/{k}/): {CAT_BLURB[k]}' for k,v in CATS.items()]
    L += ['', '## Prompts'] + [f'- [{p["title"]}]({BASE}/prompt/{p["id"]}/): {p["summary"]}' for p in PROMPTS]
    (out/'llms.txt').write_text('\n'.join(L)+'\n')
    F = [f'# {SITE}: full prompt text', f'Updated {D.get("generatedAt", TODAY)}. {D.get("disclaimer","")}', '']
    for k,v in CATS.items():
        F += [f'## {v}', CAT_BLURB[k], '']
        for p in in_cat(k):
            F += [f'### {p["title"]}', f'- Page: {BASE}/prompt/{p["id"]}/', f'- Works with: {", ".join(p.get("worksWith", []))}',
                  f'- Summary: {p["summary"]}', f'- How to use: {p["howToUse"]}', f'- Tags: {", ".join(p.get("tags", []))}', '', '```', p['body'], '```', '']
    (out/'llms-full.txt').write_text('\n'.join(F))
    print('built', len(urls), 'pages ->', out, 'BASE', BASE, 'prompts', len(PROMPTS), 'cats', len(CATS))
if __name__ == '__main__': build()
