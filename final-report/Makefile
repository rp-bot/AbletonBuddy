# Makefile for LaTeX report compilation

# Main LaTeX file
MAIN = report
TEX = $(MAIN).tex
PDF = $(MAIN).pdf

# LaTeX compiler
LATEX = pdflatex
BIBTEX = bibtex

# Compilation flags
LATEX_FLAGS = -interaction=nonstopmode -halt-on-error

# Default target
all: $(PDF)

# Build PDF from LaTeX
$(PDF): $(TEX)
	@echo "Compiling LaTeX document..."
	$(LATEX) $(LATEX_FLAGS) $(TEX)
	@echo "Building table of contents..."
	$(LATEX) $(LATEX_FLAGS) $(TEX)
	@echo "Final compilation..."
	$(LATEX) $(LATEX_FLAGS) $(TEX)
	@echo "PDF generated: $(PDF)"
	@echo "Cleaning up auxiliary files..."
	@rm -f *.aux *.log *.out *.toc *.bbl *.blg *.synctex.gz *.fdb_latexmk *.fls
	@echo "Done!"

# Build with bibliography (if you add .bib file later)
bib: $(TEX)
	@echo "Compiling with bibliography..."
	$(LATEX) $(LATEX_FLAGS) $(TEX)
	$(BIBTEX) $(MAIN)
	$(LATEX) $(LATEX_FLAGS) $(TEX)
	$(LATEX) $(LATEX_FLAGS) $(TEX)
	@echo "PDF generated: $(PDF)"
	@echo "Cleaning up auxiliary files..."
	@rm -f *.aux *.log *.out *.toc *.bbl *.blg *.synctex.gz *.fdb_latexmk *.fls
	@echo "Done!"

# Clean auxiliary files
clean:
	@echo "Cleaning auxiliary files..."
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.synctex.gz *.fdb_latexmk *.fls

# Clean everything including PDF
cleanall: clean
	@echo "Cleaning PDF..."
	rm -f $(PDF)

# View PDF (requires evince or change to your PDF viewer)
view: $(PDF)
	@if command -v evince > /dev/null; then \
		evince $(PDF) & \
	elif command -v xdg-open > /dev/null; then \
		xdg-open $(PDF) & \
	elif command -v open > /dev/null; then \
		open $(PDF) & \
	else \
		echo "Please open $(PDF) manually"; \
	fi

# Help
help:
	@echo "Available targets:"
	@echo "  make          - Compile the LaTeX document to PDF"
	@echo "  make bib      - Compile with bibliography"
	@echo "  make clean    - Remove auxiliary files (.aux, .log, .toc, etc.)"
	@echo "  make cleanall - Remove auxiliary files and PDF"
	@echo "  make view     - Open the PDF in default viewer"
	@echo "  make help     - Show this help message"

.PHONY: all bib clean cleanall view help

