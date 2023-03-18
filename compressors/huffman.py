"""
Huffman algorithm implementation.
"""

from typing import Generator, Sequence
from heapq import heapify, heappop, heappush

import pickle
from math import log2

from collections import Counter
from itertools import chain

from compressor import Compressor

class HuffmanCode(Compressor):
    """
    Huffman algorithm implementation class.
    """
    def __init__(self) -> None:
        super().__init__()
        self.bits = self.bits_dict()

    def _generate_dict(self, probs_dict: dict) -> None:
        """
        Function that generates the dictionary of the probabilities.
        Used block coding with size 'block_size'.

        Args:
            probs_dict: dictionary of the probabilities.
            block_size: size of the block.

        Returns:
            Dictionary of the probabilities, entropy of the code.
        """
        heap = [[prob, [byte, b""]] for byte, prob in probs_dict.items()]
        heapify(heap)

        while len(heap) > 1:
            low = heappop(heap)
            high = heappop(heap)

            for pair in low[1:]:
                pair[1] = b"\0" + pair[1]

            for pair in high[1:]:
                pair[1] = b"\1" + pair[1]

            heappush(heap, [low[0] + high[0]] + low[1:] + high[1:])

        return dict(heappop(heap)[1:])

    def _encode(self, data: Sequence) -> tuple[int]:
        """
        Function that encodes the file.

        Args:
            data: data to encode.

        Returns:
            Tuple of the encoded data.
        """
        probs_dict = {key: value / len(data) for key, value in Counter(data).items()}
        huffman_code = self._generate_dict(probs_dict)

        code_sequence = chain.from_iterable(
            map(lambda byte: huffman_code[byte], data)
        )

        return tuple(code_sequence), huffman_code

    def _to_bits(self, code_sequence: Sequence, huffman_code: dict) -> Generator:
        """
        Function that transforms the code sequence to bits.

        Args:
            code_sequence: sequence of the codes.
            huffman_code: dictionary of the huffman code.

        Returns:
            Generator of the compressed data.
        """
        last_block_size = len(code_sequence) % 8
        last_block = code_sequence[-last_block_size:] if last_block_size else b""

        assert last_block_size <= 8 and len(last_block) == last_block_size

        yield {value: key for key, value in huffman_code.items()}

        yield last_block_size.to_bytes(1, "big")
        yield bytes(last_block)

        for idx in range(0, (len(code_sequence) // 8) * 8, 8):
            byte = 0

            for bit_idx in range(8):
                byte = (byte << 1) | code_sequence[idx + bit_idx]

            yield byte.to_bytes(1, "big")

    def compress(self, src: str, dest: str) -> None:
        """
        Function that compresses the file.
        """
        with open(src, "rb") as in_ptr, open(dest, "wb") as out_ptr:
            code_sequence, huffman_code = self._encode(in_ptr.read())
            compress_generator = self._to_bits(code_sequence, huffman_code)

            pickle.dump(next(compress_generator), out_ptr)

            while True:
                try:
                    out_ptr.write(next(compress_generator))
                except StopIteration:
                    break

    def _from_bits(self, data: bytes, huffman_code: dict, last_block: bytes) -> Generator:
        """
        Function that decodes the file.

        Args:
            data: data to decode.
            huffman_code: dictionary of the huffman code.

        Returns:
            Generator of the decoded data.
        """
        buffer = b""
        self.bits[None] = last_block

        for byte in data + [None]:
            bits = 8 if byte is not None else len(last_block)
            for idx in range(bits):
                buffer += self.bits[byte][idx: idx + 1]

                if buffer in huffman_code:
                    yield huffman_code[buffer]
                    buffer = b""

        assert buffer == b"", "Buffer is not empty!"

    def _decompress(self, src: str) -> Generator:
        """
        Function that decompresses the file.

        Args:
            data: data to decompress.

        Returns:
            Generator of the decompressed data.
        """
        with open(src, "rb") as in_ptr:
            huffman_code = pickle.load(in_ptr)

            last_block_size = int.from_bytes(in_ptr.read(1), "big")
            last_block = in_ptr.read(last_block_size)

            decode_generator = self._from_bits(list(in_ptr.read()), huffman_code, last_block)
            while True:
                try:
                    yield next(decode_generator)
                except StopIteration:
                    break

    def decompress(self, src: str, dest: str) -> None:
        """
        Function that decompresses the file.

        Args:
            data: data to decompress.
            dest: path to the decompressed file.
        """
        with open(dest, "wb") as out_ptr:
            data_generator = self._decompress(src)

            while True:
                try:
                    out_ptr.write(next(data_generator).to_bytes(1, "big"))
                except StopIteration:
                    break

    @staticmethod
    def bits_dict() -> dict[int, bytes]:
        """
        Function that generates the dictionary of the bits
        representation of the bytes.

        Args:
            None.

        Returns:
            Dictionary of the bits representation of the bytes.
        """
        result = {}

        for idx in range(256):
            bits = b""
            byte = idx

            for _ in range(8):
                bits = b"\0" + bits if byte & 1 == 0 else b"\1" + bits
                byte >>= 1

            result[idx] = bits

        return result

    @staticmethod
    def entropy(probs: tuple[float]) -> float:
        """
        Entropy of the code.
        """
        return sum(-prop * log2(prop) for prop in probs)

if __name__ == "__main__":
    huff = HuffmanCode()

    # huff.compress("doc.rtf", "doc.huff")
    # huff.decompress("doc.huff", "doc2.rtf")
    huff.compress("..\\books\\1.txt", "..\\books\\1.huff")
    huff.decompress("..\\books\\1.huff", "..\\books\\1.huff.txt")
