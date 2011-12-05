VER := $(shell python --version 2>&1 | grep -o "[0-9].[0-9].[0-9]")
ZIP := python-${VER}-docs-html.zip
URL := http://docs.python.org/archives/${ZIP}

download:
	@if [ ! -e $(ZIP) ] ; then     \
		echo "Downloading ${URL}"; \
		wget ${URL};               \
		unzip ${ZIP};              \
	fi
	./pylookup.py -u $(ZIP:.zip=)

.PHONY: download