#!/usr/bin/env python3
"""
Vedic chart renderer v3 — refined modern design.

Designed by treating this as a print-quality deliverable: generous canvas,
proper margins, element-based color system (Fire/Earth/Air/Water), unicode
zodiac glyphs paired with illustrated icons, self-explanatory bottom legend,
subtle gradients.

Three styles supported:
  - western: Modern circular wheel (default)
  - north:   North Indian diamond style
  - south:   South Indian square style

Plus Chinese zodiac year-sign card (compute_chinese_zodiac).

Usage:
    from chart_renderer import render_chart, render_chinese_zodiac
    svg = render_chart(chart_data, style='western', title='Birth Chart')
"""

from typing import Literal
import math


# ============================================================================
# CONSTANTS
# ============================================================================

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

SIGNS_DEVANAGARI = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
                    "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"]

# Unicode zodiac glyphs
GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# Element groupings (Vedic and Western agree on this)
ELEMENTS = {
    0: "fire", 1: "earth", 2: "air", 3: "water",   # Aries-Cancer
    4: "fire", 5: "earth", 6: "air", 7: "water",   # Leo-Scorpio
    8: "fire", 9: "earth", 10: "air", 11: "water", # Sagittarius-Pisces
}

# Element colors — refined modern palette
# Each has: fill (cell tint, very light), accent (label color), border
ELEMENT_COLORS = {
    "fire":  {"fill": "#FBE9E1", "accent": "#C44B2C", "border": "#E5A893"},  # warm coral
    "earth": {"fill": "#E8EFE0", "accent": "#5A7A3C", "border": "#A8C088"},  # sage green
    "air":   {"fill": "#FAF2DC", "accent": "#A87B1F", "border": "#D9C283"},  # soft gold
    "water": {"fill": "#E1ECF3", "accent": "#3A6E96", "border": "#8FB5CF"},  # cool blue
}

# Refined neutral palette
PALETTE = {
    "bg":          "#FBFAF6",  # off-white with warmth
    "bg_alt":      "#F4F2EC",  # subtle alternate
    "frame":       "#2A2724",  # near-black for primary frame
    "line_strong": "#6B635A",  # taupe for primary divisions
    "line_soft":   "#C8C2B6",  # warm gray for secondary lines
    "text_dark":   "#1F1B17",  # near-black for headlines
    "text_body":   "#3D3833",  # warm dark for body
    "text_muted":  "#6B635A",  # taupe for labels
    "ascendant":   "#B23C28",  # deep red for ASC
    "planet":      "#1F1B17",  # near-black for planets
    "planet_retro":"#9B2D2D",  # deep red for retrograde
    "accent_gold": "#C8A04A",  # subtle gold accent
}

# Planet symbols (Unicode)
PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mars": "♂", "Mercury": "☿",
    "Jupiter": "♃", "Venus": "♀", "Saturn": "♄",
    "Rahu": "☊", "Ketu": "☋",
}

PLANET_SHORT = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
    "Rahu": "Ra", "Ketu": "Ke"
}

# Font stacks — using Noto fallbacks for CJK (Chinese), Devanagari (Sanskrit), and Symbols (zodiac glyphs)
FONT_DISPLAY = "'Cormorant Garamond', 'EB Garamond', 'Noto Serif', Georgia, 'Times New Roman', serif"
FONT_SANS = "'Inter', 'Noto Sans', 'Helvetica Neue', 'Segoe UI', system-ui, -apple-system, sans-serif"
FONT_GLYPH = "'DejaVu Sans', 'Noto Sans Symbols2', 'Noto Sans Symbols', 'Apple Symbols', 'Segoe UI Symbol', sans-serif"
FONT_CJK = "'Noto Sans CJK SC', 'Noto Serif CJK SC', 'Noto Sans CJK TC', 'PingFang SC', 'Hiragino Sans GB', sans-serif"
FONT_DEVANAGARI = "'Noto Sans Devanagari', 'Noto Serif Devanagari', sans-serif"


# ============================================================================
# SVG BUILDING BLOCKS
# ============================================================================

def _svg_open(width: int, height: int) -> str:
    """SVG root with subtle background gradient and embedded styles."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{PALETTE['bg']}" stop-opacity="1"/>
      <stop offset="100%" stop-color="{PALETTE['bg_alt']}" stop-opacity="1"/>
    </linearGradient>
    <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{PALETTE['bg']}" stop-opacity="1"/>
      <stop offset="100%" stop-color="{PALETTE['bg_alt']}" stop-opacity="0.3"/>
    </radialGradient>
    <linearGradient id="goldAccent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#D4B568" stop-opacity="0.6"/>
      <stop offset="50%" stop-color="{PALETTE['accent_gold']}" stop-opacity="1"/>
      <stop offset="100%" stop-color="#D4B568" stop-opacity="0.6"/>
    </linearGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#bgGrad)"/>
'''


def _svg_close() -> str:
    return '</svg>'


def _title_block(W: int, title: str, subtitle: str, top_y: int = 50) -> str:
    """Refined title block with gold accent line."""
    cx = W / 2
    return f'''  <text x="{cx}" y="{top_y}" text-anchor="middle" font-family="{FONT_DISPLAY}" font-size="32" font-weight="500" fill="{PALETTE['text_dark']}" letter-spacing="0.5">{title}</text>
  <line x1="{cx-60}" y1="{top_y+12}" x2="{cx+60}" y2="{top_y+12}" stroke="url(#goldAccent)" stroke-width="1.5"/>
  <text x="{cx}" y="{top_y+34}" text-anchor="middle" font-family="{FONT_SANS}" font-size="13" fill="{PALETTE['text_muted']}" letter-spacing="1.2">{subtitle.upper()}</text>
'''


def _footer_block(W: int, H: int) -> str:
    """Footer with credits."""
    return f'''  <text x="{W/2}" y="{H-22}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" fill="{PALETTE['text_muted']}" letter-spacing="1.5">THE HONEST ASTROLOGER  ·  LAHIRI AYANAMSA  ·  WHOLE-SIGN HOUSES</text>
'''


def _planets_in_house(chart_data: dict, house_num: int) -> list[dict]:
    return [
        {"name": name, "data": p}
        for name, p in chart_data["planets"].items()
        if p["house"] == house_num
    ]


def _planets_in_sign(chart_data: dict, sign_idx: int) -> list[dict]:
    sign_name = SIGNS[sign_idx]
    return [
        {"name": name, "data": p}
        for name, p in chart_data["planets"].items()
        if p["sign"] == sign_name
    ]


def _legend_strip(W: int, y_top: int, asc_sign_idx: int = -1) -> str:
    """Bottom legend showing all 12 signs with glyphs, names, and elements.
    Layout: 2 rows of 6 signs. Each cell shows: glyph + sign number + name + element color bar.
    """
    svg = ""
    # Legend title
    svg += f'  <text x="{W/2}" y="{y_top}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" font-weight="600" fill="{PALETTE['text_muted']}" letter-spacing="2">ZODIAC LEGEND</text>\n'
    svg += f'  <line x1="{W/2-40}" y1="{y_top+6}" x2="{W/2+40}" y2="{y_top+6}" stroke="{PALETTE["line_soft"]}" stroke-width="0.8"/>\n'

    # 6 columns × 2 rows
    cols = 6
    rows = 2
    margin_x = 40
    available_w = W - 2 * margin_x
    cell_w = available_w / cols
    cell_h = 42
    start_y = y_top + 18

    for i in range(12):
        col = i % cols
        row = i // cols
        x = margin_x + col * cell_w
        y = start_y + row * cell_h

        elem = ELEMENTS[i]
        ec = ELEMENT_COLORS[elem]

        # Element color bar on left side of cell
        svg += f'  <rect x="{x}" y="{y}" width="3" height="{cell_h-8}" fill="{ec["accent"]}" rx="1.5"/>\n'

        # Glyph
        svg += f'  <text x="{x+14}" y="{y+22}" text-anchor="start" font-family="{FONT_GLYPH}" font-size="18" fill="{ec["accent"]}">{GLYPHS[i]}</text>\n'

        # Sign number + name
        svg += f'  <text x="{x+38}" y="{y+15}" text-anchor="start" font-family="{FONT_SANS}" font-size="9" font-weight="600" fill="{PALETTE["text_muted"]}" letter-spacing="0.8">{i+1}</text>\n'
        svg += f'  <text x="{x+50}" y="{y+15}" text-anchor="start" font-family="{FONT_DISPLAY}" font-size="13" font-weight="500" fill="{PALETTE["text_dark"]}">{SIGNS[i]}</text>\n'
        # Element + Sanskrit name (using Devanagari font for proper rendering)
        svg += f'  <text x="{x+38}" y="{y+30}" text-anchor="start" font-family="{FONT_SANS}" font-size="9" fill="{PALETTE["text_muted"]}">{elem.title()} · <tspan font-family="{FONT_DEVANAGARI}" font-size="11">{SIGNS_DEVANAGARI[i]}</tspan></text>\n'

    # Element key on a third sub-row
    elem_y = start_y + 2 * cell_h + 8
    svg += f'  <text x="{W/2}" y="{elem_y}" text-anchor="middle" font-family="{FONT_SANS}" font-size="9" font-weight="600" fill="{PALETTE["text_muted"]}" letter-spacing="2">ELEMENTS</text>\n'
    elem_items = [("Fire", "fire"), ("Earth", "earth"), ("Air", "air"), ("Water", "water")]
    item_w = 90
    total_w = item_w * 4
    start_x = (W - total_w) / 2
    for idx, (label, key) in enumerate(elem_items):
        ec = ELEMENT_COLORS[key]
        ix = start_x + idx * item_w + item_w / 2
        # Color swatch
        svg += f'  <circle cx="{ix-30}" cy="{elem_y+16}" r="5" fill="{ec["accent"]}"/>\n'
        svg += f'  <text x="{ix-20}" y="{elem_y+19}" text-anchor="start" font-family="{FONT_SANS}" font-size="10" fill="{PALETTE["text_body"]}">{label}</text>\n'

    # Planet legend on its own line
    planet_y = elem_y + 36
    svg += f'  <text x="{W/2}" y="{planet_y}" text-anchor="middle" font-family="{FONT_SANS}" font-size="9" font-weight="600" fill="{PALETTE["text_muted"]}" letter-spacing="2">PLANETS</text>\n'
    planets_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    p_item_w = (W - 80) / 9
    for idx, pname in enumerate(planets_order):
        glyph = PLANET_GLYPHS[pname]
        short = PLANET_SHORT[pname]
        px = 40 + idx * p_item_w + p_item_w / 2
        svg += f'  <text x="{px}" y="{planet_y+18}" text-anchor="middle" font-family="{FONT_GLYPH}" font-size="14" fill="{PALETTE["text_dark"]}">{glyph}</text>\n'
        svg += f'  <text x="{px}" y="{planet_y+32}" text-anchor="middle" font-family="{FONT_SANS}" font-size="9" fill="{PALETTE["text_muted"]}">{short} · {pname}</text>\n'

    return svg


def _format_planet(p: dict, with_glyph: bool = True, with_degree: bool = True) -> str:
    """Format a planet for inline display."""
    name = p["name"]
    parts = []
    if with_glyph:
        parts.append(PLANET_GLYPHS.get(name, ""))
    parts.append(PLANET_SHORT.get(name, name[:2]))
    if with_degree:
        parts.append(f"{int(p['data']['degree'])}°")
    if p["data"].get("retrograde"):
        parts.append("R")
    return " ".join(parts)


# ============================================================================
# WESTERN CIRCULAR WHEEL — v3 refined
# ============================================================================

def render_western(chart_data: dict, title: str = "Birth Chart", subtitle: str = "") -> str:
    """Refined modern Western circular chart."""
    W, H = 850, 1050
    cx, cy = W / 2, 380  # chart vertically centered with room for title above and legend below
    R_OUTER = 280
    R_HOUSE_INNER = 225  # outer edge of house cell tints
    R_SIGN_LABEL = 258
    R_PLANET = 195
    R_HOUSE_NUM = 125
    R_INNER = 80

    asc_sign_name = chart_data["ascendant"]["sign"]
    asc_sign_idx = SIGNS.index(asc_sign_name)

    svg = _svg_open(W, H)
    svg += _title_block(W, title, subtitle)

    # Draw element-tinted house wedges. Each wedge = annular sector between R_INNER and R_HOUSE_INNER
    # spanning 30° (one house). Houses go counter-clockwise on screen.
    # In SVG y-down with our convention (mid_angle = 180 - (h-1)*30):
    #   H1 mid = 180° (left), H4 mid = 90° (bottom in SVG = +y), H7 mid = 0° (right), H10 mid = 270° (top)
    # House h spans angles [mid - 15°, mid + 15°].
    # Sweep direction: when going from larger angle to smaller (CCW on screen = decreasing angle in our coords),
    # the SVG arc with sweep-flag=0 goes CCW in SVG terms (which appears CW visually due to y-flip)
    # — but with our y+sin convention the sweep-flag=1 gives the correct visual fill.
    for house_num in range(1, 13):
        sign_idx = (asc_sign_idx + house_num - 1) % 12
        elem = ELEMENTS[sign_idx]
        ec = ELEMENT_COLORS[elem]

        mid_deg = (180 - (house_num - 1) * 30) % 360
        # Wedge from (mid-15°) to (mid+15°)
        a_start_deg = (mid_deg - 15) % 360  # this is the "earlier" boundary in our angle space
        a_end_deg = (mid_deg + 15) % 360    # this is the "later" boundary
        a_start = math.radians(a_start_deg)
        a_end = math.radians(a_end_deg)

        # Outer points
        x_out_start = cx + R_HOUSE_INNER * math.cos(a_start)
        y_out_start = cy + R_HOUSE_INNER * math.sin(a_start)
        x_out_end = cx + R_HOUSE_INNER * math.cos(a_end)
        y_out_end = cy + R_HOUSE_INNER * math.sin(a_end)
        # Inner points
        x_in_start = cx + R_INNER * math.cos(a_start)
        y_in_start = cy + R_INNER * math.sin(a_start)
        x_in_end = cx + R_INNER * math.cos(a_end)
        y_in_end = cy + R_INNER * math.sin(a_end)

        # Draw: from outer-start, arc to outer-end (sweep=1 gives the correct CCW fill in our coord system),
        # line to inner-end, arc back to inner-start (sweep=0 reverse direction), close.
        path = (
            f"M {x_out_start:.2f} {y_out_start:.2f} "
            f"A {R_HOUSE_INNER} {R_HOUSE_INNER} 0 0 1 {x_out_end:.2f} {y_out_end:.2f} "
            f"L {x_in_end:.2f} {y_in_end:.2f} "
            f"A {R_INNER} {R_INNER} 0 0 0 {x_in_start:.2f} {y_in_start:.2f} Z"
        )
        svg += f'  <path d="{path}" fill="{ec["fill"]}" stroke="none" opacity="0.85"/>\n'

    # Outer ring (sign band) — slightly more saturated tint
    for house_num in range(1, 13):
        sign_idx = (asc_sign_idx + house_num - 1) % 12
        elem = ELEMENTS[sign_idx]
        ec = ELEMENT_COLORS[elem]

        mid_deg = (180 - (house_num - 1) * 30) % 360
        a_start_deg = (mid_deg - 15) % 360
        a_end_deg = (mid_deg + 15) % 360
        a_start = math.radians(a_start_deg)
        a_end = math.radians(a_end_deg)

        x_out_start = cx + R_OUTER * math.cos(a_start)
        y_out_start = cy + R_OUTER * math.sin(a_start)
        x_out_end = cx + R_OUTER * math.cos(a_end)
        y_out_end = cy + R_OUTER * math.sin(a_end)
        x_in_start = cx + R_HOUSE_INNER * math.cos(a_start)
        y_in_start = cy + R_HOUSE_INNER * math.sin(a_start)
        x_in_end = cx + R_HOUSE_INNER * math.cos(a_end)
        y_in_end = cy + R_HOUSE_INNER * math.sin(a_end)

        path = (
            f"M {x_out_start:.2f} {y_out_start:.2f} "
            f"A {R_OUTER} {R_OUTER} 0 0 1 {x_out_end:.2f} {y_out_end:.2f} "
            f"L {x_in_end:.2f} {y_in_end:.2f} "
            f"A {R_HOUSE_INNER} {R_HOUSE_INNER} 0 0 0 {x_in_start:.2f} {y_in_start:.2f} Z"
        )
        svg += f'  <path d="{path}" fill="{ec["accent"]}" stroke="none" opacity="0.18"/>\n'

    # Strong outer circle
    svg += f'  <circle cx="{cx}" cy="{cy}" r="{R_OUTER}" fill="none" stroke="{PALETTE["frame"]}" stroke-width="2"/>\n'
    svg += f'  <circle cx="{cx}" cy="{cy}" r="{R_HOUSE_INNER}" fill="none" stroke="{PALETTE["line_strong"]}" stroke-width="0.8"/>\n'
    svg += f'  <circle cx="{cx}" cy="{cy}" r="{R_INNER}" fill="url(#centerGlow)" stroke="{PALETTE["line_strong"]}" stroke-width="0.8"/>\n'

    # House dividing lines — boundaries between houses, at mid_angle ± 15°
    for house_num in range(1, 13):
        mid_deg = (180 - (house_num - 1) * 30) % 360
        # Boundary at mid - 15° (start of this house)
        boundary_deg = (mid_deg - 15) % 360
        a = math.radians(boundary_deg)
        x1 = cx + R_OUTER * math.cos(a)
        y1 = cy + R_OUTER * math.sin(a)
        x2 = cx + R_INNER * math.cos(a)
        y2 = cy + R_INNER * math.sin(a)
        svg += f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{PALETTE["line_strong"]}" stroke-width="0.7" opacity="0.5"/>\n'

    # Subtle separator between house number and planet rings
    svg += f'  <circle cx="{cx}" cy="{cy}" r="{R_HOUSE_NUM-12}" fill="none" stroke="{PALETTE["line_soft"]}" stroke-width="0.5" opacity="0.4"/>\n'

    # House numbers and sign content
    for house_num in range(1, 13):
        sign_idx = (asc_sign_idx + house_num - 1) % 12
        elem = ELEMENTS[sign_idx]
        ec = ELEMENT_COLORS[elem]
        mid_angle_deg = (180 - (house_num - 1) * 30) % 360
        mid_angle = math.radians(mid_angle_deg)

        # House number (subtle, inner)
        hx = cx + R_HOUSE_NUM * math.cos(mid_angle)
        hy = cy + R_HOUSE_NUM * math.sin(mid_angle)
        svg += f'  <text x="{hx:.1f}" y="{hy:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" font-weight="600" fill="{PALETTE["text_muted"]}" letter-spacing="0.5" dominant-baseline="middle">{house_num}</text>\n'

        # Sign glyph + number on outer ring
        sx = cx + R_SIGN_LABEL * math.cos(mid_angle)
        sy = cy + R_SIGN_LABEL * math.sin(mid_angle)
        svg += f'  <text x="{sx:.1f}" y="{sy-3:.1f}" text-anchor="middle" font-family="{FONT_GLYPH}" font-size="20" font-weight="500" fill="{ec["accent"]}" dominant-baseline="middle">{GLYPHS[sign_idx]}</text>\n'
        svg += f'  <text x="{sx:.1f}" y="{sy+15:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="9" font-weight="700" fill="{ec["accent"]}" letter-spacing="0.5" dominant-baseline="middle">{sign_idx+1}</text>\n'

    # Ascendant marker
    asc_x = cx - R_OUTER
    svg += f'  <polygon points="{asc_x-14},{cy} {asc_x+2},{cy-9} {asc_x+2},{cy+9}" fill="{PALETTE["ascendant"]}"/>\n'
    svg += f'  <text x="{asc_x-20}" y="{cy+4}" text-anchor="end" font-family="{FONT_SANS}" font-size="11" font-weight="700" fill="{PALETTE["ascendant"]}" letter-spacing="1.5">ASC</text>\n'

    # Place planets in their houses (with refined badges)
    for house_num in range(1, 13):
        planets = _planets_in_house(chart_data, house_num)
        if not planets:
            continue
        mid_angle_deg = (180 - (house_num - 1) * 30) % 360
        mid_angle = math.radians(mid_angle_deg)
        n = len(planets)

        for j, p in enumerate(planets):
            offset = (j - (n - 1) / 2) * 18
            base_x = cx + R_PLANET * math.cos(mid_angle)
            base_y = cy + R_PLANET * math.sin(mid_angle)
            px = base_x
            py = base_y + offset
            color = PALETTE["planet_retro"] if p["data"].get("retrograde") else PALETTE["planet"]
            glyph = PLANET_GLYPHS.get(p["name"], "")
            short = PLANET_SHORT.get(p["name"], p["name"][:2])
            deg = int(p["data"]["degree"])
            retro = " R" if p["data"].get("retrograde") else ""

            # Planet glyph + label
            svg += f'  <text x="{px-22:.1f}" y="{py:.1f}" text-anchor="middle" font-family="{FONT_GLYPH}" font-size="14" font-weight="500" fill="{color}" dominant-baseline="middle">{glyph}</text>\n'
            svg += f'  <text x="{px+8:.1f}" y="{py:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="600" fill="{color}" dominant-baseline="middle">{short} {deg}°{retro}</text>\n'

    # Center text — chart info
    svg += f'  <text x="{cx}" y="{cy-6}" text-anchor="middle" font-family="{FONT_DISPLAY}" font-size="14" fill="{PALETTE["text_dark"]}" dominant-baseline="middle">Lagna</text>\n'
    svg += f'  <text x="{cx}" y="{cy+12}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" font-weight="600" fill="{ELEMENT_COLORS[ELEMENTS[asc_sign_idx]]["accent"]}" letter-spacing="1" dominant-baseline="middle">{asc_sign_name.upper()}</text>\n'

    # Legend at bottom
    svg += _legend_strip(W, 720, asc_sign_idx)

    svg += _footer_block(W, H)
    svg += _svg_close()
    return svg


# ============================================================================
# NORTH INDIAN DIAMOND — v3 refined
# ============================================================================

def render_north_indian(chart_data: dict, title: str = "Birth Chart · North Indian", subtitle: str = "") -> str:
    """Refined North Indian diamond style."""
    W, H = 850, 1050
    svg = _svg_open(W, H)
    svg += _title_block(W, title, subtitle)

    # Square frame
    SIZE = 580
    sx = (W - SIZE) / 2
    sy = 95  # below title block
    cx = sx + SIZE / 2
    cy = sy + SIZE / 2

    asc_sign_name = chart_data["ascendant"]["sign"]
    asc_sign_idx = SIGNS.index(asc_sign_name)

    # House polygon definitions (each house is a polygon)
    # North Indian standard: H1=top diamond, going CCW
    s = SIZE
    # Define each house as a polygon (list of vertices)
    # Format: [(x_offset, y_offset), ...] as fractions of SIZE relative to (sx, sy)
    # Outer corners of the square: TL=(0,0), TR=(1,0), BR=(1,1), BL=(0,1)
    # Center: (0.5, 0.5)
    # Midpoints: TM=(0.5,0), RM=(1,0.5), BM=(0.5,1), LM=(0,0.5)
    # Inner diamond corners are at the midpoints
    house_polygons = {
        1:  [(0.5, 0), (0.75, 0.25), (0.5, 0.5), (0.25, 0.25)],   # top diamond
        2:  [(0.25, 0.25), (0.5, 0), (0, 0)],                       # top-left small triangle
        3:  [(0, 0), (0.25, 0.25), (0, 0.5)],                       # left-top small triangle
        4:  [(0, 0.5), (0.25, 0.25), (0.5, 0.5), (0.25, 0.75)],   # left center diamond
        5:  [(0, 0.5), (0.25, 0.75), (0, 1)],                       # left-bottom small triangle
        6:  [(0, 1), (0.25, 0.75), (0.5, 1)],                       # bottom-left small triangle
        7:  [(0.5, 1), (0.25, 0.75), (0.5, 0.5), (0.75, 0.75)],   # bottom diamond
        8:  [(0.5, 1), (0.75, 0.75), (1, 1)],                       # bottom-right small triangle
        9:  [(1, 1), (0.75, 0.75), (1, 0.5)],                       # right-bottom small triangle
        10: [(1, 0.5), (0.75, 0.75), (0.5, 0.5), (0.75, 0.25)],   # right center diamond
        11: [(1, 0.5), (0.75, 0.25), (1, 0)],                       # right-top small triangle
        12: [(1, 0), (0.75, 0.25), (0.5, 0)],                       # top-right small triangle
    }

    house_centers = {
        1:  (0.5, 0.22),
        2:  (0.27, 0.10),
        3:  (0.10, 0.27),
        4:  (0.22, 0.5),
        5:  (0.10, 0.73),
        6:  (0.27, 0.90),
        7:  (0.5, 0.78),
        8:  (0.73, 0.90),
        9:  (0.90, 0.73),
        10: (0.78, 0.5),
        11: (0.90, 0.27),
        12: (0.73, 0.10),
    }

    # Draw filled house polygons with element colors
    for house_num, poly in house_polygons.items():
        sign_idx = (asc_sign_idx + house_num - 1) % 12
        elem = ELEMENTS[sign_idx]
        ec = ELEMENT_COLORS[elem]
        points = " ".join(f"{sx + p[0]*s:.1f},{sy + p[1]*s:.1f}" for p in poly)
        svg += f'  <polygon points="{points}" fill="{ec["fill"]}" stroke="{PALETTE["line_strong"]}" stroke-width="1" opacity="0.85"/>\n'

    # Outer frame (strong)
    svg += f'  <rect x="{sx}" y="{sy}" width="{SIZE}" height="{SIZE}" fill="none" stroke="{PALETTE["frame"]}" stroke-width="2.5"/>\n'

    # House content
    for house_num, (fx, fy) in house_centers.items():
        sign_idx = (asc_sign_idx + house_num - 1) % 12
        elem = ELEMENTS[sign_idx]
        ec = ELEMENT_COLORS[elem]
        hx = sx + fx * s
        hy = sy + fy * s

        # Sign glyph + number at top of house cell
        svg += f'  <text x="{hx:.1f}" y="{hy-26:.1f}" text-anchor="middle" font-family="{FONT_GLYPH}" font-size="16" fill="{ec["accent"]}">{GLYPHS[sign_idx]}</text>\n'
        svg += f'  <text x="{hx:.1f}" y="{hy-10:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="9" font-weight="700" fill="{ec["accent"]}" letter-spacing="0.5">{sign_idx+1}</text>\n'

        # Planets
        planets = _planets_in_house(chart_data, house_num)
        for j, p in enumerate(planets):
            py = hy + 8 + j * 15
            color = PALETTE["planet_retro"] if p["data"].get("retrograde") else PALETTE["planet"]
            glyph = PLANET_GLYPHS.get(p["name"], "")
            short = PLANET_SHORT.get(p["name"], p["name"][:2])
            retro = " R" if p["data"].get("retrograde") else ""
            # Render glyph and label as separate text elements for clean spacing
            label_text = f"{short}{retro}"
            label_w = len(label_text) * 6.5
            glyph_w = 14
            total_w = glyph_w + 4 + label_w
            start_x = hx - total_w/2
            svg += f'  <text x="{start_x:.1f}" y="{py:.1f}" text-anchor="start" font-family="{FONT_GLYPH}" font-size="13" font-weight="500" fill="{color}">{glyph}</text>\n'
            svg += f'  <text x="{start_x + glyph_w + 4:.1f}" y="{py:.1f}" text-anchor="start" font-family="{FONT_SANS}" font-size="11" font-weight="600" fill="{color}">{label_text}</text>\n'

    # ASC marker on H1
    asc_hx = sx + house_centers[1][0] * s
    asc_hy = sy + house_centers[1][1] * s
    svg += f'  <text x="{asc_hx:.1f}" y="{asc_hy-46:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" font-weight="700" fill="{PALETTE["ascendant"]}" letter-spacing="1.5">ASC</text>\n'

    # Legend at bottom
    svg += _legend_strip(W, 720, asc_sign_idx)

    svg += _footer_block(W, H)
    svg += _svg_close()
    return svg


# ============================================================================
# SOUTH INDIAN SQUARE — v3 refined
# ============================================================================

def render_south_indian(chart_data: dict, title: str = "Birth Chart · South Indian", subtitle: str = "") -> str:
    """Refined South Indian square style."""
    W, H = 850, 1050
    svg = _svg_open(W, H)
    svg += _title_block(W, title, subtitle)

    # Grid (4x4 with center 2x2 empty)
    SIZE = 580
    sx = (W - SIZE) / 2
    sy = 95
    cell = SIZE / 4

    # Fixed sign positions (South Indian convention)
    sign_positions = {
        "Pisces":      (0, 0),
        "Aries":       (0, 1),
        "Taurus":      (0, 2),
        "Gemini":      (0, 3),
        "Cancer":      (1, 3),
        "Leo":         (2, 3),
        "Virgo":       (3, 3),
        "Libra":       (3, 2),
        "Scorpio":     (3, 1),
        "Sagittarius": (3, 0),
        "Capricorn":   (2, 0),
        "Aquarius":    (1, 0),
    }

    asc_sign_name = chart_data["ascendant"]["sign"]
    asc_sign_idx = SIGNS.index(asc_sign_name)

    # Draw each cell
    for sign_name, (row, col) in sign_positions.items():
        x = sx + col * cell
        y = sy + row * cell
        sign_idx = SIGNS.index(sign_name)
        elem = ELEMENTS[sign_idx]
        ec = ELEMENT_COLORS[elem]

        # Cell background
        svg += f'  <rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{ec["fill"]}" stroke="{PALETTE["line_strong"]}" stroke-width="1" opacity="0.9"/>\n'

        # House number (relative to Lagna)
        house_num = ((sign_idx - asc_sign_idx) % 12) + 1

        # Top-left corner: sign glyph + number
        svg += f'  <text x="{x+12:.1f}" y="{y+22:.1f}" text-anchor="start" font-family="{FONT_GLYPH}" font-size="20" fill="{ec["accent"]}">{GLYPHS[sign_idx]}</text>\n'
        svg += f'  <text x="{x+38:.1f}" y="{y+18:.1f}" text-anchor="start" font-family="{FONT_SANS}" font-size="9" font-weight="700" fill="{ec["accent"]}" letter-spacing="0.5">{sign_idx+1}</text>\n'
        svg += f'  <text x="{x+38:.1f}" y="{y+30:.1f}" text-anchor="start" font-family="{FONT_DISPLAY}" font-size="11" fill="{PALETTE["text_dark"]}">{sign_name}</text>\n'

        # Top-right corner: house number badge
        svg += f'  <circle cx="{x+cell-18:.1f}" cy="{y+18:.1f}" r="11" fill="white" stroke="{PALETTE["line_strong"]}" stroke-width="0.8"/>\n'
        svg += f'  <text x="{x+cell-18:.1f}" y="{y+22:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" font-weight="700" fill="{PALETTE["text_dark"]}">H{house_num}</text>\n'

        # Mark Ascendant cell
        if sign_name == asc_sign_name:
            svg += f'  <rect x="{x+3}" y="{y+3}" width="{cell-6}" height="{cell-6}" fill="none" stroke="{PALETTE["ascendant"]}" stroke-width="2.5" stroke-dasharray="6,3"/>\n'
            svg += f'  <text x="{x+cell/2:.1f}" y="{y+cell-10:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" font-weight="700" fill="{PALETTE["ascendant"]}" letter-spacing="1.5">ASCENDANT</text>\n'

        # Planets in this sign
        planets = _planets_in_sign(chart_data, sign_idx)
        for j, p in enumerate(planets):
            py = y + cell/2 + j * 16 - (len(planets)-1)*8
            color = PALETTE["planet_retro"] if p["data"].get("retrograde") else PALETTE["planet"]
            glyph = PLANET_GLYPHS.get(p["name"], "")
            short = PLANET_SHORT.get(p["name"], p["name"][:2])
            deg = int(p["data"]["degree"])
            retro = " R" if p["data"].get("retrograde") else ""
            # Render glyph and label as separate text elements for clean spacing
            label_text = f"{short} {deg}°{retro}"
            # Estimate width: each char ~7px at size 12, plus glyph ~16px
            label_w = len(label_text) * 7
            glyph_w = 16
            total_w = glyph_w + 4 + label_w
            start_x = x + cell/2 - total_w/2
            svg += f'  <text x="{start_x:.1f}" y="{py:.1f}" text-anchor="start" font-family="{FONT_GLYPH}" font-size="14" font-weight="500" fill="{color}">{glyph}</text>\n'
            svg += f'  <text x="{start_x + glyph_w + 4:.1f}" y="{py:.1f}" text-anchor="start" font-family="{FONT_SANS}" font-size="12" font-weight="600" fill="{color}">{label_text}</text>\n'

    # Outer frame
    svg += f'  <rect x="{sx}" y="{sy}" width="{SIZE}" height="{SIZE}" fill="none" stroke="{PALETTE["frame"]}" stroke-width="2.5"/>\n'

    # Center label
    cx_center = sx + SIZE / 2
    cy_center = sy + SIZE / 2
    svg += f'  <text x="{cx_center:.1f}" y="{cy_center-12:.1f}" text-anchor="middle" font-family="{FONT_DISPLAY}" font-size="22" font-weight="500" fill="{PALETTE["text_dark"]}">Birth Chart</text>\n'
    svg += f'  <line x1="{cx_center-40}" y1="{cy_center-2}" x2="{cx_center+40}" y2="{cy_center-2}" stroke="url(#goldAccent)" stroke-width="1.5"/>\n'
    svg += f'  <text x="{cx_center:.1f}" y="{cy_center+15:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" fill="{PALETTE["text_muted"]}" letter-spacing="2">SOUTH INDIAN STYLE</text>\n'
    asc_color = ELEMENT_COLORS[ELEMENTS[asc_sign_idx]]["accent"]
    svg += f'  <text x="{cx_center:.1f}" y="{cy_center+38:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" font-weight="600" fill="{asc_color}" letter-spacing="1.5">LAGNA · {asc_sign_name.upper()}</text>\n'

    # Legend at bottom
    svg += _legend_strip(W, 720, asc_sign_idx)

    svg += _footer_block(W, H)
    svg += _svg_close()
    return svg


# ============================================================================
# CHINESE ZODIAC YEAR-SIGN CARD
# ============================================================================

CHINESE_ANIMALS = [
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"
]

CHINESE_ANIMAL_GLYPHS = {
    "Rat": "🐀", "Ox": "🐂", "Tiger": "🐅", "Rabbit": "🐇",
    "Dragon": "🐉", "Snake": "🐍", "Horse": "🐎", "Goat": "🐐",
    "Monkey": "🐒", "Rooster": "🐓", "Dog": "🐕", "Pig": "🐖",
}

CHINESE_HANZI = {
    "Rat": "鼠", "Ox": "牛", "Tiger": "虎", "Rabbit": "兔",
    "Dragon": "龍", "Snake": "蛇", "Horse": "馬", "Goat": "羊",
    "Monkey": "猴", "Rooster": "雞", "Dog": "狗", "Pig": "豬",
}

# Five elements in Chinese zodiac (Wu Xing) — cycles every 2 years through 10-year cycle
# Year ending in 0,1 = Metal; 2,3 = Water; 4,5 = Wood; 6,7 = Fire; 8,9 = Earth
CHINESE_ELEMENTS = {
    0: "Metal", 1: "Metal",
    2: "Water", 3: "Water",
    4: "Wood",  5: "Wood",
    6: "Fire",  7: "Fire",
    8: "Earth", 9: "Earth",
}

CHINESE_ELEMENT_COLORS = {
    "Metal": {"fill": "#F0EDE5", "accent": "#8A7B5C", "border": "#B8A985"},  # gold/silver
    "Water": {"fill": "#E1ECF3", "accent": "#3A6E96", "border": "#8FB5CF"},  # blue
    "Wood":  {"fill": "#E8EFE0", "accent": "#5A7A3C", "border": "#A8C088"},  # green
    "Fire":  {"fill": "#FBE9E1", "accent": "#C44B2C", "border": "#E5A893"},  # red
    "Earth": {"fill": "#F2EAD8", "accent": "#9C7B3D", "border": "#C9A969"},  # ochre/brown
}

# Yin/Yang alternation: even-ending years = Yang, odd-ending years = Yin
def _chinese_yin_yang(year: int) -> str:
    return "Yang" if year % 2 == 0 else "Yin"


def compute_chinese_zodiac(birth_year: int, birth_month: int = 6, birth_day: int = 15) -> dict:
    """Compute Chinese zodiac sign for a birth year.

    Note: Chinese New Year falls in late Jan / mid Feb. For births in January
    or early February, the previous year's animal may apply. We use a simple
    approximation: if month <= 1, or (month == 2 and day < 5), use prior year.
    For exact dates, real Chinese New Year date should be looked up.
    """
    # Simple approximation for Chinese New Year cutoff
    effective_year = birth_year
    if birth_month == 1 or (birth_month == 2 and birth_day < 5):
        effective_year = birth_year - 1

    # Animal cycle: Year 1900 was Rat (1900 % 12 = 4 corresponds to Rat in our list).
    # Adjust: 1900 = Rat. (1900 - 1900) % 12 = 0 → Rat
    animal_idx = (effective_year - 1900) % 12
    animal = CHINESE_ANIMALS[animal_idx]

    # Element from year ending digit
    year_digit = effective_year % 10
    element = CHINESE_ELEMENTS[year_digit]

    yin_yang = _chinese_yin_yang(effective_year)

    return {
        "year": effective_year,
        "animal": animal,
        "hanzi": CHINESE_HANZI[animal],
        "glyph": CHINESE_ANIMAL_GLYPHS[animal],
        "element": element,
        "yin_yang": yin_yang,
        "approximate": birth_month == 1 or (birth_month == 2 and birth_day < 6),
    }


# Animal traits — concise honest framing
CHINESE_ANIMAL_TRAITS = {
    "Rat":     {"strengths": "Quick-witted, resourceful, observant, naturally social", "watch": "Can be opportunistic, anxious in unstructured situations"},
    "Ox":      {"strengths": "Patient, reliable, methodical, deeply persistent", "watch": "Stubborn under pressure, slow to adapt to sudden change"},
    "Tiger":   {"strengths": "Bold, charismatic, courageous, naturally protective", "watch": "Impulsive, can dominate rooms, struggles with quiet routine"},
    "Rabbit":  {"strengths": "Diplomatic, gentle, refined, builds harmony in groups", "watch": "Conflict-averse, may avoid hard truths, can be overly cautious"},
    "Dragon":  {"strengths": "Visionary, magnetic, energetic, naturally a leader", "watch": "Ego-driven, impatient with mediocrity, can be domineering"},
    "Snake":   {"strengths": "Wise, intuitive, strategic, deeply analytical", "watch": "Secretive, suspicious, slow to forgive"},
    "Horse":   {"strengths": "Free-spirited, energetic, optimistic, builds momentum", "watch": "Restless, struggles with commitment, hates being controlled"},
    "Goat":    {"strengths": "Creative, gentle, empathetic, finds beauty in detail", "watch": "Indecisive, sensitive to criticism, financially dependent"},
    "Monkey":  {"strengths": "Clever, adaptable, witty, solves problems creatively", "watch": "Mischievous, can manipulate, easily bored"},
    "Rooster": {"strengths": "Honest, hardworking, observant, takes pride in craft", "watch": "Critical, perfectionist, can be vain"},
    "Dog":     {"strengths": "Loyal, fair, protective, deeply principled", "watch": "Anxious, judgmental, holds grudges"},
    "Pig":     {"strengths": "Generous, sincere, peace-loving, enjoys life fully", "watch": "Naive, indulgent, can be taken advantage of"},
}


def render_chinese_zodiac(zodiac_data: dict, title: str = "Chinese Zodiac", subtitle: str = "") -> str:
    """Render Chinese zodiac year-sign as a beautiful card."""
    W, H = 850, 1050
    svg = _svg_open(W, H)
    svg += _title_block(W, title, subtitle)

    animal = zodiac_data["animal"]
    element = zodiac_data["element"]
    yin_yang = zodiac_data["yin_yang"]
    year = zodiac_data["year"]
    hanzi = zodiac_data["hanzi"]

    ec = CHINESE_ELEMENT_COLORS[element]

    # Main card centered
    card_w = 580
    card_h = 600
    card_x = (W - card_w) / 2
    card_y = 100

    # Card background with element color
    svg += f'  <rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" fill="{ec["fill"]}" stroke="{ec["border"]}" stroke-width="2" rx="8"/>\n'
    svg += f'  <rect x="{card_x+8}" y="{card_y+8}" width="{card_w-16}" height="{card_h-16}" fill="none" stroke="{ec["accent"]}" stroke-width="0.5" stroke-dasharray="3,4" opacity="0.4" rx="4"/>\n'

    # Year banner top
    svg += f'  <text x="{W/2}" y="{card_y+50}" text-anchor="middle" font-family="{FONT_DISPLAY}" font-size="28" font-weight="500" fill="{PALETTE["text_dark"]}">YEAR {year}</text>\n'
    svg += f'  <line x1="{W/2-50}" y1="{card_y+62}" x2="{W/2+50}" y2="{card_y+62}" stroke="url(#goldAccent)" stroke-width="1.2"/>\n'

    # Hanzi character — large, centered, decorative
    svg += f'  <text x="{W/2}" y="{card_y+220}" text-anchor="middle" font-family="{FONT_CJK}" font-size="200" font-weight="500" fill="{ec["accent"]}" opacity="0.95">{hanzi}</text>\n'

    # Animal name
    svg += f'  <text x="{W/2}" y="{card_y+290}" text-anchor="middle" font-family="{FONT_DISPLAY}" font-size="46" font-weight="500" fill="{PALETTE["text_dark"]}" letter-spacing="3">{animal.upper()}</text>\n'

    # Element + Yin/Yang
    svg += f'  <text x="{W/2}" y="{card_y+325}" text-anchor="middle" font-family="{FONT_SANS}" font-size="14" font-weight="500" fill="{ec["accent"]}" letter-spacing="3">{yin_yang.upper()} · {element.upper()}</text>\n'

    # Decorative divider
    svg += f'  <line x1="{W/2-80}" y1="{card_y+345}" x2="{W/2+80}" y2="{card_y+345}" stroke="{ec["accent"]}" stroke-width="0.6"/>\n'
    svg += f'  <circle cx="{W/2}" cy="{card_y+345}" r="3" fill="{ec["accent"]}"/>\n'

    # Traits — strengths and watchouts
    traits = CHINESE_ANIMAL_TRAITS[animal]
    svg += f'  <text x="{card_x+60}" y="{card_y+390}" text-anchor="start" font-family="{FONT_SANS}" font-size="11" font-weight="700" fill="{ec["accent"]}" letter-spacing="2">STRENGTHS</text>\n'
    # Wrap strengths text
    strengths = traits["strengths"]
    svg += f'  <text x="{card_x+60}" y="{card_y+412}" text-anchor="start" font-family="{FONT_DISPLAY}" font-size="15" fill="{PALETTE["text_body"]}">{strengths}</text>\n'

    svg += f'  <text x="{card_x+60}" y="{card_y+460}" text-anchor="start" font-family="{FONT_SANS}" font-size="11" font-weight="700" fill="{ec["accent"]}" letter-spacing="2">WATCH FOR</text>\n'
    watch = traits["watch"]
    svg += f'  <text x="{card_x+60}" y="{card_y+482}" text-anchor="start" font-family="{FONT_DISPLAY}" font-size="15" fill="{PALETTE["text_body"]}">{watch}</text>\n'

    # Approximate-date warning if applicable
    if zodiac_data.get("approximate"):
        svg += f'  <text x="{W/2}" y="{card_y+card_h-20}" text-anchor="middle" font-family="{FONT_SANS}" font-size="9" fill="{PALETTE["text_muted"]}" font-style="italic">Note: Born near Chinese New Year — verify exact date for precise sign</text>\n'

    # 12-animal legend at bottom
    legend_y = 750
    svg += f'  <text x="{W/2}" y="{legend_y}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" font-weight="600" fill="{PALETTE["text_muted"]}" letter-spacing="2">THE 12 CHINESE ZODIAC ANIMALS</text>\n'
    svg += f'  <line x1="{W/2-50}" y1="{legend_y+6}" x2="{W/2+50}" y2="{legend_y+6}" stroke="{PALETTE["line_soft"]}" stroke-width="0.8"/>\n'

    # 6 columns × 2 rows
    cols = 6
    margin_x = 50
    available_w = W - 2 * margin_x
    cell_w = available_w / cols
    cell_h = 50
    start_y = legend_y + 22

    for i, anml in enumerate(CHINESE_ANIMALS):
        col = i % cols
        row = i // cols
        x = margin_x + col * cell_w
        y = start_y + row * cell_h
        is_current = (anml == animal)

        if is_current:
            svg += f'  <rect x="{x-2}" y="{y-2}" width="{cell_w-6}" height="{cell_h-4}" fill="{ec["fill"]}" stroke="{ec["accent"]}" stroke-width="1" rx="3"/>\n'

        svg += f'  <text x="{x+15}" y="{y+24}" text-anchor="start" font-family="{FONT_CJK}" font-size="22" fill="{PALETTE["text_dark"]}">{CHINESE_HANZI[anml]}</text>\n'
        color = ec["accent"] if is_current else PALETTE["text_muted"]
        svg += f'  <text x="{x+45}" y="{y+18}" text-anchor="start" font-family="{FONT_SANS}" font-size="9" font-weight="700" fill="{color}" letter-spacing="0.5">{i+1}</text>\n'
        svg += f'  <text x="{x+57}" y="{y+18}" text-anchor="start" font-family="{FONT_DISPLAY}" font-size="13" font-weight="500" fill="{PALETTE["text_dark"]}">{anml}</text>\n'

    svg += f'  <text x="{W/2}" y="{H-22}" text-anchor="middle" font-family="{FONT_SANS}" font-size="10" fill="{PALETTE["text_muted"]}" letter-spacing="1.5">THE HONEST ASTROLOGER  ·  CHINESE ZODIAC  ·  YEAR-SIGN ANIMAL</text>\n'
    svg += _svg_close()
    return svg


# ============================================================================
# DISPATCHER
# ============================================================================

def render_chart(
    chart_data: dict,
    style: Literal["western", "north", "south"] = "western",
    title: str = "Birth Chart",
    subtitle: str = "",
) -> str:
    if style == "western":
        return render_western(chart_data, title, subtitle)
    elif style == "north":
        return render_north_indian(chart_data, title, subtitle)
    elif style == "south":
        return render_south_indian(chart_data, title, subtitle)
    else:
        raise ValueError(f"Unknown style: {style}. Use 'western', 'north', or 'south'.")


def svg_to_pdf(svg_string: str, output_path: str) -> None:
    try:
        import cairosvg
        cairosvg.svg2pdf(bytestring=svg_string.encode("utf-8"), write_to=output_path)
    except ImportError:
        raise RuntimeError("PDF export requires cairosvg. Install with: pip install cairosvg")


def svg_to_png(svg_string: str, output_path: str, scale: float = 2.0) -> None:
    try:
        import cairosvg
        cairosvg.svg2png(bytestring=svg_string.encode("utf-8"), write_to=output_path,
                         output_width=int(850 * scale), output_height=int(1050 * scale))
    except ImportError:
        raise RuntimeError("PNG export requires cairosvg. Install with: pip install cairosvg")


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse, json, sys
    p = argparse.ArgumentParser(description="Render a Vedic chart from chart JSON.")
    p.add_argument("--chart-json", help="Path to chart JSON (output of compute_chart.py)")
    p.add_argument("--style", choices=["western", "north", "south", "chinese"], default="western")
    p.add_argument("--title", default=None)
    p.add_argument("--subtitle", default="")
    p.add_argument("--output", required=True, help="Output path (.svg, .png, or .pdf)")
    # Chinese zodiac options
    p.add_argument("--year", type=int, help="Birth year (for chinese style)")
    p.add_argument("--month", type=int, default=6, help="Birth month (for chinese style)")
    p.add_argument("--day", type=int, default=15, help="Birth day (for chinese style)")
    args = p.parse_args()

    if args.style == "chinese":
        if not args.year:
            print("--year required for Chinese zodiac", file=sys.stderr)
            sys.exit(1)
        zodiac = compute_chinese_zodiac(args.year, args.month, args.day)
        title = args.title or "Chinese Zodiac"
        svg = render_chinese_zodiac(zodiac, title=title, subtitle=args.subtitle)
    else:
        if not args.chart_json:
            print("--chart-json required for Vedic styles", file=sys.stderr)
            sys.exit(1)
        with open(args.chart_json) as f:
            chart_data = json.load(f)
        title = args.title or "Birth Chart"
        svg = render_chart(chart_data, style=args.style, title=title, subtitle=args.subtitle)

    if args.output.endswith(".svg"):
        with open(args.output, "w") as f:
            f.write(svg)
        print(f"Wrote SVG to {args.output}")
    elif args.output.endswith(".pdf"):
        svg_to_pdf(svg, args.output)
        print(f"Wrote PDF to {args.output}")
    elif args.output.endswith(".png"):
        svg_to_png(svg, args.output)
        print(f"Wrote PNG to {args.output}")
    else:
        print(f"Unknown output format: {args.output}", file=sys.stderr)
        sys.exit(1)
