# Build notes — news-image-20261118

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024 PNG, ~21 KB).

## Determinism check

```sh
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 python3 main.py
MAKEFUN_OUTPUT_DIR=out2 python3 main.py
sha256sum out1/entry.png out2/entry.png   # must be identical
```

Verified 18 Nov 2026: both runs
`796b314bdb5761f5d4724cbcba90f9d1283f0141f9533a79b773516fbf5cde88`
(21,284 bytes, 1024x1024, valid PNG).

## Design

- Pure Python 3 standard library only (`struct`, `zlib`, `os`, `math`).
  No network, no files read at run time, no randomness, no clock.
- Hand-written 5x7 bitmap font, all copy in capitals, newspaper style.
- Six stories, each verified against Reuters / AP / CNN / UNICEF / NASA
  reporting on 18 Nov 2026 — see NEWS.md for sources.
- `out1/` and `out2/` are local test outputs only; do not commit them.
  The repository ships no pre-rendered `entry.png`: `main.py` draws the
  image fresh on every run.
