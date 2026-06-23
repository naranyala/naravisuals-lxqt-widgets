#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# NaraVisuals - Unified Package Builder
# Builds deb, rpm, AppImage, and PyInstaller packages
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[OK]${NC} $1"; }
log_step()  { echo -e "${CYAN}[..]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[!!]${NC} $1"; }
log_error() { echo -e "${RED}[ERR]${NC} $1"; }

# =============================================================================
# Helpers
# =============================================================================

detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO_ID="${ID}"
        DISTRO_LIKE="${ID_LIKE:-}"
    else
        DISTRO_ID="unknown"
        DISTRO_LIKE=""
    fi
}

check_tool() {
    command -v "$1" &>/dev/null
}

# =============================================================================
# deb Package
# =============================================================================

build_deb() {
    log_step "Building deb package..."
    cd "$PROJECT_DIR"

    if check_tool dpkg-buildpackage; then
        dpkg-buildpackage -us -uc -b 2>/dev/null
        log_info "deb package built"
        ls -la ../*.deb 2>/dev/null || true
    elif check_tool debuild; then
        debuild -us -uc -b 2>/dev/null
        log_info "deb package built"
    else
        # Manual deb build
        local tmpdir=$(mktemp -d)
        local pkgdir="$tmpdir/naravisuals-lxqt-widgets_2.0.0-1_all"
        mkdir -p "$pkgdir/DEBIAN"
        mkdir -p "$pkgdir/usr/bin"
        mkdir -p "$pkgdir/usr/lib/python3/dist-packages"
        mkdir -p "$pkgdir/usr/share/applications"
        mkdir -p "$pkgdir/usr/share/naravisuals"
        mkdir -p "$pkgdir/usr/lib/systemd/user"

        # Copy files
        cp -r "$PROJECT_DIR/naravisuals" "$pkgdir/usr/lib/python3/dist-packages/"
        cp "$PROJECT_DIR/packaging/naravisuals-daemon.service" "$pkgdir/usr/lib/systemd/user/"

        # Create launcher scripts
        for app in nv-manager nv-manager-legacy nv-theme-store nv-desktop-manager nv-sddm-manager; do
            local module=""
            case "$app" in
                nv-manager)          module="naravisuals.manager.control_center" ;;
                nv-manager-legacy)   module="naravisuals.manager.app" ;;
                nv-theme-store)      module="naravisuals.theme_manager.app" ;;
                nv-desktop-manager)  module="naravisuals.desktop_manager.app" ;;
                nv-sddm-manager)     module="naravisuals.sddm_manager.app" ;;
            esac
            cat > "$pkgdir/usr/bin/$app" << EOF
#!/usr/bin/env bash
exec python3 -m $module "\$@"
EOF
            chmod +x "$pkgdir/usr/bin/$app"
        done

        # Copy desktop files
        cp "$PROJECT_DIR/desktop"/nv-*.desktop "$pkgdir/usr/share/applications/" 2>/dev/null || true

        # Control file
        cat > "$pkgdir/DEBIAN/control" << EOF
Package: naravisuals-lxqt-widgets
Version: 2.0.0-1
Architecture: all
Depends: python3 (>= 3.10), python3-pyqt6 (>= 6.5), python3-psutil, python3-requests, python3-dbus, python3-notify2
Maintainer: NaraVisuals <naranyala@users.noreply.github.com>
Description: Advanced LXQt desktop widgets and theme manager
 NaraVisuals provides system monitoring, theme management,
 panel configuration, and desktop entry management for LXQt.
EOF

        dpkg-deb --build "$pkgdir" "$PROJECT_DIR/dist/"
        rm -rf "$tmpdir"
        log_info "deb package built manually"
    fi
}

# =============================================================================
# rpm Package
# =============================================================================

build_rpm() {
    log_step "Building rpm package..."
    cd "$PROJECT_DIR"

    mkdir -p "$PROJECT_DIR/dist/rpmbuild"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

    # Create source tarball
    local tarname="naravisuals-lxqt-widgets-2.0.0"
    tar czf "$PROJECT_DIR/dist/rpmbuild/SOURCES/$tarname.tar.gz" \
        --transform="s,^,$tarname/," \
        --exclude='.git' \
        --exclude='dist' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        -C "$PROJECT_DIR/.." "$(basename "$PROJECT_DIR")"

    # Copy spec
    cp "$PROJECT_DIR/packaging/naravisuals-lxqt-widgets.spec" "$PROJECT_DIR/dist/rpmbuild/SPECS/"

    if check_tool rpmbuild; then
        rpmbuild -ba "$PROJECT_DIR/dist/rpmbuild/SPECS/naravisuals-lxqt-widgets.spec" \
            --define "_topdir $PROJECT_DIR/dist/rpmbuild" 2>/dev/null
        log_info "rpm package built"
        ls -la "$PROJECT_DIR/dist/rpmbuild/RPMS/"*/*.rpm 2>/dev/null || true
    else
        log_warn "rpmbuild not found, source tarball created at dist/rpmbuild/SOURCES/"
    fi
}

# =============================================================================
# AppImage
# =============================================================================

build_appimage() {
    log_step "Building AppImage..."
    cd "$PROJECT_DIR"

    local appdir="$PROJECT_DIR/dist/AppDir"
    rm -rf "$appdir"
    mkdir -p "$appdir/usr/bin"
    mkdir -p "$appdir/usr/lib/python3/dist-packages"
    mkdir -p "$appdir/usr/share/applications"
    mkdir -p "$appdir/usr/share/icons/hicolor/256x256/apps"
    mkdir -p "$appdir/usr/share/naravisuals"

    # Copy Python packages
    cp -r "$PROJECT_DIR/naravisuals" "$appdir/usr/lib/python3/dist-packages/"

    # Create launcher for theme manager
    cat > "$appdir/usr/bin/nv-theme-store" << 'EOF'
#!/usr/bin/env bash
DIR="$(dirname "$(readlink -f "$0")")"
export PYTHONPATH="$DIR/../lib/python3/dist-packages:$PYTHONPATH"
exec python3 -m naravisuals.theme_manager.app "$@"
EOF
    chmod +x "$appdir/usr/bin/nv-theme-store"

    # Create launcher for desktop manager
    cat > "$appdir/usr/bin/nv-desktop-manager" << 'EOF'
#!/usr/bin/env bash
DIR="$(dirname "$(readlink -f "$0")")"
export PYTHONPATH="$DIR/../lib/python3/dist-packages:$PYTHONPATH"
exec python3 -m naravisuals.desktop_manager.app "$@"
EOF
    chmod +x "$appdir/usr/bin/nv-desktop-manager"

    # Create launcher for control center
    cat > "$appdir/usr/bin/nv-manager" << 'EOF'
#!/usr/bin/env bash
DIR="$(dirname "$(readlink -f "$0")")"
export PYTHONPATH="$DIR/../lib/python3/dist-packages:$PYTHONPATH"
exec python3 -m naravisuals.manager.control_center "$@"
EOF
    chmod +x "$appdir/usr/bin/nv-manager"

    # Desktop file
    cat > "$appdir/nv-theme-store.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=NaraVisuals Theme Manager
Comment=Manage LXQt themes, panels, icons, fonts
Exec=nv-theme-store
Icon=nv-theme-store
Terminal=false
Categories=Utility;Settings;
EOF

    # Icon (create a simple one)
    cat > "$appdir/usr/share/icons/hicolor/256x256/apps/nv-theme-store.svg" << 'SVGEOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="32" fill="#1a1a2e"/>
  <rect x="20" y="20" width="216" height="216" rx="24" fill="#2a2a3e"/>
  <circle cx="80" cy="80" r="30" fill="#3daee9"/>
  <circle cx="176" cy="80" r="30" fill="#e74c3c"/>
  <circle cx="80" cy="176" r="30" fill="#2ecc71"/>
  <circle cx="176" cy="176" r="30" fill="#f39c12"/>
  <rect x="60" y="118" width="136" height="20" rx="10" fill="#ffffff" opacity="0.3"/>
</svg>
SVGEOF

    cp "$appdir/usr/share/icons/hicolor/256x256/apps/nv-theme-store.svg" "$appdir/nv-theme-store.svg"

    if check_tool appimagetool; then
        appimagetool "$appdir" "$PROJECT_DIR/dist/NaraVisuals-2.0.0-x86_64.AppImage" 2>/dev/null
        log_info "AppImage built"
    elif [[ -f /usr/bin/appimagetool ]]; then
        /usr/bin/appimagetool "$appdir" "$PROJECT_DIR/dist/NaraVisuals-2.0.0-x86_64.AppImage" 2>/dev/null
        log_info "AppImage built"
    else
        log_warn "appimagetool not found. AppDir created at dist/AppDir/"
        log_warn "Install with: sudo apt install appimage (or) sudo dnf install appimage"
        log_warn "Then run: appimagetool dist/AppDir dist/NaraVisuals.AppImage"
    fi
}

# =============================================================================
# Flatpak
# =============================================================================

build_flatpak() {
    log_step "Building Flatpak manifest..."
    cd "$PROJECT_DIR"

    mkdir -p "$PROJECT_DIR/dist"

    cat > "$PROJECT_DIR/dist/com.naranyala.NaraVisuals.yml" << 'EOF'
app-id: com.naranyala.NaraVisuals
runtime: org.kde.Platform
runtime-version: '6.6'
sdk: org.kde.Sdk
command: nv-theme-store
modules:
  - name: naravisuals
    buildsystem: simple
    build-commands:
      - python3 setup.py install --prefix=/app --root=/app
    sources:
      - type: dir
        path: ..
finish-args:
  - --share=ipc
  - --socket=x11
  - --socket=wayland
  - --socket=fallback-x11
  - --share=network
  - --talk-name=org.freedesktop.Notifications
  - --talk-name=org.freedesktop.DBus
  - --env=QT_QPA_PLATFORMTHEME=qt6ct
EOF

    log_info "Flatpak manifest created at dist/com.naranyala.NaraVisuals.yml"
}

# =============================================================================
# Main
# =============================================================================

usage() {
    echo ""
    echo "Usage: $0 [FORMAT...]"
    echo ""
    echo "Formats:"
    echo "  deb        Debian/Ubuntu package"
    echo "  rpm        Fedora/RHEL package"
    echo "  appimage   Portable AppImage"
    echo "  flatpak    Flatpak manifest"
    echo "  all        Build all formats"
    echo ""
    echo "Examples:"
    echo "  $0 deb           # Build deb only"
    echo "  $0 deb appimage  # Build deb + AppImage"
    echo "  $0 all           # Build everything"
    echo ""
}

main() {
    if [[ $# -eq 0 ]]; then
        usage
        exit 0
    fi

    detect_distro

    echo ""
    echo "============================================"
    echo "  NaraVisuals Package Builder"
    echo "============================================"
    echo "  Distro: $DISTRO_ID"
    echo "  Project: $PROJECT_DIR"
    echo "============================================"
    echo ""

    mkdir -p "$PROJECT_DIR/dist"

    for arg in "$@"; do
        case "$arg" in
            deb)       build_deb ;;
            rpm)       build_rpm ;;
            appimage)  build_appimage ;;
            flatpak)   build_flatpak ;;
            all)
                build_deb
                build_rpm
                build_appimage
                build_flatpak
                ;;
            clean)
                rm -rf "$PROJECT_DIR/dist"
                log_info "Cleaned dist/"
                ;;
            -h|--help) usage; exit 0 ;;
            *)         log_error "Unknown format: $arg"; usage; exit 1 ;;
        esac
    done

    echo ""
    echo "============================================"
    echo "  Build Complete"
    echo "============================================"
    echo ""
    if [[ -d "$PROJECT_DIR/dist" ]]; then
        echo "Output files:"
        find "$PROJECT_DIR/dist" -maxdepth 2 -type f \( -name "*.deb" -o -name "*.rpm" -o -name "*.AppImage" -o -name "*.yml" -o -name "*.tar.gz" \) -exec ls -lh {} \;
    fi
    echo ""
}

main "$@"
