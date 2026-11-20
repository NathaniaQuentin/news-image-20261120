#!/usr/bin/env python3
"""Draw the 20 November 2026 world-news front page (1024x1024 PNG).

A newspaper-style infographic: a masthead naming the day, six verified
stories of Friday 20 November 2026 in a 2x3 card grid (each with a tag,
a headline, a one-line summary, a flat pictogram and a dateline), an
"also today" strip with five more headlines, and a footer with sources.
Drawn from scratch with Pillow and DejaVu Sans; no copied art, no network.
"""
import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "news.png"

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PAPER = (247, 242, 231)
INK = (24, 24, 24)
SOFT = (74, 74, 74)
TEAL = (16, 42, 50)
TEAL_SOFT = (158, 182, 190)
GOLD = (214, 164, 52)
RED = (178, 44, 36)
CARD = (255, 255, 255)
EDGE = (218, 210, 192)


def load(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(text, face, max_w):
    """Greedy word wrap: lines that fit max_w pixels."""
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if face.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def softened(color, frac=0.15):
    """Tint a color toward white."""
    return tuple(int(c + (255 - c) * frac) for c in color)


def pictogram(d, kind, cx, cy, r, color):
    """Flat pictogram inside a tinted disc; one drawing per story kind."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=softened(color, 0.16))
    s = r * 0.6
    if kind == "burst":
        # explosion starburst: 8 spikes around a core
        pts = []
        for i in range(16):
            ang = math.pi * i / 8 - math.pi / 2
            rr = s if i % 2 == 0 else s * 0.45
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        d.polygon(pts, fill=color)
        d.ellipse([cx - s * 0.3, cy - s * 0.3, cx + s * 0.3, cy + s * 0.3],
                  fill=(255, 214, 90))
    elif kind == "tower":
        # tapered skyscraper with setbacks, windows and a spire
        d.polygon([(cx - s * 0.55, cy + s * 0.85), (cx - s * 0.42, cy - s * 0.35),
                   (cx - s * 0.3, cy - s * 0.35), (cx - s * 0.3, cy - s * 0.62),
                   (cx + s * 0.3, cy - s * 0.62), (cx + s * 0.3, cy - s * 0.35),
                   (cx + s * 0.42, cy - s * 0.35), (cx + s * 0.55, cy + s * 0.85)],
                  fill=color)
        d.line([cx, cy - s * 0.62, cx, cy - s], fill=color, width=4)
        for row in range(4):
            yy = cy - s * 0.1 + row * s * 0.22
            for dx in (-s * 0.28, 0, s * 0.28):
                d.ellipse([cx + dx - 2, yy - 2, cx + dx + 2, yy + 2],
                          fill=(255, 255, 255))
    elif kind == "tanker":
        # oil tanker: hull, deck block, funnel, waves
        d.polygon([(cx - s, cy + s * 0.1), (cx + s, cy + s * 0.1),
                   (cx + s * 0.82, cy + s * 0.62), (cx - s * 0.82, cy + s * 0.62)],
                  fill=color)
        d.rectangle([cx - s * 0.5, cy - s * 0.5, cx - s * 0.05, cy + s * 0.1],
                    fill=color)
        d.rectangle([cx + s * 0.3, cy - s * 0.72, cx + s * 0.55, cy + s * 0.1],
                    fill=color)
        for dx, dy in [(-s * 0.7, s * 0.85), (-s * 0.1, s * 0.85), (s * 0.5, s * 0.85)]:
            d.arc([cx + dx - s * 0.22, cy + dy - s * 0.1, cx + dx + s * 0.22,
                   cy + dy + s * 0.1], 0, 180, fill=color, width=4)
    elif kind == "cyclone":
        # spiral storm: three shrinking arcs + centre dot
        for k, rr in enumerate([s, s * 0.68, s * 0.38]):
            start = 200 * k
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], start, start + 250,
                  fill=color, width=6)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=color)
    elif kind == "drone":
        # quadcopter: body, four arms, four rotors
        d.rounded_rectangle([cx - s * 0.3, cy - s * 0.22, cx + s * 0.3,
                             cy + s * 0.22], radius=8, fill=color)
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            d.line([cx + dx * s * 0.25, cy + dy * s * 0.18,
                    cx + dx * s * 0.78, cy + dy * s * 0.6], fill=color, width=5)
            d.ellipse([cx + dx * s * 0.78 - s * 0.24, cy + dy * s * 0.6 - 4,
                       cx + dx * s * 0.78 + s * 0.24, cy + dy * s * 0.6 + 4],
                      fill=color)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
    elif kind == "shield":
        # shield outline with a check mark
        d.polygon([(cx - s * 0.72, cy - s * 0.6), (cx + s * 0.72, cy - s * 0.6),
                   (cx + s * 0.72, cy + s * 0.1), (cx, cy + s * 0.85),
                   (cx - s * 0.72, cy + s * 0.1)], outline=color, width=6)
        d.line([cx - s * 0.42, cy - s * 0.02, cx - s * 0.08, cy + s * 0.32,
                cx + s * 0.48, cy - s * 0.38], fill=color, width=6)


# tag, accent colour, pictogram, headline, summary, dateline
STORIES = [
    {"tag": "WAR", "color": (178, 44, 36), "icon": "burst",
     "headline": "Ballistic missiles hit Kyiv overnight",
     "summary": "Overnight barrage sparks fires across districts; no casualties reported yet.",
     "dateline": "KYIV, UKRAINE"},
    {"tag": "MISSILE", "color": (176, 106, 18), "icon": "tower",
     "headline": "Houthi missile hits Riyadh's tallest tower",
     "summary": "PIF Tower struck; windows blown out on 7\u20138 floors, no injuries.",
     "dateline": "RIYADH, SAUDI ARABIA"},
    {"tag": "ENERGY", "color": (14, 110, 110), "icon": "tanker",
     "headline": "Iran says tankers hit mines off Hormuz",
     "summary": "Tehran claims two supertankers carrying 4m+ barrels struck mines; unconfirmed.",
     "dateline": "STRAIT OF HORMUZ"},
    {"tag": "STORM", "color": (38, 92, 158), "icon": "cyclone",
     "headline": "Cyclone Akvan nears India's east coast",
     "summary": "Odisha evacuates 80,000+ people; landfall due Friday with 100 km/h winds.",
     "dateline": "ODISHA, INDIA"},
    {"tag": "AVIATION", "color": (104, 72, 160), "icon": "drone",
     "headline": "Drones shut Genoa airport for two hours",
     "summary": "Flights halted after drones near the runway; airport reopened after checks.",
     "dateline": "GENOA, ITALY"},
    {"tag": "POLITICS", "color": (34, 112, 74), "icon": "shield",
     "headline": "White House names new cyber chief",
     "summary": "Pentagon CIO Kirsten Davies to serve as acting national cyber director.",
     "dateline": "WASHINGTON, USA"},
]

ALSO_TODAY = [
    "S&P 500 down 2%, sixth straight loss",
    "Anthropic closes up 17% after record $81.3bn IPO",
    "COP31 closing day, fossil fuels cut from draft",
    "Trump pardons Pete Rose",
    "Senate rejects Iran war bid 51\u201348",
]


def draw_card(d, story, x, y, bw, bh):
    color = story["color"]
    d.rounded_rectangle([x, y, x + bw, y + bh], radius=12, fill=CARD,
                        outline=EDGE, width=1)
    # accent bar across the top of the card
    d.rounded_rectangle([x, y, x + bw, y + 6], radius=3, fill=color)
    f_tag = load(BOLD, 18)
    f_head = load(BOLD, 27)
    f_sum = load(REG, 22)
    f_date = load(BOLD, 14)
    # tag chip
    tw = f_tag.getlength(story["tag"]) + 20
    d.rounded_rectangle([x + 18, y + 18, x + 18 + tw, y + 18 + 26],
                        radius=6, fill=color)
    d.text((x + 28, y + 22), story["tag"], font=f_tag, fill=(255, 255, 255))
    # pictogram, top right
    pictogram(d, story["icon"], x + bw - 62, y + 60, 44, color)
    # headline, left of the pictogram, at most two lines
    lines = wrap_text(story["headline"], f_head, bw - 36 - 100)[:2]
    hy = y + 56
    for ln in lines:
        d.text((x + 18, hy), ln, font=f_head, fill=INK)
        hy += 34
    # summary, full width, at most two lines
    slines = wrap_text(story["summary"], f_sum, bw - 36)[:2]
    sy = y + 56 + 2 * 34 + 8
    for ln in slines:
        d.text((x + 18, sy), ln, font=f_sum, fill=SOFT)
        sy += 28
    # dateline at the bottom
    d.text((x + 18, y + bh - 28), story["dateline"], font=f_date, fill=color)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 118], fill=TEAL)
    d.text((32, 18), "THE WORLD IN ONE DAY", font=load(BOLD, 21),
           fill=TEAL_SOFT)
    d.text((32, 46), "20 NOVEMBER 2026", font=load(BOLD, 56),
           fill=(255, 255, 255))
    d.text((W - 32, 22), "FRIDAY", font=load(BOLD, 30), fill=GOLD, anchor="ra")
    d.text((W - 32, 60), "KYIV \u00b7 RIYADH \u00b7 HORMUZ \u00b7 ODISHA",
           font=load(BOLD, 16), fill=TEAL_SOFT, anchor="ra")
    d.rectangle([0, 118, W, 124], fill=RED)

    # ---- story grid: 2 columns x 3 rows ----
    gx, gy = 16, 140
    bw, bh, gap = 488, 238, 12
    for i, story in enumerate(STORIES):
        x = gx + (i % 2) * (bw + gap)
        y = gy + (i // 2) * (bh + gap)
        draw_card(d, story, x, y, bw, bh)

    # ---- "also today" strip, two lines ----
    ay = gy + 3 * bh + 2 * gap + 12
    d.rounded_rectangle([16, ay, W - 16, ay + 72], radius=10, fill=CARD,
                        outline=EDGE, width=1)
    f_also = load(REG, 17)
    f_also_b = load(BOLD, 17)
    line1 = " \u00b7 ".join(ALSO_TODAY[:2])
    line2 = " \u00b7 ".join(ALSO_TODAY[2:])
    d.text((32, ay + 10), "ALSO TODAY \u2014 ", font=f_also_b, fill=INK)
    lead_w = f_also_b.getlength("ALSO TODAY \u2014 ")
    d.text((32 + lead_w, ay + 10), line1, font=f_also, fill=INK)
    d.text((32, ay + 40), line2, font=f_also, fill=INK)

    # ---- footer ----
    fy = ay + 72 + 10
    d.rectangle([0, fy, W, H], fill=TEAL)
    d.text((32, fy + 8), "20 NOVEMBER 2026", font=load(BOLD, 22),
           fill=(255, 255, 255))
    d.text((32, fy + 32),
           "Sources: Reuters \u00b7 Associated Press \u00b7 The Hindu BusinessLine \u00b7 "
           "Anadolu Agency \u00b7 Corriere della Sera \u00b7 Defense One",
           font=load(REG, 15), fill=TEAL_SOFT)

    img.save(OUT, optimize=True)
    print("saved", OUT, img.size)


if __name__ == "__main__":
    main()
