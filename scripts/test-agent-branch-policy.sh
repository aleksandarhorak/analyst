#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
checker="${script_dir}/check-agent-branch.sh"

fail() {
  printf 'FAIL %s\n' "$1" >&2
  exit 1
}

expect_pass() {
  local description="$1"
  shift
  "$checker" "$@" >/dev/null 2>&1 ||
    fail "${description} was rejected"
}

expect_fail() {
  local description="$1"
  shift
  if "$checker" "$@" >/dev/null 2>&1; then
    fail "${description} was accepted"
  fi
}

expect_pass 'feature branch' feature/tested-delivery
expect_pass 'fix branch' fix/compiler-warning
expect_pass 'dev integration branch' --allow-dev dev
expect_pass 'feature integration branch' --allow-dev feature/tested-delivery
expect_fail 'direct dev work branch' dev
expect_fail 'main branch' --allow-dev main
expect_fail 'empty feature slug' 'feature/'
expect_fail 'nested feature slug' feature/phase/one
expect_fail 'uppercase feature slug' feature/Test
expect_fail 'unsupported branch prefix' chore/tested-delivery

printf 'PASS agent branch policy\n'
