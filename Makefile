.PHONY: docs docs-shell docs-build run

run:
	pip install -r requirements.txt
	./spider.sh list

# import the existing docs build cmds from docker/docker
DOCS_MOUNT := $(if $(DOCSDIR),-v $(CURDIR)/$(DOCSDIR):/$(DOCSDIR))
DOCSPORT := 8000
GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null)
DOCKER_DOCS_IMAGE := kitematic-docs$(if $(GIT_BRANCH),:$(GIT_BRANCH))
DOCKER_RUN_DOCS := docker run --rm -it $(DOCS_MOUNT)

docs: docs-build
	$(DOCKER_RUN_DOCS) -p $(if $(DOCSPORT),$(DOCSPORT):)8000 "$(DOCKER_DOCS_IMAGE)" mkdocs serve

docs-shell: docs-build
	$(DOCKER_RUN_DOCS) -p $(if $(DOCSPORT),$(DOCSPORT):)8000 "$(DOCKER_DOCS_IMAGE)" bash

docs-build:
	docker build -t "$(DOCKER_DOCS_IMAGE)" -f docs/Dockerfile .

docker-selenium-grid:
    docker pull dsgrid/selenium-hub
    docker pull dsgrid/firefox-node
    docker pull dsgrid/chrome-node
    docker pull dsgrid/phantomjs-node