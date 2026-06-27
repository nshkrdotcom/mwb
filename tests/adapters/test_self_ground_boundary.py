"""Boundary leak scan for SELF-GROUND terms in generic surfaces.

Scans README.md, docs/, src/, tests/, and pyproject.toml to ensure that
SELF-GROUND terms appear only in allowed locations:
  - src/mwb/adapters/self_ground/
  - tests/adapters/test_self_ground_*.py
  - docs/adapters/self_ground/
  - docs/archive/
  - docs/ADAPTERS.md  (adapter docs explicitly cover both adapters)
  - docs/buildout/    (build plan references the scan patterns themselves)
  - bounded optional adapter sections in README.md and docs/USAGE.md
  - explicit adapter registry import lines in registry.py
  - explicit backward-compatibility tests

Non-negotiable: generic source code, generic tests, generic top-level docs, and
default-workflow examples must not use SELF-GROUND identity.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN = re.compile(
    "|".join(
        re.escape(term)
        for term in [
            "SELF-GROUND",
            "self-ground",
            "self_ground",
            "E004",
            "e004_specificity_rescue_matrix",
            "run_self_ground",
            "/self-ground",
            "ml_research/self-ground",
            "negation_phase3",
            "phase3_calibrated",
        ]
    )
)

# Files / directory prefixes where SELF-GROUND terms are structurally allowed.
ALLOWED_PREFIXES = (
    "src/mwb/adapters/self_ground/",
    "tests/adapters/",           # all adapter tests, including boundary/ingest
    "docs/adapters/self_ground/",
    "docs/archive/",
    "docs/ADAPTERS.md",          # adapter guide covers both adapters by design
    "docs/buildout/",            # build plan references scan patterns
)

# Lines that are allowed even when the file is not fully covered by ALLOWED_PREFIXES.
ALLOWED_LINE_PATTERNS = {
    "src/mwb/adapters/registry.py": [
        "from mwb.adapters.self_ground.ingest import SelfGroundIngestAdapter",
        "from mwb.adapters.self_ground.commands import register_commands",
    ],
    # QC section of USAGE.md lists adapter test filenames as commands to run.
    "docs/USAGE.md": [
        "uv run pytest tests/adapters/test_self_ground_boundary.py",
        "uv run pytest tests/adapters/test_self_ground_ingest.py",
    ],
}

# Allowed heading-delimited sections within files that are otherwise scanned.
# Scanning strips the content between these headings and the next ## heading.
ALLOWED_SECTIONS = {
    "README.md": ["## Optional Dogfood Adapter: SELF-GROUND"],
    "docs/USAGE.md": [
        "## Optional Dogfood Adapter",
        "## Adapter Registry",   # legitimately lists both adapters side-by-side
    ],
}

SCAN_ROOTS = ["README.md", "docs", "src", "tests", "pyproject.toml"]

# Patterns that must NOT appear in README.md outside allowed sections.
README_REGRESSION_PATTERNS = [
    "uv run mwb init --name self-ground",
    "Typical SELF-GROUND dogfood loop",
    "/home/home/",
    "e004_specificity_rescue_matrix",
]


def test_self_ground_terms_do_not_appear_in_generic_surfaces() -> None:
    leaks: list[str] = []
    for path in _scan_files():
        relative = path.relative_to(ROOT).as_posix()
        if _is_allowed_path(relative):
            continue
        text = _strip_allowed_sections(relative, path.read_text(encoding="utf-8"))
        for line_number, line in enumerate(text.splitlines(), 1):
            if _is_allowed_line(relative, line):
                continue
            if FORBIDDEN.search(line):
                leaks.append(f"{relative}:{line_number}: {line.strip()}")

    assert not leaks, "\n".join(leaks)


def test_readme_and_usage_frame_self_ground_as_optional_adapter_only() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    usage = (ROOT / "docs" / "USAGE.md").read_text(encoding="utf-8")

    assert "## Optional Dogfood Adapter: SELF-GROUND" in readme
    assert "MWB does not depend on SELF-GROUND" in readme
    assert "SELF-GROUND is available only as an optional dogfood adapter" in usage
    assert "SELF-GROUND" not in _strip_allowed_sections("README.md", readme)
    assert "SELF-GROUND" not in _strip_allowed_sections("docs/USAGE.md", usage)


def test_readme_does_not_contain_regression_identities() -> None:
    """README outside the optional adapter section must not use these patterns."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    stripped = _strip_allowed_sections("README.md", readme)

    failures = [p for p in README_REGRESSION_PATTERNS if p in stripped]
    assert not failures, (
        f"README contains forbidden patterns outside allowed sections: {failures}"
    )


def _scan_files() -> list[Path]:
    files: list[Path] = []
    for entry in SCAN_ROOTS:
        path = ROOT / entry
        if path.is_file():
            files.append(path)
            continue
        files.extend(
            child
            for child in path.rglob("*")
            if child.is_file()
            and child.suffix in {".md", ".py", ".toml", ".yaml", ".yml", ".json"}
        )
    return sorted(files)


def _is_allowed_path(relative: str) -> bool:
    return relative.startswith(ALLOWED_PREFIXES)


def _is_allowed_line(relative: str, line: str) -> bool:
    return line.strip() in ALLOWED_LINE_PATTERNS.get(relative, [])


def _strip_allowed_sections(relative: str, text: str) -> str:
    allowed_headings = ALLOWED_SECTIONS.get(relative, [])
    if not allowed_headings:
        return text
    lines = text.splitlines()
    output: list[str] = []
    skipping = False
    for line in lines:
        if any(line.strip() == heading for heading in allowed_headings):
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            output.append(line)
    return "\n".join(output)
