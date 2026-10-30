#!/usr/bin/env python3
"""Compare what the generated wiki states with the mod's installed Defs.
usage: python3 check_wiki.py <docs dir> <mod 1.6 dir with Defs/ (and Patches/)> [--json out.json]
Checks every technique card on the tree pages (label, ranks, chakra per rank, cooldown per rank, class level, requirement tags,
description), every tree page title, and lists techniques that are in the mod but missing from the wiki (and the reverse).
Also scans every page for things that must never be in the wiki (the dev test suite and the showcase recorder).
Exit code 0 always; the report is the output."""
import os, re, sys, glob, json, html
import xml.etree.ElementTree as ET

if len(sys.argv) < 3:
    print(__doc__); sys.exit(0)
DOCS, MOD = sys.argv[1], sys.argv[2]
OUTJ = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None

# ───── installed defs (same inheritance handling as gen_wiki.py)
named, allel, defs = {}, [], {}
for f in sorted(glob.glob(os.path.join(MOD, 'Defs', '*.xml'))):
    try:
        for ch in ET.parse(f).getroot():
            allel.append(ch)
            if ch.get('Name'): named[ch.get('Name')] = ch
    except ET.ParseError as e:
        print('skip unreadable def file', os.path.basename(f), e)
def resolve(el, depth=0):
    par = named.get(el.get('ParentName') or '')
    if par is None or depth > 8: return
    resolve(par, depth + 1)
    have = {c.tag for c in el}
    for c in par:
        if c.tag not in have: el.append(c)
for ch in allel:
    if ch.findtext('defName'):
        resolve(ch); defs.setdefault(ch.tag, {})[ch.findtext('defName')] = ch
T = lambda tag: defs.get(tag, {})
trees, abilities, tiers = T('TaranMagicFramework.AbilityTreeDef'), T('TaranMagicFramework.AbilityDef'), T('TaranMagicFramework.AbilityTierDef')

# ───── the wiki's own formatting, copied from gen_wiki.py so the comparison is like for like
REQ_TEXT = {'bow': 'a bow, crossbow or sling', 'ranged': 'a ranged weapon', 'blade': 'a bladed weapon', 'stab': 'a thrusting weapon', 'staff': 'a staff or spear',
            'scythe': 'a scythe, glaive or axe', 'blunt': 'a blunt weapon', 'fan': 'a war fan', 'yoyo': 'a battle yo-yo', 'melee': 'a melee weapon',
            'unarmed': 'empty hands', 'instrument': 'a musical instrument', 'contract': 'a Blood Pact', 'shield': 'a shield', 'water': 'rain or water nearby',
            'earth': 'bare ground underfoot', 'bond': 'a Contract Bond partner'}
def rank_of(label):
    m = re.search(r'\(([SABCDE])\)\s*$', label or ''); return m.group(1) if m else None
def fmt(x): return f'{x:.0f}' if abs(x - round(x)) < 0.01 else f'{x:.1f}'
def cd_text(ticks):
    t = int(ticks or 0)
    if t <= 0: return 'none'
    if t < 2500: s = t / 60.0; return (f'{s:.1f}'.rstrip('0').rstrip('.') if s < 10 else f'{s:.0f}') + ' s'
    if t < 60000: h = t / 2500.0; return (f'{h:.1f}'.rstrip('0').rstrip('.')) + (' hour' if abs(h - 1) < 0.05 else ' hours')
    d = t / 60000.0; return (f'{d:.1f}'.rstrip('0').rstrip('.')) + (' day' if abs(d - 1) < 0.05 else ' days')
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
def tier_info(tn):
    t = tiers.get(tn)
    if t is None: return None
    ext = t.find("modExtensions/li[@Class='CassieKazeraikou.KZEffect']")
    kind = ext.findtext('kind') if ext is not None else None
    req = ext.findtext('requires') if ext is not None else None
    if req and req.startswith('mask:'): req_t = 'an ANBU ' + req[5:].replace(',', ' or ').lower() + ' mask'
    else: req_t = REQ_TEXT.get(req, req)
    def num(x, d=0):
        try: return float(t.findtext(x) or d)
        except ValueError: return d
    lvl = int(num('acquireRequirement/minLevel'))
    if not lvl:
        m = t.find('acquireRequirement/requiredMinimumLevels')
        if m is not None and len(m):
            try: lvl = int(float(m[0].text))
            except (TypeError, ValueError): pass
    if not kind and t.findtext('regenRate'): kind = 'toggle'
    return dict(label=t.findtext('label') or tn, rank=rank_of(t.findtext('label')), cost=num('energyCost'), cd=num('cooldownTicks'), lvl=lvl, kind=kind, req=req_t, drain=num('regenRate'))
def chakra(t):
    if t['kind'] == 'passive': return '–'
    parts = []
    if t['cost']: parts.append(fmt(t['cost']))
    if t['drain']: parts.append(f"{-t['drain'] * 60:.2f}/s while on")
    return ' + '.join(parts) or '0'
def expected(dn):
    a = abilities[dn]
    ti = [x for x in (tier_info(li.text) for li in a.findall('abilityTiers/li')) if x]
    passive = bool(ti) and all(t['kind'] == 'passive' for t in ti)
    rows = [] if passive else [(t['rank'] or '–', chakra(t), cd_text(t['cd']) if t['kind'] != 'passive' else '–', str(t['lvl'] or '–')) for t in ti]
    return dict(label=a.findtext('label') or dn, ranks=[t['rank'] for t in ti if t['rank']], rows=rows, passive=passive,
                passive_lvls=[f'{t["rank"] or "–"} {t["lvl"]}' for t in ti] if passive else [],
                reqs=sorted({'Needs ' + t['req'] for t in ti if t['req']}), desc=(a.findtext('description') or '').strip())

# ───── the wiki pages (cards are flat <details class="card unit"> blocks written by gen_wiki.py's tech_card)
TAG = re.compile(r'<[^>]+>')
def text(x): return re.sub(r'\s+', ' ', html.unescape(TAG.sub('', x or ''))).strip()
wiki = {}; page_of = {}; titles = {}
for f in sorted(glob.glob(os.path.join(DOCS, 'trees', '*.html'))):
    if f.endswith('index.html'): continue
    src = open(f, encoding='utf-8').read()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', src, re.S); titles[os.path.basename(f)] = text(m.group(1)) if m else ''
    for m in re.finditer(r'<details class="card unit" id="([^"]+)">(.*?)</details>', src, re.S):
        sid, body = m.group(1), m.group(2)
        h3 = re.search(r'<h3>(.*?)</h3>', body, re.S); h3 = h3.group(1) if h3 else ''
        label = text(h3.split('<span class="seals-r"')[0])
        ranks = re.findall(r'<span class="seal">([^<]*)</span>', h3)
        d = re.search(r'<div class="body"><p>(.*?)</p>', body, re.S)
        tags = [text(t) for t in re.findall(r'<span class="tag[^"]*">(.*?)</span>', body, re.S)]
        rows = []
        for tr in re.findall(r'<tr>(.*?)</tr>', body, re.S):
            tds = re.findall(r'<td>(.*?)</td>', tr, re.S)
            if len(tds) == 4: rows.append(tuple(text(x) for x in tds))
        meta = re.search(r'<p class="meta">(.*?)</p>', body, re.S)
        wiki[sid] = dict(id=sid, label=label, ranks=ranks, rows=rows, tags=tags, desc=text(d.group(1)) if d else '', meta=text(meta.group(1)) if meta else '')
        page_of[sid] = os.path.basename(f)
def label_wo_seals(c): return c['label']

# ───── compare
by_slug = {slug(dn): dn for dn in abilities}
issues = {'label': [], 'ranks': [], 'chakra': [], 'cooldown': [], 'class level': [], 'requirements': [], 'description': [], 'tree title': [],
          'missing from wiki': [], 'not in mod': [], 'forbidden content': []}
ours = {dn for dn in abilities if dn.startswith(('NF_', 'KZ_'))}
in_tree = set()
for tn, t in trees.items():
    pass
for sid, c in wiki.items():
    dn = by_slug.get(sid)
    where = page_of[sid]
    if dn is None: issues['not in mod'].append(f'{where}: card "{label_wo_seals(c)}" (#{sid}) has no technique in the installed defs'); continue
    e = expected(dn); in_tree.add(dn)
    wl = label_wo_seals(c)
    if wl != e['label']: issues['label'].append(f'{dn} ({where}): wiki "{wl}" / mod "{e["label"]}"')
    if c['ranks'] != e['ranks']: issues['ranks'].append(f'{dn} ({where}): wiki {"/".join(c["ranks"]) or "-"} / mod {"/".join(e["ranks"]) or "-"}')
    rows = [r for r in c['rows'] if len(r) == 4]
    if e['passive']:
        if rows: issues['chakra'].append(f'{dn} ({where}): wiki shows a cost table, mod says passive')
    else:
        if len(rows) != len(e['rows']): issues['ranks'].append(f'{dn} ({where}): wiki has {len(rows)} rank rows, mod has {len(e["rows"])}')
        for i, (wr, er) in enumerate(zip(rows, e['rows'])):
            rk = er[0]
            if wr[1] != er[1]: issues['chakra'].append(f'{dn} rank {rk} ({where}): wiki {wr[1]} / mod {er[1]}')
            if wr[2] != er[2]: issues['cooldown'].append(f'{dn} rank {rk} ({where}): wiki {wr[2]} / mod {er[2]}')
            if wr[3] != er[3]: issues['class level'].append(f'{dn} rank {rk} ({where}): wiki {wr[3]} / mod {er[3]}')
    wreq = sorted({t.strip() for t in c['tags'] if t.strip().startswith('Needs ')})
    if wreq != e['reqs']: issues['requirements'].append(f'{dn} ({where}): wiki {wreq or "none"} / mod {e["reqs"] or "none"}')
    if c['desc'] != re.sub(r'\s+', ' ', e['desc']).strip():
        issues['description'].append(f'{dn} ({where}): description differs')
# every NF/KZ technique that sits in a tree should have a card
for dn in sorted(ours - in_tree):
    a = abilities[dn]
    tr = [li.text for li in a.findall('abilityTrees/li')]
    if tr and any(t in trees for t in tr): issues['missing from wiki'].append(f'{dn} "{a.findtext("label")}" in {", ".join(tr)}')
# tree page titles
for tn, t in trees.items():
    fn = slug(tn) + '.html'
    if fn in titles and titles[fn] and titles[fn] != (t.findtext('label') or tn):
        issues['tree title'].append(f'{fn}: wiki "{titles[fn]}" / mod "{t.findtext("label")}"')
# things the wiki must never show
FORBID = [r'test suite', r'self-?test', r'showcase', r'ShareX', r'Test: ', r'NFTestSuite', r'NFShowcase', r'timeline_\d', r'cut_showcase']
for f in sorted(glob.glob(os.path.join(DOCS, '**', '*.html'), recursive=True)) + sorted(glob.glob(os.path.join(DOCS, '**', '*.js'), recursive=True)):
    txt = open(f, encoding='utf-8', errors='replace').read()
    for pat in FORBID:
        for m in re.finditer(pat, txt, re.I):
            ctx = re.sub(r'<[^>]+>', ' ', txt[max(0, m.start() - 60): m.end() + 60]); ctx = re.sub(r'\s+', ' ', ctx).strip()
            issues['forbidden content'].append(f'{os.path.relpath(f, DOCS)}: "{ctx}"'); break

total = sum(len(v) for v in issues.values())
print(f'wiki check: {len(wiki)} technique cards on {len(titles)} tree pages vs {len(ours)} NF/KZ techniques in the installed defs: {total} mismatch(es)')
for k, v in issues.items():
    if not v: continue
    print(f'\n== {k}: {len(v)}')
    for line in v[:400]: print('  ' + line)
    if len(v) > 400: print(f'  … {len(v) - 400} more')
if OUTJ: json.dump(issues, open(OUTJ, 'w'), indent=1)
