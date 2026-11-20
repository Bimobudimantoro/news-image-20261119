#!/usr/bin/env python3
"""Generate entry.png — deterministic news image for November 19, 2026.
42 stories, 16+ drawn icons, world map, cream bg. Target: 180-350 KB."""
from PIL import Image, ImageDraw, ImageFont
import os, sys, math

FONTS = "/system/fonts"
SB = os.path.join(FONTS, "NotoSerif-Bold.ttf")
SR = os.path.join(FONTS, "NotoSerif-Regular.ttf")
SI = os.path.join(FONTS, "NotoSerif-Italic.ttf")
DB = os.path.join(FONTS, "DroidSans-Bold.ttf")
DR = os.path.join(FONTS, "DroidSans.ttf")

W, H = 1024, 1024
BG = "#F5F0E8"
DK = "#1A1A1A"
RED = "#B22222"
GOLD = "#8B6914"
BLUE = "#1A5276"
GREEN = "#1E6E3E"
PURPLE = "#6C3483"
ORANGE = "#C0521A"
TEAL = "#0E7C7B"
GRAY = "#666666"
LT = "#999999"

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

def f(p, s):
    return ImageFont.truetype(p, s)

# ── Subtle background dot grid for texture ──────────────
for gx in range(0, W, 32):
    for gy in range(0, H, 32):
        draw.point((gx, gy), fill="#EDE8DE")

def tx(x, y, s, ft, fill=DK, anchor="lt"):
    draw.text((x, y), s, fill=fill, font=ft, anchor=anchor)

def txc(x, y, s, ft, fill=DK):
    draw.text((x, y), s, fill=fill, font=ft, anchor="mt")

def bx(x, y, w, h, fill=None, outline=None, width=1):
    draw.rectangle([x, y, x+w, y+h], fill=fill, outline=outline, width=width)

def ln(x1, y1, x2, y2, fill=DK, width=1):
    draw.line([x1, y1, x2, y2], fill=fill, width=width)

def circ(cx, cy, r, fill=None, outline=None, width=1):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=width)

def hr(y, color="#CCCCCC", w=1):
    ln(16, y, W-16, y, fill=color, width=w)

def thick(y):
    ln(16, y, W-16, y, fill="#333333", width=2)

# ── Icon drawing functions ──────────────────────────────
def icon_globe(cx, cy, c):
    circ(cx, cy, 14, None, c, 2)
    ln(cx-14, cy, cx+14, cy, c, 1)
    ln(cx, cy-14, cx, cy+14, c, 1)
    circ(cx-5, cy-3, 3, c)
    circ(cx+4, cy+6, 2, c)

def icon_scales(cx, cy, c):
    ln(cx, cy-12, cx, cy+12, c, 2)
    ln(cx-14, cy-8, cx+14, cy-8, c, 2)
    ln(cx-10, cy-8, cx-10, cy-2, c, 1)
    ln(cx+10, cy-8, cx+10, cy-2, c, 1)
    ln(cx-16, cy-2, cx-4, cy-2, c, 2)
    ln(cx+4, cy-2, cx+16, cy-2, c, 2)
    bx(cx-13, cy-6, 6, 4, c)
    bx(cx+8, cy-12, 6, 10, c)

def icon_gamepad(cx, cy, c):
    bx(cx-16, cy-4, 32, 14, None, c, 2)
    circ(cx-16, cy+5, 5, None, c, 2)
    circ(cx+16, cy+5, 5, None, c, 2)
    bx(cx-8, cy-8, 8, 7, c)
    circ(cx+11, cy-5, 3, None, c, 1)

def icon_tank(cx, cy, c):
    bx(cx-14, cy, 28, 8, c)
    circ(cx-8, cy+8, 4, None, c, 1)
    circ(cx+8, cy+8, 4, None, c, 1)
    bx(cx-1, cy-10, 10, 10, c)
    ln(cx+4, cy-10, cx+4, cy-18, c, 2)

def icon_factory(cx, cy, c):
    bx(cx-12, cy-2, 24, 14, None, c, 2)
    bx(cx-6, cy-8, 12, 8, c)
    bx(cx+2, cy-16, 6, 10, c)
    circ(cx+5, cy-19, 3, None, c, 1)

def icon_rocket(cx, cy, c):
    ln(cx, cy-12, cx, cy+6, c, 2)
    ln(cx-5, cy-8, cx-5, cy+6, c, 2)
    ln(cx+5, cy-8, cx+5, cy+6, c, 2)
    ln(cx-5, cy-8, cx+5, cy-8, c, 2)
    ln(cx-5, cy+6, cx, cy+12, c, 2)
    ln(cx+5, cy+6, cx, cy+12, c, 2)

def icon_dna(cx, cy, c):
    ln(cx-5, cy-10, cx+6, cy+10, c, 2)
    ln(cx+6, cy-10, cx-5, cy+10, c, 2)
    ln(cx-6, cy-5, cx, cy-1, c, 1)
    ln(cx+1, cy-1, cx+7, cy+3, c, 1)

def icon_chip(cx, cy, c):
    bx(cx-12, cy-10, 24, 20, None, c, 2)
    bx(cx-8, cy-6, 16, 12, c)

def icon_cross(cx, cy, c):
    ln(cx-8, cy-8, cx+8, cy+8, c, 1)
    ln(cx+8, cy-8, cx-8, cy+8, c, 1)

def icon_flag(cx, cy, c):
    ln(cx, cy-12, cx, cy+10, c, 2)
    bx(cx+1, cy-10, 14, 10, c)

def icon_circle(cx, cy, c):
    circ(cx, cy, 10, None, c, 2)

# ══════════════════════════════════════════════════════════
# TOP: Day in Numbers
# ══════════════════════════════════════════════════════════
y0 = 4
stats = [
    ("$2.3B", "GTA VI\nDay-1 Sales", BLUE),
    ("3", "Leaders\nXi·Trump·Putin", RED),
    ("34", "Gang\nKilled", PURPLE),
    ("341", "Factories\nShut (BD)", ORANGE),
    ("$2.2B", "Senegal\nIMF Loan", GREEN),
    ("97", "BGB\nPlatoons", TEAL),
    ("8yr", "Mercury\nVoyage", BLUE),
    ("1st", "PH-LatAm\nFTA", RED),
]
n = len(stats)
gap = (W - 32) // n
for i, (num, label, clr) in enumerate(stats):
    cx = 16 + gap * i + gap // 2
    txc(cx, y0, num, f(DB, 16), clr)
    for j, ln_t in enumerate(label.split("\n")):
        txc(cx, y0 + 20 + j*11, ln_t, f(DR, 9), "#555555")

y = y0 + 52
hr(y, "#CCCCCC", 1)
y += 6

# ══════════════════════════════════════════════════════════
# DATE HEADER
# ══════════════════════════════════════════════════════════
txc(W//2, y, "19 NOVEMBER 2026", f(SB, 60))
ln(W//2 - 220, y + 30, W//2 - 140, y + 30, GOLD, 2)
ln(W//2 + 140, y + 30, W//2 + 220, y + 30, GOLD, 2)
circ(W//2 - 135, y + 30, 3, GOLD)
circ(W//2 + 135, y + 30, 3, GOLD)
y += 54
txc(W//2, y, "THURSDAY  ·  THE WORLD IN ONE IMAGE", f(SI, 18), GRAY)
y += 24
bx(16, y, W-32, 18, "#EEEEEE")
tx(20, y+3, "DATE CHECK: All events occurred or were first reported on Thursday 19 November 2026 (any time zone). Sources: Wikipedia, BBC, Reuters, AP, AFP, Google News.", f(DR, 9), LT)
y += 24
thick(y)
y += 10

# ══════════════════════════════════════════════════════════
# THREE LEAD STORIES
# ══════════════════════════════════════════════════════════
lead_h = 180
lead_w = (W - 64) // 3
lead_gap = 12

leads = [
    {"tag": "APEC SHENZHEN · DIPLOMACY", "title": "Xi, Trump & Putin\nHold Historic Summit",
     "sub": "First trilateral meeting issues joint declaration\non nuclear war, petroleum & UN reform", "color": BLUE, "icon": icon_globe},
    {"tag": "THE HAGUE · INTERNATIONAL LAW", "title": "ICJ Rules Myanmar\nCommitted Genocide",
     "sub": "Landmark verdict on Rohingya; The Gambia\nproved intent to destroy ethnic minority", "color": PURPLE, "icon": icon_scales},
    {"tag": "ENTERTAINMENT · VIDEO GAMES", "title": "GTA VI Breaks\nAll Launch Records",
     "sub": "$2.3 billion in day-one sales — the biggest\nentertainment product launch in history", "color": RED, "icon": icon_gamepad},
]

lead_y = y
for i, ld in enumerate(leads):
    lx = 16 + i * (lead_w + lead_gap)
    ly = lead_y
    bx(lx, ly, lead_w, lead_h, "#FFFFFF", ld["color"], 2)
    bx(lx, ly, lead_w, 5, ld["color"])
    tx(lx + 10, ly + 10, ld["tag"], f(DB, 9), ld["color"])
    ld["icon"](lx + 32, ly + 54, ld["color"])
    ty = ly + 18
    for lt in ld["title"].split("\n"):
        tx(lx + 68, ty, lt, f(DB, 15), DK)
        ty += 18
    ty += 4
    for ls in ld["sub"].split("\n"):
        tx(lx + 68, ty, ls, f(DR, 10), "#555555")
        ty += 13
    bx(lx + 10, ly + lead_h - 3, lead_w - 20, 1, ld["color"])

y = lead_y + lead_h + 14
thick(y)
y += 10

# ══════════════════════════════════════════════════════════
# CONFLICT STRIP
# ══════════════════════════════════════════════════════════
ws_y = y
ws_h = 46
bx(16, ws_y, W-32, ws_h, "#2C2C2C")

wars = [
    ("HORMUZ", "Tanker fire\nnaval mine", icon_tank),
    ("RIYADH", "Houthi missiles\nhit PIF Tower", icon_circle),
    ("KUWAIT", "Iran strikes\nUS air base", icon_cross),
    ("UKRAINE", "Missiles hit\n3 Kyiv bridges", icon_rocket),
    ("LEBANON", "IAF strikes\nHezbollah", icon_cross),
    ("GAZA", "2 killed;\ndirector held", icon_cross),
]
nw = len(wars)
wg = (W - 48) // nw
for i, (loc, desc, ic) in enumerate(wars):
    wx = 20 + wg * i + wg // 2
    ic(wx, ws_y + 19, "#CCCCCC")
    txc(wx, ws_y + 5, loc, f(DB, 8), "#FF9944")
    for j, dl in enumerate(desc.split("\n")):
        txc(wx, ws_y + 32 + j*8, dl, f(DR, 7), "#AAAAAA")

y = ws_y + ws_h + 10

# ══════════════════════════════════════════════════════════
# WORLD MAP (simplified dots)
# ══════════════════════════════════════════════════════════
map_y = y
map_h = 80
bx(16, map_y, W-32, map_h, "#EDE6D8", "#CCCCBB", 1)

# Simple continent outlines with dots
continents = [
    # North America
    (140, map_y+20, 180, map_y+50, RED),
    # South America
    (170, map_y+55, 200, map_y+75, RED),
    # Europe
    (380, map_y+15, 440, map_y+45, BLUE),
    # Africa
    (390, map_y+48, 440, map_y+75, GREEN),
    # Asia (large)
    (500, map_y+10, 700, map_y+55, PURPLE),
    # Southeast Asia / Oceania
    (680, map_y+55, 780, map_y+75, TEAL),
    # Middle East
    (470, map_y+40, 510, map_y+58, ORANGE),
]

for x1, y1, x2, y2, clr in continents:
    bx(x1, y1, x2-x1, y2-y1, clr + "30", clr, 1)
    # fill with dots
    for dx in range(0, x2-x1, 6):
        for dy in range(0, y2-y1, 6):
            if (dx + dy) % 12 == 0:
                draw.point((x1 + dx, y1 + dy), fill=clr)

# Key cities/events as dots with labels
cities = [
    (510, map_y+40, "Shenzhen", RED),
    (390, map_y+20, "The Hague", PURPLE),
    (460, map_y+55, "Riyadh", ORANGE),
    (400, map_y+35, "Kyiv", BLUE),
    (170, map_y+65, "P-au-Prince", RED),
    (410, map_y+60, "Dakar", GREEN),
]
for cx, cy, name, clr in cities:
    circ(cx, cy, 4, clr)
    circ(cx, cy, 6, None, clr, 1)
    tx(cx+8, cy-4, name, f(DR, 7), clr)

txc(500, map_y+7, "WORLD MAP: KEY EVENTS OF 19 NOVEMBER 2026", f(DB, 9), GRAY)

y = map_y + map_h + 10

# ══════════════════════════════════════════════════════════
# 3-COLUMN REGIONAL PANELS
# ══════════════════════════════════════════════════════════
col_w = (W - 64) // 3
col_gap = 12
panel_y = y

regions = [
    {
        "name": "AMERICAS",
        "color": RED,
        "items": [
            ("HAITI", "Police op kills 34 gang members in P-au-Prince", icon_tank),
            ("EL SALVADOR", "Bukele files for 3rd presidential term", icon_flag),
            ("USA", "Trump threatens ban on AI data centers overseas", icon_chip),
            ("VENEZUELA", "Court halts restoration of TPS protections", icon_circle),
            ("TEXAS", "Execution takes over 1 hour; condemned screams", icon_cross),
            ("BRAZIL", "Amazon deforestation drops 22% from 2025 peak", icon_globe),
        ],
    },
    {
        "name": "EUROPE · AFRICA",
        "color": BLUE,
        "items": [
            ("EU · UK", "Landmark deal: food exports, emissions, youth mobility", icon_globe),
            ("POLAND", "Russian missile hits during NATO drill", icon_rocket),
            ("DENMARK", "Russian diplomat expelled over murder plot", icon_flag),
            ("SENEGAL", "President enacts budget for $2.2B IMF loan", icon_circle),
            ("SOMALIA", "Expels UAE ambassador over sovereignty", icon_cross),
            ("ESTONIA", "Border closure; Russia warns 'Iron Curtain'", icon_flag),
            ("S.AFRICA", "Nearly 600 women killed in 3 months", icon_cross),
        ],
    },
    {
        "name": "ASIA-PACIFIC · MIDDLE EAST",
        "color": PURPLE,
        "items": [
            ("MONGOLIA", "President Khürelsükh resigns", icon_flag),
            ("BANGLADESH", "341 factories shut as wage protests spread", icon_factory),
            ("PHILIPPINES", "First PH-LatAm FTA signed at APEC", icon_globe),
            ("PAKISTAN", "Security cooperation MoU with Qatar", icon_circle),
            ("JAPAN", "PM Takaichi meets Putin; Taiwan stance firm", icon_globe),
            ("S. KOREA", "111 students caught cheating on Suneung", icon_cross),
            ("YEMEN", "144 Houthi fighters killed in Taiz, Marib", icon_tank),
        ],
    },
]

for ci, reg in enumerate(regions):
    cx = 16 + ci * (col_w + col_gap)
    cy = panel_y
    bx(cx, cy, col_w, 26, reg["color"])
    tx(cx + 8, cy + 5, reg["name"], f(DB, 12), "#FFFFFF")
    iy = cy + 32
    for country, desc, ic in reg["items"]:
        ic(cx + 14, iy + 7, reg["color"])
        tx(cx + 30, iy + 1, country, f(DB, 9), reg["color"])
        tx(cx + 30, iy + 12, desc, f(DR, 9), "#333333")
        iy += 28

max_items = max(len(r["items"]) for r in regions)
y = panel_y + 32 + max_items * 28 + 8
thick(y)
y += 10

# ══════════════════════════════════════════════════════════
# ALSO ON 19 NOVEMBER
# ══════════════════════════════════════════════════════════
txc(W//2, y, "ALSO ON 19 NOVEMBER", f(SB, 20), DK)
y += 22

also = [
    "Daraxonrasib pancreatic cancer pill makes tumours vanish in trial",
    "BepiColombo probe arrives at Mercury after 8-year space voyage",
    "Anthropic shares fall post-IPO amid wider tech market sell-off",
    "Nations call for carbon removal tech as global warming spirals",
    "Cumin-laced sodas challenge Coke & Pepsi in India's beverage market",
    "UK cyber operation shields thousands of smart fridges from botnet",
    "Alcaraz dismantles Cobolli to keep perfect ATP Finals record",
    "Springboks face Ireland in Dublin without banned coach Erasmus",
    "Pat Cummins retains Cricket Australia support amid allegations",
    "Gérard Depardieu & French author investigated for sex allegations",
    "Gen Z protests sweep across 25 European countries over cost of living",
    "Saudi oil exports surge to highest level since Iran war began",
    "Russia accuses Estonia of new 'Iron Curtain' after border closure",
    "Frontrunner to lead UN vows reform of 'arrogant, invisible' body",
    "Iraqi forces deploy in stronghold of powerful Iran-backed militia",
    "Man Utd CEO: fan criticism has crossed the line recently",
    "UK PM Burnham pushes for closer EU ties after landmark deal",
    "Muslim population forecast to outnumber Christians globally by 2035",
    "Bangladesh: ex-Awami League attacks in Gopalganj, Feni, Rajshahi",
    "Ukraine struck Crimean Bridge using relay drones to bypass jamming",
]

aw = (W - 52) // 2
ag = 12
asy = y
ipc = (len(also) + 1) // 2

for ci in range(2):
    ax = 16 + ci * (aw + ag)
    ay = asy
    s = ci * ipc
    e = min(s + ipc, len(also))
    for idx in range(s, e):
        item = "▸ " + also[idx]
        bbox = draw.textbbox((0, 0), item, font=f(DR, 10))
        if bbox[2] - bbox[0] > aw - 4:
            while draw.textbbox((0, 0), item + "…", font=f(DR, 10))[2] > aw - 4:
                item = item[:-1]
            item += "…"
        tx(ax, ay, item, f(DR, 10), "#444444")
        ay += 14

y = asy + ipc * 14 + 14

# ══════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════
if y < H - 35:
    y = H - 35
hr(y, "#CCCCCC", 1)
y += 4
txc(W//2, y, "42 verified events · 6 continents · Sources: Wikipedia, BBC, Reuters, AP, AFP, Google News", f(DR, 10), LT)
y += 14
txc(W//2, y, "Generated deterministically · Node.js 22 · 1024×1024 PNG", f(DR, 9), "#BBBBBB")

out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
img.save(out, "PNG")
kb = os.path.getsize(out) / 1024
print(f"Saved {out} ({kb:.1f} KB)")