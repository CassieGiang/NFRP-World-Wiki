#!/usr/bin/env python3
"""NFRP World wiki: the Animations page, built from animations.json (one entry per clip; the clips live in docs/anim/).
Run on its own to (re)write docs/animations.html and add the Animations tab to every page's nav:
    python3 wiki-src/animations.py docs
gen_wiki.py also calls build() so a full regeneration keeps the page."""
import os, sys, json, re, glob, html
E = lambda s: html.escape(s or '', quote=True)
HERE = os.path.dirname(os.path.abspath(__file__))

def body():
    m = json.load(open(os.path.join(HERE, 'animations.json'), encoding='utf-8'))
    groups = []
    for c in m['clips']:
        if not groups or groups[-1][0] != c['group']: groups.append((c['group'], []))
        groups[-1][1].append(c)
    toc = ''.join(f'<a href="#{re.sub(r"[^a-z0-9]+", "-", g.lower()).strip("-")}">{E(g)}</a>' for g, _ in groups)
    out = ['<h1>Animations</h1>',
           f'<p class="lead">{E(m["intro"])}</p>',
           '<div class="toolbar"><input type="search" placeholder="Filter animations" aria-label="Filter animations" autocomplete="off" id="animq"></div>',
           f'<div class="toc">{toc}</div>']
    for g, cs in groups:
        gid = re.sub(r'[^a-z0-9]+', '-', g.lower()).strip('-')
        cards = ''.join(
            f'<figure class="anim" data-n="{E((c["label"] + " " + c.get("tree", "")).lower())}">'
            f'<video src="anim/{E(c["file"])}" muted loop playsinline preload="none" poster="anim/{E(c["poster"])}" aria-label="{E(c["label"])}"></video>'
            f'<figcaption><b>{E(c["label"])}</b>{("<small>" + E(c["tree"]) + "</small>") if c.get("tree") else ""}</figcaption></figure>'
            for c in cs)
        out.append(f'<h2 id="{gid}">{E(g)} <small>{len(cs)}</small></h2><div class="grid anims">{cards}</div>')
    out.append('''<script>
(function(){var vs=[].slice.call(document.querySelectorAll('figure.anim video'));
var io='IntersectionObserver' in window?new IntersectionObserver(function(es){es.forEach(function(e){var v=e.target;if(e.isIntersecting){v.preload='auto';var p=v.play();if(p&&p.catch)p.catch(function(){});}else v.pause();});},{rootMargin:'200px'}):null;
vs.forEach(function(v){if(io)io.observe(v);else{v.preload='auto';v.autoplay=true;}v.addEventListener('click',function(){v.paused?v.play():v.pause();});});
var q=document.getElementById('animq');if(q)q.addEventListener('input',function(){var s=q.value.trim().toLowerCase();document.querySelectorAll('figure.anim').forEach(function(f){f.style.display=!s||f.dataset.n.indexOf(s)>=0?'':'none';});});})();
</script>''')
    return ''.join(out), m

CSS = ('.grid.anims{grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}'
       'figure.anim{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden}'
       'figure.anim video{display:block;width:100%;aspect-ratio:16/9;background:#111;cursor:pointer;object-fit:cover}'
       'figure.anim figcaption{padding:8px 10px}figure.anim figcaption b{display:block;font-family:"Shippori Mincho",Georgia,serif}'
       'figure.anim figcaption small{color:var(--muted)}')

def build(page):
    b, m = body()
    page('animations.html', 'Animations', b, desc='Every hand-made technique animation, recorded in game.')
    return m

if __name__ == '__main__':
    out = sys.argv[1]
    b, m = body()
    # reuse an existing page as the shell: swap <main> and the title, mark the tab
    tpl = open(os.path.join(out, 'items.html'), encoding='utf-8').read()
    doc = re.sub(r'<main>.*</main>', lambda _: '<main>' + b + '</main>', tpl, flags=re.S)
    doc = re.sub(r'<title>.*?</title>', '<title>Animations · NFRP World</title>', doc).replace('<a href="items.html" class=on>', '<a href="items.html">')
    open(os.path.join(out, 'animations.html'), 'w', encoding='utf-8').write(doc)
    # the tab on every page (after Factions), marked "on" only on the animations page
    for f in glob.glob(os.path.join(out, '**', '*.html'), recursive=True):
        s = open(f, encoding='utf-8').read()
        if 'animations.html">Animations</a>' in s and not f.endswith('animations.html'): continue
        up = '../' * os.path.relpath(f, out).count(os.sep)
        s = re.sub(r'<a href="[./]*animations\.html"[^>]*>Animations</a>', '', s)
        on = ' class=on' if os.path.relpath(f, out) == 'animations.html' else ''
        s = re.sub(r'(<a href="' + re.escape(up) + r'factions\.html"[^>]*>Factions</a>)', r'\1<a href="' + up + 'animations.html"' + on + '>Animations</a>', s, count=1)
        open(f, 'w', encoding='utf-8').write(s)
    css = os.path.join(out, 'assets', 'style.css'); s = open(css, encoding='utf-8').read()
    if 'figure.anim' not in s: open(css, 'a', encoding='utf-8').write('\n' + CSS + '\n')
    print('animations:', len(m['clips']))
