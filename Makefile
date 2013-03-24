.PHONY: usage
usage:
	@echo "Supported targets:"
	@echo "  usage    show this help"
	@echo "  scripts  create the game launcher scripts"

.PHONY: scripts
scripts:
	@for s in skool_daze.py back_to_skool.py skool_daze_take_too.py ezad_looks.py back_to_skool_daze.py; do \
	    ln -sf pyskool.py $$s; \
	done
