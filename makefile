VER := $(shell python --version 2>&1 | grep -o "[0-9].[0-9].[0-9]")
ZIP := python-${VER}-docs-html.zip
URL := http://docs.python.org/py3k/archives/${ZIP}
URL2:= http://docs.python.org/archives/${ZIP}

ifneq ($(findstring python-2, VER),)
	URL := ${URL2}
endif

download:
	@if [ ! -e ${ZIP} ] ; then     \
		echo "Downloading ${URL}"; \
		wget ${URL};               \
		unzip ${ZIP};              \
	fi
	./pylookup.py -u $(ZIP:.zip=)

.PHONY: download