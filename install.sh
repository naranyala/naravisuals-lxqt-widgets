#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# NaraVisuals LXQt Widgets - Installer
# =============================================================================
# Installs NaraVisuals LXQt Widgets with D-Bus architecture.
# Supports Arch, Debian/Ubuntu, Fedora/RHEL/CentOS.
# =============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Project paths
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PREFIX="${PREFIX:-$HOME/.local}"
BIN_DIR="${PREFIX}/bin"
LIB_DIR="${PREFIX}/lib/naravisuals"
APP_DIR="${PREFIX}/share/applications"
PANEL_PLUGIN_DIR="${PREFIX}/share/lxqt/lxqt-panel"
SERVICE_DIR="${PREFIX}/share/systemd/user"
DBUS_DIR="${PREFIX}/share/dbus-1/services"
AUTOSTART_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/autostart"

# Error tracking
ERRORS=()
WARNINGS=()

# =============================================================================
# Utility Functions
# =============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    WARNINGS+=("$1")
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ERRORS+=("$1")
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

check_command() {
    command -v "$1" &>/dev/null
}

check_file() {
    [[ -f "$1" ]]
}

check_dir() {
    [[ -d "$1" ]]
}

# =============================================================================
# Pre-flight Checks
# =============================================================================

preflight_checks() {
    log_step "Running pre-flight checks..."
    
    # Check Python
    if check_command python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
        
        if [[ "$PYTHON_MAJOR" -ge 3 ]] && [[ "$PYTHON_MINOR" -ge 10 ]]; then
            log_success "Python $PYTHON_VERSION detected"
        else
            log_error "Python 3.10+ required (found $PYTHON_VERSION)"
        fi
    else
        log_error "Python 3 not found"
    fi
    
    # Check pip
    if check_command pip3; then
        log_success "pip3 detected"
    else
        log_warn "pip3 not found (optional)"
    fi
    
    # Check Qt6
    if python3 -c "import PyQt6" 2>/dev/null; then
        log_success "PyQt6 detected"
    else
        log_error "PyQt6 not found"
    fi
    
    # Check psutil
    if python3 -c "import psutil" 2>/dev/null; then
        log_success "psutil detected"
    else
        log_error "psutil not found"
    fi
    
    # Check D-Bus
    if [[ -n "${DBUS_SESSION_BUS_ADDRESS:-}" ]]; then
        log_success "D-Bus session bus available"
    else
        log_warn "D-Bus session bus not detected"
    fi
    
    # Check systemd
    if check_command systemctl; then
        log_success "systemctl detected"
    else
        log_warn "systemctl not found (service auto-start disabled)"
    fi
    
    # Check lxqt-panel
    if check_command lxqt-panel; then
        log_success "lxqt-panel detected"
    else
        log_warn "lxqt-panel not found"
    fi
    
    # Check display server
    if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
        log_success "Wayland display server detected"
    elif [[ -n "${DISPLAY:-}" ]]; then
        log_success "X11 display server detected"
    else
        log_warn "No display server detected"
    fi
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        log_warn "Running as root (use PREFIX=/usr for system-wide install)"
    fi
    
    echo ""
}

# =============================================================================
# Distribution Detection
# =============================================================================

detect_distro() {
    if [[ -f /etc/os-release ]]; then
        # shellcheck source=/dev/null
        . /etc/os-release
        DISTRO_ID="${ID}"
        DISTRO_NAME="${NAME:-$ID}"
        DISTRO_VERSION="${VERSION_ID:-}"
        DISTRO_LIKE="${ID_LIKE:-}"
    elif [[ -f /etc/redhat-release ]]; then
        DISTRO_ID="rhel"
        DISTRO_NAME="RHEL"
        DISTRO_LIKE="rhel fedora"
    elif [[ -f /etc/debian_version ]]; then
        DISTRO_ID="debian"
        DISTRO_NAME="Debian"
        DISTRO_LIKE="debian"
    else
        DISTRO_ID="unknown"
        DISTRO_NAME="Unknown"
        DISTRO_LIKE=""
    fi
    
    # Determine package manager
    if [[ "$DISTRO_LIKE" =~ (rhel|fedora|rhel-fedora) ]] || [[ "$DISTRO_ID" =~ ^(fedora|rhel|centos|rocky|alma|ol)$ ]]; then
        PKG_MANAGER="rpm"
    elif [[ "$DISTRO_LIKE" =~ (debian|ubuntu) ]] || [[ "$DISTRO_ID" =~ ^(debian|ubuntu|linuxmint|pop|elementary|zorin)$ ]]; then
        PKG_MANAGER="deb"
    elif [[ "$DISTRO_ID" =~ ^(arch|manjaro|endeavouros|garuda|artix)$ ]]; then
        PKG_MANAGER="pacman"
    elif [[ "$DISTRO_ID" =~ ^(opensuse|suse|sles)$ ]]; then
        PKG_MANAGER="zypper"
    else
        PKG_MANAGER="unknown"
    fi
    
    log_info "Detected: $DISTRO_NAME $DISTRO_VERSION ($PKG_MANAGER-based)"
}

# =============================================================================
# Dependency Checking
# =============================================================================

check_dependencies() {
    log_step "Checking dependencies..."
    
    local missing=()
    local optional_missing=()
    
    case $PKG_MANAGER in
        rpm)
            for pkg in python3 python3-pyqt6 python3-psutil python3-requests python3-dbus-python python3-notify2; do
                if ! rpm -q "$pkg" &>/dev/null; then
                    missing+=("$pkg")
                fi
            done
            for pkg in lxqt-panel lxqt-build-tools; do
                if ! rpm -q "$pkg" &>/dev/null; then
                    optional_missing+=("$pkg")
                fi
            done
            ;;
        deb)
            for pkg in python3 python3-pyqt6 python3-psutil python3-requests python3-dbus python3-notify2; do
                if ! dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
                    missing+=("$pkg")
                fi
            done
            for pkg in lxqt-panel lxqt-build-tools; do
                if ! dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
                    optional_missing+=("$pkg")
                fi
            done
            ;;
        pacman)
            for pkg in python python-pyqt6 python-psutil python-requests python-dbus python-notify2; do
                if ! pacman -Qi "$pkg" &>/dev/null; then
                    missing+=("$pkg")
                fi
            done
            for pkg in lxqt-panel lxqt-build-tools; do
                if ! pacman -Qi "$pkg" &>/dev/null; then
                    optional_missing+=("$pkg")
                fi
            done
            ;;
        *)
            log_warn "Cannot check dependencies for unknown package manager"
            return
            ;;
    esac
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing required packages: ${missing[*]}"
        case $PKG_MANAGER in
            rpm) echo "  Install with: sudo dnf install ${missing[*]}" ;;
            deb) echo "  Install with: sudo apt install ${missing[*]}" ;;
            pacman) echo "  Install with: sudo pacman -S ${missing[*]}" ;;
        esac
        echo ""
    else
        log_success "All required dependencies found"
    fi
    
    if [[ ${#optional_missing[@]} -gt 0 ]]; then
        log_warn "Missing optional packages: ${optional_missing[*]}"
        case $PKG_MANAGER in
            rpm) echo "  Install with: sudo dnf install ${optional_missing[*]}" ;;
            deb) echo "  Install with: sudo apt install ${optional_missing[*]}" ;;
            pacman) echo "  Install with: sudo pacman -S ${optional_missing[*]}" ;;
        esac
        echo ""
    fi
}

# =============================================================================
# Installation
# =============================================================================

install_directories() {
    log_step "Creating installation directories..."
    
    local dirs=(
        "$BIN_DIR"
        "$LIB_DIR"
        "$APP_DIR"
        "$PANEL_PLUGIN_DIR"
        "$SERVICE_DIR"
        "$DBUS_DIR"
        "$AUTOSTART_DIR"
        "$PREFIX/share/naravisuals"
    )
    
    for dir in "${dirs[@]}"; do
        if mkdir -p "$dir" 2>/dev/null; then
            log_success "Created: $dir"
        else
            log_error "Failed to create: $dir"
        fi
    done
}

install_python_packages() {
    log_step "Installing Python packages..."
    
    if cp -r "$PROJECT_DIR/naravisuals" "$LIB_DIR/"; then
        log_success "Python packages installed to $LIB_DIR"
    else
        log_error "Failed to install Python packages"
    fi
}

install_launcher_scripts() {
    log_step "Installing launcher scripts..."
    
    # nv-manager (Control Center)
    cat > "$BIN_DIR/nv-manager" << 'SCRIPT'
#!/usr/bin/env bash
exec python3 -m naravisuals.manager.control_center "$@"
SCRIPT
    chmod +x "$BIN_DIR/nv-manager"
    
    # nv-manager-legacy (Settings Hub)
    cat > "$BIN_DIR/nv-manager-legacy" << 'SCRIPT'
#!/usr/bin/env bash
exec python3 -m naravisuals.manager.app "$@"
SCRIPT
    chmod +x "$BIN_DIR/nv-manager-legacy"
    
    # nv-daemon
    cat > "$BIN_DIR/nv-daemon" << 'SCRIPT'
#!/usr/bin/env bash
exec python3 -m naravisuals.daemon "$@"
SCRIPT
    chmod +x "$BIN_DIR/nv-daemon"
    
    # nv-theme-store
    cat > "$BIN_DIR/nv-theme-store" << 'SCRIPT'
#!/usr/bin/env bash
exec python3 -m naravisuals.theme_manager.app "$@"
SCRIPT
    chmod +x "$BIN_DIR/nv-theme-store"
    
    # nv-desktop-manager
    cat > "$BIN_DIR/nv-desktop-manager" << 'SCRIPT'
#!/usr/bin/env bash
exec python3 -m naravisuals.desktop_manager.app "$@"
SCRIPT
    chmod +x "$BIN_DIR/nv-desktop-manager"
    
    log_success "Launcher scripts installed to $BIN_DIR"
}

install_systemd_service() {
    log_step "Installing systemd service..."
    
    if check_file "$PROJECT_DIR/packaging/naravisuals-daemon.service"; then
        if cp "$PROJECT_DIR/packaging/naravisuals-daemon.service" "$SERVICE_DIR/"; then
            log_success "Systemd service installed"
        else
            log_error "Failed to install systemd service"
        fi
    else
        log_error "Systemd service file not found"
    fi
}

install_dbus_service() {
    log_step "Installing D-Bus service..."
    
    cat > "$DBUS_DIR/org.naravisuals.Daemon.service" << DBUS
[D-BUS Service]
Name=org.naravisuals.Daemon
Exec=${BIN_DIR}/nv-daemon
User=${USER}
DBUS_BUS_TYPE=session
DBUS_ACTIVATABLE=true
DBUS
    chmod 644 "$DBUS_DIR/org.naravisuals.Daemon.service"
    
    log_success "D-Bus service installed"
}

install_desktop_files() {
    log_step "Installing desktop files..."
    
    local count=0
    for f in "$PROJECT_DIR/desktop/naravisuals-"*.desktop; do
        if [[ -f "$f" ]]; then
            cp "$f" "$APP_DIR/"
            ((count++))
        fi
    done
    
    log_success "Installed $count desktop files"
}

install_panel_tools() {
    log_step "Installing panel tools..."
    
    # Panel reset tool
    if check_file "$PROJECT_DIR/scripts/naravisuals-panel-reset"; then
        cp "$PROJECT_DIR/scripts/naravisuals-panel-reset" "$BIN_DIR/"
        chmod +x "$BIN_DIR/naravisuals-panel-reset"
        log_success "Panel reset tool installed"
    fi
    
    # Doctor tool
    if check_file "$PROJECT_DIR/scripts/naravisuals-doctor.sh"; then
        cp "$PROJECT_DIR/scripts/naravisuals-doctor.sh" "$BIN_DIR/naravisuals-doctor"
        chmod +x "$BIN_DIR/naravisuals-doctor"
        log_success "Diagnostic tool installed"
    fi
    
    # Logs viewer
    if check_file "$PROJECT_DIR/scripts/naravisuals-logs.sh"; then
        cp "$PROJECT_DIR/scripts/naravisuals-logs.sh" "$BIN_DIR/naravisuals-logs"
        chmod +x "$BIN_DIR/naravisuals-logs"
        log_success "Log viewer installed"
    fi
    
    # LXQt validator
    if check_file "$PROJECT_DIR/scripts/naravisuals-lxqt-validator.sh"; then
        cp "$PROJECT_DIR/scripts/naravisuals-lxqt-validator.sh" "$BIN_DIR/naravisuals-lxqt-validator"
        chmod +x "$BIN_DIR/naravisuals-lxqt-validator"
        log_success "LXQt config validator installed"
    fi
    
    # Stock panel config
    if check_file "$PROJECT_DIR/packaging/stock-panel.conf"; then
        cp "$PROJECT_DIR/packaging/stock-panel.conf" "$PREFIX/share/naravisuals/"
        log_success "Stock panel config installed"
    fi
}

install_autostart() {
    log_step "Installing autostart entry..."
    
    cat > "$AUTOSTART_DIR/naravisuals-daemon.desktop" << AUTOSTART
[Desktop Entry]
Type=Application
Name=NaraVisuals Daemon
Exec=${BIN_DIR}/nv-daemon
Terminal=false
X-LXQt-Needs=Panel
AUTOSTART
    
    log_success "Autostart entry installed"
}

# =============================================================================
# Post-installation
# =============================================================================

enable_service() {
    if check_command systemctl; then
        log_step "Enabling systemd user service..."
        
        systemctl --user daemon-reload 2>/dev/null || true
        if systemctl --user enable naravisuals-daemon.service 2>/dev/null; then
            log_success "Service enabled (will start on next login)"
        else
            log_warn "Failed to enable service (may need manual start)"
        fi
    fi
}

update_desktop_database() {
    if check_command update-desktop-database; then
        log_step "Updating desktop database..."
        update-desktop-database "$APP_DIR" 2>/dev/null || true
        log_success "Desktop database updated"
    fi
}

# =============================================================================
# Verification
# =============================================================================

verify_installation() {
    log_step "Verifying installation..."
    
    local issues=()
    
    # Check installed files
    local required_files=(
        "$BIN_DIR/nv-manager"
        "$BIN_DIR/nv-daemon"
        "$BIN_DIR/naravisuals-panel-reset"
        "$LIB_DIR/naravisuals/__init__.py"
        "$LIB_DIR/naravisuals/daemon/__main__.py"
        "$LIB_DIR/naravisuals/core/base_widget.py"
    )
    
    for file in "${required_files[@]}"; do
        if ! check_file "$file"; then
            issues+=("Missing: $file")
        fi
    done
    
    # Check Python imports
    if ! python3 -c "import sys; sys.path.insert(0, '$LIB_DIR'); import naravisuals" 2>/dev/null; then
        issues+=("Python import test failed")
    fi
    
    if [[ ${#issues[@]} -eq 0 ]]; then
        log_success "Installation verified successfully"
    else
        for issue in "${issues[@]}"; do
            log_error "$issue"
        done
    fi
}

# =============================================================================
# Summary
# =============================================================================

print_summary() {
    echo ""
    echo "============================================"
    echo "  Installation Complete"
    echo "============================================"
    echo ""
    
    if [[ ${#ERRORS[@]} -gt 0 ]]; then
        echo -e "${RED}Errors: ${#ERRORS[@]}${NC}"
        for err in "${ERRORS[@]}"; do
            echo "  - $err"
        done
        echo ""
    fi
    
    if [[ ${#WARNINGS[@]} -gt 0 ]]; then
        echo -e "${YELLOW}Warnings: ${#WARNINGS[@]}${NC}"
        for warn in "${WARNINGS[@]}"; do
            echo "  - $warn"
        done
        echo ""
    fi
    
    echo "Installed to: $PREFIX"
    echo ""
    echo "Quick Start:"
    echo "  1. Start daemon:  systemctl --user start naravisuals-daemon"
    echo "  2. Open manager:  nv-manager"
    echo "  3. Add widgets:   Right-click panel > Add Widgets > NaraVisuals"
    echo ""
    echo "GUI Apps:"
    echo "  nv-manager          Control Center"
    echo "  nv-manager-legacy   Settings Hub"
    echo "  nv-theme-store      Theme Store"
    echo "  nv-sddm-manager     SDDM Manager"
    echo ""
    echo "Troubleshooting:"
    echo "  naravisuals-doctor    Run diagnostic checks"
    echo "  naravisuals-logs      View daemon logs"
    echo ""
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo ""
    echo "============================================"
    echo "  NaraVisuals LXQt Widgets Installer"
    echo "============================================"
    echo ""
    
    # Run pre-flight checks
    preflight_checks
    
    # Detect distribution
    detect_distro
    
    # Check dependencies
    check_dependencies
    
    # Confirm installation
    echo ""
    read -p "Proceed with installation? [Y/n]: " CONFIRM
    if [[ "$CONFIRM" =~ ^[Nn]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    
    # Run installation steps
    install_directories
    install_python_packages
    install_launcher_scripts
    install_systemd_service
    install_dbus_service
    install_desktop_files
    install_panel_tools
    install_autostart
    enable_service
    update_desktop_database
    verify_installation
    
    # Print summary
    print_summary
}

main "$@"
