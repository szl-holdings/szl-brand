"""Generate Series-A social previews (1280x640 PNG) for all public SZL Holdings repos.

Re-verified 2026-05-11. All facts below are cross-referenced against:
 - lib/db/src/schema (848 provisioned tables)
 - dossier/v2/APEX_v2_Operational_Briefing.md (post-hallucination-sweep version)
 - THESIS_PUBLICATIONS.md (post-hallucination-sweep version — 11 papers, not 13)
 - packages/ (28 ouroboros packages)
 - Zenodo DOI resolution (v1-v11, latest v11 = 20119582)

Generates 14 banners: 11 product repos + 2 public research/trust repos +
org profile + Stephen's personal profile.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path("/tmp/social-previews")
OUT.mkdir(exist_ok=True)

# Brand: dark bg, purple accent
BG_TOP = (10, 10, 15)
BG_BOTTOM = (18, 18, 26)
ACCENT = (128, 90, 213)          # #805ad5
ACCENT_BRIGHT = (168, 130, 255)  # for edge glow
ACCENT_DIM = (128, 90, 213, 34)  # 22 alpha
TEXT_PRIMARY = (240, 240, 240)
TEXT_SECONDARY = (180, 180, 190)
TEXT_MUTED = (110, 110, 120)
CARD_FILL = (255, 255, 255, 8)
CARD_STROKE = (255, 255, 255, 14)

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

W, H = 1280, 640

# Per-repo content: (repo, kicker, title, subtitle, tag, a_v, a_l, b_v, b_l, c_v, c_l)
#
# VERIFIED 2026-05-11:
#  - ouroboros-thesis: 11 papers v1-v11 (NOT 13). Latest is v11 (Applied Lambda).
#    Concept DOI 10.5281/zenodo.19944926. v11 per-version DOI 20119582.
#  - ouroboros (runtime): 28 ouroboros packages, 62 guardrails tests,
#    Lambda overhead <=0.59ms p99. v11 paper ran 24,800 calls.
#  - a11oy: platform surface count is SEVEN (consolidated under A11oy).
#    Trust Plane + Decision Fabric substrate.
#  - szl-trust: 11 CPS artifacts per reference run (E4 codex-kernel).
#  - szl-cookbook: 9 SKILL.md files, Apache 2.0.
#  - Surface count everywhere: 7 (was erroneously 8 with fabricated ROSIE).
REPOS = [
    # ---- product surfaces (7) ----
    ("a11oy",            "GOVERNED EXECUTION", "A11oy",            "Orchestration + Decision Fabric + Trust Plane", "PLATFORM",   "7",       "Surfaces",      "Λ",      "Invariant",    "CPS",   "Standard"),
    ("sentra",           "CYBER",              "Sentra",           "Governed adversary loop, typed receipts",       "CYBER",      "6",       "Proof Steps",   "0",      "Drift",        "24/7",  "Posture"),
    ("vessels",          "MARITIME",           "Vessels",          "Fleet intelligence & sanctions screening",      "MARITIME",   "AIS",     "Live",          "OFAC",   "Screening",    "Dark",  "Detect"),
    ("terra",            "REAL ESTATE",        "Terra",            "Deal pipeline & portfolio analytics",           "REAL ESTATE","Deal",    "Scoring",       "Mkt",    "Signals",      "Port",  "Analytics"),
    ("counsel",          "LEGAL",              "Counsel",          "Policy-gated legal workflows",                  "LEGAL",      "Pol",     "Gated",         "Doc",    "Review",       "Obli",  "Mapping"),
    ("carlota-jo",       "ADVISORY",           "Carlota Jo",       "Concierge advisory operations",                 "ADVISORY",   "MP",      "Approval",      "CPS",    "Delivery",     "Conc",  "Workflow"),
    ("amaru",            "DATA SYNC",          "Amaru",            "Convergent multi-source data sync",             "DATA",       "Δ",       "Append-Only",   "Hash",   "Verified",     "10+",   "Innovations"),
    # ---- runtime + research ----
    ("ouroboros",        "RUNTIME",            "Ouroboros",        "Bounded-loop runtime — Λ invariant",            "RUNTIME",    "≤0.59ms", "Λ p99",         "28",     "Packages",     "62",    "Guardrails"),
    ("ouroboros-thesis", "RESEARCH",           "Ouroboros Thesis", "Lutar Invariant Family v1→v11",                 "RESEARCH",   "11",      "Papers",        "v11",    "Latest",       "DOI",   "Zenodo"),
    # ---- public trust / OSS ----
    ("szl-cookbook",     "ENGINEERING",        "szl-cookbook",     "Anthropic skills pattern — 9 SKILL.md",         "OSS",        "9",       "Skills",        "MD",     "SKILL.md",     "Apache","2.0"),
    ("szl-trust",        "PUBLIC TRUST",       "szl-trust",        "Covenant Proof Standard artifacts",             "TRUST",      "11",      "Artifacts",     "0",      "Mocked",       "Det",   "Replay"),
    # ---- org & personal ----
    (".github",          "SZL HOLDINGS",       "SZL Holdings",     "Governed decision infrastructure",              "ORG",        "7",       "Surfaces",      "11",     "Papers",       "44",    "Innovations"),
    ("stephenlutar2-hash","FOUNDER & CEO",    "Stephen P. Lutar Jr.","Founder, SZL Holdings · The Lutar Invariant","PROFILE",    "SZL",     "Holdings",      "Λ",      "Author",       "9",     "Formal Axes"),
    ("szl-brand",        "BRAND",              "szl-brand",        "Brand assets & deterministic banners",          "BRAND",      "13",      "Banners",       "CC",     "BY 4.0",       "Det",   "Builder"),
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
    od.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=CARD_FILL, outline=CARD_STROKE, width=1)
    img.paste(overlay, (0, 0), overlay)
    d = ImageDraw.Draw(img)
    # value font size scales down if too wide
    val_str = str(val)
    for size in (34, 30, 26, 22, 18):
        f_val = ImageFont.truetype(FONT_BOLD, size)
        bb = d.textbbox((0, 0), val_str, font=f_val)
        if bb[2] - bb[0] <= w - 24:
            break
    f_lbl = ImageFont.truetype(FONT_REG, 14)
    bb = d.textbbox((0, 0), val_str, font=f_val)
    vw = bb[2] - bb[0]
    vh = bb[3] - bb[1]
    d.text((x + w // 2 - vw // 2, y + 16), val_str, fill=ACCENT_BRIGHT, font=f_val)
    bb2 = d.textbbox((0, 0), label, font=f_lbl)
    lw = bb2[2] - bb2[0]
    d.text((x + w // 2 - lw // 2, y + h - 28), label, fill=TEXT_MUTED, font=f_lbl)


def build(name, kicker, title, subtitle, tag, a_v, a_l, b_v, b_l, c_v, c_l):
    img = vgradient(W, H, BG_TOP, BG_BOTTOM)
    d = ImageDraw.Draw(img)

    # Left accent bar (full height)
    d.rectangle([0, 0, 6, H], fill=ACCENT)
    # Bottom thin accent
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, H - 6, W, H], fill=(*ACCENT, 90))
    img.paste(overlay, (0, 0), overlay)

    # Kicker
    f_kick = ImageFont.truetype(FONT_REG, 18)
    d.text((80, 80), kicker, fill=TEXT_MUTED, font=f_kick)

    # Title — auto shrink if too wide for the canvas
    for tsize in (82, 74, 66, 58, 50, 44):
        f_title = ImageFont.truetype(FONT_BOLD, tsize)
        if d.textbbox((0, 0), title, font=f_title)[2] <= W - 160:
            break
    d.text((80, 140), title, fill=TEXT_PRIMARY, font=f_title)

    # Subtitle
    f_sub = ImageFont.truetype(FONT_REG, 26)
    d.text((80, 244), subtitle, fill=TEXT_SECONDARY, font=f_sub)

    # Tag pill
    f_pill = ImageFont.truetype(FONT_BOLD, 14)
    pill_w = max(110, d.textbbox((0, 0), tag, font=f_pill)[2] + 40)
    overlay2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od2 = ImageDraw.Draw(overlay2)
    od2.rounded_rectangle([80, 292, 80 + pill_w, 292 + 32], radius=4, fill=ACCENT_DIM, outline=ACCENT, width=1)
    img.paste(overlay2, (0, 0), overlay2)
    bb = d.textbbox((0, 0), tag, font=f_pill)
    tw = bb[2] - bb[0]
    d.text((80 + pill_w // 2 - tw // 2, 300), tag, fill=ACCENT, font=f_pill)

    # 3 stat cards
    draw_card(img, 80,  380, 220, 100, a_v, a_l)
    draw_card(img, 320, 380, 220, 100, b_v, b_l)
    draw_card(img, 560, 380, 220, 100, c_v, c_l)

    # Footer: org URL (left), SZL monogram (right)
    f_foot = ImageFont.truetype(FONT_REG, 16)
    d.text((80, H - 50), "github.com/szl-holdings", fill=TEXT_MUTED, font=f_foot)
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
    print(f"\nGenerated {len(REPOS)} banners.")
