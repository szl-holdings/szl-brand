<!-- Replace every {{PLACEHOLDER}}. Remove this comment before publication. -->

<div align="center">

<img src="./docs/assets/repository-hero.svg"
     alt="{{PROJECT_NAME}} - {{ONE_SENTENCE_OUTCOME}}"
     width="100%" />

# {{PROJECT_NAME}}

{{ONE_SENTENCE_OUTCOME}}

[**Use the product**]({{PRODUCT_URL}}) ·
[**Read the docs**]({{DOCUMENTATION_URL}}) ·
[**Inspect evidence**]({{EVIDENCE_URL}})

</div>

## Executive brief

| Question | Answer |
| --- | --- |
| Category | {{CATEGORY}} |
| Primary user | {{PRIMARY_USER}} |
| Outcome | {{OUTCOME}} |
| Current state | **{{OPERATIONAL_STATE}}** — [source]({{STATUS_SOURCE_URL}}), observed {{OBSERVED_AT}} |
| Evidence class | **{{EVIDENCE_CLASS}}** — {{EVIDENCE_SCOPE}} |
| Boundary | {{IMPORTANT_BOUNDARY}} |

Evidence class and operational state are separate. A reachable service does not
establish model quality, safety, compliance, or authorization.

## Why it exists

{{PROBLEM_AND_CONSEQUENCE_IN_TWO_TO_FOUR_SENTENCES}}

## What it changes

- **{{CAPABILITY_ONE}}:** {{OUTCOME_ONE}}
- **{{CAPABILITY_TWO}}:** {{OUTCOME_TWO}}
- **{{CAPABILITY_THREE}}:** {{OUTCOME_THREE}}

## Quickstart

Prerequisites: {{PREREQUISITES}}.

```{{SHELL_LANGUAGE}}
{{INSTALL_COMMAND}}
{{RUN_COMMAND}}
```

Expected result:

```text
{{EXPECTED_OUTPUT}}
```

The quickstart must be tested from a clean environment and finish in less than
ten minutes. Continue with [{{FIRST_REAL_TASK}}]({{FIRST_REAL_TASK_URL}}).

## Architecture and trust boundary

```text
{{INPUT}} -> {{POLICY_OR_CORE}} -> {{BOUNDED_OUTPUT}} -> {{EVIDENCE}}
```

| Boundary | Responsibility | Failure behavior |
| --- | --- | --- |
| `{{BOUNDARY_ONE}}` | {{RESPONSIBILITY_ONE}} | {{FAILURE_ONE}} |
| `{{BOUNDARY_TWO}}` | {{RESPONSIBILITY_TWO}} | {{FAILURE_TWO}} |
| `{{BOUNDARY_THREE}}` | {{RESPONSIBILITY_THREE}} | {{FAILURE_THREE}} |

## Verification

```{{SHELL_LANGUAGE}}
{{TEST_COMMAND}}
{{LINT_COMMAND}}
{{BUILD_OR_TYPECHECK_COMMAND}}
```

Record supported versions, expected checks, and unavailable checks. Bind release
artifacts to an immutable source revision.

## Evidence disclosure

If the named source cannot be inspected, publish **UNAVAILABLE** rather than a
cached, empty, zero, or assumed-success state.

<details>
<summary><strong>{{CLAIM}}</strong> — {{EVIDENCE_CLASS}} / {{OPERATIONAL_STATE}}</summary>

- Source: [{{SOURCE_LABEL}}]({{SOURCE_URL}})
- Observed: {{OBSERVED_AT_OR_NOT_APPLICABLE}}
- Scope: {{SCOPE}}
- Limitations: {{LIMITATIONS}}

</details>

## Limits and non-goals

- {{LIMIT_ONE}}
- {{LIMIT_TWO}}
- {{NON_GOAL}}

## Security, support, and license

- [Security policy]({{SECURITY_URL}})
- [Support]({{SUPPORT_URL}})
- [Contributing]({{CONTRIBUTING_URL}})
- [Changelog]({{CHANGELOG_URL}})
- License: {{LICENSE_SENTENCE_MATCHING_THE_ACTUAL_FILE}}

---

[SZL Holdings](https://github.com/szl-holdings) ·
[Documentation](https://holdings.a-11-oy.com/docs-site/) ·
[Evidence](https://a11oy.net) ·
[Models and data](https://huggingface.co/SZLHOLDINGS)
