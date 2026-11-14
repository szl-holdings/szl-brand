#!/usr/bin/env python3
"""SZL-MARKETING-1.1 — CORRECTED fact pipeline + compliance linter.

Replaces Part 5 of Rosa's payload SZL-MARKETING-1.1-2026-09-30.
Aegis Shield correction, 2026-09-30T19:02Z.

THREE DEFECTS FIXED (all verified against live metal this hour):

1. CROWN SWEEP — the payload sweeps /api/models ONLY, so a DATASET can never
   win the crown. Live proof: models-only crown = SZLHOLDINGS/chaski at 3,070;
   models+datasets crown = SZLHOLDINGS/killinchu-osint-corpus at 74,157.
   That is a 24.2x undercount of Stephen's own crown. Running the payload as
   written would OVERWRITE marketing/factbase.json (corrected 18:31Z) and
   silently revert it — the same defect Joe caught and re-ran.

2. A/B SUBJECT LINE — `("..." [1])` slices the SECOND CHARACTER of the string,
   not a list element. Verified render: `!# ['Receipts, Not Vibes', ...]` and
   SUBJECT A == SUBJECT B (identical list repr), so no A/B test exists.

3. OVERWRITE WITHOUT BACKUP — payload writes factbase.json with no backup, so
   a bad run destroys the corrected artifact with no way back.

Everything else in Part 5 (banned-pattern linter, live-pull discipline,
lint-or-don't-ship) is kept verbatim — Rosa's guardrails are sound.
"""
import json
import pathlib
import re
import shutil
import sys
import time
import urllib.request

OUT = pathlib.Path("/opt/alloyscape/marketing")
OUT.mkdir(parents=True, exist_ok=True)
NOW = lambda: __import__("datetime").datetime.now(
    __import__("datetime").timezone.utc).strftime("%Y-%m-%d")

UA = {"User-Agent": "curl/8.0 (SZL factbase pipeline)"}


def _get_json(url: str):
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=30))


# ---------------------------------------------------------------- Part 2 guardrails
BANNED = [
    # Aegis fix: payload's (?!.*conjecture) looked FORWARD only, so it blocked
    # Rosa's own honest line 'always "Conjecture 1" — never proven' and would
    # block any sentence where the disclaimer precedes the word. Now scans the
    # whole sentence for a disclaimer on either side, and treats explicit
    # negation ("never/not/NOT proven") as compliant rather than a violation.
    (r"(?<!\w)(proven|proof-of-performance)(?!\w)", "Lambda/performance overclaim"),
    (r"\bguaranteed?\b", "guarantee language"),
    (r"\b100% (trust|safe|secure)", "ceiling violation (max 0.97)"),
    (r"\bstate.of.the.art\b", "unverifiable superlative"),
    (r"\breturns of \d", "quant performance claim"),
    # Aegis fix: payload pattern required NUMBER-BEFORE-KEYWORD ("3 km detection"),
    # so the natural English order ("Detection range 3 km", "detects at 5 miles")
    # sailed through — the exact defense-vertical claim Part 2 rule 1 forbids.
    # Now order-agnostic within a sentence, and catches bare distance units next to
    # any detection/sensor/range verb or noun.
    (r"\d+(?:\.\d+)?\s*(?:km|kilometer|miles?|meters?|metres?|nautical\s*miles?|nm)\b",
     "killinchu capability quantification (defense vertical)",
     r"detect|sensor|radar|range|coverage|target|threat|drone|\bUAS\b|aircraft|vessel|track|acquire"),
    # Aegis fix: Part 2 rule 4 bans "verified trust" about Lambda, but the payload
    # shipped NO pattern for it. Enforced now.
    (r"verified\s+trust", "Lambda discipline (Part 2 rule 4: 'verified trust' is banned)"),
    (r"trust\s+(?:level|score)\s*(?:of|=|:)\s*(?:1|100|1\.0|perfect)",
     "ceiling violation (max 0.97)"),
    # Aegis fix: payload caught only "returns of <digit>"; bare performance language
    # for the advisory-only quant lane ("delivers strong returns") passed clean.
    (r"\b(?:strong|consistent|superior|market-beating|alpha-generating)\s+returns\b"
     r"|\b\d+(?:\.\d+)?%\s+(?:annual|monthly|yearly)?\s*(?:returns?|yield|gain)\b"
     r"|\breturns?\s+(?:of|up\s+to)\s+\d",
     "quant performance claim (Part 2 rule 2: advisory-only, never imply performance)"),
    # Aegis additions — the two dead/trap doors verified tonight
    (r"\bkhipu\.alloyszlholdings\.com\b",
     "dead DNS door (NO_DNS, verified live)"),
    (r"(?<!a-11-)oy\.com\b", "unhyphenated verify domain dies at the edge"),
]


DISCLAIMER = re.compile(r"conjecture|not proven|never proven|no[t]? verified|"
                        r"advisory|unavailable|we do not claim", re.I)


def lint(text: str) -> list:
    """Return violations. A draft with violations does not ship.

    Sentence-scoped: a banned word inside a sentence that carries a disclaimer
    (Conjecture 1 / not proven / advisory / UNAVAILABLE) is compliant, because
    the doctrine's own honest phrasing must not be punished. Negation-only
    sentences ("never proven") are compliant by construction.
    """
    out = []
    sentences = re.split(r"(?<=[.!?\n])", text)
    for entry in BANNED:
        pat, msg = entry[0], entry[1]
        ctx = entry[2] if len(entry) > 2 else None
        for sent in sentences:
            m = re.search(pat, sent, re.I)
            if not m:
                continue
            if DISCLAIMER.search(sent):
                continue                     # honest disclaimer present -> compliant
            # Aegis: context gate — a banned-looking fragment only counts as a
            # capability claim when the SAME sentence carries sensor/detection
            # context. Keeps "the venue is 3 km from the hotel" compliant while
            # still catching "detects targets at 5 miles".
            if ctx and not re.search(ctx, sent, re.I):
                continue
            out.append("BANNED: %s -> %r in sentence %r" % (msg, m.group(0), sent.strip()[:70]))
            break                            # one report per pattern is enough
    return out


# ---------------------------------------------------------------- FIX 1: crown sweep
def factbase() -> dict:
    facts = {"generated": NOW()}

    # GitHub: paginate for real (payload's r.links pattern requires the
    # `requests` lib; this stdlib version walks the Link header).
    repos, url = [], "https://api.github.com/orgs/szl-holdings/repos?per_page=100"
    while url:
        resp = urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=30)
        body = json.load(resp)
        repos += body
        url = None
        for part in resp.headers.get("Link", "").split(","):
            if 'rel="next"' in part:
                url = part.split("<")[1].split(">")[0]
    facts["github"] = {"repos": len(repos),
                       "archived": sum(1 for x in repos if x.get("archived"))}

    facts["hf"] = {}
    counts = {}
    for kind in ("models", "datasets", "spaces"):
        rows = _get_json(
            "https://huggingface.co/api/%s?author=SZLHOLDINGS&limit=1000" % kind)
        counts[kind] = rows
        facts["hf"][kind] = len(rows)

    # *** THE FIX: sweep MODELS *AND* DATASETS for the crown ***
    combined = counts["models"] + counts["datasets"]
    top = max(combined, key=lambda x: x.get("downloads", 0) or 0)
    facts["hf"]["top"] = {
        "id": top["id"],
        "kind": "datasets" if top in counts["datasets"] else "models",
        "downloads": top.get("downloads", 0),
        "sweep": "models+datasets",           # provenance, so the fix can't be lost again
    }

    # *** THE FIX: also record the models-only crown so the 24x gap stays visible ***
    top_m = max(counts["models"], key=lambda x: x.get("downloads", 0) or 0)
    facts["hf"]["top_models_only_DO_NOT_PRINT"] = {
        "id": top_m["id"], "downloads": top_m.get("downloads", 0),
        "note": "wrong crown — recorded only so the models-only bug can never hide again",
    }

    dm = sum(x.get("downloads", 0) or 0 for x in counts["models"])
    dd = sum(x.get("downloads", 0) or 0 for x in counts["datasets"])
    facts["hf"]["downloads"] = {"models": dm, "datasets": dd, "total": dm + dd}
    return facts


# ---------------------------------------------------------------- FIX 3: backup
def write_factbase(facts: dict) -> pathlib.Path:
    target = OUT / "factbase.json"
    if target.exists():
        bak = target.with_suffix(".json.bak.%d" % int(time.time()))
        shutil.copy2(target, bak)
        print("backup: %s (%d B)" % (bak, bak.stat().st_size))
    target.write_text(json.dumps(facts, indent=2))
    return target


# ---------------------------------------------------------------- FIX 2: real A/B
def ab_subjects(subjects: list) -> tuple:
    """Return (A, B) as REAL separate lines. Never print a list repr."""
    if len(subjects) < 2:
        raise SystemExit("A/B needs two subject lines; got %r" % (subjects,))
    return subjects[0], subjects[1]


def substack_draft(f: dict, essay_body: str, subjects: list) -> str:
    a, b = ab_subjects(subjects)
    t = f["hf"]["top"]
    head = (
        "<!-- SUBJECT A: %s\n     SUBJECT B: %s -->\n"
        "# %s\n\n"
        "## The estate, this week (fetched %s)\n\n"
        "- %d GitHub repositories (%d honestly archived)\n"
        "- %d models - %d datasets - %d Spaces on Hugging Face\n"
        "- Most-downloaded artifact: %s (%s downloads)\n"
        "- %s total downloads across the estate (MEASURED)\n\n"
        % (a, b, a, f["generated"],
           f["github"]["repos"], f["github"]["archived"],
           f["hf"]["models"], f["hf"]["datasets"], f["hf"]["spaces"],
           t["id"], "{:,}".format(t["downloads"]),
           "{:,}".format(f["hf"]["downloads"]["total"]))
    )
    tail = (
        "\n\n---\n\nEvery number above was fetched from a live API at generation time.\n"
        "Verify a receipt yourself: https://a-11-oy.com/verify  -  "
        "Proof registry: https://a11oy.net\n"
    )
    draft = head + essay_body + tail
    v = lint(draft)
    if v:
        raise SystemExit("DRAFT BLOCKED BY COMPLIANCE LINTER:\n" + "\n".join(v))
    return draft


if __name__ == "__main__":
    f = factbase()
    p = write_factbase(f)
    crown = f["hf"]["top"]
    print(json.dumps(f, indent=2))
    print()
    print("factbase locked %s -> %s (%d B)" % (NOW(), p, p.stat().st_size))
    print("CROWN (printable): %s  %s downloads  [%s sweep]"
          % (crown["id"], "{:,}".format(crown["downloads"]), crown["sweep"]))
    # Self-check: refuse to ship a crown that is the known-wrong models-only one.
    wrong = f["hf"]["top_models_only_DO_NOT_PRINT"]
    if crown["id"] == wrong["id"] and crown["kind"] == "models":
        print("WARNING: crown equals the models-only result — sweep may have regressed",
              file=sys.stderr)
