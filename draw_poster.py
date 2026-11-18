#!/usr/bin/env python3
"""Draw the 18 November 2026 world-news poster (1024x1024 PNG).

One day's news, in one image. Every fact below was verified against real
reporting published on 18 November 2026 (Reuters, AP, The Guardian, RNZ,
NZ MetService, AAP, Malaysiakini, Xinhua, Euronext). No event, figure or
quote is invented, and no story is carried over from any other day.

Layout: newspaper front page with a teal masthead. Lead story on the left
with a drawn map of the Gulf, five more stories plus a "By the numbers"
panel in a 2x3 grid, an "ALSO" strip, and a sources footer.
Run: python3 draw_poster.py -> entry.png
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (250, 247, 240)
INK = (24, 24, 24)
TEAL = (14, 59, 57)
TEAL_DARK = (9, 42, 41)
GOLD = (232, 184, 75)
RED = (166, 30, 30)
MUTED = (96, 104, 112)
CARD = (255, 255, 255)
BORDER = (214, 207, 190)
STRIP = (243, 233, 210)
FOOT = (107, 114, 128)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap, returns lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def starburst(draw, cx, cy, outer, inner, points, fill, outline):
    pts = []
    for i in range(points * 2):
        r = outer if i % 2 == 0 else inner
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=fill, outline=outline, width=2)


def label(draw, x, y, text, fnt, fill=(255, 255, 255)):
    """White text with a dark halo so it stays legible over the map."""
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        draw.text((x + dx, y + dy), text, font=fnt, fill=(10, 30, 40))
    draw.text((x, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- stories
LEAD = {
    "kicker": "LEAD STORY  \u2022  THE GULF",
    "headline": "IRAN DRONES STRIKE US BASE IN KUWAIT",
    "body": (
        "Tehran widened its attacks across the Gulf on Wednesday, firing "
        "drones at the US Ali Al Salem air base in Kuwait \u2014 its first "
        "strike there since September \u2014 and at targets in Bahrain, "
        "intercepted for a third time this week. It followed US strikes on "
        "a missile site on Qeshm Island."
    ),
}

STORIES = [
    {
        "tag": "POLITICS",
        "color": (30, 58, 95),
        "headline": "PELTOLA WINS ALASKA; DEMOCRATS REACH 56",
        "body": (
            "Democrat Mary Peltola wins Alaska's Senate seat, flipping it "
            "from the Republicans and lifting her party to 56 seats."
        ),
    },
    {
        "tag": "WEATHER",
        "color": (8, 102, 120),
        "headline": "CATEGORY 5 CYCLONE XAVIER HITS COOK ISLANDS",
        "body": (
            "Severe Tropical Cyclone Xavier, with gusts up to 315 km/h, "
            "reached the Northern Cook Islands. Shelters opened as the "
            "storm bore down on the atolls."
        ),
    },
    {
        "tag": "MARKETS",
        "color": (22, 101, 52),
        "headline": "ALSTOM HITS A 21-YEAR LOW",
        "body": (
            "Shares in the French train maker fell 9% to \u20ac9.08, their "
            "lowest since May 2005, after net debt more than doubled to "
            "\u20ac1.1bn."
        ),
    },
    {
        "tag": "GAZA",
        "color": (139, 26, 26),
        "headline": "UN WARNS OF \u2018ANOTHER WINTER IN TENTS AND RUBBLE\u2019",
        "body": (
            "The Board of Peace told the UN Security Council the Gaza "
            "ceasefire could collapse without urgent steps, and urged "
            "scaled-up shelter and winter aid."
        ),
    },
    {
        "tag": "DISASTER",
        "color": (71, 85, 105),
        "headline": "MAGNITUDE 6.0 QUAKE HITS PAPUA NEW GUINEA",
        "body": (
            "A magnitude 6.0 earthquake struck Papua New Guinea at a depth "
            "of 10 km, the German Research Centre for Geosciences said."
        ),
    },
]

NUMBERS = [
    "Brent $91.69 \u25bc1.6%  \u00b7  WTI $84.06 \u25bc2.3%",
    "Senate: Democrats 56 \u2013 Republicans 44",
    "Xavier gusts 315 km/h  \u00b7  pressure 910 hPa",
    "Alstom \u22129% to \u20ac9.08  \u00b7  \u221264% in 2026",
]

ALSO = (
    "Malaysia to review leaked Deutsche Bank 1MDB files  \u2022  Xi opens "
    "APEC in Shenzhen  \u2022  Gulf bourses fall"
)
FOOTER = (
    "Sources: Reuters \u00b7 AP \u00b7 The Guardian \u00b7 RNZ \u00b7 NZ "
    "MetService \u00b7 AAP \u00b7 Malaysiakini \u00b7 Xinhua \u2014 All events "
    "reported on Wednesday 18 November 2026"
)


# ---------------------------------------------------------------- drawing
def draw_gulf(draw, x0, y0, x1, y1):
    """Flat stylised map of the Gulf: sea, land, targets, drones."""
    sea = (27, 78, 98)
    land = (224, 205, 160)
    land_dark = (203, 182, 132)
    draw.rectangle([x0, y0, x1, y1], fill=sea)
    # Arabian peninsula along the bottom and left
    draw.polygon([
        (x0, y0 + 190), (x0 + 70, y0 + 150), (x0 + 150, y0 + 168),
        (x0 + 205, y0 + 205), (x0 + 235, y0 + 262), (x0 + 300, y1),
        (x0, y1),
    ], fill=land)
    # Iran along the top and right
    draw.polygon([
        (x0 + 120, y0), (x1, y0), (x1, y0 + 130), (x1 - 60, y0 + 120),
        (x1 - 130, y0 + 78), (x0 + 210, y0 + 58), (x0 + 150, y0 + 30),
    ], fill=land_dark)
    # the Gulf itself, between the two land masses
    draw.polygon([
        (x0 + 150, y0 + 30), (x0 + 210, y0 + 58), (x1 - 130, y0 + 78),
        (x1 - 60, y0 + 120), (x0 + 235, y0 + 262), (x0 + 205, y0 + 205),
        (x0 + 150, y0 + 168), (x0 + 70, y0 + 150),
    ], fill=(64, 128, 158))
    # wave marks on the water
    for xx, yy in ((x0 + 90, y0 + 100), (x0 + 250, y0 + 150),
                   (x0 + 130, y0 + 230)):
        draw.arc([xx - 14, yy - 6, xx + 14, yy + 6], 200, 340,
                 fill=(140, 185, 205), width=2)
    # Qeshm Island marker (Iran, top right)
    qx, qy = x0 + 268, y0 + 62
    draw.ellipse([qx - 5, qy - 5, qx + 5, qy + 5], fill=(255, 255, 255),
                 outline=(10, 30, 40), width=2)
    label(draw, qx + 10, qy - 8, "QESHM ISLAND", font(BOLD, 13))
    # Kuwait target: Ali Al Salem air base
    kx, ky = x0 + 100, y0 + 140
    starburst(draw, kx, ky, 30, 12, 12, (245, 158, 11), (234, 88, 12))
    starburst(draw, kx, ky, 14, 6, 8, (254, 240, 138), (234, 88, 12))
    label(draw, kx - 30, ky + 36, "KUWAIT", font(BOLD, 14))
    label(draw, kx - 30, ky + 54, "Ali Al Salem air base", font(REG, 12))
    # Bahrain target
    bx, by = x0 + 225, y0 + 225
    starburst(draw, bx, by, 24, 10, 12, (245, 158, 11), (234, 88, 12))
    starburst(draw, bx, by, 11, 5, 8, (254, 240, 138), (234, 88, 12))
    label(draw, bx + 28, by - 8, "BAHRAIN", font(BOLD, 14))
    # drones flying in from the top
    for dx, dy in ((x0 + 180, y0 + 40), (x0 + 300, y0 + 110)):
        draw.polygon([(dx, dy - 8), (dx + 14, dy), (dx, dy + 8),
                      (dx - 14, dy)], fill=(24, 24, 24))
        draw.line([(dx - 22, dy - 14), (dx - 8, dy - 6)], fill=(24, 24, 24),
                  width=2)
        draw.line([(dx + 22, dy - 14), (dx + 8, dy - 6)], fill=(24, 24, 24),
                  width=2)
    label(draw, x0 + 12, y0 + 10, "THE GULF", font(BOLD, 15))
    # scale note
    draw.text((x1 - 118, y1 - 22), "map not to scale", font=font(REG, 11),
              fill=(190, 210, 220))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    draw.rectangle([0, 0, W, 96], fill=TEAL)
    draw.rectangle([0, 92, W, 96], fill=GOLD)
    draw.text((28, 20), "THE WORLD IN ONE PAGE", font=font(BOLD, 38),
              fill=(255, 255, 255))
    draw.text((28, 66), "One day's news, drawn from verified reporting",
              font=font(REG, 15), fill=(190, 214, 210))
    draw.text((996, 18), "WEDNESDAY", font=font(BOLD, 19), fill=GOLD,
              anchor="ra")
    draw.text((996, 44), "18 NOVEMBER 2026", font=font(BOLD, 30),
              fill=(255, 255, 255), anchor="ra")

    # ---- lead story ----------------------------------------------------
    lx0, ly0, lx1, ly1 = 28, 112, 996, 436
    draw.rectangle([lx0, ly0, lx1, ly1], fill=CARD, outline=BORDER, width=1)
    draw.rectangle([lx0, ly0, lx1, ly0 + 6], fill=RED)
    draw_gulf(draw, 44, 128, 420, 420)
    tx = 444
    draw.text((tx, 134), LEAD["kicker"], font=font(BOLD, 17), fill=RED)
    hl = wrap(draw, LEAD["headline"], font(BOLD, 42), lx1 - tx - 16)
    y = draw_text_block(draw, tx, 162, hl, font(BOLD, 42), INK, 50)
    body = wrap(draw, LEAD["body"], font(REG, 19), lx1 - tx - 16)
    draw_text_block(draw, tx, y + 12, body, font(REG, 19), (51, 51, 51), 25)

    # ---- five stories + numbers panel, 2 x 3 grid -----------------------
    cols = [28, 528]
    rows = [452, 602, 752]
    cell_w, cell_h = 468, 138
    for i, st in enumerate(STORIES):
        x0 = cols[i % 2]
        y0 = rows[i // 2]
        x1, y1 = x0 + cell_w, y0 + cell_h
        draw.rectangle([x0, y0, x1, y1], fill=CARD, outline=BORDER, width=1)
        draw.rectangle([x0, y0, x0 + 5, y1], fill=st["color"])
        draw.text((x0 + 18, y0 + 12), st["tag"], font=font(BOLD, 14),
                  fill=st["color"])
        hl = wrap(draw, st["headline"], font(BOLD, 20), cell_w - 36)
        y = draw_text_block(draw, x0 + 18, y0 + 36, hl, font(BOLD, 20),
                            INK, 24)
        body = wrap(draw, st["body"], font(REG, 15), cell_w - 36)
        draw_text_block(draw, x0 + 18, y + 6, body, font(REG, 15),
                        (51, 51, 51), 19)
    # numbers panel: last cell of the grid
    nx0, ny0 = cols[1], rows[2]
    nx1, ny1 = nx0 + cell_w, ny0 + cell_h
    draw.rectangle([nx0, ny0, nx1, ny1], fill=TEAL_DARK)
    draw.text((nx0 + 18, ny0 + 12), "BY THE NUMBERS", font=font(BOLD, 15),
              fill=GOLD)
    y = ny0 + 38
    for line in NUMBERS:
        draw.text((nx0 + 18, y), line, font=font(REG, 15),
                  fill=(255, 255, 255))
        y += 22

    # ---- ALSO strip ------------------------------------------------------
    draw.rectangle([28, 906, 996, 940], fill=STRIP)
    draw.text((42, 923), "ALSO:", font=font(BOLD, 15), fill=INK,
              anchor="lm")
    aw = draw.textlength("ALSO:  ", font=font(BOLD, 15))
    draw.text((42 + aw, 923), ALSO, font=font(REG, 15), fill=INK,
              anchor="lm")

    # ---- footer ----------------------------------------------------------
    fw = draw.textlength(FOOTER, font=font(REG, 13))
    draw.text(((W - fw) / 2, 960), FOOTER, font=font(REG, 13), fill=FOOT)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, optimize=True)
    size = os.path.getsize(out)
    print(f"saved {out}  {W}x{H}  {size} bytes "
          f"({size / 1024:.1f} KiB, limit 1024 KiB)")
    assert size <= 1024 * 1024, "entry.png over the 1 MiB cap"
    print("OK: 1024x1024, under 1 MiB")


if __name__ == "__main__":
    main()
