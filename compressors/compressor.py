"""
Compressor base class.
This module contains the base class for all compressors. It is not meant to be used directly.
"""

from typing import Any

class Compressor:
    """
    Base class for all compressors.
    """
    def __init__(self, verbose=False):
        self.verbose = verbose

    def compress(self, content: list[Any]):
        """
        Compresses the content.
        """
        raise NotImplementedError('subclasses of Compressor must provide a compress() method')

    def decompress(self, **kwargs):
        """
        Decompresses the content.
        """
        raise NotImplementedError('subclasses of Compressor must provide a decompress() method')