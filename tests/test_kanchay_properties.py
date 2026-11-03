"""Hypothesis property tests for KANCHAY token extraction and the SOURCE.json manifest."""

from __future__ import annotations

import hashlib
import json
import re
import string

import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from szl_brand import kanchay

SOURCE_KEYS = ["name", "version", "base", "layers", "source_commit", "license", "sha256"]
TOKEN_ATOMS = (":root", '[data-surface="dark"]', '[data-surface="light"]')
OTHER_SELECTORS = (
    "body",
    "h1, h2",
    ".card",
    "a:hover",
    ":where(a, button):focus-visible",
    '[data-surface="dim"]',
    ":root .lead",
    "html",
)
# The extracted bundle always starts with the fixed provenance comment.
TOKENS_PREFIX = kanchay.extract_tokens("")[:-1]

blank = st.sampled_from(["", " ", "\n", "\n\n", "\t"])
comment = (
    st.text(string.ascii_letters + string.digits + " -;{}*/", max_size=16)
    .filter(lambda text: "*/" not in text)
    .map(lambda text: f"/* {text} */")
)
separator = st.tuples(blank, st.none() | comment, blank).map(
    lambda parts: parts[0] + (parts[1] or "") + parts[2]
)
value = st.text(
    string.ascii_letters + string.digits + " #%.,()\"'-", min_size=1, max_size=24
).filter(str.strip)
token_name = st.from_regex(r"--[A-Za-z0-9_-]{1,16}", fullmatch=True)
property_name = st.from_regex(r"[a-z][a-z-]{0,15}", fullmatch=True).filter(
    lambda name: name != "color-scheme"
)
token_declaration = st.tuples(token_name, blank, value).map(
    lambda parts: f"{parts[0]}{parts[1]}: {parts[2]}"
) | st.sampled_from(["color-scheme: dark", "color-scheme:light"])
plain_declaration = st.tuples(property_name, value).map(lambda parts: f"{parts[0]}: {parts[1]}")


def _body(declarations: st.SearchStrategy[str]) -> st.SearchStrategy[str]:
    item = st.tuples(st.none() | comment, declarations).map(
        lambda parts: (parts[0] + " " if parts[0] else "") + parts[1]
    )
    return st.tuples(st.lists(item, max_size=4), st.booleans()).map(
        lambda parts: "\n  " + ";\n  ".join(parts[0]) + (";" if parts[1] else "") + "\n"
    )


token_selector = st.tuples(
    st.lists(st.sampled_from(TOKEN_ATOMS), min_size=1, max_size=3),
    st.sampled_from([", ", ",", " , "]),
).map(lambda parts: parts[1].join(parts[0]))
token_rule = st.tuples(token_selector, _body(token_declaration))
plain_rule = st.tuples(st.sampled_from(OTHER_SELECTORS), _body(plain_declaration))
at_rule = st.lists(plain_rule, min_size=1, max_size=2).map(
    lambda nested: (
        "@media (prefers-reduced-motion: reduce)",
        "\n" + "\n".join(f"  {prelude} {{{body}}}" for prelude, body in nested) + "\n",
    )
)
# Each rule is tagged with whether it is a token block that extract_tokens must keep.
tagged_rules = st.lists(
    st.one_of(
        token_rule.map(lambda rule: (*rule, True)),
        plain_rule.map(lambda rule: (*rule, False)),
        at_rule.map(lambda rule: (*rule, False)),
    ),
    max_size=6,
)


def _css(rules: list[tuple[str, str]]) -> str:
    return "\n".join(f"{prelude} {{{body}}}" for prelude, body in rules)


@st.composite
def stylesheets(draw):
    """A well-formed stylesheet as (css, [(prelude, body, is_token), ...]) in source order."""

    parsed = draw(tagged_rules)
    pieces = [draw(separator) + f"{prelude} {{{body}}}" for prelude, body, _token in parsed]
    return "".join(pieces) + draw(separator), parsed


@given(stylesheets())
def test_top_level_blocks_recover_every_rule_in_order(sheet):
    css, parsed = sheet

    assert kanchay._top_level_blocks(css) == [(prelude, body) for prelude, body, _ in parsed]


@given(stylesheets())
def test_extract_tokens_keeps_exactly_the_token_blocks_byte_for_byte(sheet):
    css, parsed = sheet
    kept = [f"{prelude} {{{body}}}" for prelude, body, token in parsed if token]

    assert kanchay.extract_tokens(css) == TOKENS_PREFIX + "\n".join(kept) + "\n"


@given(stylesheets())
def test_extract_tokens_is_idempotent(sheet):
    css, _parsed = sheet
    tokens = kanchay.extract_tokens(css)

    assert kanchay.extract_tokens(tokens) == tokens


@given(st.lists(token_rule, min_size=1, max_size=4), st.integers(min_value=0), plain_declaration)
def test_token_block_with_a_non_token_declaration_fails_closed(token_rules, position, intruder):
    index = position % len(token_rules)
    prelude, body = token_rules[index]
    damaged = [
        *token_rules[:index],
        (prelude, f"{body};\n  {intruder};\n"),
        *token_rules[index + 1 :],
    ]

    with pytest.raises(ValueError, match="non-token declaration"):
        kanchay.extract_tokens(_css(damaged))


@given(stylesheets(), st.sampled_from(["prefix", "suffix", "comment"]))
def test_unbalanced_or_unterminated_css_fails_closed(sheet, damage):
    css, _parsed = sheet
    broken = {"prefix": "}" + css, "suffix": css + "{", "comment": css + "/* open"}[damage]

    with pytest.raises(ValueError, match="unbalanced CSS braces|unterminated CSS comment"):
        kanchay.extract_tokens(broken)


# A top-level comment used to reset the prelude, so ':root /* c */ {--a: 1}' parsed with
# prelude '' and extract_tokens silently dropped the token block.
@given(st.lists(token_rule, min_size=1, max_size=4), st.integers(min_value=0), comment)
@example([(":root", "--a: 1")], 0, "/* c */")
def test_comment_inside_a_selector_is_skipped_like_any_other_comment(token_rules, position, note):
    index = position % len(token_rules)
    prelude, body = token_rules[index]
    commented = [*token_rules[:index], (f"{prelude} {note}", body), *token_rules[index + 1 :]]

    assert kanchay.extract_tokens(_css(commented)) == kanchay.extract_tokens(_css(token_rules))


commits = st.from_regex(r"[0-9a-f]{40}", fullmatch=True)
payloads = st.dictionaries(st.text(min_size=1, max_size=40), st.binary(max_size=64), max_size=8)


@given(payloads, commits)
def test_source_json_pins_every_payload_file_in_manifest_order(payload, commit):
    text = kanchay.render_source_json(payload, commit)
    source = json.loads(text)

    assert text == kanchay.render_source_json(payload, commit)
    assert text == json.dumps(source, indent=2, ensure_ascii=False) + "\n"
    assert list(source) == SOURCE_KEYS
    assert source["version"] == kanchay.VERSION
    assert source["source_commit"] == commit
    assert list(source["sha256"]) == list(payload)
    assert source["sha256"] == {
        path: hashlib.sha256(data).hexdigest() for path, data in payload.items()
    }


@given(
    payloads,
    st.one_of(
        st.text(max_size=48),
        commits.map(str.upper).filter(lambda commit: re.search("[A-F]", commit)),
        commits.map(lambda commit: commit + "\n"),
        commits.map(lambda commit: commit[:39]),
        commits.map(lambda commit: " " + commit),
    ).filter(lambda commit: not re.fullmatch(r"[0-9a-f]{40}", commit)),
)
def test_source_json_refuses_anything_but_an_exact_lowercase_sha(payload, commit):
    with pytest.raises(ValueError, match="source_commit"):
        kanchay.render_source_json(payload, commit)
