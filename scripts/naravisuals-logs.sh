#!/usr/bin/env bash
# =============================================================================
# NaraVisuals LXQt Widgets - Log Viewer
# =============================================================================
# View and filter daemon logs.
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat << EOF
NaraVisuals Log Viewer

Usage: $(basename "$0") [OPTIONS]

Options:
  -f, --follow        Follow logs in real-time
  -n, --lines NUM     Number of lines to show (default: 50)
  -e, --errors        Show only errors
  -w, --warnings      Show only warnings
  -g, --grep PATTERN  Filter by pattern
  -t, --timestamp     Show timestamps
  -c, --clear         Clear log buffer
  -s, --status        Show daemon status
  -h, --help          Show this help message

Examples:
  $(basename "$0")                    # Show last 50 lines
  $(basename "$0") -f                 # Follow logs
  $(basename "$0") -n 100             # Show last 100 lines
  $(basename "$0") -e                 # Show only errors
  $(basename "$0") -g "D-Bus"         # Filter by D-Bus
  $(basename "$0") -s                 # Show daemon status

EOF
    exit 0
}

show_status() {
    echo ""
    echo -e "${BLUE}--- Daemon Status ---${NC}"
    
    if systemctl --user is-active naravisuals-daemon.service &>/dev/null; then
        echo -e "Status: ${GREEN}Active${NC}"
    else
        echo -e "Status: ${RED}Inactive${NC}"
    fi
    
    if systemctl --user is-enabled naravisuals-daemon.service &>/dev/null; then
        echo -e "Auto-start: ${GREEN}Enabled${NC}"
    else
        echo -e "Auto-start: ${YELLOW}Disabled${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}--- D-Bus Service ---${NC}"
    
    if python3 -c "
import dbus
bus = dbus.SessionBus()
names = bus.list_names()
found = any('naravisuals' in name.lower() for name in names)
exit(0 if found else 1)
" 2>/dev/null; then
        echo -e "Status: ${GREEN}Registered${NC}"
    else
        echo -e "Status: ${RED}Not Registered${NC}"
    fi
    
    echo ""
}

clear_logs() {
    journalctl --user -u naravisuals-daemon --rotate --vacuum-time=1s 2>/dev/null || true
    echo -e "${GREEN}Log buffer cleared${NC}"
}

# Defaults
FOLLOW=false
LINES=50
FILTER_ERRORS=false
FILTER_WARNINGS=false
GREP_PATTERN=""
SHOW_STATUS=false
CLEAR=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -n|--lines)
            LINES="$2"
            shift 2
            ;;
        -e|--errors)
            FILTER_ERRORS=true
            shift
            ;;
        -w|--warnings)
            FILTER_WARNINGS=true
            shift
            ;;
        -g|--grep)
            GREP_PATTERN="$2"
            shift 2
            ;;
        -t|--timestamp)
            # Already shown by default
            shift
            ;;
        -c|--clear)
            CLEAR=true
            shift
            ;;
        -s|--status)
            SHOW_STATUS=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Show status if requested
if [[ "$SHOW_STATUS" == true ]]; then
    show_status
    exit 0
fi

# Clear logs if requested
if [[ "$CLEAR" == true ]]; then
    clear_logs
    exit 0
fi

# Build journalctl command
JOURNAL_CMD="journalctl --user -u naravisuals-daemon --no-pager"

if [[ "$FOLLOW" == true ]]; then
    JOURNAL_CMD="$JOURNAL_CMD -f"
fi

JOURNAL_CMD="$JOURNAL_CMD -n $LINES"

# Apply filters
if [[ "$FILTER_ERRORS" == true ]]; then
    JOURNAL_CMD="$JOURNAL_CMD | grep -i 'error\|fail\|critical'"
fi

if [[ "$FILTER_WARNINGS" == true ]]; then
    JOURNAL_CMD="$JOURNAL_CMD | grep -i 'warn\|warning'"
fi

if [[ -n "$GREP_PATTERN" ]]; then
    JOURNAL_CMD="$JOURNAL_CMD | grep -i '$GREP_PATTERN'"
fi

# Execute
echo -e "${BLUE}--- NaraVisuals Daemon Logs ---${NC}"
echo ""

if eval "$JOURNAL_CMD" 2>/dev/null; then
    :
else
    echo -e "${YELLOW}No logs found. Daemon may not be running.${NC}"
    echo ""
    echo "Start the daemon with:"
    echo "  systemctl --user start naravisuals-daemon"
fi
