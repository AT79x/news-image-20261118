[![news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/at79x/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/at79x/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118)

# news-image-20261118 — One Day in the World

A program that draws one newspaper front page summing up the world news
of **Wednesday 18 November 2026**, as an entry for the
[make.fun bounty "Sum up 18 November's world news in one image"](https://make.fun/bounty/news-image-20261118).

`main.py` (Python 3, standard library only, no network) draws the image
from scratch — masthead, six verified stories, flat vector illustrations —
and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`. Two runs produce
byte-identical output.

## The six stories (all verified against Reuters / AP / CNN / UNICEF / NASA, 18 Nov 2026)

1. **The Gulf — war at sea.** US jets strike a missile site on Qeshm Island;
   Iran answers with attacks on US bases in Kuwait and Bahrain.
2. **Asia — APEC in Shenzhen.** Xi Jinping and Vladimir Putin meet ahead of
   Thursday's trilateral talks with Donald Trump.
3. **Europe — Ukraine war.** The Kerch Bridge road arch collapses after
   Ukrainian drone and missile strikes.
4. **America — midterms.** Mary Peltola flips Alaska; Democrats take the
   Senate 56–44.
5. **Health — USA.** The US loses its measles elimination status after
   26 years; 5,412 cases in 2026.
6. **Space.** Voyager 1 reaches one light-day from Earth — a first.

See [NEWS.md](NEWS.md) for the sources behind each story.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Output: `out/entry.png` — 1024×1024 PNG, about 21 KB.
