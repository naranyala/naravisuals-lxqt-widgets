#!/usr/bin/env bash
# =============================================================================
# NaraVisuals LXQt Config Scanner & Fixer
# =============================================================================
# Scans LXQt configuration for issues and optionally fixes them.
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Config directory
LXQT_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/lxqt"
BACKUP_DIR="$LXQT_CONFIG/backups"

# =============================================================================
# Utility Functions
# =============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_fix() {
    echo -e "${CYAN}[FIX]${NC} $1"
}

# =============================================================================
# Backup
# =============================================================================

backup_configs() {
    mkdir -p "$BACKUP_DIR"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    echo "Backing up configurations..."
    
    for conf in "$LXQT_CONFIG"/*.conf; do
        if [[ -f "$conf" ]]; then
            cp "$conf" "$BACKUP_DIR/$(basename "$conf").$timestamp"
        fi
    done
    
    log_info "Backup created in $BACKUP_DIR"
}

# =============================================================================
# Scanner Functions
# =============================================================================

scan_panel_config() {
    local config="$LXQT_CONFIG/panel.conf"
    local issues=()
    
    if [[ ! -f "$config" ]]; then
        log_error "panel.conf not found"
        return 1
    fi
    
    # Check for missing plugins section
    if ! grep -q "^\[General\]" "$config"; then
        issues+=("Missing [General] section")
    fi
    
    # Check for panels list
    if ! grep -q "^panels=" "$config"; then
        issues+=("No panels configured")
    fi
    
    # Check for orphan plugin sections (exclude panel sections)
    local plugins_in_panels=$(grep "^plugins=" "$config" | cut -d= -f2 | tr ',' '\n' | xargs)
    local sections=$(grep "^\[" "$config" | grep -v "General" | grep -v "panel" | sed 's/\[//g' | sed 's/\]//g')
    
    for section in $sections; do
        if ! echo "$plugins_in_panels" | grep -q "$section"; then
            issues+=("Orphan plugin section: $section")
        fi
    done
    
    # Check for missing plugin sections
    for plugin in $plugins_in_panels; do
        if ! grep -q "^\[$plugin\]" "$config"; then
            issues+=("Missing section for plugin: $plugin")
        fi
    done
    
    # Check for required fields
    local required_fields=("position" "plugins")
    for field in "${required_fields[@]}"; do
        if ! grep -q "^${field}=" "$config"; then
            issues+=("Missing required field: $field")
        fi
    done
    
    # Return issues
    if [[ ${#issues[@]} -gt 0 ]]; then
        for issue in "${issues[@]}"; do
            log_warn "$issue"
        done
        return 1
    fi
    
    return 0
}

scan_session_config() {
    local config="$LXQT_CONFIG/session.conf"
    local issues=()
    
    if [[ ! -f "$config" ]]; then
        log_error "session.conf not found"
        return 1
    fi
    
    # Check window manager
    if ! grep -q "^window_manager=" "$config"; then
        issues+=("No window manager configured")
    else
        local wm=$(grep "^window_manager=" "$config" | cut -d= -f2)
        if ! command -v "$wm" &>/dev/null && ! [[ -f "$wm" ]]; then
            issues+=("Window manager not found: $wm")
        fi
    fi
    
    # Return issues
    if [[ ${#issues[@]} -gt 0 ]]; then
        for issue in "${issues[@]}"; do
            log_warn "$issue"
        done
        return 1
    fi
    
    return 0
}

scan_naravisuals_config() {
    local config_dir="${XDG_CONFIG_HOME:-$HOME/.config}/naravisuals"
    local issues=()
    
    if [[ ! -d "$config_dir" ]]; then
        log_warn "NaraVisuals config directory not found"
        return 0
    fi
    
    # Check config.json
    if [[ -f "$config_dir/config.json" ]]; then
        if ! python3 -c "import json; json.load(open('$config_dir/config.json'))" 2>/dev/null; then
            issues+=("Invalid config.json")
        fi
    fi
    
    # Check weather.json
    if [[ -f "$config_dir/weather.json" ]]; then
        if ! python3 -c "import json; json.load(open('$config_dir/weather.json'))" 2>/dev/null; then
            issues+=("Invalid weather.json")
        fi
    fi
    
    # Return issues
    if [[ ${#issues[@]} -gt 0 ]]; then
        for issue in "${issues[@]}"; do
            log_warn "$issue"
        done
        return 1
    fi
    
    return 0
}

# =============================================================================
# Fixer Functions
# =============================================================================

fix_panel_config() {
    local config="$LXQT_CONFIG/panel.conf"
    
    log_fix "Fixing panel configuration..."
    
    # Check if stock config exists
    local stock_config="$HOME/.local/share/naravisuals/stock-panel.conf"
    if [[ -f "$stock_config" ]]; then
        cp "$stock_config" "$config"
        log_info "Panel config restored to stock"
    else
        # Create minimal config
        cat > "$config" << 'EOF'
[General]
panels=panel1

[panel1]
position=Bottom
plugins=fancymenu,desktopswitch,taskbar,spacer,statusnotifier,volume,worldclock,showdesktop
width=100
height=48
alignment=Center
EOF
        log_info "Minimal panel config created"
    fi
}

fix_session_config() {
    local config="$LXQT_CONFIG/session.conf"
    
    log_fix "Fixing session configuration..."
    
    # Check for common window managers
    local wm=""
    for candidate in labwc openbox kwin wayfire sway; do
        if command -v "$candidate" &>/dev/null; then
            wm="$candidate"
            break
        fi
    done
    
    if [[ -n "$wm" ]]; then
        if [[ -f "$config" ]]; then
            if grep -q "^window_manager=" "$config"; then
                sed -i "s/^window_manager=.*/window_manager=$wm/" "$config"
            else
                echo "window_manager=$wm" >> "$config"
            fi
        else
            echo "window_manager=$wm" > "$config"
        fi
        log_info "Window manager set to: $wm"
    else
        log_warn "No window manager found to set"
    fi
}

fix_naravisuals_config() {
    local config_dir="${XDG_CONFIG_HOME:-$HOME/.config}/naravisuals"
    
    log_fix "Fixing NaraVisuals configuration..."
    
    mkdir -p "$config_dir"
    
    # Fix config.json
    if [[ -f "$config_dir/config.json" ]]; then
        if ! python3 -c "import json; json.load(open('$config_dir/config.json'))" 2>/dev/null; then
            rm "$config_dir/config.json"
            log_info "Removed invalid config.json"
        fi
    fi
    
    # Fix weather.json
    if [[ -f "$config_dir/weather.json" ]]; then
        if ! python3 -c "import json; json.load(open('$config_dir/weather.json'))" 2>/dev/null; then
            rm "$config_dir/weather.json"
            log_info "Removed invalid weather.json"
        fi
    fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo ""
    echo "============================================"
    echo "  LXQt Config Scanner & Fixer"
    echo "============================================"
    echo ""
    
    local fix_mode=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --fix)
                fix_mode=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [--fix]"
                echo ""
                echo "Options:"
                echo "  --fix    Automatically fix issues"
                echo "  --help   Show this help"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Backup if fixing
    if [[ "$fix_mode" == true ]]; then
        backup_configs
    fi
    
    # Scan configurations
    echo "Scanning LXQt configurations..."
    echo ""
    
    local total_issues=0
    
    if ! scan_panel_config; then
        total_issues=$((total_issues + 1))
    fi
    
    if ! scan_session_config; then
        total_issues=$((total_issues + 1))
    fi
    
    if ! scan_naravisuals_config; then
        total_issues=$((total_issues + 1))
    fi
    
    echo ""
    echo "============================================"
    echo "  Scan Summary"
    echo "============================================"
    echo ""
    
    if [[ $total_issues -eq 0 ]]; then
        echo -e "${GREEN}No issues found!${NC}"
    else
        echo -e "${YELLOW}Found $total_issues issue(s)${NC}"
        
        if [[ "$fix_mode" == true ]]; then
            echo ""
            echo "Applying fixes..."
            echo ""
            
            fix_panel_config
            fix_session_config
            fix_naravisuals_config
            
            echo ""
            echo -e "${GREEN}Fixes applied!${NC}"
            echo "Restart lxqt-panel to apply changes."
        else
            echo ""
            echo "Run with --fix to automatically fix issues:"
            echo "  $0 --fix"
        fi
    fi
    
    echo ""
}

main "$@"
