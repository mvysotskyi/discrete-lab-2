"""
LZ77 compression algorithm.
"""

from compressor import Compressor

class LZ77(Compressor):
    """
    LZ77 compression algorithm.
    """
    def __init__(self, verbose=False, window_size=5, lookahead_buffer_size=18):
        super().__init__(verbose)
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

        with open(src, 'rb') as fpointer, open(dest, 'wb') as out:
            while True:
                match_idx, match_length, next_char = self._longest_match(fpointer)

                out.write(bytes([match_idx, match_length]))
                out.write(next_char)

                if not next_char:
                    break

    def decompress(self, src: str, dest: str):
        """
        Decompresses the content.
        """
        with open(src, 'rb') as inp, open(dest, 'wb+') as out_ptr:
            while True:
                offset, length = list(inp.read(2))
                next_char = inp.read(1)

                out_ptr.seek(-offset, 1)
                chunk = out_ptr.read(length) + next_char
                out_ptr.seek(offset - length, 1)
                out_ptr.write(chunk)

                if not next_char:
                    break

if __name__ == '__main__':
    lz77 = LZ77()
    lz77.compress('test.txt', 'test.txt.lz77')
    lz77.decompress('test.txt.lz77', 'test.txt.decomressed')
