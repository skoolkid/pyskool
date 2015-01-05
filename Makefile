.PHONY: usage
usage:
	@echo "Supported targets:"
	@echo "  usage      show this help"
	@echo "  scripts    create the game launcher scripts"
	@echo "  images     create the stock Pyskool images in ~/.pyskool"
	@echo "  ini        create the stock Pyskool game ini files in ~/.pyskool"
	@echo "  sounds     create the stock Pyskool sound files in ~/.pyskool"
	@echo "  doc        build the documentation"
	@echo "  clean      clean the documentation"
	@echo "  release    build a Pyskool release tarball and zip archive"
	@echo "  deb        build a Pyskool Debian package"
	@echo "  rpm        build a Pyskool RPM package"

.PHONY: scripts
scripts:
	@for s in skool_daze.py back_to_skool.py skool_daze_take_too.py ezad_looks.py back_to_skool_daze.py; do \
	    ln -sf pyskool.py $$s; \
	done

.PHONY: images
images:
	mkdir -p ~/.pyskool
	PYSKOOL_HOME=$$(pwd) utils/create-images.py ~/.pyskool

.PHONY: ini
ini:
	PYSKOOL_HOME=. utils/create-ini.py ~/.pyskool

.PHONY: sounds
sounds:
	PYSKOOL_HOME=. utils/create-sounds.py ~/.pyskool

.PHONY: doc
doc:
	$(MAKE) -C sphinx html

.PHONY: clean
clean:
	$(MAKE) -C sphinx clean

.PHONY: release
release:
	utils/mkpstarball

.PHONY: deb
deb:
	utils/mkpspkg deb

.PHONY: rpm
rpm:
	utils/mkpspkg rpm
