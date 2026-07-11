#!/usr/bin/env bash

set -euo pipefail
readonly VIOLATION_THRESHOLD=101

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "$SCRIPT_DIR"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "$PROJECT_ROOT"

# ANSI colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly NC='\033[0m'   # No Color

#########################################
# Configuration
#########################################

readonly SCRIPT_NAME="$(basename "$0")"

echo "========================================"
echo " Running pylint"
echo "========================================"

#########################################
# Discover Python files
#########################################

mapfile -t FILES < <(
    find "$PROJECT_ROOT" \
        -type f \
        -name "*.py" \
        ! -path "*/test/*" \
        ! -path "*/tests/*" \
        ! -name "test_*.py"
)

if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "No Python files found."
    exit 0
fi

echo "Python files found : ${#FILES[@]}"
echo

#########################################
# Execute pylint
#########################################

set +e
OUTPUT=$(pylint "${FILES[@]}" 2>&1)
PYLINT_RC=$?
set -e

printf '%s\n' "$OUTPUT"

#########################################
# Build summary
#########################################

read FATAL ERROR WARNING REFACTOR CONVENTION < <(
    awk '
    /: F[0-9][0-9][0-9][0-9]:/ {f++}
    /: E[0-9][0-9][0-9][0-9]:/ {e++}
    /: W[0-9][0-9][0-9][0-9]:/ {w++}
    /: R[0-9][0-9][0-9][0-9]:/ {r++}
    /: C[0-9][0-9][0-9][0-9]:/ {c++}
    END {
        print f+0, e+0, w+0, r+0, c+0
    }' <<< "$OUTPUT"
    )

TOTAL=$((FATAL + ERROR + WARNING + REFACTOR + CONVENTION))
echo
echo "==========================================="
echo "            PYLINT SUMMARY                 "
echo "==========================================="
printf "%-15s : %3d\n" "Fatal" "$FATAL"
printf "%-15s : %3d\n" "Errors" "$ERROR"
printf "%-15s : %3d\n" "Warnings" "$WARNING"
printf "%-15s : %3d\n" "Refactors" "$REFACTOR"
printf "%-15s : %3d\n" "Convention" "$CONVENTION"
echo "-------------------------------------------"
printf "%-15s : %3d\n" "Total Issues" "$TOTAL"
echo "==========================================="

#########################################
# Fail the build
#########################################

if (( TOTAL <= VIOLATION_THRESHOLD )); then
    printf "${GREEN}Found %d violation(s). Allowed threshold: %d.${NC}\n" \
        "$TOTAL" "$VIOLATION_THRESHOLD"
    exit 0
else
    printf "${RED}Found %d violation(s), which exceeds the allowed threshold of %d.${NC}\n" \
        "$TOTAL" "$VIOLATION_THRESHOLD"
    exit 1
fi
