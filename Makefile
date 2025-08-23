check:prepare-venv
	@if [ -f .critic.config ]; then \
		$(MAKE) dump-lua; \
	fi
	ln -sfn py-lua-parser/luaparser .
	. venv/bin/activate && ./validate-this.py

validate: prepare-venv dump-lua validate-lua

prepare-venv:
	test -d venv || python3.11 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install multimethod antlr4-python3-runtime luapatt

dump-lua:
	make -C ../src musicmud
	cd ../ && src/musicmud --dump

validate-lua:
	@if [ -f .critic.config ]; then \
		$(MAKE) dump-lua; \
	fi
	ln -sfn py-lua-parser/luaparser .
	venv/bin/python ./validator.py

