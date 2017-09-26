HOST_PATH ?= $(shell pwd)

REPO_ORG ?= $(shell basename $(HOST_PATH))
REPO = $(shell echo $(REPO_ORG) | tr A-Z a-z)

TAG = 'develop'

GUEST_PATH = '/tmp/$(REPO)'

CMD_DEV = 'cd $(GUEST_PATH) && /bin/bash'
CMD_TEST = 'cd $(GUEST_PATH) && /bin/bash run-test.sh'

HOST_PORT ?= 80

build:
	docker build \
	  -t $(REPO):$(TAG) -f Dockerfile .

run:
	docker run --rm \
	  -e DISPLAY=$(DISPLAY) \
	  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
	  -v $(HOST_PATH):$(GUEST_PATH) \
	  $(DOCKER_OPTIONS) -it $(REPO):$(TAG) /bin/bash -c $(CMD_DEV)

test:
	docker run --rm \
	  -v $(HOST_PATH):$(GUEST_PATH) \
	  $(DOCKER_OPTIONS) -it $(REPO):$(TAG) /bin/bash -c $(CMD_TEST)

