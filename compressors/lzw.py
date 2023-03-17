"""
LZ77 compression algorithm.
"""

from compressor import Compressor

class LZW(Compressor):
    """
    LZW compression algorithm.
    """
    def __init__(self):
        super().__init__()
        self.max_word_length = 0

    def _find_next(self, fpointer, codes):
        """
        Returns the next element in the file.
        """
        code = fpointer.read(self.max_word_length + 1)
        fpointer.seek(-len(code), 1)

        if not code:
            return None

        for i in range(len(code), 0, -1):
            chunk = code[:i]

            if chunk in codes:
                fpointer.seek(len(chunk), 1)

                if len(codes) > (1 << 14) - 1:
                    return codes[chunk]

                next_symbol = code[i:i + 1]
                if not next_symbol:
                    return codes[chunk]

                codes[chunk + next_symbol] = len(codes)
                if len(chunk + next_symbol) > self.max_word_length:
                    self.max_word_length = len(chunk + next_symbol)

                return codes[chunk]

    def compress(self, src: str, dest: str):
        """
        Compresses the content.
        """
        self.max_word_length = 1

        with open(src, 'rb') as fpointer, open(dest, 'wb') as out_ptr:
            codes = {bytes([idx]): idx for idx in range(256)}

            while True:
                result = self._find_next(fpointer, codes)
                if result is None:
                    break

                out_ptr.write(result.to_bytes(2, 'big'))

            self.max_word_length = 0

    def decompress(self, src: str, dest: str):
        """
        Decompresses the content.
        """
        with open(src, 'rb') as fpointer, open(dest, 'wb') as out_ptr:
            codes = {idx: bytes([idx]) for idx in range(256)}
            last_str = ()

            while True:
                raw_code = fpointer.read(2)
                if not raw_code:
                    break

                code = int.from_bytes(raw_code, 'big')

                if code in codes:
                    result = codes[code]
                    if last_str:
                        codes[len(codes)] = last_str + result[:1]
                else:
                    result = last_str + last_str[:1]
                    codes[len(codes)] = result

                out_ptr.write(result)
                last_str = result

if __name__ == '__main__':
    lzw = LZW()

    lzw.compress("doc.rtf", "doc.rtf.lzw")
    lzw.decompress("doc.rtf.lzw", "doc.rtf.decompressed")
