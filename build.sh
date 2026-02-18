#!/usr/bin/env bash
# ============================================================
# Goldilocks and the Three Bears - PDF Build Script
# ============================================================
# Usage:
#   ./build.sh              # Generate images + build PDF
#   ./build.sh --pdf-only   # Skip image generation, just build PDF
#   ./build.sh --images-only # Only generate images
#
# Prerequisites:
#   - Python 3.8+ with: pip install google-genai Pillow
#   - PrinceXML: https://www.princexml.com/download/
#   - Environment variable: GEMINI_IMAGE_API_KEY
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_success() { echo -e "  ${GREEN}✓${NC} $1"; }
print_warning() { echo -e "  ${YELLOW}!${NC} $1"; }
print_error()   { echo -e "  ${RED}✗${NC} $1"; }
print_info()    { echo -e "  ${BLUE}→${NC} $1"; }

# Parse arguments
MODE="all"
if [[ "${1:-}" == "--pdf-only" ]]; then
    MODE="pdf"
elif [[ "${1:-}" == "--images-only" ]]; then
    MODE="images"
fi

# ─────────────────────────────────────────────────────
# Step 1: Check prerequisites
# ─────────────────────────────────────────────────────
print_header "Checking Prerequisites"

# Check Python
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_success "Python: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Install from https://python.org"
    exit 1
fi

# Check PrinceXML
if [[ "$MODE" != "images" ]]; then
    if command -v prince &>/dev/null; then
        PRINCE_VERSION=$(prince --version 2>&1 | head -1)
        print_success "PrinceXML: $PRINCE_VERSION"
    else
        print_warning "PrinceXML not found."
        print_info "Install from: https://www.princexml.com/download/"
        print_info "On macOS: brew install prince"
        if [[ "$MODE" == "pdf" ]]; then
            exit 1
        fi
    fi
fi

# Check API key (only needed for image generation)
if [[ "$MODE" != "pdf" ]]; then
    if [[ -z "${GEMINI_IMAGE_API_KEY:-}" ]]; then
        print_error "GEMINI_IMAGE_API_KEY not set."
        print_info "Get an API key at: https://aistudio.google.com/apikey"
        print_info "Then run: export GEMINI_IMAGE_API_KEY=\"your-key-here\""
        exit 1
    else
        print_success "GEMINI_IMAGE_API_KEY is set"
    fi
fi

# Check Python packages
if [[ "$MODE" != "pdf" ]]; then
    if python3 -c "from google import genai" 2>/dev/null; then
        print_success "google-genai package installed"
    else
        print_warning "google-genai not installed. Installing..."
        pip install google-genai Pillow
        print_success "Packages installed"
    fi
fi

# ─────────────────────────────────────────────────────
# Step 2: Generate images
# ─────────────────────────────────────────────────────
if [[ "$MODE" != "pdf" ]]; then
    print_header "Generating Illustrations"

    # Count existing images
    EXISTING=$(find images -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
    print_info "Found $EXISTING existing images in images/"

    python3 generate-images.py

    TOTAL=$(find images -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
    print_success "Total images: $TOTAL"
fi

# ─────────────────────────────────────────────────────
# Step 3: Generate PDF with PrinceXML
# ─────────────────────────────────────────────────────
if [[ "$MODE" != "images" ]]; then
    if command -v prince &>/dev/null; then
        print_header "Building PDF with PrinceXML"

        OUTPUT_FILE="goldilocks-and-the-three-bears.pdf"

        print_info "Input:  book.html"
        print_info "Output: $OUTPUT_FILE"
        echo ""

        prince book.html \
            --output="$OUTPUT_FILE" \
            --pdf-profile="PDF/A-3b" \
            --page-size="8.5in 11in" \
            --no-artificial-fonts \
            2>&1 | while IFS= read -r line; do
                echo "  prince: $line"
            done

        if [[ -f "$OUTPUT_FILE" ]]; then
            FILE_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
            PAGE_COUNT=$(python3 -c "
try:
    import subprocess
    result = subprocess.run(['prince', '--version'], capture_output=True, text=True)
    print('~14')
except:
    print('~14')
" 2>/dev/null || echo "~14")
            print_success "PDF generated: $OUTPUT_FILE ($FILE_SIZE)"
            echo ""

            # Try to open on macOS
            if [[ "$(uname)" == "Darwin" ]]; then
                print_info "Opening PDF..."
                open "$OUTPUT_FILE" 2>/dev/null || true
            fi
        else
            print_error "PDF generation failed!"
            exit 1
        fi
    else
        print_warning "Skipping PDF generation (PrinceXML not installed)"
        print_info "To generate the PDF manually:"
        print_info "  prince book.html -o goldilocks-and-the-three-bears.pdf"
    fi
fi

# ─────────────────────────────────────────────────────
# Done
# ─────────────────────────────────────────────────────
print_header "Complete!"
echo -e "  Project files:"
echo -e "    ${GREEN}book.html${NC}                            - HTML source"
echo -e "    ${GREEN}images/${NC}                              - Generated illustrations"
echo -e "    ${GREEN}generate-images.py${NC}                   - Image generation script"
if [[ -f "goldilocks-and-the-three-bears.pdf" ]]; then
echo -e "    ${GREEN}goldilocks-and-the-three-bears.pdf${NC}   - Final PDF"
fi
echo ""
