import lzma
from struct import pack


class Writer:
    def __init__(self):
        self.buffer = b''

    def write_int(self, integer: int, ctype: int, signed: bool, endian: str = '>'):
        types = {64: "q", 32: "i", 16: "h", 8: "b"}
        ctype = types[ctype] if signed else types[ctype].upper()
        self.buffer += pack(f"{endian}{ctype}", integer)

    def write_string(self, string: str, ctype: int):
        encoded = string.encode('utf-8')
        self.write_int(len(encoded), ctype, False)
        self.buffer += encoded

    def write_bool(self, boolean: bool):
        if boolean:
            self.write_int(1, 8, False)
        else:
            self.write_int(0, 8, False)

    def get_compressed_data(self):
        return lzma.compress(self.buffer)