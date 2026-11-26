# news-image-20261126 v2 — complete (Builder 1: engine + masthead + world map
# + top row; Builder 2: middle sides, bottom row of 5, extra row of 3, ticker)
# "THE WORLD TODAY: THURSDAY, NOVEMBER 26, 2026" — 1024x1024 PNG.
# Python 3.13 stdlib ONLY. Own rasterizer, hand-built 5x7 bitmap font,
# zlib PNG encoder. Deterministic: two runs write byte-identical bytes.
# No network, no PIL, no external assets. Writes $MAKEFUN_OUTPUT_DIR/entry.png
# (default ./output/entry.png).
#
# LAYOUT (exact pixel coordinates, canvas 1024x1024, outer margin 8):
#   Masthead:            x 8..1016,   y 8..140
#   Top row:             y 148..400
#     Swiss/Pyongyang:   x 8..292     (Builder 1 — built)
#     HERO Russia:       x 300..660   (Builder 1 — built)
#     US tariffs:        x 668..1016  (Builder 1 — built)
#   Middle row:          y 408..640
#     Ranchi protest:    x 8..292     (Builder 2 — built)
#     Central world map: x 300..660   (Builder 1 — built)
#     Turkey Trot:       x 668..1016  (Builder 2 — built)
#   Bottom row of 5:     y 648..832, panels x 8..203, 211..406, 414..609,
#                        617..812, 820..1016 (Builder 2 — built)
#     VP health checks Jakarta / Bank of Korea hike / Iran Hormuz mines /
#     Cairo tanker fire / UK stalking offence
#   Extra slim row of 3: y 840..912, panels x 8..338, 346..676, 684..1016
#                        (Builder 2 — built)
#     Colombia hostages / Netanyahu charges / Anthropic $32B data centre
#   Ticker + source strip: x 8..1016, y 920..1016 (Builder 2 — built)
#
# Verified facts used (26 Nov 2026 only, from the v2 + v1 news files):
#   HERO: Russia's own figures: nearly 500,000 dead in the Ukraine war.
#   Swiss: Pyongyang orders Switzerland to close its diplomatic office.
#   Tariffs: Trump announces new tariffs; China, Japan, EU hit; Taiwan 15%.
#   Ranchi: police detain protesters opposing tree felling.
#   Turkey Trot: 51st Annual Alexandria Turkey Trot, honouring 9/11's 2,977.
#   VP checks: Amran and Sugiono health checks at RSPAD Jakarta.
#   Bank of Korea hikes to 3.25%, third hike since July.
#   Iran: ships hit mines in Hormuz; Tehran warns ships to coordinate.
#   Cairo: 31 killed in a tanker crash fire on a highway.
#   UK: stalking now a standalone crime, no more proving fear, up to 10 years.
#   Colombia: police free 20 hostages after a 17 hour standoff.
#   Netanyahu: judges recommend dropping the most serious charges.
#   Anthropic: $32B Queensland data centre cleared by the federal EPA.
#   Ticker: Australia-Solomon pact, Mercury mission, Xi probe, Constitution
#   Day, Nepal package, Bangladesh wage, IPL auction, Colombia peace deal,
#   Venezuela debt, Petrobras plan; Spain votes Sun 29 Nov, Bitcoin over
#   $61,000, US House advances Strategic Bitcoin Reserve bill.
# Nothing from the DO NOT USE lists is drawn anywhere in this file.
# Dropped v1 panels are NOT in this file: no Flipkart CEO, no Gukesh chess,
# no Nasdaq down 4 pct.

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
NAVY   = (10, 18, 38)     # page background
PANEL  = (16, 30, 58)     # panel background
PANEL2 = (20, 38, 72)     # lighter panel background
GOLD   = (255, 200, 40)   # masthead date, hero accents
GOLD_D = (200, 150, 20)
WHITE  = (255, 255, 255)
OFFW   = (225, 232, 245)  # off-white body text
MUTED  = (150, 165, 195)  # small grey-blue text
RED    = (198, 32, 32)    # Swiss flag / caption band
RED_D  = (120, 16, 16)    # hero deep red
RED_B  = (90, 10, 10)     # hero darkest red
GREEN  = (46, 160, 90)
CYAN   = (64, 200, 235)   # map glow
CYAN_D = (40, 120, 170)
BLUE   = (70, 140, 230)
ORANGE = (235, 130, 40)
BLACK  = (8, 10, 18)
GREY   = (120, 125, 135)
BROWN  = (150, 100, 50)   # tree trunks
BRN_OR = (150, 75, 15)    # burnt-orange caption band (Turkey Trot)
SKIN   = (235, 200, 160)  # figure heads
YELLOW = (255, 220, 80)   # flame cores

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits ('1' = ink). Hand-built for this entry.
FONT = {
 'A': ("01110","10001","10001","11111","10001","10001","10001"),
 'B': ("11110","10001","10001","11110","10001","10001","11110"),
 'C': ("01110","10001","10000","10000","10000","10001","01110"),
 'D': ("11110","10001","10001","10001","10001","10001","11110"),
 'E': ("11111","10000","10000","11110","10000","10000","11111"),
 'F': ("11111","10000","10000","11110","10000","10000","10000"),
 'G': ("01110","10001","10000","10111","10001","10001","01111"),
 'H': ("10001","10001","10001","11111","10001","10001","10001"),
 'I': ("01110","00100","00100","00100","00100","00100","01110"),
 'J': ("00111","00010","00010","00010","00010","10010","01100"),
 'K': ("10001","10010","10100","11000","10100","10010","10001"),
 'L': ("10000","10000","10000","10000","10000","10000","11111"),
 'M': ("10001","11011","10101","10101","10001","10001","10001"),
 'N': ("10001","11001","10101","10011","10001","10001","10001"),
 'O': ("01110","10001","10001","10001","10001","10001","01110"),
 'P': ("11110","10001","10001","11110","10000","10000","10000"),
 'Q': ("01110","10001","10001","10001","10101","10010","01101"),
 'R': ("11110","10001","10001","11110","10100","10010","10001"),
 'S': ("01111","10000","10000","01110","00001","00001","11110"),
 'T': ("11111","00100","00100","00100","00100","00100","00100"),
 'U': ("10001","10001","10001","10001","10001","10001","01110"),
 'V': ("10001","10001","10001","10001","10001","01010","00100"),
 'W': ("10001","10001","10001","10101","10101","11011","10001"),
 'X': ("10001","10001","01010","00100","01010","10001","10001"),
 'Y': ("10001","10001","01010","00100","00100","00100","00100"),
 'Z': ("11111","00001","00010","00100","01000","10000","11111"),
 '0': ("01110","10001","10011","10101","11001","10001","01110"),
 '1': ("00100","01100","00100","00100","00100","00100","01110"),
 '2': ("01110","10001","00001","00110","01000","10000","11111"),
 '3': ("11111","00010","00100","00010","00001","10001","01110"),
 '4': ("00010","00110","01010","10010","11111","00010","00010"),
 '5': ("11111","10000","11110","00001","00001","10001","01110"),
 '6': ("00110","01000","10000","11110","10001","10001","01110"),
 '7': ("11111","00001","00010","00100","01000","01000","01000"),
 '8': ("01110","10001","10001","01110","10001","10001","01110"),
 '9': ("01110","10001","10001","01111","00001","00010","01100"),
 ' ': ("00000","00000","00000","00000","00000","00000","00000"),
 ',': ("00000","00000","00000","00000","00100","00100","01000"),
 '.': ("00000","00000","00000","00000","00000","01100","01100"),
 ':': ("00000","01100","01100","00000","01100","01100","00000"),
 '-': ("00000","00000","00000","01110","00000","00000","00000"),
 '%': ("11001","11010","00010","00100","01000","01011","10011"),
 "'": ("00100","00100","01000","00000","00000","00000","00000"),
 '/': ("00001","00010","00010","00100","01000","01000","10000"),
 '(': ("00010","00100","01000","01000","01000","00100","00010"),
 ')': ("01000","00100","00010","00010","00010","00100","01000"),
 '+': ("00000","00100","00100","11111","00100","00100","00000"),
 '!': ("00100","00100","00100","00100","00100","00000","00100"),
 '?': ("01110","10001","00001","00110","00100","00000","00100"),
 '$': ("00100","01111","10100","01110","00101","11110","00100"),
 '"': ("01010","01010","00000","00000","00000","00000","00000"),
}

# ---------------------------------------------------------------- framebuffer
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]
                i += 3

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def border(self, x, y, w, h, c, t=2):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def dashed_border(self, x, y, w, h, c, t=2, dash=8):
        # dashed top/bottom
        xx = x
        while xx < x + w:
            n = min(dash, x + w - xx)
            self.fill_rect(xx, y, n, t, c)
            self.fill_rect(xx, y + h - t, n, t, c)
            xx += dash * 2
        yy = y
        while yy < y + h:
            n = min(dash, y + h - yy)
            self.fill_rect(x, yy, t, n, c)
            self.fill_rect(x + w - t, yy, t, n, c)
            yy += dash * 2

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cy + dy, 2 * dx + 1, c)

    def ring(self, cx, cy, r, c):
        for a in range(360):
            import math
            x = cx + int(r * math.cos(math.radians(a)))
            y = cy + int(r * math.sin(math.radians(a)))
            self.set(x, y, c)

    def poly(self, pts, c):
        # even-odd scanline fill
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    xs.append(x)
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.hline(int(xs[k]), y, max(1, int(xs[k + 1]) - int(xs[k])), c)

    def bezier_dots(self, p0, p1, p2, c, step=0.02, dot=2):
        import math
        t = 0.0
        while t <= 1.0:
            u = 1 - t
            x = int(u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0])
            y = int(u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])
            self.disc(x, y, dot, c)
            t += step

# ---------------------------------------------------------------- text
def text_width(s, scale, spacing=None):
    if spacing is None:
        spacing = scale
    return len(s) * (5 * scale + spacing) - spacing

def draw_text(cv, x, y, s, scale, color, spacing=None):
    if spacing is None:
        spacing = scale
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == '1':
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
        cx += 5 * scale + spacing

def draw_centered(cv, cx, y, s, scale, color, spacing=None):
    draw_text(cv, cx - text_width(s, scale, spacing) // 2, y,
              s, scale, color, spacing)

# ---------------------------------------------------------------- panels
def panel(cv, x, y, w, h, border_color, bg=PANEL, t=2):
    cv.fill_rect(x, y, w, h, bg)
    cv.border(x, y, w, h, border_color, t)

def kicker(cv, x, w, y, line1, line2, c1, c2):
    draw_centered(cv, x + w // 2, y, line1, 2, c1)
    draw_centered(cv, x + w // 2, y + 16, line2, 2, c2)

# ---------------------------------------------------------------- masthead
def draw_masthead(cv):
    cv.fill_rect(8, 8, 1008, 132, (12, 22, 46))
    cv.border(8, 8, 1008, 132, GOLD, 3)
    draw_centered(cv, 512, 16, "THE WORLD TODAY", 7, WHITE)
    draw_centered(cv, 512, 68, "THURSDAY, NOVEMBER 26, 2026", 6, GOLD)
    # gold rule with end dots under the date
    cv.hline(120, 116, 784, GOLD)
    cv.disc(116, 116, 4, GOLD)
    cv.disc(908, 116, 4, GOLD)
    draw_centered(cv, 512, 122, "ONE DAY. EVERY REGION. WHAT HAPPENED.",
                  2, MUTED)

# ---------------------------------------------------------------- top left: Swiss / Pyongyang
def draw_swiss(cv):
    x, y, w, h = 8, 148, 284, 252
    panel(cv, x, y, w, h, CYAN)
    kicker(cv, x, w, y + 10, "DIPLOMATIC TENSION",
           "PYONGYANG, NORTH KOREA", OFFW, GOLD)
    # Swiss flag (red square, white cross)
    fx, fy, fs = x + 28, y + 56, 84
    cv.fill_rect(fx, fy, fs, fs, RED)
    cv.fill_rect(fx + fs // 2 - 9, fy + 12, 18, fs - 24, WHITE)
    cv.fill_rect(fx + 12, fy + fs // 2 - 9, fs - 24, 18, WHITE)
    # Barred diplomatic gate: building + red bars
    gx, gy = x + 148, y + 56
    cv.fill_rect(gx, gy, 108, 14, GOLD_D)          # roof
    cv.fill_rect(gx + 8, gy + 14, 92, 46, GREY)    # facade
    cv.fill_rect(gx + 40, gy + 28, 28, 32, BLACK)  # door
    for i in range(6):                              # gate bars
        cv.vline(gx + 6 + i * 17, gy + 62, 22, RED)
    cv.hline(gx, gy + 62, 108, RED)
    cv.hline(gx, gy + 82, 108, RED)
    draw_centered(cv, x + w // 2, y + 144, "GATE BARRED", 2, MUTED)
    # red caption band (4 lines, 23px pitch = 2px leading)
    cv.fill_rect(x + 3, y + 159, w - 6, 91, RED)
    draw_centered(cv, x + w // 2, y + 160, "SWISS DIPLOMATIC", 3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 183, "OFFICE CLOSED", 3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 206, "PYONGYANG ORDERS", 3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 229, "SWISS OUT", 3, WHITE, 0)

# ---------------------------------------------------------------- hero: Russia 500,000
def draw_hero(cv):
    x, y, w, h = 300, 148, 360, 252
    cv.fill_rect(x, y, w, h, RED_D)
    cv.border(x, y, w, h, GOLD, 3)
    cv.fill_rect(x + 3, y + 3, w - 6, 3, GOLD_D)
    draw_centered(cv, x + w // 2, y + 10, "RUSSIA'S OWN FIGURES", 3, GOLD, 0)
    draw_centered(cv, x + w // 2, y + 34, "MOSCOW'S OWN COUNT", 2, OFFW)
    draw_centered(cv, x + w // 2, y + 56, "NEARLY", 5, WHITE)
    # big number band
    cv.fill_rect(x + 10, y + 96, w - 20, 66, RED_B)
    cv.border(x + 10, y + 96, w - 20, 66, GOLD_D, 1)
    draw_centered(cv, x + w // 2, y + 104, "500,000", 8, GOLD)
    # row of remembrance crosses
    cy = y + 178
    for i in range(8):
        cx = x + 34 + i * 40
        cv.fill_rect(cx - 2, cy, 5, 18, WHITE)
        cv.fill_rect(cx - 8, cy + 5, 17, 5, WHITE)
    # black bottom band
    cv.fill_rect(x + 3, y + 206, w - 6, 43, BLACK)
    draw_centered(cv, x + w // 2, y + 216, "DEAD IN UKRAINE WAR", 3, WHITE, 0)

# ---------------------------------------------------------------- top right: US tariffs
def draw_tariffs(cv):
    x, y, w, h = 668, 148, 348, 252
    panel(cv, x, y, w, h, CYAN)
    kicker(cv, x, w, y + 10, "TRADE WAR", "WASHINGTON, USA", OFFW, GOLD)
    # rising tariff bar chart; last two bars red (the new hikes)
    bx, by = x + 24, y + 140   # baseline
    heights = [26, 38, 32, 52, 44, 64, 78]
    bw = 34
    for i, hh in enumerate(heights):
        col = RED if i >= 5 else CYAN
        cv.fill_rect(bx + i * 44, by - hh, bw, hh, col)
        cv.fill_rect(bx + i * 44, by - hh, bw, 3, WHITE)
    cv.hline(bx, by, 7 * 44, WHITE)
    draw_centered(cv, x + w // 2, y + 146, "TARIFFS RISE - 15% ON TAIWAN",
                  2, MUTED)
    # caption band (4 lines, 23px pitch = 2px leading)
    cv.fill_rect(x + 3, y + 160, w - 6, 90, PANEL2)
    draw_centered(cv, x + w // 2, y + 160, "TRUMP ANNOUNCES", 3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 183, "NEW TARIFFS", 3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 206, "CHINA, JAPAN, EU HIT", 3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 229, "TAIWAN 15%", 3, GOLD, 0)

# ---------------------------------------------------------------- central world map
CONTINENTS = [
    # North America
    [(4, 18), (12, 8), (26, 6), (34, 12), (30, 20), (24, 26), (18, 32),
     (10, 30), (4, 26)],
    # Greenland
    [(30, 4), (38, 2), (40, 8), (33, 10)],
    # South America
    [(24, 42), (32, 40), (38, 46), (36, 58), (30, 68), (26, 58), (22, 48)],
    # Europe
    [(46, 10), (56, 8), (60, 14), (54, 20), (48, 18), (44, 14)],
    # Africa
    [(46, 28), (58, 26), (64, 32), (62, 44), (56, 56), (50, 52), (46, 40)],
    # Asia
    [(60, 8), (82, 4), (96, 10), (94, 22), (84, 26), (76, 34),
     (68, 28), (62, 20)],
    # SE Asia islands
    [(78, 40), (86, 42), (84, 48), (76, 46)],
    # Australia
    [(80, 58), (92, 56), (96, 62), (88, 68), (80, 66)],
]

# cities in 0..100 map space: (x, y, colour)
CITIES = [
    (8, 22, GOLD),    # Washington
    (88, 16, RED),    # Pyongyang
    (62, 10, GOLD),   # Moscow
    (52, 30, GOLD),   # Cairo
    (84, 46, GOLD),   # Jakarta
    (70, 34, CYAN),   # Delhi / Ranchi region
    (24, 52, CYAN),   # Bogota region
    (48, 14, CYAN),   # London region
]

def draw_map(cv):
    x, y, w, h = 300, 408, 360, 232
    panel(cv, x, y, w, h, CYAN)
    draw_centered(cv, x + w // 2, y + 8, "WORLD MAP", 3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 30, "26 NOV 2026 - EVERY REGION",
                  2, GOLD)
    bx, by, bw, bh = x + 14, y + 52, w - 28, h - 64

    def mx(px):
        return bx + int(px * bw / 100)

    def my(py):
        return by + int(py * bh / 100)

    # faint graticule
    for i in range(1, 6):
        cv.vline(bx + i * bw // 6, by, bh, (24, 44, 78))
        cv.hline(bx, by + i * bh // 6, bw, (24, 44, 78))
    # continents, glowing cyan-blue
    for cont in CONTINENTS:
        pts = [(mx(px), my(py)) for px, py in cont]
        cv.poly(pts, CYAN_D)
        for i in range(len(pts)):
            cv.line(pts[i][0], pts[i][1],
                    pts[(i + 1) % len(pts)][0],
                    pts[(i + 1) % len(pts)][1], CYAN)
    # route arcs between the day's story cities
    arcs = [
        ((8, 22), (30, 2), (88, 16)),    # Washington -> Pyongyang
        ((62, 10), (75, 2), (88, 16)),   # Moscow -> Pyongyang
        ((52, 30), (66, 26), (84, 46)),  # Cairo -> Jakarta
        ((48, 14), (40, 30), (24, 52)),  # London -> Bogota
        ((70, 34), (60, 44), (52, 30)),  # Delhi -> Cairo
    ]
    for a, b, c in arcs:
        cv.bezier_dots((mx(a[0]), my(a[1])), (mx(b[0]), my(b[1])),
                       (mx(c[0]), my(c[1])), GOLD, step=0.03, dot=2)
    # glowing city dots
    for px, py, col in CITIES:
        cx, cy = mx(px), my(py)
        cv.disc(cx, cy, 6, (30, 90, 120))
        cv.disc(cx, cy, 3, col)
        cv.set(cx, cy, WHITE)

# ---------------------------------------------------------------- Builder 2
# Middle-left: Ranchi tree-felling protest.
def draw_ranchi(cv):
    x, y, w, h = 8, 408, 284, 232
    panel(cv, x, y, w, h, GREEN)
    kicker(cv, x, w, y + 8, "ENVIRONMENTAL PROTEST",
           "RANCHI, INDIA", OFFW, GOLD)
    # two trees, left
    cv.fill_rect(x + 22, y + 92, 7, 34, BROWN)
    cv.disc(x + 26, y + 84, 14, GREEN)
    cv.disc(x + 48, y + 92, 11, GREEN)
    cv.fill_rect(x + 62, y + 100, 6, 26, BROWN)
    cv.disc(x + 65, y + 94, 10, GREEN)
    # placard 1: STOP TREE FELLING (white board, green letters)
    cv.fill_rect(x + 92, y + 54, 178, 20, WHITE)
    draw_centered(cv, x + 92 + 89, y + 59, "STOP TREE FELLING", 1, GREEN)
    cv.vline(x + 120, y + 74, 26, BROWN)
    cv.vline(x + 240, y + 74, 26, BROWN)
    # placard 2: SAVE OUR FORESTS (green board, white letters)
    cv.fill_rect(x + 104, y + 80, 154, 20, GREEN)
    draw_centered(cv, x + 104 + 77, y + 85, "SAVE OUR FORESTS", 1, WHITE)
    cv.vline(x + 130, y + 100, 12, BROWN)
    cv.vline(x + 230, y + 100, 12, BROWN)
    # row of five protesters
    shirts = [RED, GOLD, CYAN, WHITE, GREEN]
    for i, shirt in enumerate(shirts):
        cx = x + 78 + i * 40
        cv.disc(cx, y + 118, 5, SKIN)
        cv.fill_rect(cx - 6, y + 124, 12, 22, shirt)
    cv.hline(x + 14, y + 148, w - 28, GREY)
    # green caption band, 3 lines scale 3, pitch 24 (3px leading)
    cv.fill_rect(x + 3, y + 150, w - 6, 79, GREEN)
    draw_centered(cv, x + w // 2, y + 155, "STOP TREE FELLING", 3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 179, "RANCHI POLICE", 3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 203, "DETAIN PROTESTERS", 3, WHITE, 0)

# Middle-right: 51st Annual Alexandria Turkey Trot.
def draw_turkey(cv):
    x, y, w, h = 668, 408, 348, 232
    panel(cv, x, y, w, h, ORANGE)
    kicker(cv, x, w, y + 8, "THANKSGIVING TRADITION",
           "ALEXANDRIA, VIRGINIA, USA", OFFW, GOLD)
    # bunting dots
    for i in range(13):
        cv.disc(x + 24 + i * 24, y + 44, 3,
                [GOLD, RED, CYAN][i % 3])
    # orange race banner on two poles
    cv.fill_rect(x + 24, y + 54, 300, 26, ORANGE)
    draw_centered(cv, x + w // 2, y + 59, "51ST ANNUAL TURKEY TROT",
                  2, WHITE, 0)
    cv.fill_rect(x + 24, y + 80, 3, 48, GREY)
    cv.fill_rect(x + 321, y + 80, 3, 48, GREY)
    # five runners
    shirts = [RED, GREEN, CYAN, GOLD, WHITE]
    for i, shirt in enumerate(shirts):
        cx = x + 50 + i * 60
        cv.disc(cx, y + 100, 5, SKIN)
        cv.fill_rect(cx - 6, y + 106, 12, 16, shirt)
        cv.fill_rect(cx - 6, y + 122, 4, 10, BLACK)
        cv.fill_rect(cx + 2, y + 122, 4, 10, BLACK)
    cv.hline(x + 16, y + 134, w - 32, GREY)
    # burnt-orange caption band, 4 lines scale 3, pitch 23 (2px leading)
    cv.fill_rect(x + 3, y + 138, w - 6, 91, BRN_OR)
    draw_centered(cv, x + w // 2, y + 139, "51ST ANNUAL", 3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 162, "TURKEY TROT", 3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 185, "HONORING 9/11 VICTIMS",
                  3, WHITE, 0)
    draw_centered(cv, x + w // 2, y + 208, "2,977 NAMES", 3, WHITE, 0)

# ---------------------------------------------------------------- bottom row
# Generic narrow panel: kicker, art, caption band. lines are scale 2.
def draw_bottom(cv, x, border, band, band_text, kick1, kick2, lines, art):
    y, w, h = 648, 195 if x < 820 else 196, 184
    panel(cv, x, y, w, h, border)
    draw_centered(cv, x + w // 2, y + 6, kick1, 2, OFFW, 0)
    draw_centered(cv, x + w // 2, y + 22, kick2, 2, GOLD, 0)
    art(cv, x)
    cv.fill_rect(x + 3, y + 102, w - 6, 79, band)
    n = len(lines)
    pitch = 15 if n >= 5 else 18
    ly = y + 118 if n == 3 else (y + 106 if n == 4 else y + 104)
    for i, ln in enumerate(lines):
        draw_centered(cv, x + w // 2, ly + i * pitch, ln, 2, band_text, 0)

def art_vp(cv, x):
    # hospital building with red cross + two figures in white coats
    cv.fill_rect(x + 14, 694, 58, 50, WHITE)
    cv.fill_rect(x + 14, 694, 58, 4, GOLD)
    cv.fill_rect(x + 38, 700, 10, 38, RED)
    cv.fill_rect(x + 26, 712, 34, 10, RED)
    for cx, shirt in ((x + 104, WHITE), (x + 148, (200, 210, 230))):
        cv.disc(cx, 704, 6, SKIN)
        cv.fill_rect(cx - 7, 711, 14, 33, shirt)
    cv.hline(x + 10, 747, 175, GREY)

def art_bok(cv, x):
    # rising rate bars, last one gold; gold trend arrow + 3.25% label
    draw_text(cv, x + 16, 686, "3.25%", 2, GOLD, 0)
    heights = [16, 24, 32, 40, 50]
    for i, hh in enumerate(heights):
        col = GOLD if i == 4 else CYAN
        bx = x + 16 + i * 32
        cv.fill_rect(bx, 744 - hh, 24, hh, col)
        cv.fill_rect(bx, 744 - hh, 24, 3, WHITE)
    pts = [(x + 28, 724), (x + 60, 716), (x + 92, 708),
           (x + 124, 700), (x + 156, 690)]
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], GOLD)
    cv.poly([(x + 160, 686), (x + 149, 689), (x + 153, 695)], GOLD)
    cv.hline(x + 14, 744, 167, WHITE)

def art_iran(cv, x):
    # ship on the strait, spiky mines in the water below it
    cv.hline(x + 12, 740, 171, CYAN_D)
    cv.hline(x + 12, 745, 171, CYAN_D)
    cv.poly([(x + 30, 714), (x + 160, 714), (x + 148, 736),
             (x + 42, 736)], GREY)
    cv.fill_rect(x + 60, 702, 40, 12, (90, 95, 105))
    cv.fill_rect(x + 110, 700, 14, 14, RED)
    cv.vline(x + 62, 690, 12, WHITE)
    cv.fill_rect(x + 62, 690, 14, 8, RED)
    for cx in (x + 28, x + 95, x + 166):
        cy = 742
        for dx, dy in ((-7, 0), (7, 0), (0, -7), (0, 7),
                       (-5, -5), (5, -5), (-5, 5), (5, 5)):
            cv.line(cx, cy, cx + dx, cy + dy, BLACK)
        cv.disc(cx, cy, 4, BLACK)

def art_cairo(cv, x):
    # flames over a fuel tanker on the highway
    cv.poly([(x + 97, 688), (x + 112, 714), (x + 82, 714)], ORANGE)
    cv.poly([(x + 97, 700), (x + 106, 714), (x + 88, 714)], YELLOW)
    cv.poly([(x + 62, 700), (x + 74, 714), (x + 50, 714)], RED)
    cv.poly([(x + 132, 698), (x + 144, 714), (x + 120, 714)], RED)
    cv.fill_rect(x + 30, 718, 90, 22, GREY)
    cv.disc(x + 30, 729, 11, GREY)
    cv.disc(x + 120, 729, 11, GREY)
    cv.fill_rect(x + 124, 720, 34, 20, RED)
    cv.fill_rect(x + 130, 723, 12, 8, WHITE)
    for cx in (x + 52, x + 100, x + 142):
        cv.disc(cx, 742, 5, BLACK)
    cv.hline(x + 12, 748, 171, GREY)

def art_uk(cv, x):
    # scales of justice
    cv.fill_rect(x + 82, 742, 30, 6, GOLD)
    cv.fill_rect(x + 95, 692, 3, 50, GOLD)
    cv.fill_rect(x + 62, 696, 68, 3, GOLD)
    cv.disc(x + 97, 690, 4, GOLD)
    cv.line(x + 70, 699, x + 62, 714, GOLD)
    cv.line(x + 70, 699, x + 78, 714, GOLD)
    cv.poly([(x + 60, 714), (x + 80, 714), (x + 70, 722)], GOLD)
    cv.line(x + 124, 699, x + 116, 714, GOLD)
    cv.line(x + 124, 699, x + 132, 714, GOLD)
    cv.poly([(x + 114, 714), (x + 134, 714), (x + 124, 722)], GOLD)

# ---------------------------------------------------------------- extra row
def draw_extra(cv, x, w, border, kick, line1, line2, rack=False):
    y = 840
    panel(cv, x, y, w, 72, border)
    cx = x + w // 2 + (20 if rack else 0)
    draw_centered(cv, cx, y + 7, kick, 2, GOLD, 0)
    draw_centered(cv, cx, y + 26, line1, 2, WHITE, 0)
    draw_centered(cv, cx, y + 44, line2, 2, WHITE, 0)
    if rack:
        # three stacked server units
        for i in range(3):
            ry = y + 18 + i * 13
            cv.fill_rect(x + 14, ry, 26, 10, (30, 45, 75))
            cv.border(x + 14, ry, 26, 10, CYAN, 1)
            cv.disc(x + 20, ry + 5, 2, CYAN)
            cv.disc(x + 34, ry + 5, 2, GOLD)

# ---------------------------------------------------------------- ticker
def draw_ticker(cv):
    x, y, w, h = 8, 920, 1008, 96
    panel(cv, x, y, w, h, CYAN)
    draw_centered(cv, x + w // 2, y + 6,
                  "ALSO TODAY - MORE FROM 26 NOVEMBER", 2, GOLD)
    lines = [
        "AUSTRALIA AND SOLOMON ISLANDS SIGN LANDMARK SECURITY PACT - "
        "JAPAN-EUROPE MISSION REACHES MERCURY AFTER 8 YEARS",
        "XI GRAFT PROBE SHAKES SHANGHAI - INDIA MARKS CONSTITUTION DAY - "
        "NEPAL GETS RS 15,000 CRORE PACKAGE - BANGLADESH RAISES GARMENT "
        "WAGE 36 PCT",
        "IPL 2027 AUCTION: 1,220 PLAYERS - COLOMBIA MARKS 10 YEARS OF "
        "PEACE DEAL - VENEZUELA DEBT 237.5 BILLION USD - PETROBRAS 122 "
        "BILLION USD PLAN",
        "SPAIN VOTES SUNDAY 29 NOV - FEIJOO AHEAD, VOX SURGES - BITCOIN "
        "BACK ABOVE $61,000 - US HOUSE ADVANCES STRATEGIC BITCOIN RESERVE "
        "BILL",
    ]
    for i, ln in enumerate(lines):
        draw_centered(cv, x + w // 2, y + 26 + i * 12, ln, 1, OFFW)
    cv.hline(x + 10, y + 76, w - 20, GOLD_D)
    draw_centered(cv, x + w // 2, y + 82,
                  "SOURCES: ANTARA - AP - INDIAN EXPRESS - JAGRANJOSH - "
                  "EUR RADIO - THE ZEBRA - ALXNOW - SELFSTUDYS - LIBRE NEWS "
                  "- M.LAMEDITERRANEE - PAPARAZZI.FUN", 1, MUTED)

# ---------------------------------------------------------------- main
def build():
    cv = Canvas(W, H, NAVY)
    cv.border(0, 0, W, H, GOLD_D, 2)
    draw_masthead(cv)
    draw_swiss(cv)
    draw_hero(cv)
    draw_tariffs(cv)

    # Middle row: Builder 2 regions left/right, map centre (Builder 1).
    draw_ranchi(cv)
    draw_map(cv)
    draw_turkey(cv)

    # Bottom row of 5 (Builder 2).
    draw_bottom(cv, 8, GREEN, GREEN, WHITE,
                "POLITICAL VETTING", "JAKARTA, INDONESIA",
                ["VP HEALTH CHECKS", "AMRAN, SUGIONO", "RSPAD JAKARTA"],
                art_vp)
    draw_bottom(cv, 211, GOLD, GOLD, BLACK,
                "CENTRAL BANK", "SEOUL, KOREA",
                ["BANK OF KOREA", "HIKES TO 3.25%",
                 "THIRD HIKE", "SINCE JULY"],
                art_bok)
    draw_bottom(cv, 414, RED, RED, WHITE,
                "CONFLICT AT SEA", "STRAIT OF HORMUZ",
                ["IRAN: SHIPS HIT", "MINES IN HORMUZ",
                 "TEHRAN WARNS", "SHIPS COORDINATE"],
                art_iran)
    draw_bottom(cv, 617, ORANGE, ORANGE, BLACK,
                "DEADLY CRASH", "CAIRO, EGYPT",
                ["31 KILLED IN", "CAIRO FIRE",
                 "TANKER CRASH", "ON HIGHWAY"],
                art_cairo)
    draw_bottom(cv, 820, BLUE, BLUE, WHITE,
                "LAW REFORM", "LONDON, ENGLAND",
                ["UK: STALKING NOW", "A STANDALONE CRIME",
                 "NO MORE PROVING", "FEAR", "UP TO 10 YEARS"],
                art_uk)

    # Extra slim row of 3 (Builder 2).
    draw_extra(cv, 8, 330, GREEN, "BOGOTA, COLOMBIA",
               "POLICE FREE 20 HOSTAGES", "AFTER 17 HOUR STANDOFF")
    draw_extra(cv, 346, 330, CYAN, "JERUSALEM, ISRAEL",
               "JUDGES: DROP NETANYAHU", "MOST SERIOUS CHARGES")
    draw_extra(cv, 684, 332, GOLD, "QUEENSLAND, AUSTRALIA",
               "ANTHROPIC'S $32B", "DATA CENTRE CLEARED", rack=True)

    # Ticker + source strip (Builder 2).
    draw_ticker(cv)
    return cv

# ---------------------------------------------------------------- PNG encoder
def png_bytes(cv):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))

def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./output")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)

if __name__ == "__main__":
    main()
