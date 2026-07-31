#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf '%s\n' \
    'Usage: scripts/check-dependency-hygiene.sh' \
    '' \
    'Checks that required C/C++ dependencies are vendored as pinned GitHub submodules.'
}

while [ "$#" -gt 0 ]; do
  case "$1" in
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
done

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  printf 'FAIL not inside a Git repository\n' >&2
  exit 1
}
cd "$repo_root"

exceptions_file="docs/dependency-exceptions.md"
failures=0

fail() {
  printf 'FAIL %s\n' "$1" >&2
  failures=$((failures + 1))
}

pass() {
  printf 'PASS %s\n' "$1"
}

load_exception_section() {
  local heading="$1"

  [ -f "$exceptions_file" ] || return 0

  awk -v heading="$heading" '
    /^## / {
      in_section = ($0 == "## " heading)
      next
    }
    in_section && /^-/ {
      print
    }
  ' "$exceptions_file" |
    sed -n -E \
      -e 's/^-+[[:space:]]+`([^`]+)`.*/\1/p' \
      -e 's/^-+[[:space:]]+([A-Za-z0-9_.+\/:-]+).*/\1/p' |
    sed -E 's/:$//' |
    grep -Ev '^(None|None\.)$' || true
}

is_allowed() {
  local needle="$1"
  shift

  local value
  for value in "$@"; do
    if [ "$needle" = "$value" ]; then
      return 0
    fi
  done

  return 1
}

scan_files_for_pattern() {
  local description="$1"
  local pattern="$2"
  shift 2

  if [ "$#" -eq 0 ]; then
    pass "$description (no files)"
    return 0
  fi

  if grep -nE "$pattern" "$@"; then
    fail "$description"
  else
    pass "$description"
  fi
}

mapfile -t allowed_find_packages < <(
  load_exception_section 'Allowed Platform/Toolchain Find Packages'
)
mapfile -t allowed_external_paths < <(
  load_exception_section 'Allowed External Paths Without Submodule'
)

mapfile -t cmake_files < <(
  git ls-files |
    while IFS= read -r path; do
      case "$path" in
        CMakeLists.txt|*/CMakeLists.txt|*.cmake)
          printf '%s\n' "$path"
          ;;
      esac
    done
)

mapfile -t repository_scripts < <(
  git ls-files 'scripts/*' |
    grep -v '^scripts/check-dependency-hygiene\.sh$' |
    grep -v '^scripts/install-linux-cpp-tools\.sh$' || true
)

download_shortcuts='FetchContent|ExternalProject_Add|file[[:space:]]*\([[:space:]]*DOWNLOAD'
package_shortcuts='(^|[^A-Za-z0-9_])(PackageKit|pkcon|apt-get|apt|dnf|yum|pacman|zypper|rpm|dpkg|apk|brew|port|choco|scoop|nix-env|guix|vcpkg|conan|curl|wget|unzip|tar)([^A-Za-z0-9_]|$)'
tmp_dependency_paths='/tmp/[^[:space:]]*(dep|dependency|third[-_]?party|external|install|build)'

scan_files_for_pattern \
  'repository CMake has no FetchContent, ExternalProject_Add, or file(DOWNLOAD)' \
  "$download_shortcuts" \
  "${cmake_files[@]}"

scan_files_for_pattern \
  'repository CMake has no package/archive dependency shortcuts' \
  "$package_shortcuts|$tmp_dependency_paths" \
  "${cmake_files[@]}"

scan_files_for_pattern \
  'repository scripts have no package/archive dependency shortcuts outside the toolchain installer' \
  "$package_shortcuts|$tmp_dependency_paths" \
  "${repository_scripts[@]}"

find_package_violations=''
for cmake_file in "${cmake_files[@]}"; do
  while IFS=: read -r line_number line_text; do
    line_without_comment="${line_text%%#*}"
    if [[ "$line_without_comment" =~ find_package[[:space:]]*\([[:space:]]*([A-Za-z0-9_.+-]+) ]]; then
      package_name="${BASH_REMATCH[1]}"
      if ! is_allowed "$package_name" "${allowed_find_packages[@]}"; then
        find_package_violations="${find_package_violations}${cmake_file}:${line_number}: find_package(${package_name}) is not in ${exceptions_file}"$'\n'
      fi
    fi
  done < <(grep -nE 'find_package[[:space:]]*\(' "$cmake_file" || true)
done

if [ -n "$find_package_violations" ]; then
  fail "CMake uses find_package for non-exception dependencies: ${find_package_violations//$'\n'/; }"
else
  pass 'CMake find_package calls are limited to documented platform/toolchain exceptions'
fi

submodule_paths=''
if [ -f .gitmodules ]; then
  submodule_paths="$(
    git config -f .gitmodules --get-regexp '^submodule\..*\.path$' 2>/dev/null |
      awk '{ print $2 }' || true
  )"
fi

submodule_url_violations=''
if [ -f .gitmodules ]; then
  while IFS=' ' read -r _ url; do
    [ -n "${url:-}" ] || continue
    case "$url" in
      https://github.com/*|git@github.com:*)
        ;;
      *)
        submodule_url_violations="${submodule_url_violations}${url}"$'\n'
        ;;
    esac
  done < <(git config -f .gitmodules --get-regexp '^submodule\..*\.url$' 2>/dev/null || true)
fi

if [ -n "$submodule_url_violations" ]; then
  fail "submodule URLs are not GitHub repositories: ${submodule_url_violations//$'\n'/; }"
else
  pass 'submodule URLs are GitHub repositories'
fi

submodule_gitlink_violations=''
while IFS= read -r submodule_path; do
  [ -n "$submodule_path" ] || continue
  mode="$(git ls-files -s -- "$submodule_path" | awk '{ print $1 }' | head -n 1)"
  if [ "$mode" != "160000" ]; then
    submodule_gitlink_violations="${submodule_gitlink_violations}${submodule_path}"$'\n'
  fi
done <<< "$submodule_paths"

if [ -n "$submodule_gitlink_violations" ]; then
  fail "submodule paths are not tracked as Git submodule gitlinks: ${submodule_gitlink_violations//$'\n'/; }"
else
  pass 'submodule paths are tracked as Git submodule gitlinks'
fi

external_paths_file="$(mktemp /tmp/dependency-hygiene-external-paths.XXXXXX)"
trap 'rm -f "$external_paths_file"' EXIT

git ls-files |
  while IFS= read -r path; do
    case "$path" in
      external/*/*)
        rest="${path#external/}"
        name="${rest%%/*}"
        printf 'external/%s\n' "$name"
        ;;
    esac
  done > "$external_paths_file"

if [ "${#cmake_files[@]}" -gt 0 ]; then
  grep -hEo 'external/[A-Za-z0-9._+-]+' "${cmake_files[@]}" >> "$external_paths_file" || true
fi

external_paths="$(sort -u "$external_paths_file")"

missing_submodules=''
while IFS= read -r external_path; do
  [ -n "$external_path" ] || continue
  if is_allowed "$external_path" "${allowed_external_paths[@]}"; then
    continue
  fi
  if ! printf '%s\n' "$submodule_paths" | grep -Fxq "$external_path"; then
    missing_submodules="${missing_submodules}${external_path}"$'\n'
  fi
done <<< "$external_paths"

if [ -n "$missing_submodules" ]; then
  fail "external dependencies are referenced or tracked without .gitmodules entries: ${missing_submodules//$'\n'/; }"
else
  pass 'external dependency paths have matching .gitmodules entries or documented exceptions'
fi

external_ignore_violations=''
mapfile -t gitignore_files < <(
  git ls-files |
    while IFS= read -r path; do
      case "$path" in
        .gitignore|*/.gitignore)
          printf '%s\n' "$path"
          ;;
      esac
    done
)

for gitignore_file in "${gitignore_files[@]}"; do
  line_number=0
  while IFS= read -r line_text || [ -n "$line_text" ]; do
    line_number=$((line_number + 1))
    trimmed="${line_text#"${line_text%%[![:space:]]*}"}"
    trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"

    case "$trimmed" in
      ''|\#*|!*)
        continue
        ;;
    esac

    if [[ "$trimmed" =~ external/([A-Za-z0-9._+-]+) ]]; then
      ignored_path="external/${BASH_REMATCH[1]}"
      if ! is_allowed "$ignored_path" "${allowed_external_paths[@]}"; then
        external_ignore_violations="${external_ignore_violations}${gitignore_file}:${line_number}: ${trimmed}"$'\n'
      fi
    fi
  done < "$gitignore_file"
done

if [ -n "$external_ignore_violations" ]; then
  fail "gitignore hides external dependency directories: ${external_ignore_violations//$'\n'/; }"
else
  pass 'gitignore does not hide required external dependency directories'
fi

if [ "$failures" -ne 0 ]; then
  printf '\nDependency hygiene check failed with %d issue(s).\n' "$failures" >&2
  exit 1
fi

printf '\nDependency hygiene check passed.\n'
