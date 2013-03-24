.PHONY: usage
usage:
	@echo "Supported targets:"
	@echo "  usage    show this help"
	@echo "  scripts  create the game launcher scripts"
	@echo "  doc      build the documentation"
	@echo "  clean    clean the documentation"

.PHONY: scripts
scripts:
	@for s in skool_daze.py back_to_skool.py skool_daze_take_too.py ezad_looks.py back_to_skool_daze.py; do \
	    ln -sf pyskool.py $$s; \
	done

.PHONY: doc
doc:
	$(MAKE) -C sphinx html

.PHONY: clean
clean:
	$(MAKE) -C sphinx clean
