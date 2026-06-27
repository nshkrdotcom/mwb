"""Boundary leak scan for SELF-GROUND terms in generic surfaces.

Scans README.md, docs/, src/, tests/, and pyproject.toml to ensure that
SELF-GROUND terms appear only in allowed locations:
  - src/mwb/adapters/self_ground/
  - tests/adapters/test_self_ground_boundary.py
  - tests/adapters/test_self_ground_ingest.py
  - docs/adapters/self_ground/
  - docs/archive/
  - bounded optional adapter sections in README.md and docs/USAGE.md
  - explicit adapter registry import lines in src/mwb/adapters/registry.py
  - specific named lines in docs/ADAPTERS.md, docs/USAGE.md, docs/buildout/

Non-negotiable: generic source code, generic tests (including
tests/adapters/test_generic_bundle_ingest.py), generic top-level docs, and
default-workflow examples must not use SELF-GROUND identity.

docs/ADAPTERS.md and docs/buildout/ are NOT wholesale-allowed. Every allowed
hit in those files must be a named line or a bounded section.
tests/adapters/ is NOT wholesale-allowed. Only the two SELF-GROUND-specific
adapter test files are exempt; generic adapter tests are scanned.
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

# Directory/file prefixes where SELF-GROUND terms are structurally allowed.
# Do NOT add tests/adapters/ here — only specific SELF-GROUND test files are exempt.
ALLOWED_PREFIXES = (
    "src/mwb/adapters/self_ground/",
    "docs/adapters/self_ground/",
    "docs/archive/",
    # Compliance doc that necessarily documents the boundary policy and scan results.
    "docs/RELEASE_HARDENING_REPORT.md",
)

# Specific test files in tests/adapters/ that are SELF-GROUND-specific and exempt.
# Generic adapter tests (e.g. test_generic_bundle_ingest.py) are NOT listed here
# and therefore ARE scanned by the boundary test.
ALLOWED_TEST_FILE_PATTERNS = (
    "tests/adapters/test_self_ground_boundary.py",
    "tests/adapters/test_self_ground_ingest.py",
)

# ---------------------------------------------------------------------------
# Per-file explicit line allowlists.
#
# These allow specific lines that legitimately mention dogfood-adapter terms
# outside the structurally-allowed prefixes.  Every entry must have a comment
# explaining why it is allowed.
# ---------------------------------------------------------------------------
ALLOWED_LINE_PATTERNS: dict[str, list[str]] = {
    # registry.py imports the SELF-GROUND adapter by name — required.
    "src/mwb/adapters/registry.py": [
        "from mwb.adapters.self_ground.ingest import SelfGroundIngestAdapter",
        "from mwb.adapters.self_ground.commands import register_commands",
    ],
    # USAGE.md QC section references adapter test filenames as commands to run.
    "docs/USAGE.md": [
        "uv run pytest tests/adapters/test_self_ground_boundary.py",
        "uv run pytest tests/adapters/test_self_ground_ingest.py",
        # Optional dogfood section: convenience alias documentation.
        "uv run mwb ingest self-ground /path/to/self-ground/runs/<run-id>",
    ],
    # test_generic_bundle_ingest.py verifies registry completeness, which
    # requires asserting that self-ground is present in the adapter list.
    # These are legitimate test assertions, not generic-surface identity leaks.
    "tests/adapters/test_generic_bundle_ingest.py": [
        'assert set(adapters) >= {"generic-bundle", "self-ground"}',
        'assert "self-ground" in adapter_ids',
    ],
    # ADAPTERS.md: adapter guide that covers both adapters; each allowed line is
    # explicit adapter CLI usage or boundary-rule text in the adapter guide.
    "docs/ADAPTERS.md": [
        "uv run mwb adapters inspect self-ground --json",
        "uv run mwb adapters can-ingest self-ground /path/to/self-ground/runs/<run-id> --json",  # noqa: E501
        "uv run mwb ingest external self-ground /path/to/self-ground/runs/<run-id>",
        "uv run mwb ingest self-ground /path/to/self-ground/runs/<run-id>",
        "| `self-ground`    | optional dogfood adapter | import selected SELF-GROUND run artifacts into generic MWB contracts | no            |",  # noqa: E501
        "| `self-ground`      | optional dogfood adapter                 | import selected external run artifacts into generic MWB artifact contracts | no                                                            |",  # noqa: E501
        "SELF-GROUND is available only as an optional dogfood adapter.",
        "The `ingest self-ground` command is a convenience alias. It routes through the same generic adapter dispatcher as `ingest external self-ground`.",  # noqa: E501
        "This adapter is useful for dogfooding MWB against real mechanistic-interpretability artifacts, but MWB does not depend on SELF-GROUND and is not a SELF-GROUND-specific codebase.",  # noqa: E501
        "SELF-GROUND-specific artifact schemas, filenames, metric mappings, source validation, and run-shape assumptions must remain under:",  # noqa: E501
        "src/mwb/adapters/self_ground/",
        "tests/adapters/test_self_ground_*.py",
        "docs/adapters/self_ground/",
        "Generic docs, generic tests, and core modules must not use SELF-GROUND terminology as default product identity.",  # noqa: E501
        "SELF-GROUND terms are allowed only in:",
        "bounded optional adapter sections in README.md and docs/USAGE.md",
    ],
    # buildout/README.md references adapter test filenames for the QC checklist
    # and lists the allowed-path rules verbatim.
    "docs/buildout/README.md": [
        "# See tests/adapters/test_self_ground_boundary.py for the exact terms and",
        "uv run pytest tests/adapters/test_self_ground_boundary.py -v",
        "uv run pytest tests/adapters/test_self_ground_boundary.py",
        "uv run pytest tests/adapters/test_self_ground_ingest.py",
        "src/mwb/adapters/self_ground/",
        "tests/adapters/test_self_ground_*.py",
        "docs/adapters/self_ground/",
    ],
}

# Allowed heading-delimited sections within files that are otherwise scanned.
# Only add an entire section here when there is no practical alternative to
# enumerating individual lines.
ALLOWED_SECTIONS = {
    "README.md": ["## Optional Dogfood Adapter: SELF-GROUND"],
    "docs/USAGE.md": ["## Optional Dogfood Adapter"],
}

SCAN_ROOTS = ["README.md", "docs", "src", "tests", "pyproject.toml"]

# ---------------------------------------------------------------------------
# Regression patterns — these must NEVER appear in active docs outside
# bounded sections, regardless of whether they are in FORBIDDEN.
# ---------------------------------------------------------------------------
_DOC_REGRESSION_PATTERNS = [
    "uv run mwb init --name self-ground",
    "Typical SELF-GROUND dogfood loop",
    "/home/home/",
    "e004_specificity_rescue_matrix",
    "run_self_ground",
    "negation_phase3_calibrated",
    "phase3_calibrated",
]

_ACTIVE_DOCS = [
    ("README.md", "README.md"),
    ("docs/USAGE.md", "docs/USAGE.md"),
    ("docs/ADAPTERS.md", "docs/ADAPTERS.md"),
    ("docs/buildout/README.md", "docs/buildout/README.md"),
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


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
    # USAGE.md stripped of the optional dogfood section must contain no self-ground
    # terms — the generic Adapter Registry section must be SELF-GROUND-free.
    # Filter out the individual named-allowed lines before checking, since those
    # lines (e.g. QC test filenames) are intentionally present.
    usage_allowed_lines = set(ALLOWED_LINE_PATTERNS.get("docs/USAGE.md", []))
    stripped_usage = _strip_allowed_sections("docs/USAGE.md", usage)
    usage_non_allowed = "\n".join(
        line for line in stripped_usage.splitlines()
        if line.strip() not in usage_allowed_lines
    )
    for term in ("self-ground", "SELF-GROUND", "self_ground"):
        assert term not in usage_non_allowed, (
            f"docs/USAGE.md contains {term!r} outside the Optional Dogfood Adapter section"
        )


def test_active_docs_do_not_contain_forbidden_default_identity_patterns() -> None:
    """Active docs must not contain forbidden dogfood/default identity patterns.

    This is a regression guard. Each pattern is checked after stripping allowed
    sections so that legitimate bounded sections do not trigger false positives.
    """
    failures: list[str] = []
    for rel_key, rel_path in _ACTIVE_DOCS:
        doc_path = ROOT / rel_path
        if not doc_path.exists():
            continue
        text = _strip_allowed_sections(rel_key, doc_path.read_text(encoding="utf-8"))
        for pattern in _DOC_REGRESSION_PATTERNS:
            if pattern in text:
                failures.append(f"{rel_path}: contains forbidden pattern: {pattern!r}")
    assert not failures, "\n".join(failures)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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
    return relative.startswith(ALLOWED_PREFIXES) or relative in ALLOWED_TEST_FILE_PATTERNS


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
