
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test
test: ## Run all tests and lints
	pipenv run pytest
	pipenv run mypy *.py chocula/*.py --ignore-missing-imports

.PHONY: build
build: src/*.rs src/bin/*.rs
	cargo build --release

.PHONY: install
install:
	$(INSTALL) -t $(PREFIX)/bin target/release/einhyrningsins
	$(INSTALL) -t $(PREFIX)/bin target/release/einhyrningsinsctl
	# Trying to install manpages; ok if this fails
	$(INSTALL) -m 644 -t $(PREFIX)/share/man/man1 doc/einhyrningsins.1
	$(INSTALL) -m 644 -t $(PREFIX)/share/man/man1 doc/einhyrningsinsctl.1

