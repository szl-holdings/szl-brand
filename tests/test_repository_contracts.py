from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_public_license_claims_match_checked_in_license_and_notice() -> None:
    root_license = read("LICENSE")
    kit_license = read("kit/LICENSE")
    notice = read("NOTICE")
    readme = read("README.md")
    notice_words = " ".join(notice.split())

    assert root_license == kit_license
    assert "Creative Commons Attribution 4.0 International" in root_license
    assert "Creative Commons Attribution 4.0 International License" in notice_words
    assert "Repository content: CC BY 4.0" in readme
    assert "kit/LICENSE" not in readme


def test_contribution_identity_and_license_boundary_are_not_stale() -> None:
    contributing = read("CONTRIBUTING.md")

    assert contributing.startswith("# Contributing to KANCHAY / szl-brand")
    assert "source-available, proprietary software" not in contributing
    assert "Contributing to ouroboros" not in contributing
    assert "LICENSE" in contributing
    assert "NOTICE" in contributing
    assert "external contributors" in contributing.lower()


def test_security_policy_uses_current_doctrine_label() -> None:
    security = read("SECURITY.md")

    assert "Doctrine v11 LOCKED 749/14/163" in security
    assert "Doctrine v7" not in security
    assert "unobserved or unverified control" in security


def test_agent_instructions_do_not_request_privileged_external_workspace_mutation() -> None:
    agents = read("AGENTS.md")

    assert "sudo chmod" not in agents
    assert "sudo mkdir" not in agents
    assert "Do not create, chmod, mount" in agents
    assert "Do not run those legacy scripts in automation" in agents
