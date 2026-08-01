#!/usr/bin/env python3
"""Validate local documentation links and stable user-guide contracts."""

from __future__ import annotations

from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
DOCS = REPO_ROOT / "docs"
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
EXPECTED_PROMPT_HEADINGS = {
    "Research One Company",
    "Value a Company",
    "Build a Complete Investment Thesis",
    "Analyze Current News or an Earnings Release",
    "Analyze the Macroeconomy",
    "Analyze a Commodity or Futures Contract",
    "Assess Market Behavior Without Guessing Psychology",
    "Review a Portfolio Using Synthetic Data",
    "Review Suitability Without Inventing Client Facts",
    "Plan Trade Execution Without Placing an Order",
    "Verify a Financial Claim at a Historical Cutoff",
    "Request Directional Probabilities",
    "Add or Archive a Watchlist Symbol",
    "Evaluate the Agent",
    "Improve This Repository",
}


def github_slug(heading: str) -> str:
    plain = re.sub(r"[`*_~]", "", heading.strip().casefold())
    plain = re.sub(r"[^\w\- ]", "", plain)
    return re.sub(r"\s+", "-", plain)


def anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    seen: dict[str, int] = {}
    result: set[str] = set()
    for heading in HEADING_RE.findall(text):
        base = github_slug(heading)
        count = seen.get(base, 0)
        seen[base] = count + 1
        result.add(base if count == 0 else f"{base}-{count}")
    return result


def local_target(source: Path, raw_target: str) -> tuple[Path, str | None] | None:
    target = raw_target.strip()
    if target.startswith(("https://", "http://", "mailto:")):
        return None
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    path_text, separator, fragment = target.partition("#")
    target_path = source if not path_text else (source.parent / path_text).resolve()
    return target_path, fragment if separator else None


def main() -> int:
    failures: list[str] = []
    docs = [README, *sorted(DOCS.glob("*.md"))]
    for path in docs:
        if not path.is_file():
            failures.append(f"missing documentation file: {path.relative_to(REPO_ROOT)}")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    readme_text = README.read_text(encoding="utf-8")
    if "do symbols research" not in readme_text:
        failures.append("README lacks the exact do symbols research trigger")
    if len(readme_text.splitlines()) > 180:
        failures.append("README exceeds the 180-line navigation-guide limit")

    prompts = DOCS / "PROMPTS.md"
    prompt_headings = set(HEADING_RE.findall(prompts.read_text(encoding="utf-8")))
    missing_prompts = sorted(EXPECTED_PROMPT_HEADINGS - prompt_headings)
    if missing_prompts:
        failures.append(f"prompt cookbook is missing headings: {missing_prompts}")

    for source in docs:
        text = source.read_text(encoding="utf-8")
        for raw_target in LINK_RE.findall(text):
            resolved = local_target(source, raw_target)
            if resolved is None:
                continue
            target_path, fragment = resolved
            label = f"{source.relative_to(REPO_ROOT)} -> {raw_target}"
            if not target_path.exists():
                failures.append(f"broken local link: {label}")
                continue
            if fragment and target_path.is_file() and target_path.suffix.lower() == ".md":
                if fragment not in anchors(target_path):
                    failures.append(f"broken Markdown anchor: {label}")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    print(
        f"PASS documentation: {len(docs)} files, local links, anchors, "
        f"{len(EXPECTED_PROMPT_HEADINGS)} prompt recipes, and concise README"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
