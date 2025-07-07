.PHONY: validate prepare-venv dump-lua validate-lua

validate: prepare-venv dump-lua validate-lua

# libmusicmud.so:
# 	make -C ../src libmusicmud.so

colour.so:
	make -C ../src/modules colour.so

prepare-venv:
	test -d venv || python3.11 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install multimethod antlr4-python3-runtime luapatt phunspell

dump-lua:
	make -C ../src musicmud
	cd ../ && src/musicmud --dump

validate-lua:#libmusicmud.so colour.so
	ln -sfn ../vendor/py-lua-parser/luaparser .
	venv/bin/python ./validator.py

check:prepare-venv
	ln -sfn py-lua-parser/luaparser .
	. venv/bin/activate && ./validate-this.py

quis-custodiet-ipsos-custodes:prepare-venv dump-lua #libmusicmud.so colour.so 
	ln -sfn py-lua-parser/luaparser .
	. venv/bin/activate && ./validate-this.py
