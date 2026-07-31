#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf '%s\n' \
    'Usage: scripts/agent-quality-gate.sh [--ci] [--stage]' \
    '' \
    'Runs agent workflow and dependency hygiene checks before commits and merges.' \
    '' \
    'Options:' \
    '  --ci      Skip local branch enforcement for CI on main or pull requests.' \
    '  --stage   Allow an active TODO plan for an intermediate work-branch commit.'
}

ci_mode=0
stage_mode=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --ci)
      ci_mode=1
      ;;
    --stage)
      stage_mode=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

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

if [ "$ci_mode" -eq 0 ]; then
  branch="$(git branch --show-current)"
  if scripts/check-agent-branch.sh --allow-dev "$branch" >/dev/null 2>&1; then
    pass "current branch is allowed: ${branch}"
  else
    fail "current branch is '$branch', expected dev, feature/<slug>, or fix/<slug>"
  fi
else
  pass 'CI mode skips local branch enforcement'
fi

if git diff --check; then
  pass 'unstaged whitespace check'
else
  fail 'unstaged whitespace check'
fi

if git diff --cached --check; then
  pass 'staged whitespace check'
else
  fail 'staged whitespace check'
fi

status_output="$(git status --porcelain)"
if [ -n "$status_output" ]; then
  dirty_details=''
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    index_status="${line:0:1}"
    worktree_status="${line:1:1}"
    if [ "$index_status" = "?" ] && [ "$worktree_status" = "?" ]; then
      dirty_details="${dirty_details}${line}"$'\n'
    elif [ "$worktree_status" != " " ]; then
      dirty_details="${dirty_details}${line}"$'\n'
    fi
  done <<< "$status_output"

  if [ -n "$dirty_details" ]; then
    fail "worktree has unstaged or untracked files: ${dirty_details//$'\n'/; }"
  else
    pass 'worktree has no unstaged or untracked files'
  fi
else
  pass 'worktree is clean'
fi

if [ ! -f TODO.md ]; then
  fail 'TODO.md is missing'
elif [ "$stage_mode" -eq 1 ]; then
  pass 'stage mode allows an active TODO.md plan'
else
  current_task_section="$(
    awk '
      /^## Current Task[[:space:]]*$/ { in_section = 1; next }
      /^## / && in_section { exit }
      in_section { print }
    ' TODO.md
  )"
  active_todo_items="$(
    printf '%s\n' "$current_task_section" |
      grep -E '^[[:space:]]*-[[:space:]]\[[ xX]\]' |
      grep -v -E '^[[:space:]]*-[[:space:]]\[ \][[:space:]]+None\.[[:space:]]*$' || true
  )"
  if [ -n "$active_todo_items" ]; then
    fail 'TODO.md Current Task still contains active checklist items'
  else
    pass 'TODO.md Current Task is empty or summary-only'
  fi
fi

tracked_generated=''
while IFS= read -r path; do
  [ -n "$path" ] || continue
  first_component="${path%%/*}"
  if [ "$path" = "$first_component" ]; then
    case "$path" in
      CMakeCache.txt|cmake_install.cmake|compile_commands.json|install_manifest.txt)
        tracked_generated="${tracked_generated}${path}"$'\n'
        ;;
    esac
  else
    case "$first_component" in
      build*|install*|cmake-build-*|CMakeFiles|Testing|coverage|htmlcov|dist|out|generated)
        tracked_generated="${tracked_generated}${path}"$'\n'
        ;;
    esac
  fi
done < <(git ls-files)

if [ -n "$tracked_generated" ]; then
  fail "generated build/install artifacts are tracked: ${tracked_generated//$'\n'/; }"
else
  pass 'no tracked generated build/install artifacts'
fi

if scripts/check-dependency-hygiene.sh; then
  pass 'dependency hygiene check'
else
  fail 'dependency hygiene check'
fi

if [ -x scripts/test-agent-branch-policy.sh ]; then
  if scripts/test-agent-branch-policy.sh; then
    pass 'agent branch policy regression test'
  else
    fail 'agent branch policy regression test'
  fi
fi

if [ -x scripts/test-install-agent-setup.sh ]; then
  if scripts/test-install-agent-setup.sh; then
    pass 'Codex installer regression test'
  else
    fail 'Codex installer regression test'
  fi
fi

if [ "$failures" -ne 0 ]; then
  printf '\nAgent quality gate failed with %d issue(s).\n' "$failures" >&2
  exit 1
fi

printf '\nAgent quality gate passed.\n'
