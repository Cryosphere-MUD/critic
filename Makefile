check:prepare-venv
	@if [ -f .critic.config ]; then \
		$(MAKE) dump-lua; \
	fi
	ln -sfn py-lua-parser/luaparser src
	. venv/bin/activate && src/validate-this.py

validate: prepare-venv dump-lua validate-lua

ifneq ("$(wildcard .critic.Makefile)","")
  include .critic.Makefile
else
  include .critic.Makefile-default
endif

prepare-venv:
	test -d venv || python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install multimethod antlr4-python3-runtime luapatt

validate-lua:
	@if [ -f .critic.config ]; then \
		$(MAKE) dump-lua; \
	fi
	ln -sfn py-lua-parser/luaparser src
	venv/bin/python src/validator.py

