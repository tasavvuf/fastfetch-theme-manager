#!/usr/bin/env bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

echo -e "${BLUE}
  _____ _______ __  __ 
 |  ___|__   __|  \/  |
 | |_     | |  | \  / |
 |  _|    | |  | |\/| |
 |_|      |_|  |_|  |_|  v3.0.0
${NC}"

# --- Detect install target ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HAS_LOCAL_SOURCE=false
if [ -d "$SCRIPT_DIR/src/ftm" ] && [ -f "$SCRIPT_DIR/src/ftm/cli.py" ]; then
    HAS_LOCAL_SOURCE=true
fi

# --- Determine install paths ---
if [ "$EUID" -eq 0 ]; then
    INSTALL_BIN="/usr/local/bin"
    INSTALL_LIB="/usr/local/lib/ftm"
    echo -e "${YELLOW}* Running as root — installing to ${INSTALL_BIN}${NC}"
else
    INSTALL_BIN="$HOME/.local/bin"
    INSTALL_LIB="$HOME/.local/lib/ftm"
    mkdir -p "$INSTALL_BIN" "$INSTALL_LIB"
fi

# --- Install the package ---
if $HAS_LOCAL_SOURCE; then
    echo -e "${BLUE}* Installing from local source...${NC}"
    mkdir -p "$INSTALL_LIB"
    cp -r "$SCRIPT_DIR/src/ftm" "$INSTALL_LIB/"
    chmod -R 644 "$INSTALL_LIB/ftm/"*.py
    chmod 755 "$INSTALL_LIB/ftm" "$INSTALL_LIB/ftm/__main__.py"
    echo -e "${GREEN}* Package installed to $INSTALL_LIB/ftm${NC}"
else
    echo -e "${BLUE}* Downloading from GitHub...${NC}"
    mkdir -p "$INSTALL_LIB"
    TMP_DIR=$(mktemp -d)
    echo -e "${BLUE}* Cloning repository...${NC}"
    if command -v git &>/dev/null; then
        git clone --depth 1 https://github.com/itz-dev-tasavvuf/fastfetch-theme-manager.git "$TMP_DIR" 2>/dev/null || {
            echo -e "${RED}* Git failed. Trying pip...${NC}"
        }
    fi
    if [ -d "$TMP_DIR/src/ftm" ]; then
        cp -r "$TMP_DIR/src/ftm" "$INSTALL_LIB/"
        chmod -R 644 "$INSTALL_LIB/ftm/"*.py
        chmod 755 "$INSTALL_LIB/ftm" "$INSTALL_LIB/ftm/__main__.py"
    else
        echo -e "${RED}* Could not fetch package. Falling back to pip...${NC}"
        pip3 install --user git+https://github.com/itz-dev-tasavvuf/fastfetch-theme-manager.git 2>/dev/null && {
            echo -e "${GREEN}* Installed via pip${NC}"
            echo -e "\n${GREEN}Installation Complete!${NC}"
            echo -e "Try: ${BLUE}ftm info${NC}"
            exit 0
        }
        echo -e "${RED}* All install methods failed.${NC}"
        exit 1
    fi
    rm -rf "$TMP_DIR"
fi

# --- Create launcher script ---
LAUNCHER="$INSTALL_BIN/ftm"
cat > "$LAUNCHER" << 'LAUNCHER'
#!/usr/bin/env python3
import sys
import os

# Determine install location
launcher_path = os.path.abspath(__file__)
lib_dir = os.path.normpath(os.path.join(os.path.dirname(launcher_path), "..", "lib", "ftm"))

# Also check relative to the script location
pkg_dir = os.path.join(lib_dir, "ftm")
if os.path.isdir(pkg_dir):
    sys.path.insert(0, os.path.dirname(pkg_dir))
else:
    # Fallback: check if we're in the source tree
    for candidate in [
        os.path.join(os.path.dirname(launcher_path), "..", "src"),
        os.path.join(os.path.dirname(launcher_path), "src"),
    ]:
        if os.path.isdir(os.path.join(candidate, "ftm")):
            sys.path.insert(0, os.path.abspath(candidate))
            break

from ftm.cli import main
main()
LAUNCHER

chmod +x "$LAUNCHER"
echo -e "${GREEN}* Launcher installed to $LAUNCHER${NC}"

# --- Dependencies ---
echo -e "\n${BLUE}* Checking dependencies...${NC}"
MISSING=0
if ! command -v fastfetch &>/dev/null; then
    echo -e "${RED}* Fastfetch is missing.${NC}"
    MISSING=1
else
    echo -e "${GREEN}* Fastfetch: $(fastfetch --version 2>&1 | head -1)${NC}"
fi
if ! command -v fzf &>/dev/null; then
    echo -e "${YELLOW}* fzf missing (optional, for 'ftm pick')${NC}"
fi
if [ $MISSING -eq 1 ]; then
    echo -e "\n${BLUE}* Install fastfetch with:${NC}"
    for mgr in pacman apt dnf zypper emerge apk xbps-install brew; do
        if command -v $mgr &>/dev/null; then
            case $mgr in
                pacman) echo "  sudo pacman -S fastfetch fzf";;
                apt) echo "  sudo apt install fastfetch fzf";;
                dnf) echo "  sudo dnf install fastfetch fzf";;
                zypper) echo "  sudo zypper install fastfetch fzf";;
                emerge) echo "  sudo emerge --ask fastfetch";;
                apk) echo "  sudo apk add fastfetch fzf";;
                xbps-install) echo "  sudo xbps-install -S fastfetch fzf";;
                brew) echo "  brew install fastfetch fzf";;
            esac
            break
        fi
    done
fi

# --- PATH check ---
if [ "$EUID" -ne 0 ]; then
    case ":$PATH:" in
        *":$INSTALL_BIN:"*) ;;
        *)
            echo -e "\n${YELLOW}* Add to your PATH:${NC}"
            echo "  export PATH=\"$INSTALL_BIN:\$PATH\""
            echo "  (add this to ~/.bashrc or ~/.zshrc)"
            ;;
    esac
fi

echo -e "\n${GREEN}Installation Complete!${NC}"
echo -e "Run: ${BLUE}ftm info${NC}  or  ${BLUE}ftm help${NC}"
