#!/usr/bin/env bash
# =============================================================================
# NaraVisuals LXQt Widgets - Diagnostic Tool
# =============================================================================
# Runs comprehensive checks to diagnose installation and runtime issues.
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNED=0

# =============================================================================
# Utility Functions
# =============================================================================

check_pass() {
    echo -e "  ${GREEN}[PASS]${NC} $1"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
}

check_fail() {
    echo -e "  ${RED}[FAIL]${NC} $1"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
}

check_warn() {
    echo -e "  ${YELLOW}[WARN]${NC} $1"
    CHECKS_WARNED=$((CHECKS_WARNED + 1))
}

check_info() {
    echo -e "  ${BLUE}[INFO]${NC} $1"
}

section_header() {
    echo ""
    echo -e "${CYAN}--- $1 ---${NC}"
}

# =============================================================================
# System Checks
# =============================================================================

check_system() {
    section_header "System Information"
    
    # OS
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        check_info "OS: $NAME $VERSION_ID"
    else
        check_info "OS: Unknown"
    fi
    
    # Kernel
    check_info "Kernel: $(uname -r)"
    
    # Architecture
    check_info "Architecture: $(uname -m)"
    
    # Display server
    if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
        check_pass "Wayland display server detected"
    elif [[ -n "${DISPLAY:-}" ]]; then
        check_pass "X11 display server detected"
    else
        check_warn "No display server detected"
    fi
    
    # D-Bus
    if [[ -n "${DBUS_SESSION_BUS_ADDRESS:-}" ]]; then
        check_pass "D-Bus session bus: $DBUS_SESSION_BUS_ADDRESS"
    else
        check_fail "D-Bus session bus not available"
    fi
}

# =============================================================================
# Installation Checks
# =============================================================================

check_installation() {
    section_header "Installation Status"
    
    local prefix="${PREFIX:-$HOME/.local}"
    local bin_dir="$prefix/bin"
    local lib_dir="$prefix/lib/naravisuals"
    
    # Check directories
    if [[ -d "$bin_dir" ]]; then
        check_pass "Bin directory exists: $bin_dir"
    else
        check_fail "Bin directory missing: $bin_dir"
    fi
    
    if [[ -d "$lib_dir" ]]; then
        check_pass "Library directory exists: $lib_dir"
    else
        check_fail "Library directory missing: $lib_dir"
    fi
    
    # Check executables
    local executables=(
        "nv-manager"
        "nv-daemon"
        "naravisuals-panel-reset"
    )
    
    for exe in "${executables[@]}"; do
        if [[ -x "$bin_dir/$exe" ]]; then
            check_pass "Executable found: $exe"
        else
            check_fail "Executable missing: $exe"
        fi
    done
    
    # Check Python package
    if python3 -c "import sys; sys.path.insert(0, '$lib_dir'); import naravisuals" 2>/dev/null; then
        check_pass "Python package importable"
    else
        check_fail "Python package not importable"
    fi
}

# =============================================================================
# Dependency Checks
# =============================================================================

check_dependencies() {
    section_header "Dependencies"
    
    # Python
    if command -v python3 &>/dev/null; then
        local version=$(python3 --version 2>&1 | awk '{print $2}')
        local major=$(echo "$version" | cut -d. -f1)
        local minor=$(echo "$version" | cut -d. -f2)
        
        if [[ "$major" -ge 3 ]] && [[ "$minor" -ge 10 ]]; then
            check_pass "Python $version (3.10+ required)"
        else
            check_fail "Python $version (3.10+ required)"
        fi
    else
        check_fail "Python 3 not found"
    fi
    
    # PyQt6
    if python3 -c "import PyQt6" 2>/dev/null; then
        check_pass "PyQt6 installed"
    else
        check_fail "PyQt6 not installed"
    fi
    
    # psutil
    if python3 -c "import psutil" 2>/dev/null; then
        check_pass "psutil installed"
    else
        check_fail "psutil not installed"
    fi
    
    # requests
    if python3 -c "import requests" 2>/dev/null; then
        check_pass "requests installed"
    else
        check_fail "requests not installed"
    fi
    
    # dbus-python
    if python3 -c "import dbus" 2>/dev/null; then
        check_pass "dbus-python installed"
    else
        check_fail "dbus-python not installed"
    fi
    
    # notify2
    if python3 -c "import notify2" 2>/dev/null; then
        check_pass "notify2 installed"
    else
        check_warn "notify2 not installed (optional)"
    fi
    
    # lxqt-panel
    if command -v lxqt-panel &>/dev/null; then
        check_pass "lxqt-panel installed"
    else
        check_warn "lxqt-panel not found"
    fi
    
    # systemctl
    if command -v systemctl &>/dev/null; then
        check_pass "systemctl available"
    else
        check_warn "systemctl not found"
    fi
}

# =============================================================================
# Service Checks
# =============================================================================

check_services() {
    section_header "Service Status"
    
    # systemd user service
    if command -v systemctl &>/dev/null; then
        local status=$(systemctl --user is-active naravisuals-daemon.service 2>/dev/null || true)
        local enabled=$(systemctl --user is-enabled naravisuals-daemon.service 2>/dev/null || true)
        
        if [[ "$status" == "active" ]]; then
            check_pass "Daemon service: active"
        elif [[ "$status" == "inactive" ]]; then
            check_warn "Daemon service: inactive"
        else
            check_fail "Daemon service: $status"
        fi
        
        if [[ "$enabled" == "enabled" ]]; then
            check_pass "Daemon service: enabled (auto-start)"
        else
            check_warn "Daemon service: not enabled"
        fi
    fi
    
    # D-Bus service
    if python3 -c "
import dbus
bus = dbus.SessionBus()
names = bus.list_names()
found = any('naravisuals' in name.lower() for name in names)
exit(0 if found else 1)
" 2>/dev/null; then
        check_pass "D-Bus service: registered"
    else
        check_fail "D-Bus service: not registered"
    fi
}

# =============================================================================
# Configuration Checks
# =============================================================================

check_configuration() {
    section_header "Configuration"
    
    local config_dir="${XDG_CONFIG_HOME:-$HOME/.config}/naravisuals"
    local lxqt_config="$HOME/.config/lxqt"
    
    # Naravisuals config
    if [[ -d "$config_dir" ]]; then
        check_pass "Config directory exists: $config_dir"
    else
        check_warn "Config directory missing (will be created)"
    fi
    
    if [[ -f "$config_dir/config.json" ]]; then
        check_pass "Config file exists"
    else
        check_warn "Config file missing (will be created)"
    fi
    
    # LXQt panel config
    if [[ -f "$lxqt_config/panel.conf" ]]; then
        check_pass "LXQt panel config exists"
        
        # Check for NaraVisuals widgets
        if grep -q "naravisuals" "$lxqt_config/panel.conf"; then
            check_pass "NaraVisuals widgets found in panel config"
        else
            check_warn "No NaraVisuals widgets in panel config"
        fi
    else
        check_warn "LXQt panel config not found"
    fi
    
    # Backup directory
    local backup_dir="$config_dir/backups"
    if [[ -d "$backup_dir" ]]; then
        local count=$(ls -1 "$backup_dir"/*.conf 2>/dev/null | wc -l)
        check_pass "Backup directory exists ($count backups)"
    else
        check_info "No backups yet"
    fi
}

# =============================================================================
# Runtime Checks
# =============================================================================

check_runtime() {
    section_header "Runtime Environment"
    
    # Check if daemon can be imported
    if python3 -c "
import sys
sys.path.insert(0, '${PREFIX:-$HOME/.local}/lib/naravisuals')
from naravisuals.daemon.dbus_service import NaraVisualsDaemon
" 2>/dev/null; then
        check_pass "Daemon module importable"
    else
        check_fail "Daemon module not importable"
    fi
    
    # Check if theme engine works
    if python3 -c "
import sys
sys.path.insert(0, '${PREFIX:-$HOME/.local}/lib/naravisuals')
from naravisuals.core.theme_engine import theme
" 2>/dev/null; then
        check_pass "Theme engine importable"
    else
        check_fail "Theme engine not importable"
    fi
    
    # Check data providers
    if python3 -c "
import sys
sys.path.insert(0, '${PREFIX:-$HOME/.local}/lib/naravisuals')
from naravisuals.data_providers.system import SystemMonitorProvider
p = SystemMonitorProvider()
p.start()
data = p.get_data()
assert 'cpu_percent' in data
" 2>/dev/null; then
        check_pass "Data providers working"
    else
        check_fail "Data providers not working"
    fi
}

# =============================================================================
# Logs
# =============================================================================

check_logs() {
    section_header "Recent Logs"
    
    if command -v journalctl &>/dev/null; then
        local logs=$(journalctl --user -u naravisuals-daemon -n 5 --no-pager 2>/dev/null || true)
        if [[ -n "$logs" ]]; then
            echo "$logs" | head -10
        else
            check_info "No recent daemon logs"
        fi
    fi
}

# =============================================================================
# Summary
# =============================================================================

print_summary() {
    echo ""
    echo "============================================"
    echo "  Diagnostic Summary"
    echo "============================================"
    echo ""
    echo -e "  ${GREEN}Passed: $CHECKS_PASSED${NC}"
    echo -e "  ${YELLOW}Warnings: $CHECKS_WARNED${NC}"
    echo -e "  ${RED}Failed: $CHECKS_FAILED${NC}"
    echo ""
    
    if [[ $CHECKS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}All checks passed! System is ready.${NC}"
    else
        echo -e "${RED}Some checks failed. Please fix the issues above.${NC}"
        echo ""
        echo "Common fixes:"
        echo "  1. Install missing dependencies:"
        echo "     sudo apt install python3-pyqt6 python3-psutil python3-requests python3-dbus"
        echo ""
        echo "  2. Start the daemon:"
        echo "     systemctl --user start naravisuals-daemon"
        echo ""
        echo "  3. View logs for more details:"
        echo "     journalctl --user -u naravisuals-daemon -f"
    fi
    
    echo ""
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo ""
    echo "============================================"
    echo "  NaraVisuals LXQt Widgets Diagnostic Tool"
    echo "============================================"
    
    check_system
    check_installation
    check_dependencies
    check_services
    check_configuration
    check_runtime
    check_logs
    
    print_summary
}

main "$@"
