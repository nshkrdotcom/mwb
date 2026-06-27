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

ALLOWED_FILES = {
    "README.md": "public optional adapter section",
    "docs/USAGE.md": "usage optional adapter section",
    "src/mwb/adapters/__init__.py": "adapter package export",
    "src/mwb/adapters/registry.py": "registered adapter loading boundary",
}

SCAN_ROOTS = ["README.md", "docs", "src", "tests", "pyproject.toml"]


def test_self_ground_terms_do_not_appear_in_generic_surfaces() -> None:
    leaks: list[str] = []
    for path in _scan_files():
        relative = path.relative_to(ROOT).as_posix()
        if _is_allowed(relative):
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FORBIDDEN.search(line):
                leaks.append(f"{relative}:{line_number}: {line.strip()}")

    assert not leaks, "\n".join(leaks)


def test_readme_and_usage_frame_self_ground_as_optional_adapter_only() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    usage = (ROOT / "docs" / "USAGE.md").read_text(encoding="utf-8")

    assert "## Optional Dogfood Adapter: SELF-GROUND" in readme
    assert "MWB does not depend on SELF-GROUND" in readme
    assert "SELF-GROUND is available only as an optional dogfood adapter" in usage


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


def _is_allowed(relative: str) -> bool:
    if relative in ALLOWED_FILES:
        return True
    return relative.startswith(ALLOWED_PREFIXES)
