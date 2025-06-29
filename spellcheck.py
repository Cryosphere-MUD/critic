
if False:

	from phunspell import Phunspell
	import re

	from musictypes import TypeSpecificMudObject

	spell = Phunspell("en_GB")

	custom_words = []

	with open("../data/spellcheck_wordlist") as f:
		for line in f:
			custom_words.append(line.strip())

	with open("../data/spellcheck_wordlist_dialogue") as f:
		for line in f:
			custom_words.append(line.strip())

	import ctypes

	dep = ctypes.CDLL("../vendor/fmt/build/libfmt.so", mode=ctypes.RTLD_GLOBAL)

	# dep = ctypes.CDLL("../vendor/fmt/build/libfmt.so", mode=ctypes.RTLD_GLOBAL)

	dep = ctypes.CDLL("../src/libmusicmud.so", mode=ctypes.RTLD_GLOBAL)

	mydll = ctypes.CDLL("../src/modules/colour.so")

	mydll.strip_colour_for_python.argtypes = [ctypes.c_char_p]
	mydll.strip_colour_for_python.restype = ctypes.c_char_p

	global is_enabled

	def is_word(token):
		return token.isalpha()

	def spellcheck(self, mob, text, node):
		if not is_enabled:
			return

		if isinstance(mob, TypeSpecificMudObject):
			if mob.mudobject.get("nation") in ("french", "canadian"):
				# don't spellcheck french speaking mobs as they use eye-dialect
				return

		text = mydll.strip_colour_for_python(text.encode("UTF-8")).decode()
		words = re.split(r"[ .,!?;:<>\n]+", text)
		for w in words:
			if is_word(w) and w not in custom_words and not spell.lookup(w):
				self.warning(f"apparent misspelling {repr(w)}", node)

def spellcheck(self, mob, text, node):
	return

def enable():
	global is_enabled
	is_enabled = True

def disable():
        global is_enabled
        is_enabled = False
