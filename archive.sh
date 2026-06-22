#!/usr/bin/env bash
set -e

# =============================================================================
# NaraVisuals LXQt Widgets - Archive Script
# =============================================================================
# Creates a clean source archive excluding build artifacts, caches,
# and external dependencies.
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_NAME="naravisuals-lxqt-widgets"
VERSION=$(grep -oP 'version\s*=\s*"\K[^"]+' "$SCRIPT_DIR/setup.py" 2>/dev/null || echo "2.0.0")
TIMESTAMP=$(date +%Y%m%d)
ARCHIVE_NAME="${PROJECT_NAME}-${VERSION}-${TIMESTAMP}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    cat << EOF
NaraVisuals Archive Script

Usage: $(basename "$0") [OPTIONS]

Options:
  --format FORMAT    Archive format: tar.gz (default), tar.xz, zip
  --output DIR       Output directory (default: current directory)
  --full             Include everything (no exclusions)
  --source-only      Source code only (no packaging/docs)
  --help             Show this help message

Examples:
  $(basename "$0")                          # Create tar.gz in current dir
  $(basename "$0") --format tar.xz         # Create tar.xz
  $(basename "$0") --output /tmp            # Save to /tmp
  $(basename "$0") --source-only            # Source code only

EOF
    exit 0
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
FORMAT="tar.gz"
OUTPUT_DIR="."
FULL=false
SOURCE_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --full)
            FULL=true
            shift
            ;;
        --source-only)
            SOURCE_ONLY=true
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate format
if [[ ! "$FORMAT" =~ ^(tar\.gz|tar\.xz|zip)$ ]]; then
    log_error "Invalid format: $FORMAT (use tar.gz, tar.xz, or zip)"
    exit 1
fi

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Preview and confirm
echo ""
echo "============================================"
echo "  Archive Preview"
echo "============================================"
echo "  Name:     ${ARCHIVE_NAME}.${FORMAT}"
echo "  Output:   ${OUTPUT_DIR}/"
echo "  Mode:     $(if $SOURCE_ONLY; then echo 'Source-only'; elif $FULL; then echo 'Full (includes deps)'; else echo 'Standard'; fi)"
echo "============================================"
echo ""

read -p "Proceed with archive creation? [Y/n]: " CONFIRM
if [[ "$CONFIRM" =~ ^[Nn]$ ]]; then
    log_warn "Archive creation cancelled by user"
    exit 0
fi

# Create temporary staging directory
STAGING_DIR=$(mktemp -d)
STAGING_PROJECT="${STAGING_DIR}/${PROJECT_NAME}"

log_info "Creating archive: ${ARCHIVE_NAME}.${FORMAT}"
log_info "Staging to: ${STAGING_DIR}"

# Copy project files
log_info "Copying project files..."
cp -a "$SCRIPT_DIR" "${STAGING_PROJECT}"

# Clean staging directory
log_info "Cleaning staging directory..."

# Always exclude these
cd "${STAGING_PROJECT}"

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remove .pyc files
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Remove .pyo files
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Remove build artifacts
rm -rf build/ dist/ *.egg-info/ .eggs/ 2>/dev/null || true

# Remove C++ build artifacts
rm -rf native-plugin/build/ 2>/dev/null || true
find . -name "*.o" -delete 2>/dev/null || true
find . -name "*.so" -delete 2>/dev/null || true
find . -name "*.a" -delete 2>/dev/null || true

# Remove IDE files
rm -rf .idea/ .vscode/ *.swp *.swo 2>/dev/null || true

# Remove OS files
rm -rf .DS_Store Thumbs.db 2>/dev/null || true

# Remove log files
find . -name "*.log" -delete 2>/dev/null || true

# Remove .pytest_cache
rm -rf .pytest_cache/ 2>/dev/null || true

# Remove mypy cache
rm -rf .mypy_cache/ 2>/dev/null || true

# Remove downloaded dependencies (unless --full)
if [[ "$FULL" == false ]]; then
    log_info "Excluding external dependencies..."
    rm -rf liblxqt-2.3.0/ 2>/dev/null || true
    rm -rf lxqt-panel-2.3.2/ 2>/dev/null || true
    rm -f *.tar.xz *.tar.xz.asc *.dsc *.debian.tar.xz *.orig.tar.xz 2>/dev/null || true
fi

# Source-only mode
if [[ "$SOURCE_ONLY" == true ]]; then
    log_info "Source-only mode: removing packaging and docs..."
    rm -rf packaging/ docs/ desktop/ desktop-panel/ tests/ 2>/dev/null || true
    rm -f PKGBUILD install.sh refactor.py *.md 2>/dev/null || true
fi

# Remove .git directory (we want source archive, not git repo)
rm -rf .git/ 2>/dev/null || true

# Remove this script from archive
rm -f archive.sh 2>/dev/null || true

# Go back to staging root
cd "${STAGING_DIR}"

# Create archive
log_info "Creating ${FORMAT} archive..."

case "$FORMAT" in
    tar.gz)
        tar czf "${OUTPUT_DIR}/${ARCHIVE_NAME}.tar.gz" "${PROJECT_NAME}"
        ;;
    tar.xz)
        tar cJf "${OUTPUT_DIR}/${ARCHIVE_NAME}.tar.xz" "${PROJECT_NAME}"
        ;;
    zip)
        zip -r "${OUTPUT_DIR}/${ARCHIVE_NAME}.zip" "${PROJECT_NAME}"
        ;;
esac

# Cleanup staging
rm -rf "${STAGING_DIR}"

# Get archive size
ARCHIVE_FILE="${OUTPUT_DIR}/${ARCHIVE_NAME}.${FORMAT}"
if [[ -f "$ARCHIVE_FILE" ]]; then
    SIZE=$(du -h "$ARCHIVE_FILE" | cut -f1)
    log_info "Archive created successfully!"
    echo ""
    echo "============================================"
    echo "  Archive: ${ARCHIVE_FILE}"
    echo "  Size:    ${SIZE}"
    echo "  Format:  ${FORMAT}"
    echo "============================================"
    echo ""
    
    # Show contents summary
    log_info "Archive contents:"
    case "$FORMAT" in
        tar.gz)
            tar tzf "$ARCHIVE_FILE" | head -30
            ;;
        tar.xz)
            tar tJf "$ARCHIVE_FILE" | head -30
            ;;
        zip)
            zipinfo -1 "$ARCHIVE_FILE" | head -30
            ;;
    esac
    
    TOTAL=$(case "$FORMAT" in
        tar.gz) tar tzf "$ARCHIVE_FILE" | wc -l ;;
        tar.xz) tar tJf "$ARCHIVE_FILE" | wc -l ;;
        zip) zipinfo -1 "$ARCHIVE_FILE" | wc -l ;;
    esac)
    
    if [[ $TOTAL -gt 30 ]]; then
        echo "  ... and $((TOTAL - 30)) more files"
    fi
    echo "  Total: ${TOTAL} files/directories"
else
    log_error "Failed to create archive"
    exit 1
fi
