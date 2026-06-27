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
        ]
    )
)

ALLOWED_PREFIXES = (
    "src/mwb/adapters/self_ground/",
    "tests/adapters/",
    "docs/adapters/self_ground/",
    "docs/archive/",
)

ALLOWED_LINE_PATTERNS = {
    "src/mwb/adapters/registry.py": [
        "from mwb.adapters.self_ground.ingest import SelfGroundIngestAdapter",
        "from mwb.adapters.self_ground.commands import register_commands",
    ],
}

ALLOWED_SECTIONS = {
    "README.md": ["## Optional Dogfood Adapter: SELF-GROUND"],
    "docs/USAGE.md": ["## Optional Dogfood Adapter"],
}

SCAN_ROOTS = ["README.md", "docs", "src", "tests", "pyproject.toml"]


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
            if child.is_file() and child.suffix in {".md", ".py", ".toml", ".yaml", ".yml", ".json"}
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
