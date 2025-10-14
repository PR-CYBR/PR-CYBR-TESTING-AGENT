#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
COMMON_HELPERS="${ROOT_DIR}/scripts/runtime/common.sh"

if [[ ! -f "$COMMON_HELPERS" ]]; then
    echo "Missing helper library at $COMMON_HELPERS" >&2
    exit 1
fi

source "$COMMON_HELPERS"

LOG_FILE=${LOG_FILE:-"${ROOT_DIR}/logs/setup.log"}
init_log_file "$LOG_FILE"

STATUS_LOG=()

usage() {
    cat <<USAGE
Usage: $(basename "$0") [options]

Options:
  --skip-tests       Skip executing the repository self-tests.
  --status-only      Only print the most recent status report.
  --help             Display this help message and exit.
USAGE
}

SKIP_TESTS=0
STATUS_ONLY=0

while (($#)); do
    case "$1" in
        --skip-tests)
            SKIP_TESTS=1
            ;;
        --status-only)
            STATUS_ONLY=1
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

broadcast_event 'setup.start' 'Setup workflow initiated.'
log_message "Starting PR-CYBR-TESTING-AGENT setup workflow."

if (( STATUS_ONLY )); then
    print_status_report
    exit 0
fi

missing_deps=()
if ! check_core_dependencies missing_deps; then
    log_message "Missing dependencies detected: ${missing_deps[*]}" "ERROR"
    print_status_report
    broadcast_event 'setup.failed' "Missing dependencies: ${missing_deps[*]}"
    exit 1
fi

if (( ! SKIP_TESTS )); then
    if ! run_python_tests "Repository self-tests"; then
        log_message "Self-tests reported failures." "ERROR"
        print_status_report
        broadcast_event 'setup.failed' 'Self-tests failed. Review logs for details.'
        exit 1
    fi
else
    record_status "SKIP" "Repository self-tests" "Execution skipped by --skip-tests flag."
fi

log_message "Setup workflow completed successfully."
broadcast_event 'setup.complete' 'Setup workflow completed successfully.'
print_status_report
