import lzma
from io import BufferedReader, BytesIO
from struct import unpack


class Reader(BufferedReader):
    def __init__(self, initial_bytes: bytes):
        super(Reader, self).__init__(BytesIO(initial_bytes))

    def read_int(self, ctype: int, signed: bool, endian: str = '>') -> int:
        types = {64: "q", 32: "i", 16: "h", 8: "b"}
        _ctype = types[ctype] if signed else types[ctype].upper()
        result = unpack(f"{endian}{_ctype}", self.read(round(ctype / 8)))[0]
        if 2 ** ctype - 1 == result:
            return -1
        return result

    def read_char(self, length: int = 1, decode: bool = True) -> str | bytes:
        if decode:
            return self.read(length).decode('utf-8')
        else:
            return b'' + self.read(length)

    def read_bool(self) -> bool:
        return self.read_int(8, False) == 1

    def read_string(self, ctype: int, decode: bool = True) -> str:
        length = self.read_int(ctype, False)
        if length == -1:
            return ""
        return self.read_char(length, decode)

    @staticmethod
    def decompress_data(data: bytes):
        try:
            return lzma.decompress(data)
        except lzma.LZMAError:
            return b""
