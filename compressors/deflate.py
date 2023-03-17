"""
Deflate compression algorithm.
"""

from tempfile import NamedTemporaryFile, mkdtemp

from huffman import HuffmanCode
from lz77 import LZ77

class Deflate(LZ77, HuffmanCode):
    """
    Deflate algorithm implementation class.
    """
    def compress(self, src: str, dest: str):
        tmp_dir = mkdtemp()
        lz77_file = NamedTemporaryFile(dir=tmp_dir, delete=False)

        LZ77.compress(self, src, lz77_file.name)
        HuffmanCode.compress(self, lz77_file.name, dest)

    def decompress(self, src: str, dest: str):
        tmp_dir = mkdtemp()
        huff_file = NamedTemporaryFile(dir=tmp_dir, delete=False)

        HuffmanCode.decompress(self, src, huff_file.name)
        LZ77.decompress(self, huff_file.name, dest)

if __name__ == '__main__':
    deflate = Deflate()

    deflate.compress('doc.rtf', 'doc.deflate')
    deflate.decompress('doc.deflate', 'doc.inflate.rtf')
