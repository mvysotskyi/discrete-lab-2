"""
LZ77 compression algorithm.
"""

from compressor import Compressor

class LZ77(Compressor):
    """
    LZ77 compression algorithm.
    """
    def __init__(self, window_size=8192, lookahead_buffer_size=254):
        super().__init__()
        self._window_size = window_size
        self._window = b""
        self._lookahead_buffer_size = lookahead_buffer_size

    def _update_window(self, fpointer, match_length: int):
        """
        Updates the window.
        """
        self._window += fpointer.read(match_length)
        next_char = fpointer.read(1)

        if next_char:
            diff = len(self._window) - self._window_size
            self._window = self._window[max(0, diff):]
            self._window += next_char

            return next_char

        return b''

    def _longest_match(self, fpointer) -> tuple:
        """
        Finds the longest match between the window and the lookahead buffer.
        """
        offset = 0
        length = 0

        lookahead_buffer = fpointer.read(self._lookahead_buffer_size)
        bytes_read = len(lookahead_buffer)

        for i in range(1, bytes_read + 1):
            try:
                offset = len(self._window) - self._window.rindex(lookahead_buffer[:i])
                length = i
            except ValueError:
                break

        fpointer.seek(-bytes_read, 1)
        return offset, length, self._update_window(fpointer, length)

    def compress(self, src: str, dest: str):
        """
        Compresses the content.
        """
        self._window = b""

        with open(src, 'rb') as fpointer, open(dest, 'wb+') as out:
            while True:
                match_idx, match_length, next_char = self._longest_match(fpointer)

                out.write(match_idx.to_bytes(2, 'big'))
                out.write(match_length.to_bytes(1, 'big'))
                out.write(next_char)

                if not next_char:
                    break

    def _decompress(self, data: tuple, out_ptr):
        """
        Decompresses the content.

        Args:
            data (tuple): The data to decompress.
            out_ptr: The output file pointer.

        Returns:
            None
        """
        for offset, length, next_char in data:

            try:
                out_ptr.seek(-offset, 1)
                chunk = out_ptr.read(length) + next_char
                out_ptr.seek(offset - length, 1)
                out_ptr.write(chunk)
            except OSError:
                print(out_ptr.tell(), offset, length, next_char)

    def decompress(self, src: str, dest: str):
        """
        Decompresses the content.
        """
        with open(src, "rb") as in_ptr, open(dest, 'wb+') as out_ptr:
            data = []

            while True:
                offset = int.from_bytes(in_ptr.read(2), 'big')
                length = int.from_bytes(in_ptr.read(1), 'big')
                next_char = in_ptr.read(1)

                data.append((offset, length, next_char))

                if not next_char:
                    break

            self._decompress(data, out_ptr)

if __name__ == '__main__':
    lz77 = LZ77()

    # lz77.compress("doc.rtf", "doc.lz77")
    # lz77.decompress("doc.lz77", "doc.lz77.rtf")

    for i in range(1, 6):
        # if i in (2, 1):
        #     continue
        # print(i)
        lz77.compress(f"..\\books\\{i}.txt", f"..\\books\\{i}.txt.deflate")
        lz77.decompress(f"..\\books\\{i}.txt.deflate", f"..\\books\\{i}.txt.deflate.txt")
    # deflate.compress("..\\books\\1.txt", "..\\books\\1.txt.deflate")
    # deflate.decompress("..\\books\\1.txt.deflate", "..\\books\\1.txt.deflate.txt")
