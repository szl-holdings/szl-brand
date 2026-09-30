#!/usr/bin/env python3
"""SZL-MARKETING-1.1: fact pipeline + compliance linter + channel drafts."""
import json, pathlib, re, requests
from datetime import datetime, timezone

OUT = pathlib.Path("marketing"); OUT.mkdir(exist_ok=True)
NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d")

BANNED = [  # Part 2 guardrails, machine-enforced
    (r"\bproven\b(?!.*(conjecture|never|not ))", "Λ/performance overclaim"),
    (r"\bguaranteed?\b(?!.*(banned|discipline|doctrine|forbidden))", "guarantee language"),
    (r"\b100% (trust|safe|secure)", "ceiling violation (max 0.97)"),
    (r"\bstate.of.the.art\b(?!.*(catches|banned|linter|guard|doctrine))", "unverifiable superlative"),
    (r"\breturns of \d", "quant performance claim"),
    # FIX (aegis, 2026-09-30, Vigil's crack 2026-09-30T13:5xZ): the old rule matched
    # ONLY unit-then-word order ("5 km detection"), so it caught the phrasing nobody
    # writes and let through the one everybody writes ("detection range of 5 km",
    # "detects at 5 km", "kilometer-scale detection"). Rosa's hard floor is
    # "no killinchu capability numbers" -- so ban number+unit ANYWHERE, plus the
    # vague "-scale" dodge. Conjecture/Lambda carve-out preserved.
    (r"\b\d+(\.\d+)?\s?(km|kilometers?|kilometres?|miles?|meters?|metres?)\b(?!.*(conjecture|Λ))", "capability quantification"),
    (r"\b(kilometer|kilometre|mile|meter|metre)-scale\b", "capability quantification"),
    (r"\b\d+\ ?(km|miles|meter) (detection|range)", "killinchu capability quantification"),
    # FIX (aegis, 2026-09-30): Rosa's Part 2 rule 4 bans "verified trust" about Lambda,
    # but the canonical BANNED list shipped NO pattern for it -- the file the room runs
    # did not enforce the rule its own author wrote. Additive; nothing removed.
    (r"verified\s+trust", "Lambda discipline (Part 2 rule 4: 'verified trust' banned)"),
    # FIX (aegis, 2026-09-30): Part 2 rule 2 is advisory-only/paper-only for szl-quant --
    # never imply performance. Old list only caught the literal "returns of <digit>";
    # bare performance language ("strong returns", "8% returns") passed clean. Additive.
    (r"\b(strong|consistent|superior|market-beating|alpha-generating)\s+returns\b"
     r"|\b\d+(\.\d+)?%\s+(annual|monthly|yearly)?\s*(returns?|yield|gain)\b"
     r"|\breturns?\s+(of|up\s+to)\s+\d", "quant performance claim (Part 2 rule 2)"),
]

def lint(text: str) -> list[str]:
    """Return violations. A draft with violations does not ship."""
    return [f"BANNED: {msg} -> {m.group(0)!r}" for pat, msg in BANNED
            if (m := re.search(pat, text, re.I))]

def factbase() -> dict:
    facts = {"generated": NOW()}
    repos, url = [], "https://api.github.com/orgs/szl-holdings/repos?per_page=100"
    while url:
        r = requests.get(url, timeout=30); repos += r.json()
        url = r.links.get("next", {}).get("url")
    facts["github"] = {"repos": len(repos),
                       "archived": sum(1 for x in repos if x.get("archived"))}
    facts["hf"] = {}
    for kind in ("models", "datasets", "spaces"):
        facts["hf"][kind] = len(requests.get(
            f"https://huggingface.co/api/{kind}?author=SZLHOLDINGS&limit=1000",
            timeout=30).json())
    # FIX (aegis, 2026-09-30): the old sweep ranked MODELS ONLY, so a dataset
    # crown could never surface — it reported chaski (3,070) while the real top
    # artifact is a DATASET, killinchu-osint-corpus (74,157). A 24x undercount
    # of Stephen's estate in every piece of marketing copy. Sweep both kinds.
    ranked = []
    for kind in ("models", "datasets"):
        rows = requests.get(
            f"https://huggingface.co/api/{kind}?author=SZLHOLDINGS&limit=1000",
            timeout=30).json()
        for x in rows:
            ranked.append({"id": x.get("id"), "kind": kind,
                           "downloads": x.get("downloads", 0)})
    top = max(ranked, key=lambda x: x["downloads"]) if ranked else \
        {"id": "UNAVAILABLE", "kind": "none", "downloads": 0}
    facts["hf"]["top"] = {"id": top["id"], "kind": top["kind"],
                          "downloads": top["downloads"],
                          "sweep": "models+datasets"}
    facts["hf"]["downloads"] = {"models": sum(x["downloads"] for x in ranked if x["kind"] == "models"),
                               "datasets": sum(x["downloads"] for x in ranked if x["kind"] == "datasets")}
    facts["hf"]["downloads"]["total"] = facts["hf"]["downloads"]["models"] + facts["hf"]["downloads"]["datasets"]
    return facts

def substack_draft(f: dict, essay_body: str, subjects: list[str]) -> str:
    """A/B subject lines included; fact block injected; linted before return."""
    head = (f"<!-- SUBJECT A: {subjects[0]}\n     SUBJECT B: {subjects[1] if len(subjects)>1 else subjects[0]} -->\n"
            f"# {subjects[0]}\n\n## The estate, this week (fetched {f['generated']})\n\n"
            f"- {f['github']['repos']} GitHub repositories "
            f"({f['github']['archived']} honestly archived)\n"
            f"- {f['hf']['models']} models · {f['hf']['datasets']} datasets · "
            f"{f['hf']['spaces']} Spaces on Hugging Face\n"
            f"- Most-downloaded artifact: {f['hf']['top']['id']} "
            f"({f['hf']['top']['downloads']:,} downloads)\n\n")
    tail = ("\n\n---\n\nEvery number above was fetched from a live API at generation time. "
            "Verify a receipt yourself: https://a-11-oy.com/verify · "
            "Proof registry: https://a11oy.net\n")
    draft = head + essay_body + tail
    if v := lint(draft):
        raise SystemExit("DRAFT BLOCKED BY COMPLIANCE LINTER:\n" + "\n".join(v))
    return draft

if __name__ == "__main__":
    f = factbase()
    (OUT / "factbase.json").write_text(json.dumps(f, indent=2))
    print(json.dumps(f, indent=2))
    print("factbase locked", NOW(), "— draft with substack_draft(f, body, subjects)")
