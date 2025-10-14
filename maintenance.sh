#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
COMMON_HELPERS="${ROOT_DIR}/scripts/runtime/common.sh"

if [[ ! -f "$COMMON_HELPERS" ]]; then
    echo "Missing helper library at $COMMON_HELPERS" >&2
    exit 1
fi

source "$COMMON_HELPERS"

LOG_FILE=${LOG_FILE:-"${ROOT_DIR}/logs/maintenance.log"}
init_log_file "$LOG_FILE"

STATUS_LOG=()

usage() {
    cat <<USAGE
Usage: $(basename "$0") [options]

Options:
  --skip-tests    Skip executing repository test suites.
  --quick         Run only lightweight health checks.
  --help          Display this help message and exit.
USAGE
}

SKIP_TESTS=0
QUICK_MODE=0

while (($#)); do
    case "$1" in
        --skip-tests)
            SKIP_TESTS=1
            ;;
        --quick)
            QUICK_MODE=1
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
    esac
    shift
done

broadcast_event 'maintenance.start' 'Maintenance workflow initiated.'
log_message "Starting PR-CYBR-TESTING-AGENT maintenance workflow."

missing_deps=()
if ! check_core_dependencies missing_deps; then
    log_message "Missing dependencies detected: ${missing_deps[*]}" "ERROR"
fi

pip_health_check || true

if (( ! SKIP_TESTS )) && (( ! QUICK_MODE )); then
    if ! run_python_tests "Scheduled maintenance self-tests"; then
        log_message "Scheduled self-tests encountered failures." "ERROR"
    fi
else
    reason="Skipped by flag"
    if (( QUICK_MODE )); then
        reason="Skipped in --quick mode"
    fi
    record_status "SKIP" "Scheduled maintenance self-tests" "${reason}."
fi

if command -v git >/dev/null 2>&1; then
    branch=$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    changes=$(git -C "$ROOT_DIR" status --short 2>/dev/null | wc -l)
    record_status "INFO" "Git Workspace" "Branch ${branch}, ${changes} tracked change(s)."
else
    record_status "WARN" "Git Workspace" "git not available; unable to summarize repository status."
fi

print_status_report

if (( ${#missing_deps[@]} )); then
    broadcast_event 'maintenance.warn' "Missing dependencies: ${missing_deps[*]}"
else
    broadcast_event 'maintenance.complete' 'Maintenance workflow finished.'
fi
