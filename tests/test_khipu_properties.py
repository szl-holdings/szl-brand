"""Hypothesis property tests: the KHIPU disclosure validator is total, canonical and fail-closed."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from hypothesis import assume, given
from hypothesis import strategies as st

from szl_brand.khipu import validate_surface

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads(
    (ROOT / "kit" / "contracts" / "khipu-command-system.example.json").read_text(encoding="utf-8")
)
# Every object section of the contract, as (JSON path, error path, required, optional).
SECTIONS = (
    ((), "$", set(EXAMPLE), set()),
    (("source",), "$.source", set(EXAMPLE["source"]), set()),
    (("responsive",), "$.responsive", set(EXAMPLE["responsive"]), set()),
    (("accessibility",), "$.accessibility", set(EXAMPLE["accessibility"]), set()),
    (("executiveBrief",), "$.executiveBrief", set(EXAMPLE["executiveBrief"]), set()),
    (("evidence", 0), "$.evidence[0]", set(EXAMPLE["evidence"][0]), {"observedAt"}),
    (("links",), "$.links", set(EXAMPLE["links"]), set()),
)

# Anything json.loads can return, including NaN and infinities.
json_values = st.recursive(
    st.none() | st.booleans() | st.integers() | st.floats() | st.text(max_size=40),
    lambda children: (
        st.lists(children, max_size=4) | st.dictionaries(st.text(max_size=16), children, max_size=4)
    ),
    max_leaves=24,
)


def _paths(value: object, prefix: tuple = ()) -> list[tuple]:
    paths = [prefix]
    if isinstance(value, dict):
        for key, child in value.items():
            paths.extend(_paths(child, (*prefix, key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_paths(child, (*prefix, index)))
    return paths


EXAMPLE_PATHS = [path for path in _paths(EXAMPLE) if path]


def _at(document: object, path: tuple) -> object:
    for part in path:
        document = document[part]
    return document


def _assert_canonical(errors: object) -> None:
    assert isinstance(errors, list)
    assert all(isinstance(error, str) for error in errors)
    assert errors == sorted(set(errors))


@given(json_values)
def test_validator_is_total_and_canonical_on_any_json_value(document):
    snapshot = copy.deepcopy(document)
    errors = validate_surface(document)

    _assert_canonical(errors)
    assert validate_surface(document) == errors
    if not isinstance(document, dict):
        assert errors == ["$ must be an object"]
    # The validator only reads its input.
    assert json.dumps(document, sort_keys=True) == json.dumps(snapshot, sort_keys=True)


@given(st.sampled_from(EXAMPLE_PATHS), json_values)
def test_any_field_replaced_by_any_json_value_never_crashes(path, replacement):
    document = copy.deepcopy(EXAMPLE)
    parent = _at(document, path[:-1])
    original = parent[path[-1]]
    parent[path[-1]] = replacement

    errors = validate_surface(document)

    _assert_canonical(errors)
    if json.dumps(replacement) == json.dumps(original) and type(replacement) is type(original):
        assert errors == []


@given(st.sampled_from(SECTIONS), st.data())
def test_dropping_a_required_key_is_reported_by_name(section, data):
    path, label, required, _optional = section
    key = data.draw(st.sampled_from(sorted(required)))
    document = copy.deepcopy(EXAMPLE)
    del _at(document, path)[key]

    errors = validate_surface(document)

    _assert_canonical(errors)
    assert f"{label}.{key} is required" in errors


@given(st.sampled_from(SECTIONS), st.text(min_size=1, max_size=24), json_values)
def test_unknown_keys_are_refused_in_every_section(section, key, value):
    path, label, required, optional = section
    assume(key not in required | optional)
    document = copy.deepcopy(EXAMPLE)
    _at(document, path)[key] = value

    errors = validate_surface(document)

    _assert_canonical(errors)
    assert f"{label}.{key} is not allowed" in errors
