.PHONEY: help
help:
	@echo "Targets:"
	@echo "  clean: Removes distribution folders and artifacts from building"
	@echo "  manylinux-wheels: Builds binary and manylinux wheels for several python versions"

.PHONY: clean
clean:
	rm -rf dist wheelhouse build __pycache__ *.so *.egg-info

.PHONY: manylinux-wheels
manylinux-wheels:
	docker run --user $(shell id -u):$(shell id -g) -v $(shell pwd):/io quay.io/pypa/manylinux1_x86_64:latest \
		/io/bin/build-manylinux-wheel.sh 27 35 36 37 38
