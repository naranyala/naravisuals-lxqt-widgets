#!/usr/bin/env bash
# =============================================================================
# NaraVisuals LXQt Config Validator
# =============================================================================
# Scans and validates LXQt configuration files for missing or misconfigured
# settings.
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
ISSUES_FOUND=0

# Config directory
LXQT_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/lxqt"
NARA_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/naravisuals"

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
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
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
    echo -e "${CYAN}=== $1 ===${NC}"
}

# =============================================================================
# LXQt Core Config Validation
# =============================================================================

validate_lxqt_conf() {
    section_header "LXQt Core Configuration"
    
    local config="$LXQT_CONFIG/lxqt.conf"
    
    if [[ ! -f "$config" ]]; then
        check_fail "lxqt.conf not found"
        return
    fi
    
    check_pass "lxqt.conf exists"
    
    # Check required sections
    local required_sections=("general" "proxy")
    for section in "${required_sections[@]}"; do
        if grep -qi "^\[$section\]" "$config" 2>/dev/null; then
            check_pass "Section [$section] found"
        else
            check_warn "Section [$section] missing"
        fi
    done
}

validate_session_conf() {
    section_header "Session Configuration"
    
    local config="$LXQT_CONFIG/session.conf"
    
    if [[ ! -f "$config" ]]; then
        check_fail "session.conf not found"
        return
    fi
    
    check_pass "session.conf exists"
    
    # Check window_manager
    if grep -q "^window_manager=" "$config" 2>/dev/null; then
        local wm=$(grep "^window_manager=" "$config" | cut -d= -f2)
        if [[ -n "$wm" ]]; then
            check_pass "Window manager configured: $wm"
            
            # Check if WM exists
            if command -v "$wm" &>/dev/null || [[ -f "$wm" ]]; then
                check_pass "Window manager binary exists"
            else
                check_warn "Window manager binary not found: $wm"
            fi
        else
            check_warn "Window manager not set"
        fi
    else
        check_warn "window_manager not configured"
    fi
    
    # Check desktop_session
    if grep -q "^desktop_session=" "$config" 2>/dev/null; then
        check_pass "Desktop session configured"
    else
        check_warn "desktop_session not configured"
    fi
}

# =============================================================================
# Panel Configuration Validation
# =============================================================================

validate_panel_conf() {
    section_header "Panel Configuration"
    
    local config="$LXQT_CONFIG/panel.conf"
    
    if [[ ! -f "$config" ]]; then
        check_fail "panel.conf not found"
        return
    fi
    
    check_pass "panel.conf exists"
    
    # Check General section
    if grep -q "^\[General\]" "$config" 2>/dev/null; then
        check_pass "General section found"
        
        # Check panels list
        if grep -q "^panels=" "$config" 2>/dev/null; then
            local panels=$(grep "^panels=" "$config" | cut -d= -f2)
            local panel_count=$(echo "$panels" | tr ',' '\n' | grep -c "panel" || true)
            check_pass "Panels configured: $panel_count"
        else
            check_fail "No panels configured"
        fi
        
        # Check preferred_backend
        if grep -q "^preferred_backend=" "$config" 2>/dev/null; then
            local backend=$(grep "^preferred_backend=" "$config" | cut -d= -f2)
            check_pass "Backend configured: $backend"
        else
            check_warn "preferred_backend not set"
        fi
    else
        check_fail "General section missing"
    fi
    
    # Validate each panel
    local panels=$(grep "^panels=" "$config" 2>/dev/null | cut -d= -f2 | tr ',' '\n')
    for panel in $panels; do
        panel=$(echo "$panel" | xargs)  # Trim whitespace
        validate_panel_section "$config" "$panel"
    done
}

validate_panel_section() {
    local config="$1"
    local panel="$2"
    
    section_header "Panel: $panel"
    
    if grep -q "^\[$panel\]" "$config" 2>/dev/null; then
        check_pass "Section [$panel] exists"
        
        # Check required fields
        local required_fields=("position" "plugins" "width" "height")
        for field in "${required_fields[@]}"; do
            if grep -q "^${field}=" "$config" 2>/dev/null; then
                local value=$(grep "^${field}=" "$config" | head -1 | cut -d= -f2)
                if [[ -n "$value" ]]; then
                    check_pass "$field = $value"
                else
                    check_warn "$field is empty"
                fi
            else
                check_fail "$field missing"
            fi
        done
        
        # Check plugins
        if grep -q "^plugins=" "$config" 2>/dev/null; then
            local plugins=$(grep "^plugins=" "$config" | head -1 | cut -d= -f2)
            validate_plugins "$config" "$plugins"
        fi
    else
        check_fail "Section [$panel] missing"
    fi
}

validate_plugins() {
    local config="$1"
    local plugins="$2"
    
    section_header "Plugin Validation"
    
    # Split plugins by comma
    IFS=',' read -ra PLUGIN_ARRAY <<< "$plugins"
    
    for plugin in "${PLUGIN_ARRAY[@]}"; do
        plugin=$(echo "$plugin" | xargs)  # Trim whitespace
        
        # Check if plugin section exists
        if grep -q "^\[$plugin\]" "$config" 2>/dev/null; then
            check_pass "Plugin [$plugin] configured"
            
            # Check type field
            if grep -A5 "^\[$plugin\]" "$config" 2>/dev/null | grep -q "^type="; then
                local type=$(grep -A5 "^\[$plugin\]" "$config" 2>/dev/null | grep "^type=" | head -1 | cut -d= -f2)
                check_pass "Plugin type: $type"
            else
                check_warn "Plugin [$plugin] missing type"
            fi
        else
            check_warn "Plugin [$plugin] not configured (using defaults)"
        fi
    done
}

# =============================================================================
# NaraVisuals Configuration Validation
# =============================================================================

validate_naravisuals_config() {
    section_header "NaraVisuals Configuration"
    
    if [[ ! -d "$NARA_CONFIG" ]]; then
        check_warn "NaraVisuals config directory not found"
        return
    fi
    
    check_pass "NaraVisuals config directory exists"
    
    # Check config.json
    local config_file="$NARA_CONFIG/config.json"
    if [[ -f "$config_file" ]]; then
        check_pass "config.json exists"
        
        # Validate JSON
        if python3 -c "import json; json.load(open('$config_file'))" 2>/dev/null; then
            check_pass "config.json is valid JSON"
        else
            check_fail "config.json is invalid JSON"
        fi
    else
        check_warn "config.json not found (will be created)"
    fi
    
    # Check weather.json
    local weather_file="$NARA_CONFIG/weather.json"
    if [[ -f "$weather_file" ]]; then
        check_pass "weather.json exists"
        
        # Check if city is set
        local city=$(python3 -c "import json; print(json.load(open('$weather_file')).get('city', ''))" 2>/dev/null)
        if [[ -n "$city" ]]; then
            check_pass "Weather city configured: $city"
        else
            check_warn "Weather city not configured"
        fi
    else
        check_warn "weather.json not found"
    fi
    
    # Check theme.json
    local theme_file="$NARA_CONFIG/theme.json"
    if [[ -f "$theme_file" ]]; then
        check_pass "theme.json exists"
        
        # Validate JSON
        if python3 -c "import json; json.load(open('$theme_file'))" 2>/dev/null; then
            check_pass "theme.json is valid JSON"
        else
            check_fail "theme.json is invalid JSON"
        fi
    else
        check_info "theme.json not found (using defaults)"
    fi
}

# =============================================================================
# Plugin Binary Validation
# =============================================================================

validate_plugin_binaries() {
    section_header "Plugin Binaries"
    
    local plugin_dirs=(
        "$HOME/.local/lib/lxqt-panel"
        "/usr/lib/x86_64-linux-gnu/lxqt-panel"
        "/usr/lib64/lxqt-panel"
    )
    
    local found=false
    for dir in "${plugin_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            check_pass "Plugin directory found: $dir"
            found=true
            
            # Check for NaraVisuals plugins
            local nv_plugins=$(ls "$dir"/libnaravisuals*.so 2>/dev/null | wc -l)
            if [[ $nv_plugins -gt 0 ]]; then
                check_pass "NaraVisuals plugins found: $nv_plugins"
            else
                check_warn "NaraVisuals plugins not found"
            fi
        fi
    done
    
    if [[ "$found" == false ]]; then
        check_warn "No lxqt-panel plugin directories found"
    fi
}

# =============================================================================
# D-Bus Service Validation
# =============================================================================

validate_dbus_service() {
    section_header "D-Bus Service"
    
    # Check if daemon is running
    if systemctl --user is-active naravisuals-daemon.service &>/dev/null; then
        check_pass "Daemon service active"
    else
        check_fail "Daemon service not active"
    fi
    
    # Check D-Bus registration
    if python3 -c "
import dbus
bus = dbus.SessionBus()
names = bus.list_names()
found = any('naravisuals' in name.lower() for name in names)
exit(0 if found else 1)
" 2>/dev/null; then
        check_pass "D-Bus service registered"
    else
        check_fail "D-Bus service not registered"
    fi
}

# =============================================================================
# Theme Validation
# =============================================================================

validate_theme() {
    section_header "Theme Configuration"
    
    local config="$LXQT_CONFIG/lxqt-config-appearance.conf"
    
    if [[ -f "$config" ]]; then
        check_pass "Appearance config exists"
        
        # Check theme
        if grep -q "^theme=" "$config" 2>/dev/null; then
            local theme=$(grep "^theme=" "$config" | cut -d= -f2)
            if [[ -n "$theme" ]]; then
                check_pass "Theme configured: $theme"
            else
                check_warn "Theme not set"
            fi
        else
            check_warn "theme not configured"
        fi
        
        # Check icon theme
        if grep -q "^icon_theme=" "$config" 2>/dev/null; then
            local icon_theme=$(grep "^icon_theme=" "$config" | cut -d= -f2)
            if [[ -n "$icon_theme" ]]; then
                check_pass "Icon theme configured: $icon_theme"
            else
                check_warn "Icon theme not set"
            fi
        else
            check_warn "icon_theme not configured"
        fi
    else
        check_warn "Appearance config not found"
    fi
}

# =============================================================================
# Window Manager Validation
# =============================================================================

validate_window_manager() {
    section_header "Window Manager"
    
    local config="$LXQT_CONFIG/session.conf"
    
    if [[ ! -f "$config" ]]; then
        check_warn "session.conf not found"
        return
    fi
    
    # Get window manager
    local wm=""
    if grep -q "^window_manager=" "$config" 2>/dev/null; then
        wm=$(grep "^window_manager=" "$config" | cut -d= -f2)
    fi
    
    if [[ -z "$wm" ]]; then
        check_warn "No window manager configured"
        return
    fi
    
    check_pass "Window manager: $wm"
    
    # Check if it's a command or path
    if [[ "$wm" == /* ]]; then
        # Absolute path
        if [[ -f "$wm" ]]; then
            check_pass "Window manager binary exists"
        else
            check_fail "Window manager binary not found: $wm"
        fi
    else
        # Command name
        if command -v "$wm" &>/dev/null; then
            check_pass "Window manager command found"
        else
            check_warn "Window manager command not in PATH: $wm"
        fi
    fi
}

# =============================================================================
# Autostart Validation
# =============================================================================

validate_autostart() {
    section_header "Autostart"
    
    local autostart_dir="$LXQT_CONFIG/autostart"
    
    if [[ ! -d "$autostart_dir" ]]; then
        check_warn "Autostart directory not found"
        return
    fi
    
    check_pass "Autostart directory exists"
    
    # Check for NaraVisuals autostart
    local nv_autostart=$(ls "$autostart_dir"/naravisuals*.desktop 2>/dev/null | wc -l)
    if [[ $nv_autostart -gt 0 ]]; then
        check_pass "NaraVisuals autostart entries: $nv_autostart"
    else
        check_warn "No NaraVisuals autostart entries"
    fi
    
    # Check for critical autostart entries
    local critical_entries=("lxqt-panel.desktop" "lxqt-session.desktop")
    for entry in "${critical_entries[@]}"; do
        if [[ -f "$autostart_dir/$entry" ]]; then
            check_pass "Critical autostart: $entry"
        else
            check_warn "Missing autostart: $entry"
        fi
    done
}

# =============================================================================
# Summary
# =============================================================================

print_summary() {
    echo ""
    echo "============================================"
    echo "  LXQt Configuration Validation Summary"
    echo "============================================"
    echo ""
    echo -e "  ${GREEN}Passed: $CHECKS_PASSED${NC}"
    echo -e "  ${YELLOW}Warnings: $CHECKS_WARNED${NC}"
    echo -e "  ${RED}Failed: $CHECKS_FAILED${NC}"
    echo ""
    
    if [[ $ISSUES_FOUND -eq 0 ]]; then
        echo -e "${GREEN}No critical issues found!${NC}"
    else
        echo -e "${RED}Found $ISSUES_FOUND critical issue(s) that need attention.${NC}"
        echo ""
        echo "Run 'naravisuals-doctor' for more diagnostics."
    fi
    
    echo ""
}

# =============================================================================
# Fix Suggestions
# =============================================================================

print_fix_suggestions() {
    if [[ $ISSUES_FOUND -gt 0 ]]; then
        echo -e "${CYAN}Suggested fixes:${NC}"
        echo ""
        
        if ! grep -q "^\[General\]" "$LXQT_CONFIG/panel.conf" 2>/dev/null; then
            echo "  1. Reset panel config:"
            echo "     naravisuals-panel-reset --stock"
            echo ""
        fi
        
        if ! systemctl --user is-active naravisuals-daemon.service &>/dev/null; then
            echo "  2. Start daemon:"
            echo "     systemctl --user start naravisuals-daemon"
            echo ""
        fi
        
        echo "  3. View detailed diagnostics:"
            echo "     naravisuals-doctor"
            echo ""
    fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo ""
    echo "============================================"
    echo "  LXQt Configuration Validator"
    echo "============================================"
    
    # Validate configs
    validate_lxqt_conf
    validate_session_conf
    validate_panel_conf
    validate_theme
    validate_window_manager
    validate_autostart
    validate_plugin_binaries
    validate_naravisuals_config
    validate_dbus_service
    
    # Print summary
    print_summary
    print_fix_suggestions
}

main "$@"
