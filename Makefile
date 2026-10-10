GIMP ?= gimp-console-3.0
POC_OUTPUT ?= $(CURDIR)/tmp/pdb-poc.json
POC_SCRIPT := $(CURDIR)/scripts/capture_pdb_poc.py

.PHONY: pdb-poc

pdb-poc:
	@command -v "$(GIMP)" >/dev/null 2>&1 || { echo "GIMP CLI not found: $(GIMP) (override with GIMP=/path/to/gimp-console)" >&2; exit 1; }
	PDB_POC_OUTPUT="$(POC_OUTPUT)" "$(GIMP)" -i --batch-interpreter=python-fu-eval -b "exec(open('$(POC_SCRIPT)', encoding='utf-8').read())" --quit
