# Set these if not defined already
export BIND_ADDRESS?=0.0.0.0
export PORT?=8080
export DEBUG?=False
export PROFILER?=False
export DATABASE_PATH?=./northwind.db
export PYTHONIOENCODING=UTF_8:replace
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export CURRENT_GIT_BRANCH?=`git symbolic-ref --short HEAD`

.DEFAULT_GOAL := help

deps: ## Install Dependencies (assumes pyenv)
	pip install -U --break-system-packages -r requirements.txt

deps-upgrade: ## Interactively upgrade requirements.txt
	pip-upgrade --skip-package-installation --skip-virtualenv-check requirements.txt

init-db: ## Initialize the database
	sqlite3 $(DATABASE_PATH) < assets/northwind.sql

clean: ## Clean environment
	rm -f $(BYTECODE)
	rm -f $(PYTHONCODE)
	rm -f $(DATABASE_PATH)*

serve: ## Run with the embedded web server
	python -m stub.app

%.png: %.pstats ## Render pstats profiler files into nice PNGs (requires dot)
	python tools/gprof2dot.py -f pstats $< | dot -Tpng -o $@

profile: $(CALL_DIAGRAMS) ## Render profile

debug-%: ; @echo $*=$($*)

help:
	@grep -hE '^[A-Za-z0-9_ \-]*?:.*##.*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
