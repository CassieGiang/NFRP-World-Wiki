#!/usr/bin/env python3
"""NFRP World wiki: a static site generated from the mod's own Defs and textures.
usage: python3 gen_wiki.py <mod_src> <out>
  mod_src: folder with Defs/, Patches/, About/ and img/ (thumbnails made from Textures/, same relative paths)
Writes a plain HTML site (no build step) for GitHub Pages."""
import os, sys, re, json, glob, shutil, html
import xml.etree.ElementTree as ET

SRC, OUT = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
E = lambda s: html.escape(s or '', quote=True)

# ───────────────────────────── read defs
defs = {}; named = {}
allel = []
for f in sorted(glob.glob(os.path.join(SRC, 'Defs', '*.xml'))):
    try:
        for ch in ET.parse(f).getroot():
            allel.append(ch)
            if ch.get('Name'): named[ch.get('Name')] = ch
    except ET.ParseError as e:
        print('skip', f, e)
# resolve XML inheritance (Name / ParentName) for the fields we read: copy missing children from parents
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

def T(tag): return defs.get(tag, {})
trees, abilities, tiers = T('TaranMagicFramework.AbilityTreeDef'), T('TaranMagicFramework.AbilityDef'), T('TaranMagicFramework.AbilityTierDef')
things, seals, genes = T('ThingDef'), T('CassieNFRP.SealDef'), T('GeneDef')
# gene labels from World of Naruto and NFRP World (WoN's genes aren't in the wiki source files)
import json as _json
try: GENE_LABELS = _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gene_labels.json'), encoding='utf-8'))
except Exception: GENE_LABELS = {}
def gene_label(g):
    gd = genes.get(g)
    return (gd.findtext('label') if gd is not None else None) or GENE_LABELS.get(g) or g

# which class each tree belongs to (from patches)
tree_class = {}
for f in glob.glob(os.path.join(SRC, 'Patches', '*.xml')):
    try: root = ET.parse(f).getroot()
    except ET.ParseError: continue
    for op in root.iter('Operation'):
        xp = op.findtext('xpath') or ''
        m = re.search(r'AbilityClassDef\[defName="([^"]+)"\]/abilityTrees', xp)
        if m:
            for li in op.findall('value/li'): tree_class[li.text] = m.group(1)

def img(path, tree=False):
    if not path: return None
    rel = path + ('.jpg' if tree else '.png')
    return rel if os.path.exists(os.path.join(SRC, 'img', rel)) else None

RANKS = 'DCBAS'
def rank_of(label):
    m = re.search(r'\(([SABCDE])\)\s*$', label or '')
    return m.group(1) if m else None

def group_of(t):
    if t.startswith(('NF_Clan', 'KZ_Clan')) or t in ('NF_NinjutsuCrystal', 'NF_NinjutsuPaper'): return 'Clans and bloodlines'
    if t.startswith('NF_Arts'): return 'Elements'
    if t.startswith('NF_Gen'): return 'Genjutsu'
    if t.startswith('NF_Style'): return 'Fighting and weapon styles'
    if t.startswith('NF_UTai'): return 'Universal taijutsu'
    if t.startswith(('NF_Prof', 'NF_Anbu')): return 'Professions and ANBU'
    if t.startswith(('NF_Craft', 'NF_ArtEnh', 'NF_Alch')): return 'Crafting arts'
    if t == 'NF_Medical': return 'Medical'
    if t.startswith('NF_Arch'):   # archive trees (u41/u42) go by the class they sit in
        c = tree_class.get(t)
        if t == 'NF_ArchMedicalSkill': return 'Medical'
        if c == 'WN_Clan': return 'Clans and bloodlines'
        if c == 'WN_Genjutsu': return 'Genjutsu'
        if c == 'WN_Taijutsu': return 'Fighting and weapon styles'
        if t[7:].startswith(('Skill', 'Onimusha', 'Veritas', 'ArtisanPaths', 'Troll')): return 'Skills and beast arts'
    return 'Universal ninjutsu'
GROUPS = ['Clans and bloodlines', 'Elements', 'Genjutsu', 'Fighting and weapon styles', 'Universal taijutsu', 'Universal ninjutsu',
          'Medical', 'Professions and ANBU', 'Skills and beast arts', 'Crafting arts']

KIND_TEXT = {'toggle': 'Toggle: drains chakra while on', 'passive': 'Passive (always on, no button)', 'nfsummon': 'Summon', 'fabled': 'Summon', 'cone': 'Area: cone', 'zone': 'Area: zone',
             'strike': 'Single target', 'hediff': 'Status', 'areahediff': 'Area status', 'heal': 'Healing', 'massheal': 'Area healing',
             'shield': 'Barrier', 'dash': 'Movement', 'bind': 'Bind', 'tame': 'Taming', 'capture': 'Capture', 'gas': 'Gas cloud'}
REQ_TEXT = {'bow': 'a bow, crossbow or sling', 'ranged': 'a ranged weapon', 'blade': 'a bladed weapon', 'stab': 'a thrusting weapon', 'staff': 'a staff or spear',
            'scythe': 'a scythe, glaive or axe', 'blunt': 'a blunt weapon', 'fan': 'a war fan', 'yoyo': 'a battle yo-yo', 'melee': 'a melee weapon',
            'unarmed': 'empty hands', 'instrument': 'a musical instrument', 'contract': 'a Blood Pact', 'shield': 'a shield', 'water': 'rain or water nearby',
            'earth': 'bare ground underfoot', 'bond': 'a Contract Bond partner'}

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
    gn = [g.text for g in t.findall('acquireRequirement/requiredGenes/li')]
    if not kind and t.findtext('regenRate'): kind = 'toggle'
    return dict(label=t.findtext('label') or tn, rank=rank_of(t.findtext('label')), cost=num('energyCost'), cd=num('cooldownTicks') / 60.0,
                lvl=lvl, kind=kind, req=req_t, genes=gn, drain=num('regenRate'))

def tree_gate(el):
    g = el.find("modExtensions/li[@Class='CassieNFRP.NFGeneTree']")
    if g is None: return None
    if g.findtext('gene'):
        return 'Unlocks for pawns with the ' + gene_label(g.findtext('gene')) + ' gene.'
    if g.findtext('parentTree'):
        pt = trees.get(g.findtext('parentTree'))
        if pt is not None: return 'Unlocks once the pawn has ' + pt.findtext('label') + '.'
        ptn = g.findtext('parentTree'); m_ = re.match(r'WN_(Ninjutsu|Clan)?(\w+)', ptn or '')
        return 'Unlocks once the pawn has World of Naruto\'s ' + (re.sub(r'(?<!^)([A-Z])', r' \1', m_.group(2)).lower() + ' tree' if m_ else ptn) + '.'
    return None

NOTE = {
    'NF_Medical': 'Every ninja can learn it, but only up to D rank. Higher ranks need a Medical Specialist build.',
    'NF_ProfSensor': 'Counts as a medical tree: D rank only, unless the pawn has a Medical Specialist build.',
    'NF_ProfSoulcaster': 'Counts as a medical tree: D rank only, unless the pawn has a Medical Specialist build.',
}
by_tree = {}
for dn, a in abilities.items():
    for li in a.findall('abilityTrees/li'):
        by_tree.setdefault(li.text, []).append(dn)

def pos(a):
    m = re.findall(r'[-\d.]+', a.findtext('uiPosition') or '')
    return (float(m[1]), float(m[0])) if len(m) >= 2 else (9, 9)

# ───────────────────────────── page shell
NAV = [('index.html', 'Home'), ('guides/index.html', 'Guides'), ('trees/index.html', 'Technique trees'), ('items.html', 'Items'),
       ('seals.html', 'Seals'), ('creatures.html', 'Creatures'), ('factions.html', 'Factions')]

def page(path, title, body, depth=None, desc=''):
    depth = path.count('/') if depth is None else depth
    up = '../' * depth
    nav = ''.join(f'<a href="{up}{h}"{" class=on" if h == path else ""}>{E(l)}</a>' for h, l in NAV)
    doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · NFRP World</title><meta name="description" content="{E(desc or title)}">
<link rel="stylesheet" href="{up}assets/style.css"><link rel="icon" href="{up}assets/icon.png">
</head><body>
<header><a class="brand" href="{up}index.html"><img src="{up}assets/icon.png" alt=""><span>NFRP World</span></a>
<nav>{nav}</nav>
<div class="search"><input id="q" type="search" placeholder="Search techniques, items, seals…" autocomplete="off" aria-label="Search"><div id="hits"></div></div>
</header>
<main>{body}</main>
<footer>NFRP World is a RimWorld mod by Cassie, an add-on for World of Naruto and Taran Magic Framework. Technique and clan material from the Naruto Forum Role-play (NFRP) community archive. The Kazeraikou clan was created by Marii from NFRP and is used with her permission. This wiki is generated from the mod's files.</footer>
<script>window.ROOT="{up}";</script><script src="{up}assets/search.js"></script>
</body></html>'''
    p = os.path.join(OUT, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(doc)

def icon(path, up, cls='ic', tree=False):
    i = img(path, tree)
    return f'<img class="{cls}" src="{up}img/{E(i)}" alt="" loading="lazy">' if i else f'<span class="{cls} blank"></span>'

def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

index = []   # search index: [label, kind, url, extra]

# ───────────────────────────── trees
def tech_card(dn, up, url_tree):
    a = abilities[dn]
    label = a.findtext('label') or dn
    ti = [x for x in (tier_info(li.text) for li in a.findall('abilityTiers/li')) if x]
    ranks = '/'.join(t['rank'] for t in ti if t['rank'])
    passive = ti and all(t['kind'] == 'passive' for t in ti)
    rows = ''
    if not passive:
        rows = ''.join(f'<tr><td>{E(t["rank"] or "–")}</td><td>{(f"{t['cost']:.0f}" if t["cost"] or not t["drain"] else f"{-t['drain']*60:.2f}/s")}</td><td>{t["cd"]:.0f} s</td><td>{t["lvl"] or "–"}</td></tr>' for t in ti)
        rows = f'<table class="tiers"><tr><th>Rank</th><th>Chakra</th><th>Cooldown</th><th>Class level</th></tr>{rows}</table>'
    else:
        rows = '<p class="meta">Learn at class level ' + ', '.join(f'{t["rank"]} {t["lvl"]}' for t in ti) + '</p>'
    kinds = sorted({KIND_TEXT.get(t['kind'], '') for t in ti if t['kind']} - {''})
    reqs = sorted({t['req'] for t in ti if t['req']})
    tags = ''.join(f'<span class="tag">{E(k)}</span>' for k in kinds) + ''.join(f'<span class="tag req">Needs {E(r)}</span>' for r in reqs)
    index.append([label, 'Technique', url_tree + '#' + slug(dn), ranks])
    return f'''<article class="tech" id="{slug(dn)}">{icon(a.findtext('uiSkillIcon'), up)}
<div><h3>{E(label)} <span class="rk">{E(ranks)}</span></h3><p>{E(a.findtext('description'))}</p>
<div class="tags">{tags}</div>{rows}</div></article>'''

tree_list = {}
for tdn, t in trees.items():
    if tdn not in by_tree: continue
    tree_list.setdefault(group_of(tdn), []).append(tdn)

for g in GROUPS:
    for tdn in sorted(tree_list.get(g, []), key=lambda x: trees[x].findtext('label') or x):
        t = trees[tdn]; path = f'trees/{slug(tdn)}.html'; up = '../'
        techs = sorted(by_tree[tdn], key=lambda d: pos(abilities[d]))
        gate = tree_gate(t)
        open_t = (t.findtext('unlockedByDefault') or '').lower() == 'true'
        if not gate:
            gl = set()
            for d in techs:
                for li in abilities[d].findall('abilityTiers/li'):
                    ti_ = tier_info(li.text)
                    if ti_: gl |= set(ti_['genes'])
            if gl: gate = 'Needs the ' + ' or '.join(gene_label(g) for g in sorted(gl)) + ' gene.'
        note = NOTE.get(tdn) or gate or ('Open to every ninja. How high a ninja can go depends on their ninja build.' if open_t else 'Learned from technique scrolls, mission rewards, written scrolls and scroll merchants; some NPC ninja know it. It counts toward the ninja build like other trees.' if tdn.startswith('NF_Arch') else 'Unlocks through World of Naruto\'s own trees, a gene, a build choice or a profession.')
        bg = img(t.findtext('backgroundTexPath'), True)
        hero = f'<img class="treebg" src="{up}img/{E(bg)}" alt="">' if bg else ''
        body = f'''<div class="hero tree">{hero}<div><p class="crumb"><a href="index.html">Technique trees</a> › {E(g)}</p>
<h1>{E(t.findtext('label'))}</h1><p class="lead">{len(techs)} techniques · {E(tree_class.get(tdn, '').replace('WN_', '') or 'class')} tab</p><p>{E(note)}</p></div></div>
<section class="techs">{''.join(tech_card(d, up, path) for d in techs)}</section>'''
        page(path, t.findtext('label'), body, desc=f'{t.findtext("label")}: all {len(techs)} techniques of the NFRP World tree.')
        index.append([t.findtext('label'), 'Tree', path, g])

cards = ''
for g in GROUPS:
    lst = sorted(tree_list.get(g, []), key=lambda x: trees[x].findtext('label') or x)
    if not lst: continue
    cards += f'<h2 id="{slug(g)}">{E(g)} <small>{len(lst)} trees</small></h2><div class="grid trees">'
    for tdn in lst:
        t = trees[tdn]; bg = img(t.findtext('backgroundTexPath'), True)
        cards += f'<a class="treecard" href="{slug(tdn)}.html">{"<img src=../img/" + E(bg) + " alt=\"\" loading=lazy>" if bg else "<span class=blank></span>"}<b>{E(t.findtext("label"))}</b><small>{len(by_tree[tdn])} techniques</small></a>'
    cards += '</div>'
ntech = sum(len(by_tree[t]) for g in tree_list.values() for t in g)
page('trees/index.html', 'Technique trees', f'<h1>Technique trees</h1><p class="lead">{sum(len(v) for v in tree_list.values())} trees and {ntech} techniques, read straight from the mod.</p>{cards}')

# ───────────────────────────── items
ITEM_GROUPS = [('Brews, pills and drugs', ('MakeableDrugBase', 'DrugPillBase', 'DrugBase')), ('Bombs and grenades', ('BaseMakeableGrenade',)),
               ('Apparel and gear', ('Apparel', 'Headgear', 'Armor')), ('Weapons and instruments', ('BaseWeapon', 'BaseMelee', 'BaseHumanMakeableGun', 'Weapon')),
               ('Workbenches and buildings', ('BenchBase', 'BuildingBase', 'Building', 'DoorBase', 'StorageShelfBase', 'TableGatherSpotBase', 'FurnitureBase', 'FurnitureWithQualityBase', 'AnimalBedFurnitureBase')), ('Other items', ('ResourceBase', 'ResourceVerbBase', 'BodyPartBase', 'OrganicProductBase'))]
items = {g: [] for g, _ in ITEM_GROUPS}
for dn, t in things.items():
    par = t.get('ParentName') or ''
    if dn.startswith('NF_SealItem_') or not t.findtext('description') or not t.findtext('label'): continue
    if any(x in par for x in ('Projectile', 'Ethereal', 'Shield', 'TMF_', 'Mote', 'AnimalThingBase', 'Blueprint')): continue
    for g, keys in ITEM_GROUPS:
        if any(k in par for k in keys) or (g == 'Apparel and gear' and t.find('apparel') is not None) or (g == 'Weapons and instruments' and (t.find('verbs') is not None or t.find('tools') is not None) and t.find('race') is None):
            items[g].append(dn); break
body = '<h1>Items</h1><p class="lead">Everything the mod adds that you can hold, wear, drink, throw or build. Seals have <a href="seals.html">their own page</a>.</p>'
for g, _ in ITEM_GROUPS:
    if not items[g]: continue
    body += f'<h2 id="{slug(g)}">{E(g)} <small>{len(items[g])}</small></h2><div class="grid items">'
    for dn in sorted(items[g], key=lambda d: things[d].findtext('label').lower()):
        t = things[dn]
        tex = t.findtext('graphicData/texPath') or ''
        ic = img(tex) or img(tex + '_south') or img(tex + '/' + tex.split('/')[-1]) or img(t.findtext('uiIconPath'))
        icimg = f'<img class="ic" src="img/{E(ic)}" alt="" loading="lazy">' if ic else '<span class="ic blank"></span>'
        body += f'<article class="item" id="{slug(dn)}">{icimg}<div><h3>{E(t.findtext("label").capitalize())}</h3><p>{E(t.findtext("description"))}</p></div></article>'
        index.append([t.findtext('label'), 'Item', 'items.html#' + slug(dn), g])
    body += '</div>'
page('items.html', 'Items', body)

# ───────────────────────────── seals
def seal_line(s):
    out = []
    for m in s.findall('statOffsets/*'): out.append(f'{m.tag} {m.text}')
    for k, lab in (('extraDamageDef', 'extra damage'), ('hediff', 'applies'), ('hitMental', 'can cause'), ('reactDamageDef', 'hurts melee attackers with'), ('wornHediff', 'worn effect')):
        if s.findtext(k): out.append(f'{lab}: {s.findtext(k)}')
    if s.find('resist') is not None: out.append('resists ' + ', '.join(li.text for li in s.findall('resist/li')))
    if s.findtext('storeJutsu') == 'true': out.append('stores a technique')
    if s.findtext('technique'): out.append('made with the ' + (abilities.get(s.findtext('technique')).findtext('label') if abilities.get(s.findtext('technique')) is not None else s.findtext('technique')) + ' technique')
    return '; '.join(out)
body = '''<h1>Enchantment seals</h1><p class="lead">Seals are inked at a crafting spot, tailoring bench or scribe desk and pressed into gear. Weapon seals act on every hit; armour seals help the wearer.</p>
<p>Gear has 1 seal slot, 2 at excellent or masterwork and 3 at legendary. A new seal goes on at C rank at most and then rises one rank at a time. Inscribing needs a minimum ninjutsu level (D 1, C 4, B 8, A 12, S 16); every level above it makes the seal stronger. Seals marked with a technique can only be made by an artisan who knows it (Equipment enhancing tree).</p>'''
for fw, title in (('true', 'Weapon seals'), ('false', 'Armour seals')):
    lst = sorted([s for s in seals.values() if (s.findtext('forWeapon') or 'true') == fw], key=lambda s: s.findtext('label').lower())
    body += f'<h2>{title} <small>{len(lst)}</small></h2><table class="seals"><tr><th></th><th>Seal</th><th>Ranks</th><th>What it does</th></tr>'
    for s in lst:
        name = s.findtext('defName')[8:]
        lo, hi = int(s.findtext('minRank') or 0), int(s.findtext('maxRank') or 3)
        ic = img(f'NFRP/Seals/{name}_{RANKS[lo]}')
        body += f'<tr id="{slug(name)}"><td>{"<img class=sic src=img/" + E(ic) + " alt=\"\" loading=lazy>" if ic else ""}</td><td><b>{E(s.findtext("label").capitalize())}</b></td><td>{RANKS[lo]}–{RANKS[hi]}</td><td>{E(s.findtext("description"))}<br><small>{E(seal_line(s))}</small></td></tr>'
        index.append([s.findtext('label') + ' seal', 'Seal', 'seals.html#' + slug(name), RANKS[lo] + '–' + RANKS[hi]])
    body += '</table>'
page('seals.html', 'Enchantment seals', body)

# ───────────────────────────── creatures (summons)
body = '<h1>Creatures</h1><p class="lead">Summons, golems, contract animals and companions.</p><div class="grid items">'
for dn, t in sorted(things.items(), key=lambda kv: (kv[1].findtext('label') or '')):
    if (t.get('ParentName') or '') != 'AnimalThingBase' or not t.findtext('description'): continue
    kind = T('PawnKindDef').get(dn)
    tex = kind.findtext('lifeStages/li/bodyGraphicData/texPath') if kind is not None else None
    ic = img((tex or '') + '_south') or img((tex or '') + '_east')
    icimg = f'<img class="ic big" src="img/{E(ic)}" alt="" loading="lazy">' if ic else '<span class="ic big blank"></span>'
    body += f'<article class="item" id="{slug(dn)}">{icimg}<div><h3>{E((t.findtext("label") or dn).capitalize())}</h3><p>{E(t.findtext("description"))}</p></div></article>'
    index.append([t.findtext('label'), 'Creature', 'creatures.html#' + slug(dn), ''])
body += '</div>'
page('creatures.html', 'Creatures', body)

# ───────────────────────────── factions
body = '<h1>Factions</h1><p class="lead">Hidden villages, a criminal syndicate, an order of witch-hunters and three feudal houses.</p><div class="grid items">'
for dn, f in sorted(T('FactionDef').items(), key=lambda kv: kv[1].findtext('label') or ''):
    ic = img(f.findtext('factionIconPath'))
    icimg = f'<img class="ic big" src="img/{E(ic)}" alt="" loading="lazy">' if ic else '<span class="ic big blank"></span>'
    body += f'<article class="item">{icimg}<div><h3>{E((f.findtext("label") or dn))}</h3><p>{E(f.findtext("description"))}</p></div></article>'
    index.append([f.findtext('label'), 'Faction', 'factions.html', ''])
body += '</div><p>See the <a href="guides/factions.html">factions and missions guide</a> for the war, the one-year truce and ranked missions.</p>'
page('factions.html', 'Factions', body)

# ───────────────────────────── guides (hand-written, markdown-lite in guides/*.md)
def md(text, up):
    out, para, lst = [], [], []
    def flush():
        nonlocal para, lst
        if para: out.append('<p>' + ' '.join(para) + '</p>'); para = []
        if lst: out.append('<ul>' + ''.join(f'<li>{x}</li>' for x in lst) + '</ul>'); lst = []
    for line in text.splitlines():
        s = line.rstrip()
        s2 = E(s)
        s2 = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s2)
        s2 = re.sub(r'\[(.+?)\]\((.+?)\)', lambda m: f'<a href="{m.group(2) if m.group(2).startswith("http") else up + m.group(2)}">{m.group(1)}</a>', s2)
        if not s: flush(); continue
        if s.startswith('# '): flush(); out.append(f'<h1>{s2[2:]}</h1>')
        elif s.startswith('## '): flush(); out.append(f'<h2>{s2[3:]}</h2>')
        elif s.startswith('- '): para and flush(); lst.append(s2[2:])
        else: lst and flush(); para.append(s2)
    flush()
    return '\n'.join(out)

gdir = os.path.join(HERE, 'guides')
glist = []
for f in sorted(glob.glob(os.path.join(gdir, '*.md'))):
    name = os.path.basename(f)[:-3]
    text = open(f, encoding='utf-8').read()
    title = text.splitlines()[0].lstrip('# ').strip()
    blurb = next((l for l in text.splitlines()[1:] if l.strip() and not l.startswith('#')), '')
    page(f'guides/{name[3:]}.html', title, '<article class="guide">' + md(text, '../') + '</article>')
    glist.append((name[3:], title, blurb))
    index.append([title, 'Guide', f'guides/{name[3:]}.html', ''])
page('guides/index.html', 'Guides', '<h1>Guides</h1><p class="lead">How the systems work, step by step.</p><div class="grid guides">' +
     ''.join(f'<a class="guidecard" href="{n}.html"><b>{E(t)}</b><small>{E(b[:160])}</small></a>' for n, t, b in glist) + '</div>')

# ───────────────────────────── home
home = open(os.path.join(HERE, 'home.md'), encoding='utf-8').read()
stats = f'<div class="stats"><div><b>{ntech}</b>techniques</div><div><b>{sum(len(v) for v in tree_list.values())}</b>trees</div><div><b>{len(seals)}</b>seals</div><div><b>{sum(len(v) for v in items.values())}</b>items</div></div>'
quick = '<div class="grid guides">' + ''.join(f'<a class="guidecard" href="guides/{n}.html"><b>{E(t)}</b><small>{E(b[:140])}</small></a>' for n, t, b in glist[:8]) + '</div>'
page('index.html', 'Home', '<div class="hero home"><img src="assets/preview.png" alt=""><div>' + md(home, '') + '</div></div>' + stats + '<h2>Start here</h2>' + quick)

# ───────────────────────────── assets
os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
for f in ('style.css', 'search.js'): shutil.copy(os.path.join(HERE, f), os.path.join(OUT, 'assets', f))
pv = os.path.join(SRC, 'About', 'Preview.png')
if os.path.exists(pv):
    from PIL import Image
    im = Image.open(pv).convert('RGB'); im.thumbnail((640, 360)); im.save(os.path.join(OUT, 'assets', 'preview.png'))
    im.thumbnail((64, 64)); im.save(os.path.join(OUT, 'assets', 'icon.png'))
json.dump(index, open(os.path.join(OUT, 'assets', 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
# only the images the pages use
used = set()
for f in glob.glob(os.path.join(OUT, '**', '*.html'), recursive=True):
    used |= set(re.findall(r'img/([^"\s>]+\.(?:png|jpg))', open(f, encoding='utf-8').read()))
for u in used:
    s = os.path.join(SRC, 'img', html.unescape(u)); d = os.path.join(OUT, 'img', html.unescape(u))
    if os.path.exists(s): os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy(s, d)
open(os.path.join(OUT, '.nojekyll'), 'w').close()
print('pages:', len(glob.glob(os.path.join(OUT, '**', '*.html'), recursive=True)), 'images:', len(used), 'index:', len(index))
