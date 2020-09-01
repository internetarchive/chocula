
TODAY ?= $(shell date --iso --utc)
SNAPSHOTITEM ?= $(shell grep ia_item sources.toml | cut -f2 -d'"')

.PHONY: help
help: ## Print info about all commands
	@echo "Commands:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "    \033[01;32m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: dep
dep: ## Create local virtualenv using pipenv
	pipenv install --dev

.PHONY: lint
lint: ## Run lints (eg, flake8, mypy)
	pipenv run flake8 *.py chocula/*.py chocula/*/*.py tests/ --exit-zero
	pipenv run mypy *.py chocula/*.py chocula/*/*.py --ignore-missing-imports

.PHONY: fmt
fmt: ## Run code formating on all source code
	pipenv run black *.py chocula/ tests/

.PHONY: test
test: lint ## Run all tests and lints
	pipenv run pytest

.PHONY: coverage
coverage: ## Run all tests with coverage
	pipenv run pytest --cov

data/container_stats.json:
	mkdir -p data
	cat data/container_export.json | jq .issnl -r | sort -u > /tmp/container_issnl.tsv
	cat /tmp/container_issnl.tsv | parallel -j10 curl -s 'https://fatcat.wiki/container/issnl/{}/stats.json' | jq -c . > /tmp/container_stats.json
	mv /tmp/container_stats.json data

.PHONY: container-stats
container-stats: data/container_stats.json
	wc -l data/container_stats.json
	@echo
	@echo Done

data/homepage_status.json:
	pipenv run ./chocula.py export_urls | shuf > /tmp/chocula_urls_to_crawl.tsv
	pipenv run parallel -j10 --bar --pipepart -a /tmp/chocula_urls_to_crawl.shuf.tsv ./check_issn_urls.py > /tmp/homepage_status.json
	cp /tmp/homepage_status.json data/

.PHONY: homepage-status
homepage-status: data/homepage_status.json
	wc -l data/homepage-status.json
	@echo
	@echo Done

.PHONY: fetch-sources
fetch-sources: ## Download existing snapshot versions of all sources from archive.org
	mkdir -p data
	ia download --checksum --no-directories $(SNAPSHOTITEM) --destdir data/
	rm data/$(SNAPSHOTITEM)_*

data/$(TODAY)/kbart_JSTOR.txt:
	mkdir -p data/$(TODAY)
	wget -c "https://www.jstor.org/kbart/collections/all-archive-titles?contentType=journals" -O $@.wip
	mv $@.wip $@

data/$(TODAY)/kbart_CLOCKSS.txt:
	wget -c "https://reports.clockss.org/kbart/kbart_CLOCKSS.txt" -O $@.wip
	mv $@.wip $@

data/$(TODAY)/kbart_CLOCKSS-triggered.txt:
	wget -c "https://reports.clockss.org/kbart/kbart_CLOCKSS-triggered.txt" -O $@.wip
	mv $@.wip $@

data/$(TODAY)/kbart_LOCKSS.txt:
	wget -c "https://reports.lockss.org/kbart/kbart_LOCKSS.txt" -O $@.wip
	mv $@.wip $@

data/$(TODAY)/kbart_Portico.txt:
	wget -c "http://api.portico.org/kbart/Portico_Holding_KBart.txt" -O $@.wip
	mv $@.wip $@

data/$(TODAY)/ISSN-to-ISSN-L.txt:
	wget -c "https://www.issn.org/wp-content/uploads/2014/03/issnltables.zip" -O /tmp/issnltables.$(TODAY).zip
	unzip -p /tmp/issnltables.$(TODAY).zip "*.ISSN-to-ISSN-L.txt" > $@.wip
	mv $@.wip $@

data/$(TODAY)/entrez.csv:
	wget -c "ftp://ftp.ncbi.nlm.nih.gov/pubmed/J_Entrez.txt" -O $@.wip
	mv $@.wip $@

data/$(TODAY)/doaj.csv:
	wget -c "https://doaj.org/csv" -O $@.wip
	mv $@.wip $@

data/$(TODAY)/crossref_titles.csv:
	wget -c "https://wwwold.crossref.org/titlelist/titleFile.csv" -O $@.wip
	mv $@.wip $@

data/$(TODAY)/onix_pkp_pln.csv:
	wget -c "http://pkp.sfu.ca/files/pkppn/onix.csv" -O $@.wip
	mv $@.wip $@

.PHONY: update-sources
update-sources: data/$(TODAY)/kbart_JSTOR.txt data/$(TODAY)/kbart_CLOCKSS.txt data/$(TODAY)/kbart_CLOCKSS-triggered.txt data/$(TODAY)/kbart_LOCKSS.txt data/$(TODAY)/kbart_Portico.txt data/$(TODAY)/ISSN-to-ISSN-L.txt data/$(TODAY)/entrez.csv data/$(TODAY)/doaj.csv data/$(TODAY)/crossref_titles.csv data/$(TODAY)/onix_pkp_pln.csv  ## Download new versions of updatable sources
	@echo
	@echo "Successfully updated for date (UTC): $(TODAY)"

data/$(TODAY)/homepage_status.json:
	pipenv run python -m chocula export_urls | shuf | pv -l > /tmp/chocula_urls.tsv
	pipenv run parallel -j10 --pipepart --line-buffer -a /tmp/chocula_urls.tsv ./check_issn_urls.py | pv -l > /tmp/homepage_status.json
	mv /tmp/url_status.json $@

data/$(TODAY)/container_stats.json: data/container_export.json
	cat data/container_export.json | jq .issnl -r | sort -u > /tmp/container_issnl.tsv
	cat /tmp/container_issnl.tsv | parallel -j10 curl --fail -s 'https://fatcat.wiki/container/issnl/{}/stats.json' | jq -c . | pv -l > /tmp/container_stats.json
	cp /tmp/container_stats.json $@

.PHONY: upload-sources
upload-sources: update-sources ## Upload most recent update-able sources to a new IA item
	ia upload --checksum -m collection:ia_biblio_metadata chocula-sources-snapshot-$(TODAY) data/*.tsv data/*.json data/*.txt data/*.csv

.PHONY: upload-database
upload-database: ## Upload an sqlite snapshot to archive.org
	ia upload --checksum --no-derive -m collection:ia_biblio_metadata chocula-database-snapshot-$(TODAY) chocula.sqlite sources.toml README.md extra/count_chocula.jpg

.PHONY: database
database: ## Build database from sources
	@if [ ! -f data/ISSN-to-ISSN-L.txt ]; then echo "You must run 'make fetch-sources' first"; exit -1; fi
	pipenv run python -m chocula everything
