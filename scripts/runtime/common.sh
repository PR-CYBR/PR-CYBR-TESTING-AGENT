#!/usr/bin/env bash

# Shared helpers for setup and maintenance workflows.
# These utilities borrow concepts from scripts/local_setup.sh by providing
# structured logging, dependency validation, and status reporting.

# shellcheck disable=SC2034
STATUS_LOG=()

init_log_file() {
    local logfile=$1
    local logdir
    logdir=$(dirname "$logfile")
    mkdir -p "$logdir"
    touch "$logfile"
}

log_message() {
    local message=$1
    local level=${2:-INFO}
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local formatted="${timestamp} [${level}] ${message}"
    echo "$formatted"
    if [[ -n "${LOG_FILE:-}" ]]; then
        echo "$formatted" >>"$LOG_FILE"
    fi
}

record_status() {
    local status=$1
    local label=$2
    local detail=${3:-}
    STATUS_LOG+=("${status}|${label}|${detail}")
}

print_status_report() {
    log_message "---- Status Report ----"
    printf '%-8s | %-30s | %s\n' "STATUS" "STEP" "DETAIL"
    printf '%s\n' "--------------------------------------------------------------"
    local entry status label detail
    for entry in "${STATUS_LOG[@]}"; do
        IFS='|' read -r status label detail <<<"$entry"
        printf '%-8s | %-30s | %s\n' "$status" "$label" "$detail"
    done
}

emit_event() {
    local stream=$1
    local event=$2
    local message=$3
    local url=""

    case "$stream" in
        codex)
            url=${CODEX_EVENT_STREAM_URL:-${CODEX_EVENT_STREAM:-}}
            ;;
        agentkit)
            url=${AGENTKIT_EVENT_STREAM_URL:-${AGENTKIT_EVENT_STREAM:-}}
            ;;
        *)
            log_message "Unknown event stream '${stream}', skipping emit." "WARN"
            return 0
            ;;
    esac

    if [[ -z "$url" ]]; then
        log_message "${stream^} event '${event}': ${message}" "DEBUG"
        return 0
    fi

    if ! command -v curl >/dev/null 2>&1; then
        log_message "curl is unavailable; cannot publish '${event}' to ${stream}." "WARN"
        return 0
    fi

    local sanitized_message=${message//\"/\\\"}
    local payload
    payload=$(printf '{"event":"%s","message":"%s","timestamp":"%s"}' \
        "$event" "$sanitized_message" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')")

    if ! curl -sf -X POST "$url" -H 'Content-Type: application/json' -d "$payload" >/dev/null; then
        log_message "Failed to emit '${event}' to ${stream} at ${url}." "WARN"
    fi
}

broadcast_event() {
    local event=$1
    local message=$2
    emit_event codex "$event" "$message"
    emit_event agentkit "$event" "$message"
}

check_command_presence() {
    local command=$1
    local label=$2
    local remediation=$3
    if command -v "$command" >/dev/null 2>&1; then
        record_status "PASS" "$label" "${command} available."
        return 0
    fi
    record_status "FAIL" "$label" "$remediation"
    return 1
}

check_core_dependencies() {
    local -n missing_ref=$1
    missing_ref=()

    log_message "Validating required tooling..."
    broadcast_event 'dependencies.start' 'Validating required runtime dependencies.'

    check_command_presence git "Git" "Install Git to manage repository clones." || missing_ref+=("git")
    check_command_presence python3 "Python 3" "Install Python 3.8+ to execute agent tooling." || missing_ref+=("python3")

    if command -v pip3 >/dev/null 2>&1 || python3 -m pip --version >/dev/null 2>&1; then
        record_status "PASS" "Python Package Manager" "pip is available."
    else
        record_status "FAIL" "Python Package Manager" "Install pip for Python dependency management."
        missing_ref+=("pip3")
    fi

    check_command_presence docker "Docker" "Install Docker Engine to run containerized agents." || missing_ref+=("docker")

    if command -v docker-compose >/dev/null 2>&1; then
        record_status "PASS" "Docker Compose" "docker-compose binary detected."
    elif docker compose version >/dev/null 2>&1; then
        record_status "PASS" "Docker Compose" "docker compose plugin detected."
    else
        record_status "FAIL" "Docker Compose" "Install Docker Compose v2 or the docker-compose plugin."
        missing_ref+=("docker-compose")
    fi

    if command -v curl >/dev/null 2>&1; then
        record_status "PASS" "curl" "curl available for webhook integrations."
    else
        record_status "WARN" "curl" "curl not found; event hooks will log locally only."
    fi

    if [[ ${#missing_ref[@]} -eq 0 ]]; then
        broadcast_event 'dependencies.complete' 'All required runtime dependencies are available.'
        return 0
    fi

    broadcast_event 'dependencies.failed' "Missing dependencies: ${missing_ref[*]}"
    return 1
}

run_python_tests() {
    local label=${1:-"Python self-tests"}
    local test_command=${PYTHON_TEST_COMMAND:-"python -m unittest discover -s tests"}

    log_message "Running ${label} with: ${test_command}"
    broadcast_event 'self-tests.start' "Executing ${label}."

    if bash -lc "$test_command"; then
        record_status "PASS" "$label" "${label} completed successfully."
        broadcast_event 'self-tests.complete' "${label} succeeded."
        return 0
    fi

    local exit_code=$?
    record_status "FAIL" "$label" "${label} exited with status ${exit_code}."
    broadcast_event 'self-tests.failed' "${label} failed with status ${exit_code}."
    return $exit_code
}

pip_health_check() {
    if ! command -v python3 >/dev/null 2>&1; then
        record_status "WARN" "Dependency Health" "Python 3 unavailable; skipping pip integrity check."
        return 0
    fi

    if ! python3 -m pip --version >/dev/null 2>&1; then
        record_status "WARN" "Dependency Health" "pip not installed; skipping integrity check."
        return 0
    fi

    log_message "Running 'python3 -m pip check' to validate installed packages."
    broadcast_event 'dependencies.health-check' 'Running pip dependency validation.'

    if python3 -m pip check; then
        record_status "PASS" "Dependency Health" "pip check reported no conflicts."
        return 0
    fi

    local exit_code=$?
    record_status "WARN" "Dependency Health" "pip check reported conflicts (exit ${exit_code})."
    return $exit_code
}
