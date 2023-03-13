"""
LZ77 compression algorithm.
"""

from compressor import Compressor

class LZW(Compressor):
    """
    LZW compression algorithm.
    """
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.max_word_length = 0

    def _find_next(self, fpointer, codes):
        """
        Returns the next element in the file.
        """
        for i in range(self.max_word_length, 0, -1):
            code = fpointer.read(i)
            i = len(code)

            if code in codes:
                if len(codes) > (1 << 14) - 1:
                    return codes[code]

                next_symbol = fpointer.read(1)
                if not next_symbol:
                    return codes[code]

                codes[code + next_symbol] = len(codes)
                self.max_word_length = max(self.max_word_length, len(code) + 1)
                fpointer.seek(-1, 1)

                return codes[code]

            fpointer.seek(-len(code), 1)

        return None

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
    lzw = LZW(verbose=True)

    lzw.compress('text.txt', 'text.txt.lzw')
    lzw.decompress('text.txt.lzw', 'text.txt.decompressed')
