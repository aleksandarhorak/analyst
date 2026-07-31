#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf '%s\n' \
    'Usage: scripts/check-agent-branch.sh [--allow-dev] [branch]' \
    '' \
    'Accepts lowercase kebab-case feature/<slug> or fix/<slug> branches.' \
    'With --allow-dev, also accepts dev for merge and merged-state checks.'
}

allow_dev=0
branch=''

while [ "$#" -gt 0 ]; do
  case "$1" in
    --allow-dev)
      allow_dev=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      printf 'Unknown option: %s\n\n' "$1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [ -n "$branch" ]; then
        printf 'Only one branch argument is accepted.\n\n' >&2
        usage >&2
        exit 2
      fi
      branch="$1"
      ;;
  esac
  shift
done

if [ -z "$branch" ]; then
  branch="$(git branch --show-current 2>/dev/null)" || {
    printf 'Not inside a Git repository.\n' >&2
    exit 1
  }
fi

if [[ "$branch" =~ ^(feature|fix)/[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  exit 0
fi

if [ "$allow_dev" -eq 1 ] && [ "$branch" = 'dev' ]; then
  exit 0
fi

if [ "$allow_dev" -eq 1 ]; then
  printf "Invalid branch '%s'; expected dev, feature/<slug>, or fix/<slug>.\n" \
    "$branch" >&2
else
  printf "Invalid work branch '%s'; expected feature/<slug> or fix/<slug>.\n" \
    "$branch" >&2
fi
exit 1
