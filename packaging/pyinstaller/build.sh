#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# NaraVisuals PyInstaller Builder
# Builds standalone executables for all GUI apps
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_DIR/dist"
SPEC_DIR="$SCRIPT_DIR/specs"

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
# Pre-checks
# =============================================================================

check_pyinstaller() {
    if ! command -v pyinstaller &>/dev/null; then
        log_error "PyInstaller not found."
        echo "  Install with: pip install pyinstaller"
        echo "  Or: pipx install pyinstaller"
        exit 1
    fi
    log_info "PyInstaller $(pyinstaller --version 2>/dev/null || echo 'installed')"
}

check_python() {
    if ! command -v python3 &>/dev/null; then
        log_error "Python 3 not found."
        exit 1
    fi
    log_info "Python $(python3 --version 2>&1 | awk '{print $2}')"
}

# =============================================================================
# Build Functions
# =============================================================================

build_app() {
    local name="$1"
    local module="$2"
    local desc="$3"

    log_step "Building $name ($desc)..."

    pyinstaller \
        --name "$name" \
        --onefile \
        --windowed \
        --noconfirm \
        --clean \
        --distpath "$BUILD_DIR" \
        --workpath "$BUILD_DIR/build/$name" \
        --specpath "$SPEC_DIR" \
        --add-data "$PROJECT_DIR/naravisuals/theme_manager/data:naravisuals/theme_manager/data" \
        --hidden-import naravisuals.core.theme_engine \
        --hidden-import naravisuals.core.config_manager \
        --hidden-import naravisuals.core.base_widget \
        --hidden-import naravisuals.manager.control_center \
        --hidden-import naravisuals.manager.app \
        --hidden-import naravisuals.theme_manager.app \
        --hidden-import naravisuals.desktop_manager.app \
        --hidden-import naravisuals.sddm_manager.app \
        --collect-submodules naravisuals \
        "$PROJECT_DIR/run_${name#nv-}.sh" 2>/dev/null || true

    # Build from module directly
    pyinstaller \
        --name "$name" \
        --onefile \
        --windowed \
        --noconfirm \
        --clean \
        --distpath "$BUILD_DIR" \
        --workpath "$BUILD_DIR/build/$name" \
        --specpath "$SPEC_DIR" \
        --hidden-import naravisuals \
        --hidden-import naravisuals.core \
        --hidden-import naravisuals.core.theme_engine \
        --hidden-import naravisuals.core.config_manager \
        --hidden-import naravisuals.manager \
        --hidden-import naravisuals.manager.control_center \
        --hidden-import naravisuals.theme_manager \
        --hidden-import naravisuals.theme_manager.app \
        --hidden-import naravisuals.desktop_manager \
        --hidden-import naravisuals.desktop_manager.app \
        --hidden-import naravisuals.sddm_manager \
        --hidden-import naravisuals.sddm_manager.app \
        --collect-all naravisuals \
        --paths "$PROJECT_DIR" \
        -c "import sys; sys.path.insert(0, '$PROJECT_DIR'); from naravisuals.${module} import main; main()" \
        2>/dev/null

    if [[ -f "$BUILD_DIR/$name" ]]; then
        log_info "Built: $BUILD_DIR/$name ($(du -h "$BUILD_DIR/$name" | cut -f1))"
    else
        log_error "Failed to build $name"
        return 1
    fi
}

build_app_simple() {
    local name="$1"
    local module_path="$2"
    local module_name="$3"

    log_step "Building $name..."

    cd "$PROJECT_DIR"

    # Create a temporary entry script
    local tmp_entry="$BUILD_DIR/build_${name}.py"
    cat > "$tmp_entry" << PYEOF
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath("$PROJECT_DIR")))
from $module_path import main
main()
PYEOF

    pyinstaller \
        --name "$name" \
        --onefile \
        --windowed \
        --noconfirm \
        --clean \
        --distpath "$BUILD_DIR" \
        --workpath "$BUILD_DIR/build/$name" \
        --specpath "$SPEC_DIR" \
        --hidden-import $module_name \
        --hidden-import naravisuals.core \
        --hidden-import naravisuals.core.theme_engine \
        --hidden-import naravisuals.core.config_manager \
        --hidden-import naravisuals.core.base_widget \
        --collect-all naravisuals \
        "$tmp_entry" 2>/dev/null

    rm -f "$tmp_entry"

    if [[ -f "$BUILD_DIR/$name" ]]; then
        chmod +x "$BUILD_DIR/$name"
        log_info "Built: $BUILD_DIR/$name ($(du -h "$BUILD_DIR/$name" | cut -f1))"
    else
        log_error "Failed: $name"
    fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo ""
    echo "============================================"
    echo "  NaraVisuals PyInstaller Builder"
    echo "============================================"
    echo ""

    check_python
    check_pyinstaller

    mkdir -p "$BUILD_DIR" "$SPEC_DIR"

    local apps=(
        "nv-manager:naravisuals.manager.control_center:Control Center"
        "nv-manager-legacy:naravisuals.manager.app:Settings Hub (Legacy)"
        "nv-theme-store:naravisuals.theme_manager.app:Theme Manager"
        "nv-desktop-manager:naravisuals.desktop_manager.app:Desktop Manager"
        "nv-sddm-manager:naravisuals.sddm_manager.app:SDDM Manager"
    )

    echo ""
    echo "Building apps..."
    echo ""

    for entry in "${apps[@]}"; do
        IFS=':' read -r name module desc <<< "$entry"
        build_app_simple "$name" "$module" "$name"
        echo ""
    done

    echo "============================================"
    echo "  Build Complete"
    echo "============================================"
    echo ""
    echo "Output: $BUILD_DIR/"
    echo ""

    if [[ -d "$BUILD_DIR" ]]; then
        echo "Executables:"
        for f in "$BUILD_DIR"/nv-*; do
            if [[ -f "$f" ]]; then
                echo "  $(basename "$f")  ($(du -h "$f" | cut -f1))"
            fi
        done
    fi

    echo ""
    echo "To install system-wide:"
    echo "  sudo cp $BUILD_DIR/nv-* /usr/local/bin/"
    echo ""
}

# Parse arguments
case "${1:-all}" in
    all)
        main
        ;;
    nv-manager|nv-manager-legacy|nv-theme-store|nv-desktop-manager|nv-sddm-manager)
        check_python
        check_pyinstaller
        mkdir -p "$BUILD_DIR" "$SPEC_DIR"
        case "$1" in
            nv-manager)          build_app_simple "$1" "naravisuals.manager.control_center" "$1" ;;
            nv-manager-legacy)   build_app_simple "$1" "naravisuals.manager.app" "$1" ;;
            nv-theme-store)      build_app_simple "$1" "naravisuals.theme_manager.app" "$1" ;;
            nv-desktop-manager)  build_app_simple "$1" "naravisuals.desktop_manager.app" "$1" ;;
            nv-sddm-manager)     build_app_simple "$1" "naravisuals.sddm_manager.app" "$1" ;;
        esac
        ;;
    clean)
        rm -rf "$BUILD_DIR" "$SPEC_DIR"
        log_info "Cleaned build artifacts"
        ;;
    *)
        echo "Usage: $0 [all|nv-manager|nv-manager-legacy|nv-theme-store|nv-desktop-manager|nv-sddm-manager|clean]"
        exit 1
        ;;
esac
