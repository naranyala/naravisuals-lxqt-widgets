#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SPEC_FILE="$PROJECT_DIR/packaging/naravisuals-lxqt-widgets.spec"
BUILD_DIR="$PROJECT_DIR/rpmbuild"

usage() {
    cat << EOF
NaraVisuals RPM Build Script

Usage: $(basename "$0") [OPTIONS]

Options:
  --setup         Initialize RPM build environment
  --srpm          Build source RPM
  --rpm           Build binary RPM
  --all           Build both source and binary RPMs
  --clean         Clean build directory
  --install       Install built RPM (requires root)
  --help          Show this help message

Examples:
  $(basename "$0") --setup              # Initialize build environment
  $(basename "$0") --all                # Build all RPMs
  $(basename "$0") --install            # Install the built RPM

EOF
    exit 0
}

log_info() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

log_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

setup_build_env() {
    log_info "Setting up RPM build environment..."
    
    # Check for required tools
    if ! command -v rpmbuild &> /dev/null; then
        log_error "rpmbuild not found. Install rpm-build package:"
        echo "  Fedora: sudo dnf install rpm-build"
        echo "  RHEL:   sudo yum install rpm-build"
        exit 1
    fi
    
    # Create build directories
    mkdir -p "$BUILD_DIR"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    
    # Create tarball
    log_info "Creating source tarball..."
    cd "$PROJECT_DIR"
    tar czf "$BUILD_DIR/SOURCES/naravisuals-lxqt-widgets-2.0.0.tar.gz" \
        --transform='s,^,naravisuals-lxqt-widgets-2.0.0/,' \
        --exclude='.git' \
        --exclude='rpmbuild' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        .
    
    # Copy spec file
    cp "$SPEC_FILE" "$BUILD_DIR/SPECS/"
    
    log_info "Build environment ready at: $BUILD_DIR"
}

build_srpm() {
    log_info "Building source RPM..."
    rpmbuild -bs "$BUILD_DIR/SPECS/naravisuals-lxqt-widgets.spec" \
        --define "_topdir $BUILD_DIR"
    
    log_info "Source RPM built successfully"
    ls -la "$BUILD_DIR"/SRPMS/*.src.rpm
}

build_rpm() {
    log_info "Building binary RPM..."
    rpmbuild -bb "$BUILD_DIR/SPECS/naravisuals-lxqt-widgets.spec" \
        --define "_topdir $BUILD_DIR"
    
    log_info "Binary RPM built successfully"
    ls -la "$BUILD_DIR"/RPMS/*/*.rpm
}

build_all() {
    build_srpm
    build_rpm
}

clean_build() {
    log_info "Cleaning build directory..."
    rm -rf "$BUILD_DIR"
    log_info "Build directory cleaned"
}

install_rpm() {
    local rpm_file=$(ls -t "$BUILD_DIR"/RPMS/*/*.rpm 2>/dev/null | head -1)
    
    if [ -z "$rpm_file" ]; then
        log_error "No RPM found. Build first with: $(basename "$0") --all"
        exit 1
    fi
    
    log_info "Installing RPM: $rpm_file"
    sudo rpm -ivh --force "$rpm_file"
    
    log_info "Installation complete"
    echo ""
    echo "Next steps:"
    echo "  1. Start the daemon: systemctl --user start naravisuals-daemon"
    echo "  2. Enable auto-start: systemctl --user enable naravisuals-daemon"
    echo "  3. Add widgets: Right-click panel > Add Widgets > NaraVisuals"
}

# Parse arguments
ACTION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --setup)
            ACTION="setup"
            shift
            ;;
        --srpm)
            ACTION="srpm"
            shift
            ;;
        --rpm)
            ACTION="rpm"
            shift
            ;;
        --all)
            ACTION="all"
            shift
            ;;
        --clean)
            ACTION="clean"
            shift
            ;;
        --install)
            ACTION="install"
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

if [ -z "$ACTION" ]; then
    log_error "No action specified"
    usage
fi

# Execute action
case $ACTION in
    setup)
        setup_build_env
        ;;
    srpm)
        build_srpm
        ;;
    rpm)
        build_rpm
        ;;
    all)
        build_all
        ;;
    clean)
        clean_build
        ;;
    install)
        install_rpm
        ;;
esac
