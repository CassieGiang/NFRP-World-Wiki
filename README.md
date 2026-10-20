# NFRP World

A RimWorld mod that brings the clans, bloodlines and techniques of the Naruto Forum Role-play (NFRP) archive into World of Naruto.

**Wiki:** https://cassiegiang.github.io/NFRP-World-Wiki/

Requires Harmony, Taran Magic Framework and World of Naruto (load in that order, then NFRP World). Giddy-Up is recommended for riding. RimWorld 1.6 and 1.7.

## This repository
- `docs/`: the wiki, a static site served by GitHub Pages. It is generated from the mod's own files.
- `wiki-src/`: the generator (`gen_wiki.py`), styles and the hand-written guides (`guides/*.md`, `home.md`).

To regenerate: `python3 wiki-src/gen_wiki.py <mod_src> docs` where `mod_src` holds the mod's `Defs/`, `Patches/`, `About/` and an `img/` folder of thumbnails made from `Textures/`.

## Credits
The Kazeraikou clan was created by Marii from NFRP and is used with her permission. Technique and clan material from the Naruto Forum Role-play (NFRP) community archive. Built on World of Naruto and Taran Magic Framework.
