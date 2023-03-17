"""
Compressor base class.
This module contains the base class for all compressors. It is not meant to be used directly.
"""

class Compressor:
    """
    Base class for all compressors.
    """
    def compress(self, src: str, dest: str):
        """
        Compresses the content.
        """
        raise NotImplementedError('subclasses of Compressor must provide a compress() method')

    def decompress(self, src: str, dest: str):
        """
        Decompresses the content.
        """
        raise NotImplementedError('subclasses of Compressor must provide a decompress() method')
