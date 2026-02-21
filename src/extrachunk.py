extra_chunks = []

class ExtraChunk:
        def __init__(self, lua):
                self.lua = lua

def add_extra_chunk(chunk):
        extra_chunks.append(chunk)