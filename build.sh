#!/usr/bin/env bash
# ============================================================
# AI Storybook Studio - PDF Build Script
# ============================================================
# Usage:
#   ./build.sh <book-name>                # Generate images + build PDF
#   ./build.sh <book-name> --pdf-only     # Skip image generation, just build PDF
#   ./build.sh <book-name> --images-only  # Only generate images
#   ./build.sh --list                     # List available books
#
# Examples:
#   ./build.sh goldilocks
#   ./build.sh goldilocks --pdf-only
#
# Prerequisites:
#   - Python 3.8+ with: pip install google-genai Pillow pymupdf
#   - PrinceXML: https://www.princexml.com/download/
#   - Environment variable: GEMINI_IMAGE_API_KEY
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOKS_DIR="$SCRIPT_DIR/books"

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

# ─────────────────────────────────────────────────────
# List books
# ─────────────────────────────────────────────────────
if [[ "${1:-}" == "--list" ]]; then
    print_header "Available Books"
    for dir in "$BOOKS_DIR"/*/; do
        name=$(basename "$dir")
        has_html=$([[ -f "$dir/book.html" ]] && echo "✓" || echo "✗")
        has_images=$(find "$dir/images" -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  ${GREEN}${name}${NC}  (html: ${has_html}, images: ${has_images})"
    done
    echo ""
    exit 0
fi

# ─────────────────────────────────────────────────────
# Parse arguments
# ─────────────────────────────────────────────────────
if [[ -z "${1:-}" ]]; then
    print_error "Usage: ./build.sh <book-name> [--pdf-only|--images-only]"
    print_info "Run ./build.sh --list to see available books"
    exit 1
fi

BOOK_NAME="$1"
BOOK_DIR="$BOOKS_DIR/$BOOK_NAME"

if [[ ! -d "$BOOK_DIR" ]]; then
    print_error "Book not found: $BOOK_NAME"
    print_info "Available books:"
    for dir in "$BOOKS_DIR"/*/; do
        echo "    $(basename "$dir")"
    done
    exit 1
fi

MODE="all"
if [[ "${2:-}" == "--pdf-only" ]]; then
    MODE="pdf"
elif [[ "${2:-}" == "--images-only" ]]; then
    MODE="images"
fi

print_header "Building: $BOOK_NAME"

# ─────────────────────────────────────────────────────
# Step 1: Check prerequisites
# ─────────────────────────────────────────────────────
print_header "Checking Prerequisites"

if command -v python3 &>/dev/null; then
    print_success "Python: $(python3 --version 2>&1)"
else
    print_error "Python 3 not found."
    exit 1
fi

if [[ "$MODE" != "images" ]]; then
    if command -v prince &>/dev/null; then
        print_success "PrinceXML: $(prince --version 2>&1 | head -1)"
    else
        print_warning "PrinceXML not found. Install: brew install prince"
        [[ "$MODE" == "pdf" ]] && exit 1
    fi
fi

if [[ "$MODE" != "pdf" ]]; then
    if [[ -z "${GEMINI_IMAGE_API_KEY:-}" ]]; then
        print_error "GEMINI_IMAGE_API_KEY not set."
        exit 1
    else
        print_success "GEMINI_IMAGE_API_KEY is set"
    fi

    if python3 -c "from google import genai" 2>/dev/null; then
        print_success "google-genai package installed"
    else
        print_warning "Installing google-genai..."
        pip install google-genai Pillow pymupdf
    fi
fi

# ─────────────────────────────────────────────────────
# Step 2: Generate images
# ─────────────────────────────────────────────────────
if [[ "$MODE" != "pdf" ]]; then
    print_header "Generating Illustrations"
    cd "$BOOK_DIR"
    python3 generate-images.py
    TOTAL=$(find images -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
    print_success "Total images: $TOTAL"
    cd "$SCRIPT_DIR"
fi

# ─────────────────────────────────────────────────────
# Step 3: Generate PDF with PrinceXML
# ─────────────────────────────────────────────────────
if [[ "$MODE" != "images" ]]; then
    if command -v prince &>/dev/null; then
        print_header "Building PDF with PrinceXML"

        OUTPUT_FILE="$BOOK_DIR/${BOOK_NAME}.pdf"

        print_info "Input:  $BOOK_DIR/book.html"
        print_info "Output: $OUTPUT_FILE"
        echo ""

        prince "$BOOK_DIR/book.html" \
            --output="$OUTPUT_FILE" \
            --page-size="8.5in 11in" \
            --no-artificial-fonts \
            2>&1 | while IFS= read -r line; do
                echo "  prince: $line"
            done

        # Strip Prince watermark annotation
        if [[ -f "$OUTPUT_FILE" ]]; then
            python3 -c "
import fitz, shutil, sys
pdf_path = sys.argv[1]
tmp_path = pdf_path + '.tmp'
doc = fitz.open(pdf_path)
for page in doc:
    for annot in list(page.annots() or []):
        page.delete_annot(annot)
doc.save(tmp_path, deflate=True, garbage=4)
doc.close()
shutil.move(tmp_path, pdf_path)
" "$OUTPUT_FILE" 2>/dev/null || true

            FILE_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
            print_success "PDF generated: $OUTPUT_FILE ($FILE_SIZE)"

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
    fi
fi

# ─────────────────────────────────────────────────────
# Done
# ─────────────────────────────────────────────────────
print_header "Complete: $BOOK_NAME"
echo -e "  ${GREEN}$BOOK_DIR/${NC}"
echo -e "    book.html           - HTML source"
echo -e "    generate-images.py  - Image generation script"
echo -e "    images/             - Illustrations"
[[ -f "$BOOK_DIR/${BOOK_NAME}.pdf" ]] && echo -e "    ${BOOK_NAME}.pdf    - Final PDF"
echo ""
