.PHONY: all dist install install-dev test qa

all:

install:
	pip3 install -r requirements/requirements.txt --no-binary :all:
	./setup.py install

install-dev:
	pip3 install -r requirements/requirements.txt --no-binary :all:
	pip3 install -r requirements/requirements-dev-1.txt --no-binary :all:
	pip3 install -r requirements/requirements-dev-2.txt --no-binary :all:
	pip3 install -r requirements/requirements-dev-3.txt --no-binary :all:
	./setup.py develop

test:
	python3 -m unittest -q

qa:
	coverage run -m unittest -q
	coverage report -m
	isort --check-only --diff --recursive .
	mypy .
	pycodestyle .
	pyflakes .
	pylint --output-format parseable setup.py ossaudit tests
	yapf --diff --recursive .
	ossaudit --installed \
		--ignore-id 06e60262-8241-42ef-8f64-e3d72091de19 \
		--ignore-id e4c955a3-2004-472e-920b-783fea46c3cd

dist:
	rm -rf dist tmp

	tag="$$(git tag --sort=-creatordate |head -n 1)" && \
	git verify-tag "$$tag" && \
	git clone --shared --branch "$$tag" . tmp

	cd tmp && \
	./setup.py sdist && \
	gpg --detach-sign --armor "$$(ls dist/*.tar.gz)"

	mv tmp/dist .
	rm -rf tmp
	gpg --verify dist/*.asc
