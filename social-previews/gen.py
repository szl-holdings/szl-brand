"""Generate Series-A social previews (1280x640 PNG) for all public SZL Holdings repos."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path("/tmp/social-previews")
OUT.mkdir(exist_ok=True)

# Brand: dark bg, purple accent
BG_TOP = (10, 10, 15)
BG_BOTTOM = (18, 18, 26)
ACCENT = (128, 90, 213)        # #805ad5
ACCENT_DIM = (128, 90, 213, 34) # 22 alpha
TEXT_PRIMARY = (240, 240, 240)
TEXT_SECONDARY = (153, 153, 153)
TEXT_MUTED = (102, 102, 102)
CARD_FILL = (255, 255, 255, 6)
CARD_STROKE = (255, 255, 255, 10)

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

W, H = 1280, 640

# Per-repo content: (repo_name, kicker, title, subtitle, tag, stat_a_val, stat_a_label, stat_b_val, stat_b_label, stat_c_val, stat_c_label)
REPOS = [
    ("a11oy",            "GOVERNED EXECUTION", "A11oy",            "Governed agentic execution fabric",      "PLATFORM",  "Λ",     "Invariant",     "8",   "Verticals",     "CPS",   "Trust Plane"),
    ("ouroboros",        "RUNTIME",            "Ouroboros",        "Bounded-loop runtime — Λ invariant",     "RUNTIME",   "≤0.59ms","Λ p99 overhead","28",  "Packages",     "62",    "Guardrails"),
    ("ouroboros-thesis", "RESEARCH",           "Ouroboros Thesis", "Lutar Invariant Family & Λ₁₀",          "RESEARCH",  "13",    "Papers",        "v10", "Latest",       "DOI",   "Zenodo"),
    ("sentra",           "CYBER",              "Sentra",           "Governed adversary loop",                "CYBER",     "6",     "Proof Steps",   "0",   "Drift",        "24/7",  "Posture"),
    ("vessels",          "MARITIME",           "Vessels",          "Fleet intelligence & sanctions",         "MARITIME",  "Dark",  "Vessel Detect", "OFAC","Screening",    "AIS",   "Mesh"),
    ("terra",            "REAL ESTATE",        "Terra",            "Deal pipeline & portfolio analytics",    "REAL ESTATE","Deal","Scoring",       "Mkt", "Signals",      "Port",  "Analytics"),
    ("counsel",          "LEGAL",              "Counsel",          "Policy-gated legal workflows",           "LEGAL",     "Pol",   "Gated",         "Doc", "Review",       "Obli",  "Mapping"),
    ("carlota-jo",       "ADVISORY",           "Carlota Jo",       "Concierge advisory ops",                 "ADVISORY",  "MP",    "Approval",      "CPS", "Delivery",     "Conc",  "Workflow"),
    ("amaru",            "DATA SYNC",          "Amaru",            "Convergent multi-source data sync",      "DATA",      "Δ",     "Append-Only",   "Hash","Verified",     "10+",   "Innovations"),
    ("szl-cookbook",     "ENGINEERING",        "szl-cookbook",     "Anthropic skills pattern",               "COOKBOOK",  "9",     "Skills",        "MD",  "SKILL.md",     "OSS",   "Apache 2.0"),
    ("szl-trust",        "PUBLIC TRUST",       "szl-trust",        "Covenant Proof Standard artifacts",      "TRUST",     "11",    "Artifacts",     "0",   "Mocked",       "Det",   "Replay"),
]


def vgradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h), top)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def draw_card(img, x, y, w, h, val, label):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=CARD_FILL, outline=CARD_STROKE, width=1)
    img.paste(overlay, (0, 0), overlay)
    d = ImageDraw.Draw(img)
    f_val = ImageFont.truetype(FONT_BOLD, 32)
    f_lbl = ImageFont.truetype(FONT_REG, 14)
    bb = d.textbbox((0, 0), val, font=f_val)
    vw = bb[2] - bb[0]
    d.text((x + w // 2 - vw // 2, y + 14), val, fill=ACCENT, font=f_val)
    bb2 = d.textbbox((0, 0), label, font=f_lbl)
    lw = bb2[2] - bb2[0]
    d.text((x + w // 2 - lw // 2, y + h - 28), label, fill=TEXT_MUTED, font=f_lbl)


def build(name, kicker, title, subtitle, tag, a_v, a_l, b_v, b_l, c_v, c_l):
    img = vgradient(W, H, BG_TOP, BG_BOTTOM)
    d = ImageDraw.Draw(img)
    # Left accent bar
    d.rectangle([0, 0, 6, H], fill=ACCENT)
    # Bottom thin accent
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, H - 6, W, H], fill=(*ACCENT, 76))
    img.paste(overlay, (0, 0), overlay)

    # Kicker
    f_kick = ImageFont.truetype(FONT_REG, 18)
    d.text((80, 88), kicker, fill=TEXT_MUTED, font=f_kick)
    # Title
    f_title = ImageFont.truetype(FONT_BOLD, 78)
    d.text((80, 150), title, fill=TEXT_PRIMARY, font=f_title)
    # Subtitle
    f_sub = ImageFont.truetype(FONT_REG, 26)
    d.text((80, 250), subtitle, fill=TEXT_SECONDARY, font=f_sub)
    # Tag pill
    f_pill = ImageFont.truetype(FONT_BOLD, 14)
    pill_w = max(110, d.textbbox((0,0), tag, font=f_pill)[2] + 40)
    overlay2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od2 = ImageDraw.Draw(overlay2)
    od2.rounded_rectangle([80, 296, 80 + pill_w, 296 + 32], radius=4, fill=ACCENT_DIM, outline=ACCENT, width=1)
    img.paste(overlay2, (0, 0), overlay2)
    bb = d.textbbox((0, 0), tag, font=f_pill)
    tw = bb[2] - bb[0]
    d.text((80 + pill_w // 2 - tw // 2, 304), tag, fill=ACCENT, font=f_pill)

    # 3 stat cards
    draw_card(img, 80,  380, 220, 100, a_v, a_l)
    draw_card(img, 320, 380, 220, 100, b_v, b_l)
    draw_card(img, 560, 380, 220, 100, c_v, c_l)

    # Footer: org URL
    f_foot = ImageFont.truetype(FONT_REG, 16)
    d.text((80, H - 50), "github.com/szl-holdings", fill=TEXT_MUTED, font=f_foot)
    # Footer right: szl logo monogram
    f_mono = ImageFont.truetype(FONT_MONO, 24)
    bb_m = d.textbbox((0, 0), "SZL", font=f_mono)
    mw = bb_m[2] - bb_m[0]
    d.text((W - 80 - mw, H - 54), "SZL", fill=ACCENT, font=f_mono)

    out = OUT / f"{name}.png"
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    for spec in REPOS:
        build(*spec)
