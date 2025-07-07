.PHONY: validate prepare-venv dump-lua validate-lua

check:prepare-venv
	ln -sfn py-lua-parser/luaparser .
	. venv/bin/activate && ./validate-this.py

validate: prepare-venv dump-lua validate-lua

prepare-venv:
	test -d venv || python3.11 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install multimethod antlr4-python3-runtime luapatt

dump-lua:
	make -C ../src musicmud
	cd ../ && src/musicmud --dump

validate-lua:
	ln -sfn ../vendor/py-lua-parser/luaparser .
	venv/bin/python ./validator.py

