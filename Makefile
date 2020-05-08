
TODAY := $(shell date --iso --utc)
SNAPSHOTITEM := $(shell grep ia_item sources.toml | cut -f2 -d'"')

.PHONY: help
help: ## Print info about all commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: test
test: ## Run all tests and lints
	pipenv run pytest
	pipenv run mypy *.py chocula/*.py chocula/*/*.py --ignore-missing-imports

#.PHONY: database
#database: ## Build database from sources
#	@if [ ! -f data/ISSN-to-ISSN-L.txt ]; then echo "You must run 'make fetch-sources' first"; exit -1; fi
#	pipenv run ./chocula_tool.py everything

#data/container_stats.json:
#	cat data/container_export.json | jq .issnl -r | sort -u > /tmp/container_issnl.tsv
#	cat /tmp/container_issnl.tsv | parallel -j10 curl -s 'https://fatcat.wiki/container/issnl/{}/stats.json' | jq -c . > /tmp/container_stats.json
#	mv /tmp/container_stats.json data

#.PHONY: container-stats
#container-stats: data/container_stats.json
#	wc -l data/container_stats.json
#	@echo
#	@echo Done

#data/homepage_status.json:
#	pipenv run ./chocula.py export_urls | shuf > /tmp/chocula_urls_to_crawl.tsv
#	pipenv run parallel -j10 --bar --pipepart -a /tmp/chocula_urls_to_crawl.shuf.tsv ./check_issn_urls.py > /tmp/homepage_status.json
#	cp /tmp/homepage_status.json data/

#.PHONY: homepage-status
#homepage-status: data/homepage_status.json
#	wc -l data/homepage-status.json
#	@echo
#	@echo Done

.PHONY: fetch-sources
fetch-sources: ## Download existing snapshot versions of all sources from archive.org
	mkdir -p data
	ia download --checksum --no-directories $(SNAPSHOTITEM) --destdir data/

.PHONY: update-sources
update-sources: ## Download new versions of updatable sources
	mkdir -p data/$(TODAY)
	wget -c "https://www.issn.org/wp-content/uploads/2014/03/issnltables.zip" -O /tmp/issnltables.$(TODAY).zip
	unzip -p /tmp/issnltables.$(TODAY).zip "*.ISSN-to-ISSN-L.txt" > /tmp/ISSN-to-ISSN-L.$(TODAY).txt
	mv /tmp/ISSN-to-ISSN-L.$(TODAY).txt data/$(TODAY)/ISSN-to-ISSN-L.txt
	wget -c "ftp://ftp.ncbi.nlm.nih.gov/pubmed/J_Entrez.txt" -O /tmp/entrez.$(TODAY).csv
	cp /tmp/entrez.$(TODAY).csv data/$(TODAY)/entrez.csv
	wget -c "https://doaj.org/csv" -O /tmp/doaj.$(TODAY).csv
	cp /tmp/doaj.$(TODAY).csv data/$(TODAY)/doaj.csv
	wget -c "https://wwwold.crossref.org/titlelist/titleFile.csv" -O /tmp/crossref_titles.$(TODAY).csv
	cp /tmp/crossref_titles.$(TODAY).csv data/$(TODAY)/crossref_titles.csv
	@echo
	@echo "Successfully updated for date (UTC): $(TODAY)"

#.PHONY: upload-sources
#upload-sources: ## Upload an updated snapshot of sources to archive.org
#	ia upload --checksum chocula-sources-$(TODAY) data/*.tsv data/*.csv data/*.json data/*.txt

#.PHONY: upload-snapshot
#upload-snapshot: ## Upload an sqlite snapshot to archive.org
#	ia upload --checksum --no-derive chocula-snapshot-$(TODAY) chocula.sqlite3 README.md extra/count_chocula.jpg

