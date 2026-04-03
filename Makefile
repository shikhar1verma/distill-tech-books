SHELL := /bin/bash
PYTHON := python3

BOOK_PDF := books/Fluent Python.pdf
BOOK_SLUG := fluent-python
LIBRARY := library
RAW_DATA := raw-data

.PHONY: init extract distill index validate clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

init: ## Initialize book structure from PDF TOC
	$(PYTHON) src/extract.py init "$(BOOK_PDF)" --slug $(BOOK_SLUG) --raw-dir $(RAW_DATA)

extract: ## Extract all chapters to raw markdown (output to raw-data/)
	$(PYTHON) src/extract.py extract "$(BOOK_PDF)" --slug $(BOOK_SLUG) --raw-dir $(RAW_DATA)

extract-ch: ## Extract single chapter: make extract-ch CH=1
	$(PYTHON) src/extract.py extract "$(BOOK_PDF)" --slug $(BOOK_SLUG) --raw-dir $(RAW_DATA) --chapter $(CH)

index: ## Rebuild all indexes (chapter, concept, book, library)
	$(PYTHON) src/wiki_builder.py book-index $(LIBRARY)/$(BOOK_SLUG)
	$(PYTHON) src/wiki_builder.py concepts-index $(LIBRARY)/$(BOOK_SLUG)
	$(PYTHON) src/wiki_builder.py library-index $(LIBRARY)

validate: ## Check for broken wikilinks
	$(PYTHON) src/wiki_builder.py validate $(LIBRARY)/$(BOOK_SLUG)

clean: ## Remove raw extractions from private submodule
	rm -f $(RAW_DATA)/$(BOOK_SLUG)/*.md
	rm -f $(RAW_DATA)/$(BOOK_SLUG)/*-concepts.yaml
