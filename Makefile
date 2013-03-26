.PHONY: usage
usage:
	@echo "Supported targets:"
	@echo "  usage      show this help"
	@echo "  scripts    create the game launcher scripts"
	@echo "  images     create the stock Pyskool images in ~/.pyskool"
	@echo "  ini        create the stock Pyskool game ini files in ~/.pyskool"
	@echo "  doc        build the documentation"
	@echo "  clean      clean the documentation"
	@echo "  release    build a Pyskool release tarball and zip archive"
	@echo "  deb        build a Pyskool Debian package"
	@echo "  deb-clean  clean up after 'make deb'"
	@echo "  rpm        build a Pyskool RPM package"

.PHONY: scripts
scripts:
	@for s in skool_daze.py back_to_skool.py skool_daze_take_too.py ezad_looks.py back_to_skool_daze.py; do \
	    ln -sf pyskool.py $$s; \
	done

.PHONY: images
images:
	PYSKOOL_HOME=. utils/get-images.py ~/.pyskool

.PHONY: ini
ini:
	PYSKOOL_HOME=. utils/create-ini.py ~/.pyskool

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
deb: clean doc
	rsync -a --exclude=.buildinfo --exclude=objects.inv sphinx/build/html/ docs
	utils/get-images.py . > /dev/null
	rm -rf ini
	utils/create-ini.py -q .
	man/create-manpages man/pyskool.py.rst man
	debuild -b -us -uc
	mkdir -p dist
	mv ../pyskool_*.deb dist

.PHONY: deb-clean
deb-clean:
	rm -rf ../pyskool_*.build ../pyskool_*.changes build docs debian/pyskool debian/files debian/pyskool.debhelper.log debian/pyskool.postinst.debhelper debian/pyskool.prerm.debhelper debian/pyskool.substvars man/*.6

.PHONY: rpm
rpm:
	rm -f dist/pyskool-*.tar.xz
	utils/mkpstarball -t
	cp -p dist/pyskool-*.tar.xz ~/rpmbuild/SOURCES
	rm -f ~/rpmbuild/RPMS/noarch/pyskool-*.rpm
	cp -p rpm/pyskool.spec ~/rpmbuild/SPECS
	rpmbuild -bb ~/rpmbuild/SPECS/pyskool.spec
	mv ~/rpmbuild/RPMS/noarch/pyskool-*.rpm dist
