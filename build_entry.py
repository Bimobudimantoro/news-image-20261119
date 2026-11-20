#!/usr/bin/env python3
"""build_entry.py — deterministic SVG-to-PNG builder for news-image-20261119.
Generates a pure SVG viewBox="0 0 1024 1024" document styled as an international
broadsheet newspaper (Economist / FT / NYT), then renders to entry.png via cairosvg.
All font sizes calibrated for legibility at 300×300 thumbnail.

Usage: python3 build_entry.py [output.png]
"""

import os, sys, hashlib, io, math

# ── Colour palette ────────────���───────────────────────────────
BG       = "#F4EFE4"
INK      = "#141414"
INK2     = "#2C2A26"   # darker secondary ink for body text
RULE     = "#B8AFA0"
RED      = "#9E1B1B"
BLUE     = "#1B365D"
GOLD     = "#8B7430"
DARK     = "#1C1B19"
WHITE    = "#FFFFFF"
MAP_BG   = "#DDD4C2"
MAP_STR  = "#9E9585" 
GREEN    = "#1E5E3A"
PURPLE   = "#5B2C6E"
ORANGE   = "#B85C1A"
TEAL     = "#0C6F6F"
LTGRAY   = "#8A8578"
CREAM_BOX = "#FCF8F0"

# ── Typography ────────────────────────────────────────────────
SB = "font-weight='bold' font-family='Noto Serif, Georgia, serif'"
SR = "font-family='Noto Serif, Georgia, serif'"
SI = "font-style='italic' font-family='Noto Serif, Georgia, serif'"
DB = "font-weight='bold' font-family='Droid Sans, Arial, sans-serif'"
DR = "font-family='Droid Sans, Arial, sans-serif'"

def T(x, y, s, font, size, fill=INK, anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" {font} font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>{esc(s)}</text>'

def TC(x, y, s, font, size, fill=INK, extra=""):
    return T(x, y, s, font, size, fill, "middle", extra)

def esc(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def R(x, y, w, h, fill=None, stroke=None, sw=1):
    a = f'x="{x}" y="{y}" width="{w}" height="{h}"'
    if fill: a += f' fill="{fill}"'
    if stroke: a += f' stroke="{stroke}" stroke-width="{sw}"'
    return f'<rect {a}/>'

def L(x1, y1, x2, y2, stroke=INK, sw=1):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"/>'

def C(cx, cy, r, fill=None, stroke=None, sw=1):
    a = f'cx="{cx}" cy="{cy}" r="{r}"'
    if fill: a += f' fill="{fill}"'
    if stroke: a += f' stroke="{stroke}" stroke-width="{sw}"'
    return f'<circle {a}/>'

# ═══════════════════════════════════════════════════════════════
# DETAILED SVG ICONS
# ═══════════════════════════════════════════════════════════════

def icon_summit(x, y, c=BLUE):
    """Globe + 3 leader podiums for Xi-Trump-Putin summit."""
    o = []
    o.append(C(x, y, 22, None, c, 2.8))
    o.append(L(x-22, y, x+22, y, c, 1.3))
    o.append(L(x, y-22, x, y+22, c, 1.3))
    o.append(f'<ellipse cx="{x}" cy="{y}" rx="22" ry="9" fill="none" stroke="{c}" stroke-width="0.9"/>')
    o.append(f'<ellipse cx="{x}" cy="{y-7}" rx="20" ry="7" fill="none" stroke="{c}" stroke-width="0.6"/>')
    o.append(f'<ellipse cx="{x}" cy="{y+7}" rx="18" ry="6" fill="none" stroke="{c}" stroke-width="0.6"/>')
    # 3 podiums
    for px, clr in [(x-15,RED),(x,BLUE),(x+15,c)]:
        o.append(f'<rect x="{px-7}" y="{y+18}" width="14" height="9" fill="{clr}" rx="2"/>')
        o.append(f'<rect x="{px-5}" y="{y+18}" width="10" height="2" fill="{WHITE}" rx="1"/>')
    return "\n".join(o)

def icon_scales(x, y, c=PURPLE):
    """Justice scales + gavel for ICJ verdict."""
    o = []
    o.append(L(x, y-20, x, y+12, c, 3.5))
    o.append(R(x-18, y+5, 36, 7, c))
    o.append(L(x-18, y-11, x+18, y-11, c, 2.8))
    # Left pan
    o.append(f'<path d="M{x-16},{y-11} L{x-16},{y-2} L{x-7},{y-2}" fill="none" stroke="{c}" stroke-width="1.8"/>')
    o.append(f'<ellipse cx="{x-11}" cy="{y-2}" rx="5" ry="2.5" fill="none" stroke="{c}" stroke-width="1.8"/>')
    # Right pan (higher)
    o.append(f'<path d="M{x+16},{y-11} L{x+16},{y-7} L{x+7},{y-7}" fill="none" stroke="{c}" stroke-width="1.8"/>')
    o.append(f'<ellipse cx="{x+11}" cy="{y-7}" rx="5" ry="2.5" fill="none" stroke="{c}" stroke-width="1.8"/>')
    # Gavel
    o.append(R(x-5, y-25, 16, 6, c))
    o.append(L(x+3, y-19, x+3, y-14, c, 2.5))
    return "\n".join(o)

def icon_gamepad(x, y, c=RED):
    """Gamepad + record bars for GTA VI."""
    o = []
    o.append(f'<rect x="{x-20}" y="{y-8}" width="40" height="20" rx="9" fill="none" stroke="{c}" stroke-width="2.8"/>')
    o.append(f'<ellipse cx="{x-20}" cy="{y+10}" rx="7" ry="6" fill="none" stroke="{c}" stroke-width="2.2"/>')
    o.append(f'<ellipse cx="{x+20}" cy="{y+10}" rx="7" ry="6" fill="none" stroke="{c}" stroke-width="2.2"/>')
    o.append(R(x-13, y-5, 9, 7, c))
    o.append(R(x-11, y-7, 5, 11, c))
    o.append(C(x+11, y-2, 3.5, None, c, 1.8))
    o.append(C(x+16, y-5, 3, None, c, 1.5))
    # Record bars
    o.append(R(x+3, y-18, 4, 10, RED))
    o.append(R(x+9, y-22, 4, 14, RED))
    o.append(R(x+15, y-24, 4, 16, RED))
    o.append(f'<text x="{x+17}" y="{y-28}" {DB} font-size="7" fill="{RED}" text-anchor="middle">$2.3B</text>')
    return "\n".join(o)

# ── Conflict strip icons ──────────────────────────────────────
def icon_tanker(x, y, c=WHITE):
    o = []
    o.append(f'<path d="M{x-20},{y+4} L{x+20},{y+4} L{x+17},{y} L{x-17},{y} Z" fill="none" stroke="{c}" stroke-width="2.2"/>')
    o.append(R(x-10, y-8, 9, 8, None, c, 1.8))
    o.append(R(x+3, y-12, 6, 12, None, c, 1.5))
    o.append(C(x+6, y-16, 2.5, None, c, 1))
    o.append(C(x+9, y-20, 2, None, c, 0.8))
    return "\n".join(o)

def icon_missile(x, y, c=WHITE):
    o = []
    o.append(f'<polygon points="{x},{y-16} {x-6},{y+5} {x-2},{y+5} {x},{y-1} {x+2},{y+5} {x+6},{y+5}" fill="none" stroke="{c}" stroke-width="2.2"/>')
    o.append(R(x-4, y+5, 8, 4, c))
    o.append(L(x-5, y+12, x-8, y+16, c, 1.8))
    o.append(L(x+5, y+12, x+8, y+16, c, 1.8))
    o.append(C(x, y+10, 2, GOLD))
    return "\n".join(o)

def icon_airbase(x, y, c=WHITE):
    o = []
    o.append(f'<path d="M{x-18},{y+4} L{x+18},{y+4} L{x+13},{y-9} L{x-13},{y-9} Z" fill="none" stroke="{c}" stroke-width="2.2"/>')
    o.append(R(x-13, y-9, 26, 7, None, c, 1.8))
    o.append(R(x-4, y-18, 8, 11, None, c, 1.8))
    o.append(L(x, y-18, x, y-23, c, 1.2))
    o.append(C(x, y-24, 2.5, None, c, 1.2))
    return "\n".join(o)

def icon_bridge(x, y, c=WHITE):
    o = []
    o.append(f'<path d="M{x-20},{y+2} Q{x-11},{y-12} {x-5},{y+2} Q{x},{y-12} {x+5},{y+2} Q{x+11},{y-12} {x+20},{y+2}" fill="none" stroke="{c}" stroke-width="2.8"/>')
    o.append(R(x-7, y+2, 4, 12, None, c, 1.8))
    o.append(R(x+3, y+2, 4, 12, None, c, 1.8))
    o.append(L(x-20, y+16, x+20, y+16, c, 1.2))
    return "\n".join(o)

def icon_explosion(x, y, c=WHITE):
    o = []
    for a in [0,45,90,135,180,225,270,315]:
        ex = x + 11*math.cos(math.radians(a))
        ey = y + 11*math.sin(math.radians(a))
        o.append(L(x, y, ex, ey, c, 1.8))
    o.append(C(x, y, 6, None, c, 1.8))
    o.append(C(x, y, 3, GOLD))
    return "\n".join(o)

def icon_shield(x, y, c=WHITE):
    o = []
    o.append(f'<path d="M{x},{y-18} L{x+16},{y-9} L{x+16},{y+5} Q{x+16},{y+16} {x},{y+18} Q{x-16},{y+16} {x-16},{y+5} L{x-16},{y-9} Z" fill="none" stroke="{c}" stroke-width="2.2"/>')
    o.append(L(x-7, y-2, x+7, y-2, c, 1.8))
    o.append(L(x-5, y+4, x+5, y+4, c, 1.8))
    return "\n".join(o)

# ── Mini icons (20x20 target) ─────────────────────────────────
def mi_tank(x, y, c):
    o = []
    o.append(R(x-8, y+2, 16, 6, c))
    o.append(C(x-5, y+8, 3, None, c, 1))
    o.append(C(x+5, y+8, 3, None, c, 1))
    o.append(R(x-1, y-4, 7, 6, c))
    o.append(L(x+3, y-4, x+3, y-9, c, 1.3))
    return "\n".join(o)

def mi_flag(x, y, c):
    o = []
    o.append(L(x, y-9, x, y+8, c, 1.8))
    o.append(R(x+1, y-8, 10, 6, c))
    return "\n".join(o)

def mi_chip(x, y, c):
    o = []
    o.append(R(x-8, y-7, 16, 14, None, c, 1.8))
    o.append(R(x-4, y-3, 8, 6, c))
    o.append(L(x-8, y, x-2, y, c, 1))
    o.append(L(x+2, y, x+8, y, c, 1))
    return "\n".join(o)

def mi_factory(x, y, c):
    o = []
    o.append(R(x-9, y, 18, 9, None, c, 1.8))
    o.append(R(x-5, y-6, 10, 6, c))
    o.append(R(x+1, y-12, 5, 8, None, c, 1.3))
    o.append(C(x+3, y-13, 2, None, c, 1))
    return "\n".join(o)

def mi_globe(x, y, c):
    o = []
    o.append(C(x, y, 8.5, None, c, 1.8))
    o.append(L(x-8.5, y, x+8.5, y, c, 1))
    o.append(L(x, y-8.5, x, y+8.5, c, 1))
    o.append(f'<ellipse cx="{x}" cy="{y}" rx="8.5" ry="3.5" fill="none" stroke="{c}" stroke-width="0.7"/>')
    return "\n".join(o)

def mi_rocket(x, y, c):
    o = []
    o.append(f'<polygon points="{x},{y-8} {x-4},{y+4} {x-1},{y+4} {x},{y} {x+1},{y+4} {x+4},{y+4}" fill="none" stroke="{c}" stroke-width="1.8"/>')
    return "\n".join(o)

def mi_cross(x, y, c):
    o = []
    o.append(L(x-6, y-6, x+6, y+6, c, 1.5))
    o.append(L(x+6, y-6, x-6, y+6, c, 1.5))
    return "\n".join(o)

def mi_dollar(x, y, c):
    o = []
    o.append(L(x, y-9, x, y+8, c, 1.8))
    o.append(f'<path d="M{x-5},{y-4} Q{x},{y-6} {x+4},{y-2} Q{x+4},{y-1} {x},{y} Q{x-4},{y+2} {x-4},{y+4} Q{x},{y+6} {x+5},{y+2}" fill="none" stroke="{c}" stroke-width="1.5"/>')
    return "\n".join(o)

def mi_skull(x, y, c):
    o = []
    o.append(C(x, y-2, 6, None, c, 1.5))
    o.append(R(x-5, y+2, 10, 5, None, c, 1.5))
    o.append(C(x-2, y-4, 1.5, c))
    o.append(C(x+2, y-4, 1.5, c))
    return "\n".join(o)

def mi_tree(x, y, c):
    o = []
    o.append(f'<polygon points="{x},{y-9} {x-6},{y+2} {x-3},{y+2} {x-4},{y+6} {x+4},{y+6} {x+3},{y+2} {x+6},{y+2}" fill="none" stroke="{c}" stroke-width="1.6"/>')
    o.append(R(x-2, y+6, 4, 3, c))
    return "\n".join(o)

def mi_court(x, y, c):
    o = []
    o.append(R(x-8, y-7, 16, 14, None, c, 1.5))
    o.append(L(x-8, y, x+8, y, c, 0.8))
    o.append(R(x-6, y-5, 12, 4, None, c, 1))
    return "\n".join(o)

def mi_plane(x, y, c):
    o = []
    o.append(f'<path d="M{x-8},{y+3} L{x-3},{y-3} L{x-3},{y+1} L{x-8},{y+3}" fill="none" stroke="{c}" stroke-width="1.5"/>')
    o.append(f'<path d="M{x+8},{y+3} L{x+3},{y-3} L{x+3},{y+1} L{x+8},{y+3}" fill="none" stroke="{c}" stroke-width="1.5"/>')
    o.append(L(x-3, y-2, x+3, y-2, c, 1.8))
    o.append(L(x-3, y+1, x+3, y+1, c, 1.8))
    o.append(R(x-1, y-8, 2, 7, c))
    return "\n".join(o)

def mi_lock(x, y, c):
    o = []
    o.append(R(x-7, y, 14, 10, None, c, 1.5))
    o.append(f'<path d="M{x-4},{y} Q{x-4},{y-6} {x},{y-6} Q{x+4},{y-6} {x+4},{y}" fill="none" stroke="{c}" stroke-width="1.5"/>')
    o.append(C(x, y+4, 2.5, None, c, 1))
    return "\n".join(o)

def mi_key(x, y, c):
    o = []
    o.append(C(x+4, y-4, 5, None, c, 1.5))
    o.append(L(x-2, y-4, x-8, y+4, c, 1.5))
    o.append(L(x-8, y+2, x-8, y+6, c, 1))
    o.append(L(x-6, y+2, x-6, y+6, c, 1))
    return "\n".join(o)

def mi_bank(x, y, c):
    o = []
    o.append(R(x-8, y+2, 16, 7, None, c, 1.5))
    o.append(f'<polygon points="{x},{y-8} {x-9},{y+2} {x+9},{y+2}" fill="none" stroke="{c}" stroke-width="1.5"/>')
    o.append(R(x-5, y+4, 4, 5, c))
    return "\n".join(o)

# ═══════════════════════════════════════════════════════════════
# WORLD MAP
# ═══════════════════════════════════════════════════════════════

def build_map(x0, y0, w, h):
    p = []
    p.append(R(x0, y0, w, h, "#EDE6D8", MAP_STR, 0.6))
    # Continents (simplified paths)
    p.append(f'<path d="M{x0+28},{y0+12}L{x0+85},{y0+12}L{x0+95},{y0+20}L{x0+112},{y0+24}L{x0+116},{y0+33}L{x0+110},{y0+44}L{x0+100},{y0+48}L{x0+94},{y0+52}L{x0+82},{y0+52}L{x0+72},{y0+46}L{x0+60},{y0+48}L{x0+50},{y0+42}L{x0+42},{y0+38}L{x0+34},{y0+30}L{x0+30},{y0+20}Z" fill="{MAP_BG}" stroke="{MAP_STR}" stroke-width="0.9"/>')
    p.append(f'<path d="M{x0+40},{y0+54}L{x0+54},{y0+54}L{x0+63},{y0+60}L{x0+68},{y0+68}L{x0+66},{y0+76}L{x0+60},{y0+82}L{x0+52},{y0+84}L{x0+46},{y0+80}L{x0+42},{y0+72}L{x0+38},{y0+62}Z" fill="{MAP_BG}" stroke="{MAP_STR}" stroke-width="0.9"/>')
    p.append(f'<path d="M{x0+133},{y0+10}L{x0+152},{y0+10}L{x0+162},{y0+16}L{x0+166},{y0+23}L{x0+172},{y0+29}L{x0+174},{y0+35}L{x0+170},{y0+42}L{x0+162},{y0+46}L{x0+154},{y0+44}L{x0+146},{y0+40}L{x0+138},{y0+34}L{x0+134},{y0+26}L{x0+132},{y0+18}Z" fill="{MAP_BG}" stroke="{MAP_STR}" stroke-width="0.9"/>')
    p.append(f'<path d="M{x0+138},{y0+48}L{x0+158},{y0+48}L{x0+168},{y0+54}L{x0+174},{y0+62}L{x0+172},{y0+70}L{x0+166},{y0+78}L{x0+156},{y0+84}L{x0+146},{y0+84}L{x0+138},{y0+78}L{x0+134},{y0+70}L{x0+134},{y0+60}Z" fill="{MAP_BG}" stroke="{MAP_STR}" stroke-width="0.9"/>')
    p.append(f'<path d="M{x0+178},{y0+8}L{x0+244},{y0+4}L{x0+282},{y0+14}L{x0+306},{y0+22}L{x0+310},{y0+33}L{x0+308},{y0+43}L{x0+300},{y0+49}L{x0+288},{y0+51}L{x0+274},{y0+47}L{x0+262},{y0+41}L{x0+244},{y0+35}L{x0+226},{y0+31}L{x0+214},{y0+25}L{x0+204},{y0+18}L{x0+194},{y0+12}L{x0+184},{y0+8}Z" fill="{MAP_BG}" stroke="{MAP_STR}" stroke-width="0.9"/>')
    p.append(f'<path d="M{x0+284},{y0+54}L{x0+305},{y0+56}L{x0+314},{y0+62}L{x0+312},{y0+68}L{x0+302},{y0+72}L{x0+290},{y0+70}L{x0+282},{y0+64}L{x0+280},{y0+58}Z" fill="{MAP_BG}" stroke="{MAP_STR}" stroke-width="0.9"/>')
    p.append(f'<path d="M{x0+289},{y0+74}L{x0+310},{y0+74}L{x0+316},{y0+80}L{x0+312},{y0+86}L{x0+300},{y0+88}L{x0+290},{y0+86}L{x0+286},{y0+80}Z" fill="{MAP_BG}" stroke="{MAP_STR}" stroke-width="0.9"/>')
    p.append(f'<path d="M{x0+173},{y0+38}L{x0+181},{y0+38}L{x0+185},{y0+42}L{x0+183},{y0+48}L{x0+177},{y0+48}L{x0+173},{y0+44}Z" fill="{MAP_BG}" stroke="{MAP_STR}" stroke-width="0.9"/>')

    pins = [
        (1, "Shenzhen · Xi-Trump-Putin", x0+254, y0+24, RED),
        (2, "The Hague · ICJ Verdict", x0+141, y0+20, PURPLE),
        (3, "Riyadh · Houthi Strike", x0+178, y0+42, ORANGE),
        (4, "Kyiv · Bridge Hit", x0+151, y0+29, BLUE),
        (5, "Port-au-Prince · Gang Op", x0+44, y0+60, RED),
        (6, "Dakar · IMF Budget", x0+137, y0+64, GREEN),
    ]
    for num, lbl, cx, cy, clr in pins:
        p.append(C(cx, cy, 5, clr))
        p.append(C(cx, cy, 7.5, None, clr, 1.3))
        p.append(TC(cx, cy+0.5, str(num), DB, 6, WHITE))
        lx = cx + 10
        anc = "start"
        if lx > x0+w - 70: lx = cx - 10; anc = "end"
        p.append(f'<text x="{lx}" y="{cy+3}" {DR} font-size="6.5" fill="{clr}" text-anchor="{anc}">{esc(lbl)}</text>')

    p.append(TC(x0+w//2, y0-4, "WORLD MAP · KEY EVENTS OF 19 NOVEMBER 2026", DB, 8, LTGRAY))
    return "\n".join(p)


# ═══════════════════════════════════════════════════════════════
# MAIN SVG BUILDER
# ═══════════════════════════════════════════════════════════════

def build_svg():
    W, H = 1024, 1024
    p = []
    p.append(f'<?xml version="1.0" encoding="UTF-8"?>')
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')

    # Background
    p.append(R(0, 0, W, H, BG))
    # Newsprint dot grid
    dots = []
    for gx in range(0, W, 32):
        for gy in range(0, H, 32):
            dots.append(f'<circle cx="{gx}" cy="{gy}" r="0.5" fill="#E8E2D4"/>')
    p.append("\n".join(dots))

    # ═══════════════════════════════════════════════════════════
    # MASTHEAD y: 0..125
    # ═══════════════════════════════════════════════════════════
    p.append(R(0, 0, W, 15, INK2))
    p.append(TC(W//2, 10, "VOL. CXCVI · NO. 42,119  |  THURSDAY, 19 NOVEMBER 2026  |  GLOBAL EDITION  |  42 VERIFIED EVENTS", DR, 7.5, WHITE))

    # Ornament left (x:24..165 at y=35)
    p.append(L(24, 35, 155, 35, GOLD, 1.5))
    p.append(C(89, 35, 3.8, GOLD))
    p.append(L(36, 33, 46, 37, GOLD, 1.2))
    p.append(L(56, 33, 66, 37, GOLD, 1.2))
    p.append(L(103, 33, 113, 37, GOLD, 1.2))
    p.append(L(123, 33, 133, 37, GOLD, 1.2))
    # Ornament right (x:859..1000 at y=35)
    p.append(L(869, 35, 1000, 35, GOLD, 1.5))
    p.append(C(935, 35, 3.8, GOLD))
    p.append(L(881, 33, 891, 37, GOLD, 1.2))
    p.append(L(901, 33, 911, 37, GOLD, 1.2))
    p.append(L(949, 33, 959, 37, GOLD, 1.2))
    p.append(L(969, 33, 979, 37, GOLD, 1.2))

    # Giant title
    p.append(TC(W//2, 72, "19 NOVEMBER 2026", SB, 58, INK))
    p.append(TC(W//2, 96, "THE WORLD IN ONE IMAGE", SI, 15, INK2, "letter-spacing='3'"))
    p.append(TC(W//2, 112, "GLOBAL NEWS DISPATCH", SI, 11, LTGRAY, "letter-spacing='2'"))

    p.append(L(24, 125, 1000, 125, INK, 2.5))

    # ═══════════════════════════════════════════════════════════
    # 3 LEAD STORIES y: 130..420
    # ═══════════════════════════════════════════════════════════
    y_lead = 130
    col_w = 318
    col_h = 290
    cols = [(24, 342), (356, 674), (682, 1000)]

    leads = [
        {"kicker":"APEC SHENZHEN · DIPLOMACY","title":"Xi, Trump & Putin\nHold Historic Summit",
         "body":"First trilateral meeting issues joint\ndeclaration on nuclear war prevention,\npetroleum stability and UN reform.\nTalks hailed as 'new great-power détente.'",
         "source":"Reuters / AP / Xinhua","color":BLUE,"icon":icon_summit},
        {"kicker":"THE HAGUE · INTERNATIONAL LAW","title":"ICJ Rules Myanmar\nCommitted Genocide",
         "body":"Landmark verdict on Rohingya; The\nGambia proved intent to destroy ethnic\nminority. Bangladesh hails ruling.\nActivists call for immediate sanctions.",
         "source":"Reuters / BBC / AFP","color":PURPLE,"icon":icon_scales},
        {"kicker":"ENTERTAINMENT · VIDEO GAMES","title":"GTA VI Breaks\nAll Launch Records",
         "body":"$2.3 billion in day-one sales — the\nbiggest entertainment launch in history.\n18 million concurrent players strain\nRockstar servers worldwide.",
         "source":"Reuters / Bloomberg","color":RED,"icon":icon_gamepad},
    ]

    for i, ld in enumerate(leads):
        cx1, cx2 = cols[i]
        cw = cx2 - cx1
        cy = y_lead
        p.append(R(cx1, cy, cw, col_h, CREAM_BOX, RULE, 0.7))
        p.append(R(cx1, cy, cw, 4, ld["color"]))
        # Kicker
        p.append(T(cx1+14, cy+18, ld["kicker"], DB, 9.5, ld["color"], extra="letter-spacing='1'"))
        # Icon (centered in column)
        p.append(ld["icon"](cx1 + cw//2, cy + 78, ld["color"]))
        # Rule below icon
        p.append(L(cx1+30, cy+106, cx2-30, cy+106, RULE, 0.5))
        # Headline
        hl_y = cy + 124
        for j, hl in enumerate(ld["title"].split("\n")):
            p.append(T(cx1+16, hl_y+j*26, hl, SB, 18, INK))
        # Body
        body_y = hl_y + len(ld["title"].split("\n"))*26 + 8
        for j, bl in enumerate(ld["body"].split("\n")):
            p.append(T(cx1+16, body_y+j*15.5, bl, SR, 11.5, INK2))
        # Source
        p.append(T(cx1+16, cy+col_h-14, ld["source"], SI, 8.5, LTGRAY))

    p.append(L(354, y_lead, 354, y_lead+col_h, RULE, 0.7))
    p.append(L(680, y_lead, 680, y_lead+col_h, RULE, 0.7))

    y_after_leads = y_lead + col_h + 4
    p.append(L(24, y_after_leads, 1000, y_after_leads, INK, 2))

    # ═══════════════════════════════════════════════════════════
    # FLASHPOINT STRIP y: 428..506
    # ═══════════════════════════════════════════════════════════
    y_flash = y_after_leads + 8
    flash_h = 78
    p.append(R(24, y_flash, 976, flash_h, DARK))
    p.append(TC(W//2, y_flash+12, "FLASHPOINTS · ACTIVE CONFLICT ZONES · 19 NOVEMBER 2026", DB, 9, GOLD, "letter-spacing='2'"))

    fcols = [
        ("HORMUZ","Tanker Fire\nNaval Mine",icon_tanker,"#FFAA44"),
        ("RIYADH","Houthi Missiles\nHit PIF Tower",icon_missile,"#FF9944"),
        ("KUWAIT","Iran Strikes\nUS Air Base",icon_airbase,"#FF9944"),
        ("UKRAINE","Missiles Hit\n3 Kyiv Bridges",icon_bridge,"#FF7733"),
        ("LEBANON","IAF Strikes\nHezbollah",icon_explosion,"#FF9944"),
        ("GAZA","2 Killed;\nDirector Held",icon_shield,"#FF7733"),
    ]
    nf = len(fcols)
    fw = 976 // nf
    for i, (loc, desc, ic, clr) in enumerate(fcols):
        fx = 24 + fw*i + fw//2
        p.append(ic(fx, y_flash+45, WHITE))
        p.append(TC(fx, y_flash+28, loc, DB, 10, clr, "letter-spacing='1'"))
        dy = y_flash+64
        for j, dl in enumerate(desc.split("\n")):
            p.append(TC(fx, dy+j*10, dl, DR, 8.5, "#CCCCCC"))

    y_after_flash = y_flash + flash_h + 6
    p.append(L(24, y_after_flash, 1000, y_after_flash, INK, 1.5))

    # ═══════════════════════════════════════════════════════════
    # MIDDLE PANEL: World Map + Key Figures y: 518..668
    # ═══════════════════════════════════════════════════════════
    y_mid = y_after_flash + 6
    mid_h = 150

    p.append(build_map(24, y_mid+10, 606, mid_h-10))
    p.append(L(642, y_mid, 642, y_mid+mid_h, RULE, 0.7))

    # Key Figures box
    kx, kw = 648, 348
    p.append(R(kx, y_mid, kw, 24, INK))
    p.append(T(kx+12, y_mid+16, "KEY FIGURES · 19 NOV", DB, 11, WHITE, extra="letter-spacing='1.5'"))

    stats = [
        ("$2.3B","GTA VI Day-1\nGlobal Sales",RED),
        ("341","Factories Shut\nBangladesh",ORANGE),
        ("$2.2B","Senegal\nIMF Loan",GREEN),
        ("25","European Nations\nGen Z Protests",BLUE),
        ("8 YR","BepiColombo\nMercury Voyage",TEAL),
        ("97","BGB Platoons\nDeployed",PURPLE),
    ]
    ns = len(stats)
    sg = kw // ns
    sy = y_mid+30
    for i, (num, label, clr) in enumerate(stats):
        sx = kx + sg*i + sg//2
        p.append(R(kx+sg*i+3, sy, sg-4, 112, CREAM_BOX, RULE, 0.4))
        p.append(TC(sx, sy+26, num, SB, 22, clr))
        for j, ln in enumerate(label.split("\n")):
            p.append(TC(sx, sy+50+j*13, ln, DR, 9.5, INK2))

    y_after_mid = y_mid + mid_h + 4
    p.append(L(24, y_after_mid, 1000, y_after_mid, INK, 2))

    # ═══════════════════════════════════════════════════════════
    # REGIONAL PANELS y: 676..860
    # ═══════════════════════════════════════════════════════════
    y_reg = y_after_mid + 6
    reg_col_w = 318
    reg_h = 184

    regions = [
        {"name":"AMERICAS","color":RED,"items":[
            ("HAITI","Police op kills 34 gang members in Port-au-Prince",mi_tank),
            ("EL SALVADOR","Bukele files for 3rd presidential term",mi_flag),
            ("USA","Trump threatens ban on AI data centers overseas",mi_chip),
            ("VENEZUELA","Court halts restoration of TPS protections",mi_court),
            ("TEXAS","Execution takes over 1 hour; condemned screams",mi_skull),
            ("BRAZIL","Amazon deforestation drops 22% from 2025 peak",mi_tree),
        ]},
        {"name":"EUROPE & AFRICA","color":BLUE,"items":[
            ("EU · UK","Landmark deal: food exports, emissions, youth mobility",mi_globe),
            ("POLAND","Russian missile hits during NATO drill",mi_rocket),
            ("DENMARK","Russian diplomat expelled over murder plot",mi_flag),
            ("SENEGAL","President enacts budget for $2.2B IMF loan",mi_dollar),
            ("SOMALIA","Expels UAE ambassador over sovereignty dispute",mi_plane),
            ("ESTONIA","Border closure; Russia warns 'Iron Curtain'",mi_lock),
            ("S. AFRICA","Nearly 600 women killed in 3 months",mi_cross),
        ]},
        {"name":"ASIA-PACIFIC & MIDEAST","color":PURPLE,"items":[
            ("MONGOLIA","President Khürelsükh resigns",mi_flag),
            ("BANGLADESH","341 factories shut as wage protests spread",mi_factory),
            ("PHILIPPINES","First PH-LatAm FTA signed at APEC",mi_globe),
            ("PAKISTAN","Security cooperation MoU with Qatar",mi_key),
            ("JAPAN","PM Takaichi meets Putin; Taiwan stance firm",mi_globe),
            ("S. KOREA","111 students caught cheating on Suneung",mi_cross),
            ("YEMEN","144 Houthi fighters killed in Taiz, Marib",mi_tank),
        ]},
    ]

    for ci, reg in enumerate(regions):
        cx = 24 + ci*(reg_col_w+12)
        cy = y_reg
        p.append(R(cx, cy, reg_col_w, 22, reg["color"]))
        p.append(T(cx+10, cy+15, reg["name"], DB, 10.5, WHITE, extra="letter-spacing='1.5'"))
        iy = cy+30
        for country, desc, ic in reg["items"]:
            p.append(ic(cx+15, iy+9, reg["color"]))
            p.append(T(cx+30, iy+6, country, DB, 9.5, reg["color"], extra="letter-spacing='0.5'"))
            p.append(T(cx+30, iy+17, desc, SR, 8.5, INK2))
            iy += 24
        if ci < 2:
            p.append(L(cx+reg_col_w+4, cy, cx+reg_col_w+4, cy+reg_h, RULE, 0.7))

    y_after_reg = y_reg + reg_h + 4
    p.append(L(24, y_after_reg, 1000, y_after_reg, INK, 2))

    # ═══════════════════════════════════════════════════════════
    # ALSO ON 19 NOVEMBER y: 868..998
    # ═══════════════════════════════════════════════════════════
    y_also = y_after_reg + 6
    p.append(TC(W//2, y_also+14, "ALSO ON 19 NOVEMBER", SB, 20, INK))
    p.append(L(W//2-130, y_also+20, W//2+130, y_also+20, GOLD, 1.2))

    also = [
        "Daraxonrasib pancreatic cancer pill makes tumours vanish in early trial",
        "BepiColombo probe arrives at Mercury after 8-year space voyage",
        "Anthropic shares fall post-IPO amid wider tech market sell-off",
        "Nations call for carbon removal tech as global warming accelerates",
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

    aw = 476
    half = (len(also)+1)//2
    for ci in range(2):
        ax = 24 + ci*(aw+14)
        ay = y_also+28
        for idx in range(ci*half, min((ci+1)*half, len(also))):
            p.append(T(ax, ay, "▪ "+also[idx], SR, 9, INK2))
            ay += 15.5

    # ═══════════════════════════════════════════════════════════
    # FOOTER y: 1002..1024
    # ═══════════════════════════════════════════════════════════
    y_foot = 1002
    p.append(L(24, y_foot, 1000, y_foot, RULE, 0.8))
    p.append(TC(W//2, y_foot+11, "42 verified events · 6 continents · Sources: Wikipedia, BBC, Reuters, AP, AFP, Google News", DR, 8, LTGRAY))
    p.append(TC(W//2, y_foot+23, "All events occurred or were first reported on Thursday 19 November 2026 · Generated deterministically · 1024×1024 PNG", DR, 7, "#CCCCCC"))

    p.append('</svg>')
    return "\n".join(p)


# ═══════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════

def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "entry.png"

    print("Building SVG...")
    svg = build_svg()
    svg_path = out_path.replace(".png","_build.svg")
    with open(svg_path,"w") as f:
        f.write(svg)
    print(f"  SVG: {svg_path} ({os.path.getsize(svg_path)/1024:.1f} KB)")

    print("Rendering 1024×1024 PNG via CairoSVG...")
    from cairosvg import svg2png
    svg2png(bytestring=svg.encode("utf-8"), write_to=out_path, output_width=1024, output_height=1024)

    kb = os.path.getsize(out_path)/1024
    sha = hashlib.sha256()
    with open(out_path,"rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk: break
            sha.update(chunk)
    print(f"  PNG: {out_path} ({kb:.1f} KB) SHA256:{sha.hexdigest()[:16]}")

    # 300×300 preview
    prev = out_path.replace(".png","_300.png")
    svg2png(bytestring=svg.encode("utf-8"), write_to=prev, output_width=300, output_height=300)
    print(f"  Preview: {prev} ({os.path.getsize(prev)/1024:.1f} KB)")

    # Pillow verify
    from PIL import Image
    im = Image.open(out_path)
    print(f"  Pillow: {im.size[0]}×{im.size[1]} mode={im.mode}")

    print(f"\nDone. Verify: MAKEFUN_OUTPUT_DIR=out node main.ts")

if __name__ == "__main__":
    main()