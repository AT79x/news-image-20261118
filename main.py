#!/usr/bin/env python3
"""news-image-20261118 — one image summing up the world news of
Wednesday 18 November 2026.

Pure Python 3 standard library only. No network, no files read at run
time: every pixel is drawn in code, deterministically, so two runs
write byte-identical PNGs.

Layout (1024 x 1024, newspaper front page):
  masthead  : THE WORLD IN ONE DAY / WEDNESDAY 18 NOVEMBER 2026
  hero      : Gulf war escalation (US strikes Qeshm Island, Iran hits
              bases in Kuwait and Bahrain)
  row 2     : Shenzhen summit (Xi + Putin at APEC) | Kerch Bridge falls
  row 3     : Alaska flips the Senate 56-44 | US loses measles status
  footer    : Voyager 1 reaches one light-day from Earth

All six stories were verified against Reuters / AP / CNN / UNICEF /
NASA reporting on 18 November 2026 (see NEWS.md in this repository).
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)   # newsprint cream
INK = (17, 17, 17)        # near-black
NAVY = (20, 38, 74)       # masthead / deep blue
NAVY_D = (12, 24, 48)
RED = (176, 42, 30)       # alert red
GOLD = (201, 162, 39)
SKY = (58, 110, 165)
SKY_L = (147, 190, 224)
SEA = (28, 68, 110)
SEA_D = (16, 44, 76)
SAND = (214, 196, 150)
GREY = (90, 90, 88)
WHITE = (255, 255, 255)
GREEN = (38, 110, 66)
TEAL = (18, 96, 96)
SPACE = (8, 10, 26)
CREAM2 = (232, 224, 200)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 pixels, "#" = on, "." = off.
# All copy is rendered in capitals, so only one case is needed.
FONT = {
    "A": (" .###. ", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#.#", ".#.#.", "..##.", ".#.#.", "####."),
}
# Normalise every glyph row to exactly 5 characters.
FONT = {k: tuple(r.strip()[:5].ljust(5, ".") for r in v) for k, v in FONT.items()}


def _chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def write_png(path, rgb, w, h):
    """Write an RGB bytearray as a deterministic PNG (filter 0 rows)."""
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * w * 3:(y + 1) * w * 3]
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", comp)
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def _i(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._i(x, y)
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = self._i(x0, yy)
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x, y, w, c, t=1):
        for k in range(t):
            self.rect(x, y + k, w, 1, c)

    def vline(self, x, y, h, c, t=1):
        for k in range(t):
            self.rect(x + k, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r:
                        self.set(xx, yy, c)

    def disc(self, cx, cy, r, c):
        self.circle(cx, cy, r, c, fill=True)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            self.circle(cx, cy, r - k, c, fill=False)

    def tri(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by) or yy == ymax and yy == max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.rect(xa, yy, xb - xa + 1, 1, c)

    def starburst(self, cx, cy, r0, r1, n, c):
        import math
        pts = []
        for k in range(2 * n):
            r = r1 if k % 2 == 0 else r0
            a = math.pi * k / n - math.pi / 2
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        for k in range(len(pts)):
            self.tri((pts[k], pts[(k + 1) % len(pts)], (cx, cy)), c)

    # ------------------------------------------------------------ text
    def text_w(self, s, scale):
        return len(s) * (5 * scale + scale) - scale

    def draw_text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for ry in range(7):
                row = g[ry]
                for rx in range(5):
                    if row[rx] == "#":
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, c):
        w = self.text_w(s, scale)
        return self.draw_text(cx - w // 2, y, s, scale, c)

    def wrap(self, s, scale, maxw):
        words = s.upper().split()
        lines, cur = [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if self.text_w(trial, scale) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

# ------------------------------------------------------- illustrations
def illo_gulf(c, x, y, w, h):
    """Strait of Hormuz at night: Qeshm Island, jets, blasts, bases."""
    c.rect(x, y, w, h, NAVY_D)
    # stars
    for sx, sy in ((30, 18), (90, 10), (150, 26), (220, 12), (300, 22),
                   (380, 10), (470, 20), (560, 12), (640, 24), (720, 10),
                   (800, 18), (880, 12), (940, 22), (60, 44), (420, 40)):
        c.set(x + sx % w, y + sy % (h // 2), WHITE)
    # moon
    c.disc(x + w - 70, y + 34, 16, CREAM2)
    c.disc(x + w - 76, y + 30, 14, NAVY_D)
    # sea
    sea_y = y + h * 3 // 5
    c.rect(x, sea_y, w, y + h - sea_y, SEA)
    c.rect(x, sea_y, w, 3, SKY_L)
    for wx in range(0, w, 46):
        c.hline(x + wx, sea_y + 22, 26, SKY_L, 2)
        c.hline(x + wx + 20, sea_y + 44, 26, (90, 140, 190), 2)
    # Qeshm Island (left)
    ix, iy = x + 60, sea_y - 26
    c.tri(((ix, iy + 26), (ix + 60, iy), (ix + 150, iy + 10)), SAND)
    c.rect(ix, iy + 10, 150, 16, SAND)
    c.draw_text(ix + 18, iy + 14, "QESHM ISLAND", 1, INK)
    # missile site + blast on the island
    c.starburst(ix + 78, iy - 6, 8, 26, 8, GOLD)
    c.starburst(ix + 78, iy - 6, 4, 14, 8, RED)
    # jets
    for jx, jy in ((x + 330, y + 40), (x + 400, y + 62)):
        c.tri(((jx, jy), (jx + 34, jy + 7), (jx, jy + 14)), WHITE)
        c.tri(((jx + 8, jy + 2), (jx + 20, jy - 8), (jx + 22, jy + 4)), WHITE)
        c.line(jx - 4, jy + 7, jx - 46, jy + 16, GOLD, 2)
    # Bahrain / Kuwait bases (right) under attack
    bx = x + w - 260
    c.rect(bx, sea_y - 34, 200, 34, (52, 62, 80))
    c.rect(bx, sea_y - 34, 200, 4, GOLD)
    c.draw_text(bx + 14, sea_y - 26, "KUWAIT  .  BAHRAIN", 1, WHITE)
    c.draw_text(bx + 14, sea_y - 12, "U.S. BASES", 1, SKY_L)
    c.starburst(bx + 40, sea_y - 44, 6, 18, 8, GOLD)
    c.starburst(bx + 150, sea_y - 40, 5, 15, 8, RED)
    # incoming arcs
    c.line(bx + 40, sea_y - 52, bx + 110, y + 30, (220, 220, 220), 1)
    c.line(bx + 150, sea_y - 48, bx + 190, y + 44, (220, 220, 220), 1)


def illo_shenzhen(c, x, y, w, h):
    """Shenzhen skyline at dusk, two flags, APEC. All sizes relative to h."""
    c.rect(x, y, w, h, (233, 214, 178))
    c.rect(x, y, w, h // 2, (250, 226, 190))
    # sun
    c.disc(x + w - 56, y + 26, 18, GOLD)
    # skyline silhouettes, heights as fractions of h
    base = y + h
    towers = [(0.00, 0.55, 0.10), (0.11, 0.72, 0.09), (0.21, 0.60, 0.11),
              (0.33, 0.88, 0.10), (0.44, 0.64, 0.09), (0.54, 0.78, 0.10),
              (0.65, 0.58, 0.09), (0.75, 0.86, 0.10), (0.86, 0.62, 0.09)]
    for fx, fh, fw in towers:
        tx, tw, th = x + int(fx * w), int(fw * w), int(fh * h)
        c.rect(tx, base - th, tw, th, NAVY)
        for wy in range(base - th + 6, base - 4, 10):
            for wx in range(tx + 4, tx + tw - 4, 10):
                c.set(wx, wy, GOLD)
    # flags on poles (top left)
    fx = x + 10
    c.vline(fx, y + 6, 30, INK, 3)
    c.rect(fx + 3, y + 6, 40, 20, RED)
    c.starburst(fx + 12, y + 16, 2, 5, 5, GOLD)
    c.vline(fx + 92, y + 6, 30, INK, 3)
    c.rect(fx + 95, y + 6, 40, 20, WHITE)
    c.rect(fx + 95, y + 13, 40, 6, (0, 57, 166))
    c.rect(fx + 95, y + 19, 40, 7, (213, 0, 50))
    c.draw_text(x + w - 66, y + 8, "APEC", 2, NAVY)


def illo_kerch(c, x, y, w, h):
    """The Kerch Bridge: road arch collapsed into the strait. Relative coords."""
    c.rect(x, y, w, h, SKY_L)
    # clouds
    for fx, fy in ((0.05, 0.12), (0.42, 0.08), (0.75, 0.14)):
        cx0, cy0 = x + int(fx * w), y + int(fy * h)
        c.disc(cx0, cy0, 7, WHITE)
        c.disc(cx0 + 10, cy0 + 2, 9, WHITE)
        c.disc(cx0 + 21, cy0, 6, WHITE)
    # sea
    sea_y = y + int(h * 0.66)
    c.rect(x, sea_y, w, y + h - sea_y, SEA)
    for wx in range(0, w, 40):
        c.hline(x + wx, sea_y + 10, 22, SKY_L, 2)
    # bridge deck left and right, gap in the middle
    deck_y = y + int(h * 0.44)
    c.rect(x, deck_y, int(w * 0.36), 8, INK)
    c.rect(x + int(w * 0.62), deck_y, w - int(w * 0.62), 8, INK)
    c.rect(x, deck_y + 8, 8, int(h * 0.20), INK)
    c.rect(x + w - 8, deck_y + 8, 8, int(h * 0.20), INK)
    # standing arch (right side)
    ax = x + int(w * 0.80)
    c.line(x + int(w * 0.63), deck_y, ax, deck_y - int(h * 0.34), INK, 4)
    c.line(x + w - 4, deck_y, ax, deck_y - int(h * 0.34), INK, 4)
    # collapsed arch falling into the water (middle)
    mx = x + w // 2
    my = deck_y + int(h * 0.20)
    c.line(x + int(w * 0.36), deck_y, mx, my, RED, 5)
    c.line(x + int(w * 0.62), deck_y, mx, my, RED, 5)
    c.starburst(mx, my + 4, 4, 12, 7, WHITE)
    # smoke above the break
    for fx, fy, sr in ((0.44, 0.30, 8), (0.50, 0.24, 10), (0.56, 0.30, 8)):
        c.disc(x + int(fx * w), y + int(fy * h), sr, (120, 120, 118))


def illo_alaska(c, x, y, w, h):
    """Ballot box, mountains, and the 56-44 count. Relative coords."""
    c.rect(x, y, w, h, (214, 232, 240))
    # mountains
    c.tri(((x, y + h), (x + int(w * 0.26), y + int(h * 0.30)),
           (x + int(w * 0.52), y + h)), (120, 150, 180))
    c.tri(((x + int(w * 0.16), y + int(h * 0.55)),
           (x + int(w * 0.26), y + int(h * 0.30)),
           (x + int(w * 0.36), y + int(h * 0.55))), WHITE)
    c.tri(((x + int(w * 0.48), y + h), (x + int(w * 0.78), y + int(h * 0.38)),
           (x + w, y + h)), (96, 128, 160))
    # ballot box (bottom left)
    bx, by, bw, bh = x + 12, y + h - 32, 56, 30
    c.rect(bx, by, bw, bh, NAVY)
    c.rect(bx, by - 8, bw, 8, RED)
    c.rect(bx + 20, by - 8, 16, 8, PAPER)
    c.disc(bx + bw // 2, by + bh // 2 + 2, 8, GOLD)
    # big count (top right of the panel art)
    c.draw_text(x + int(w * 0.42), y + 8, "56-44", 4, NAVY)


def illo_measles(c, x, y, w, h):
    """Virus icon and the lost 26-year status. Relative coords."""
    c.rect(x, y, w, h, (250, 236, 220))
    # virus (left)
    vx, vy, vr = x + 52, y + h // 2 + 4, 22
    import math
    for k in range(10):
        a = math.pi * 2 * k / 10
        ex, ey = int(vx + (vr + 11) * math.cos(a)), int(vy + (vr + 11) * math.sin(a))
        c.line(vx, vy, ex, ey, RED, 3)
        c.disc(ex, ey, 3, RED)
    c.disc(vx, vy, vr, RED)
    c.disc(vx - 7, vy - 6, 6, (214, 90, 70))
    c.disc(vx + 8, vy + 8, 5, (214, 90, 70))
    # "26 YEARS" struck through (right)
    tx = x + 108
    c.draw_text(tx, y + 8, "26 YEARS", 3, INK)
    c.line(tx - 2, y + 19, tx + c.text_w("26 YEARS", 3) + 2, y + 19, RED, 4)
    c.draw_text(tx, y + 38, "STATUS LOST", 2, INK)


def illo_voyager(c, x, y, w, h):
    """Interstellar space: stars, Earth, Voyager 1 with its dish."""
    c.rect(x, y, w, h, SPACE)
    import math
    for sx, sy in ((14, 10), (48, 26), (90, 8), (130, 20), (180, 12),
                   (230, 28), (280, 10), (330, 22), (380, 8), (430, 18),
                   (20, 60), (70, 74), (150, 66), (260, 70), (350, 62),
                   (410, 76), (455, 60)):
        c.disc(x + sx % w, y + sy, 2, WHITE)
    # sun glow, far left (dim halo first, bright core on top)
    c.disc(x + 8, y + h // 2, 22, (120, 90, 20))
    c.disc(x + 8, y + h // 2, 12, GOLD)
    # Earth
    ex, ey = x + 84, y + h // 2 + 6
    c.disc(ex, ey, 20, SKY)
    c.disc(ex - 6, ey - 6, 8, GREEN)
    c.disc(ex + 8, ey + 7, 6, GREEN)
    c.draw_text(ex - 22, ey + 26, "EARTH", 1, WHITE)
    # dashed signal path Earth -> Voyager
    vx, vy = x + w - 130, y + 30
    for t in range(0, 21):
        px = int(ex + (vx - ex) * t / 20)
        py = int(ey + (vy - ey) * t / 20)
        if t % 2 == 0:
            c.disc(px, py, 2, GOLD)
    # Voyager: bus + dish + boom
    c.rect(vx - 12, vy - 8, 26, 16, WHITE)
    c.rect(vx - 12, vy - 8, 26, 4, GOLD)
    c.line(vx + 14, vy, vx + 34, vy - 14, WHITE, 3)
    c.disc(vx + 38, vy - 16, 12, WHITE)
    c.disc(vx + 38, vy - 16, 8, NAVY)
    c.line(vx - 12, vy + 4, vx - 34, vy + 16, WHITE, 3)
    c.disc(vx - 38, vy + 18, 5, GOLD)
    c.draw_text(vx - 44, vy + 28, "VOYAGER 1", 1, WHITE)

# ------------------------------------------------------------- layout
def panel(c, x, y, w, h, kicker, kcolor, headline, deck, illo):
    c.rect(x, y, w, h, PAPER)
    c.hline(x, y, w, INK, 3)
    c.hline(x, y + h - 3, w, INK, 3)
    c.vline(x, y, h, INK, 3)
    c.vline(x + w - 3, y, h, INK, 3)
    c.rect(x + 3, y + 3, w - 6, 26, kcolor)
    c.draw_text(x + 14, y + 10, kicker, 2, WHITE)
    lines = c.wrap(headline, 3, w - 28)[:2]
    hy = y + 38
    for ln in lines:
        c.draw_text(x + 14, hy, ln, 3, INK)
        hy += 25
    iy = hy + 4
    ih = (y + h - 38) - iy
    if ih > 10:
        illo(c, x + 6, iy, w - 12, ih)
    dlines = c.wrap(deck, 2, w - 28)[:2]
    dy = y + h - 38
    for ln in dlines:
        c.draw_text(x + 14, dy, ln, 2, GREY)
        dy += 15


def build():
    c = Canvas(W, H, PAPER)

    # ---- masthead
    c.rect(24, 24, 976, 104, NAVY)
    c.hline(24, 24, 976, GOLD, 3)
    c.hline(24, 125, 976, GOLD, 3)
    c.text_center(512, 38, "THE WORLD IN ONE DAY", 3, WHITE)
    c.text_center(512, 72, "WEDNESDAY 18 NOVEMBER 2026", 5, GOLD)

    # ---- hero: Gulf war escalation
    hx, hy, hw, hh = 24, 140, 976, 284
    c.rect(hx, hy, hw, hh, PAPER)
    c.hline(hx, hy, hw, INK, 3)
    c.hline(hx, hy + hh - 3, hw, INK, 3)
    c.vline(hx, hy, hh, INK, 3)
    c.vline(hx + hw - 3, hy, hh, INK, 3)
    c.rect(hx + 3, hy + 3, hw - 6, 30, RED)
    c.draw_text(hx + 15, hy + 11, "THE GULF - WAR AT SEA", 2, WHITE)
    hlines = c.wrap("U.S. STRIKES IRAN, IRAN HITS U.S. BASES IN KUWAIT AND BAHRAIN",
                    4, hw - 30)[:2]
    yy = hy + 44
    for ln in hlines:
        c.draw_text(hx + 15, yy, ln, 4, INK)
        yy += 32
    illo_gulf(c, hx + 6, yy + 4, hw - 12, 118)
    dlines = c.wrap("FIGHTER JETS HIT A MISSILE SITE ON QESHM ISLAND. TEHRAN "
                    "ANSWERS WITH STRIKES ON ALI AL SALEM AIR BASE AND BAHRAIN.",
                    2, hw - 30)[:2]
    dy = hy + hh - 36
    for ln in dlines:
        c.draw_text(hx + 15, dy, ln, 2, GREY)
        dy += 15

    # ---- row 2
    panel(c, 24, 436, 482, 200, "ASIA - APEC IN SHENZHEN", TEAL,
          "XI AND PUTIN MEET BEFORE TRUMP TALKS",
          "AT APEC IN SHENZHEN, XI HITS OUT AT PROTECTIONISM. "
          "PUTIN HITS SANCTIONS.", illo_shenzhen)
    panel(c, 518, 436, 482, 200, "EUROPE - UKRAINE WAR", RED,
          "KERCH BRIDGE ROAD ARCH FALLS",
          "UKRAINE'S DRONES AND MISSILES CUT THE 19 KM LINK. "
          "ROAD SHUT, RAIL BACK.", illo_kerch)

    # ---- row 3
    panel(c, 24, 648, 482, 200, "AMERICA - MIDTERMS", NAVY,
          "PELTOLA FLIPS ALASKA, SENATE NOW 56-44",
          "DEMOCRAT BEATS SULLIVAN IN ALASKA. "
          "FIRST ALASKA NATIVE IN THE SENATE.", illo_alaska)
    panel(c, 518, 648, 482, 200, "HEALTH - USA", RED,
          "U.S. LOSES MEASLES FREE STATUS",
          "5,412 CASES IN 2026, MOST SINCE 1991. "
          "PAHO ENDS 26-YEAR ELIMINATION.", illo_measles)

    # ---- footer: Voyager 1
    fx, fy, fw, fh = 24, 860, 976, 116
    c.rect(fx, fy, fw, fh, SPACE)
    c.hline(fx, fy, fw, GOLD, 3)
    c.hline(fx, fy + fh - 3, fw, GOLD, 3)
    c.vline(fx, fy, fh, GOLD, 3)
    c.vline(fx + fw - 3, fy, fh, GOLD, 3)
    illo_voyager(c, fx + 6, fy + 6, 400, fh - 12)
    c.draw_text(fx + 430, fy + 12, "SPACE", 2, GOLD)
    c.draw_text(fx + 430, fy + 32, "VOYAGER 1 REACHES", 3, WHITE)
    c.draw_text(fx + 430, fy + 56, "ONE LIGHT-DAY", 3, WHITE)
    dlines = c.wrap("16 BILLION MILES OUT. ITS SIGNALS NOW TAKE A FULL DAY "
                    "TO REACH EARTH.", 2, fw - 460)[:2]
    dy = fy + 84
    for ln in dlines:
        c.draw_text(fx + 430, dy, ln, 2, (200, 205, 220))
        dy += 15
    return c


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    c = build()
    path = os.path.join(outdir, "entry.png")
    write_png(path, c.px, W, H)
    print("WROTE", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
