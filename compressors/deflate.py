"""
Deflate compression algorithm.
"""

import pickle

from huffman import HuffmanCode
from lz77 import LZ77

class Deflate(LZ77, HuffmanCode):
    """
    Deflate algorithm implementation class.
    """
    def __init__(self, window_size=512):
        super().__init__(window_size=window_size)

    def compress(self, src: str, dest: str):
        with open(src, "rb") as in_ptr, open(dest, "wb") as out_ptr:
            code_sequence = []

            while True:
                offset, length, next_char = self._longest_match(in_ptr)
                code_sequence.append((offset, length, next_char))

                if not next_char:
                    break

            code_sequence, huffman_code = HuffmanCode._encode(self, code_sequence)
            compress_generator = self._to_bits(code_sequence, huffman_code)
            pickle.dump(next(compress_generator), out_ptr)

            while True:
                try:
                    out_ptr.write(next(compress_generator))
                except StopIteration:
                    break

    def decompress(self, src: str, dest: str):
        """
        Decompresses the content.
        """
        with open(dest, "wb+") as out_ptr:
            code_sequence = HuffmanCode._decompress(self, src)
            out_ptr.seek(0)
            LZ77._decompress(self, list(code_sequence), out_ptr)

if __name__ == '__main__':
    deflate = Deflate()

    for i in range(1, 6):
        if i in (2, 1):
            continue
        print(i)
        deflate.compress(f"..\\books\\{i}.txt", f"..\\books\\{i}.txt.deflate")
        deflate.decompress(f"..\\books\\{i}.txt.deflate", f"..\\books\\{i}.txt.deflate.txt")
    # deflate.compress("..\\books\\1.txt", "..\\books\\1.txt.deflate")
    # deflate.decompress("..\\books\\1.txt.deflate", "..\\books\\1.txt.deflate.txt")
