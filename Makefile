VER2 := $(shell python2 --version 2>&1 | grep -o "[0-9].[0-9].[0-9]*")
VER3 := $(shell python3 --version 2>&1 | grep -o "[0-9].[0-9]*.[0-9]*")
ZIP2 := python-$(VER2)-docs-html.zip
ZIP3 := python-$(VER3)-docs-html.zip
URL2 := https://docs.python.org/2/archives/$(ZIP2)
URL3 := https://docs.python.org/3/archives/$(ZIP3)

define download
	@if [ ! -e $(1) ] ; then     \
		echo "Downloading $(2)"; \
		wget $(2);               \
		unzip $(1);              \
	fi
endef

build:
	$(call download,$(ZIP2),$(URL2))
	$(call download,$(ZIP3),$(URL3))

	./pylookup.py -d pylookup2.db -u $(ZIP2:.zip=)
	./pylookup.py -d pylookup3.db -u $(ZIP3:.zip=)

.PHONY: download
