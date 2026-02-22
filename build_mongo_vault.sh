#!/usr/bin/env bash

# ============================================================
#   🍃 MongoVault — Clean & Build Pipeline
# ============================================================

set -euo pipefail

# ─── Terminal Styling ──────────────────────────────────────
RESET="\033[0m"
BOLD="\033[1m"
DIM="\033[2m"
GREEN="\033[32m"
YELLOW="\033[33m"
CYAN="\033[36m"
RED="\033[31m"
BLUE="\033[34m"
MAGENTA="\033[35m"
BG_GREEN="\033[42m"
BG_RED="\033[41m"
BLACK="\033[30m"
WHITE="\033[37m"

# ─── Global State ──────────────────────────────────────────
TOTAL_STEPS=2
CURRENT_STEP=0
BUILD_START_TIME=$(date +%s)
LOG_FILE="mongovault-build-$(date '+%Y%m%d_%H%M%S').log"
ERRORS_ENCOUNTERED=0

# ─── Logging ───────────────────────────────────────────────
log() {
  echo -e "$(date '+%H:%M:%S') | $*" | tee -a "$LOG_FILE"
}

divider() {
  echo -e "${DIM}${CYAN}────────────────────────────────────────────────────────${RESET}" | tee -a "$LOG_FILE"
}

step_success() {
  echo -e "${BG_GREEN}${BLACK} ✔ SUCCESS ${RESET} $1"
}

step_failure() {
  echo -e "${BG_RED}${WHITE} ✘ FAILED ${RESET} $1"
  ERRORS_ENCOUNTERED=$((ERRORS_ENCOUNTERED+1))
}

run_cmd() {
  local cmd="$1"
  log "Running: $cmd"
  if eval "$cmd" >> "$LOG_FILE" 2>&1; then
    return 0
  else
    return 1
  fi
}

format_elapsed() {
  local secs="$1"
  if (( secs < 60 )); then
    echo "${secs}s"
  else
    echo "$(( secs / 60 ))m $(( secs % 60 ))s"
  fi
}

build_summary() {
  local end=$(date +%s)
  local total=$(( end - BUILD_START_TIME ))

  echo ""
  divider
  echo -e "${BOLD}${MAGENTA}BUILD SUMMARY${RESET}"
  divider
  echo -e "Elapsed: $(format_elapsed $total)"
  echo -e "Log File: ${LOG_FILE}"
  echo ""

  if [[ "$ERRORS_ENCOUNTERED" -eq 0 ]]; then
    echo -e "${BG_GREEN}${BLACK} BUILD COMPLETED SUCCESSFULLY ${RESET}"
  else
    echo -e "${BG_RED}${WHITE} BUILD FINISHED WITH ERRORS ${RESET}"
  fi
}

clear

echo -e "${BOLD}${GREEN}"
echo "🍃 MongoVault — Clean & Build"
echo -e "${RESET}"

log "Build started"
echo ""

# ============================================================
# STEP 1 — CLEAN
# ============================================================

CURRENT_STEP=1
echo -e "${BOLD}${YELLOW}STEP 1/${TOTAL_STEPS} — Cleaning previous artifacts${RESET}"
divider

CMD="rm -rf build && rm -rf dist && rm -f MongoVault.spec"

if run_cmd "$CMD"; then
  step_success "Previous build artifacts removed."
else
  step_failure "Failed cleaning artifacts."
fi

echo ""

# ============================================================
# STEP 2 — BUILD WITH PYINSTALLER
# ============================================================

CURRENT_STEP=2
echo -e "${BOLD}${YELLOW}STEP 2/${TOTAL_STEPS} — Building macOS App${RESET}"
divider

if [[ ! -f version.txt ]]; then
  echo -e "${RED}version.txt not found!${RESET}"
  exit 1
fi

VERSION=$(cat version.txt | tr -d '[:space:]')
log "Detected Version: ${VERSION}"

CMD="pyinstaller \
  --windowed \
  --noconfirm \
  --name MongoVault \
  --icon assets/icon.icns \
  --osx-bundle-identifier com.yourname.mongovault \
  --add-data \"version.txt:.\" \
  run.py"

if run_cmd "$CMD"; then
  step_success "Application built → dist/MongoVault.app"
else
  step_failure "PyInstaller build failed."
fi

echo ""

# ============================================================
# FINAL SUMMARY
# ============================================================

build_summary
exit "$ERRORS_ENCOUNTERED"