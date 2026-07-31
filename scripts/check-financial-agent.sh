#!/usr/bin/env bash
set -euo pipefail

failures=0

fail() {
  printf 'FAIL %s\n' "$1" >&2
  failures=$((failures + 1))
}

pass() {
  printf 'PASS %s\n' "$1"
}

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  printf 'FAIL not inside a Git repository\n' >&2
  exit 1
}
cd "$repo_root"

required_skills=(
  technical-research
  implementation-planning
  git-tested-delivery
  acquire-point-in-time-financial-data
  verify-financial-evidence
  analyze-company-fundamentals
  value-company-and-forecast
  calibrate-financial-forecasts
  analyze-macroeconomy
  analyze-news-catalysts
  analyze-market-behavior
  research-symbol-watchlist
  plan-trade-execution
  manage-portfolio-risk
  build-investment-thesis
  check-broker-suitability
  evaluate-financial-agent
)

for skill in "${required_skills[@]}"; do
  skill_file=".codex/skills/${skill}/SKILL.md"
  metadata_file=".codex/skills/${skill}/agents/openai.yaml"

  if [ ! -f "$skill_file" ]; then
    fail "required skill is missing: ${skill}"
    continue
  fi
  if ! grep -Fqx "name: ${skill}" "$skill_file"; then
    fail "skill frontmatter name is invalid: ${skill}"
  fi
  if [ ! -f "$metadata_file" ]; then
    fail "skill UI metadata is missing: ${skill}"
  elif ! grep -Fq "\$${skill}" "$metadata_file"; then
    fail "skill default prompt does not name \$${skill}"
  fi
done
pass 'required financial and development skills inspected'

forbidden_skills=(
  cpp-architecture-review
  cpp-build-fix-loop
  cpp-cmake-project-setup
  cpp-dependency-submodules
  cpp-linux-toolchain-quality
  cpp-performance-benchmark
  cpp-performance-optimization
  cpp-sanitizer-validation
  tbb-concurrency
)

for skill in "${forbidden_skills[@]}"; do
  if [ -e ".codex/skills/${skill}" ]; then
    fail "removed development skill still exists: ${skill}"
  fi
done
pass 'removed development skill paths inspected'

while IFS= read -r skill_dir; do
  skill="${skill_dir##*/}"
  found=0
  for expected in "${required_skills[@]}"; do
    if [ "$skill" = "$expected" ]; then
      found=1
      break
    fi
  done
  if [ "$found" -eq 0 ]; then
    fail "unreviewed skill directory is present: ${skill}"
  fi
done < <(find .codex/skills -mindepth 1 -maxdepth 1 -type d | sort)
pass 'skill inventory inspected'

stale_policy=''
while IFS= read -r path; do
  [ -n "$path" ] || continue
  if matches="$(grep -En 'C\+\+|CMake|TBB|cpp-' "$path" || true)" &&
     [ -n "$matches" ]; then
    stale_policy="${stale_policy}${path}: ${matches}"$'\n'
  fi
done < <(printf '%s\n' AGENTS.md MEMORY.md; find .codex/skills -type f | sort)

if [ -n "$stale_policy" ]; then
  fail "stale development-language policy remains: ${stale_policy//$'\n'/; }"
else
  pass 'no stale development-language policy remains in active instructions'
fi

manifest='research/financial-analyst-agent/papers/manifest.md'
if [ ! -f "$manifest" ]; then
  fail 'financial research paper manifest is missing'
else
  for lane in T C E N; do
    count="$(grep -Ec "^### ${lane}[0-9]+:" "$manifest" || true)"
    if [ "$count" -lt 10 ]; then
      fail "research lane ${lane} has ${count} papers; expected at least 10"
    else
      pass "research lane ${lane} has ${count} papers"
    fi
  done

  source_count="$(grep -Ec '^- \*\*Source:\*\* https://' "$manifest" || true)"
  review_count="$(grep -Ec 'reviewed:' "$manifest" || true)"
  if [ "$source_count" -lt 40 ]; then
    fail "paper manifest has only ${source_count} stable source entries"
  else
    pass "paper manifest has ${source_count} stable source entries"
  fi
  if [ "$review_count" -lt 40 ]; then
    fail "paper manifest has only ${review_count} full-review confirmations"
  else
    pass "paper manifest has ${review_count} full-review confirmations"
  fi
fi

behavior_manifest='research/market-behavior/papers/manifest.md'
if [ ! -f "$behavior_manifest" ]; then
  fail 'market-behavior paper manifest is missing'
else
  behavior_count="$(grep -Ec '^## B[0-9]+:' "$behavior_manifest" || true)"
  behavior_sources="$(grep -Ec '^- \*\*Source:\*\* https://' "$behavior_manifest" || true)"
  behavior_reviews="$(grep -Ec 'full text reviewed: yes' "$behavior_manifest" || true)"
  if [ "$behavior_count" -lt 10 ] || [ "$behavior_sources" -lt 10 ] ||
     [ "$behavior_reviews" -lt 10 ]; then
    fail "market-behavior research is incomplete: ${behavior_count} papers, ${behavior_sources} sources, ${behavior_reviews} reviews"
  else
    pass "market-behavior research has ${behavior_count} fully sourced and reviewed papers"
  fi
fi

if python3 scripts/check-symbol-research.py; then
  pass 'symbol research workflow integrity'
else
  fail 'symbol research workflow integrity check failed'
fi

if python3 scripts/test-financial-data.py; then
  pass 'point-in-time financial data adapter regressions'
else
  fail 'point-in-time financial data adapter regressions failed'
fi

if python3 scripts/test-financial-evals.py; then
  pass 'executable financial-agent evaluation regressions'
else
  fail 'executable financial-agent evaluation regressions failed'
fi

if python3 scripts/test-forecast-calibration.py; then
  pass 'forecast ledger and calibration regressions'
else
  fail 'forecast ledger and calibration regressions failed'
fi

for phrase in 'point-in-time' 'Never promise returns' 'does not grant authority to place orders'; do
  if grep -Fq "$phrase" AGENTS.md; then
    pass "core guardrail is present: ${phrase}"
  else
    fail "core guardrail is missing: ${phrase}"
  fi
done

if [ "$failures" -ne 0 ]; then
  printf '\nFinancial agent check failed with %d issue(s).\n' "$failures" >&2
  exit 1
fi

printf '\nFinancial agent check passed.\n'
