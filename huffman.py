"""
Huffman algorithm implementation.
"""

from math import log2

class HuffmanCode:
    """
    Huffman algorithm implementation class.

    Attributes:
        props: tuple of probabilities of the symbols.
        huffman_code: tuple of the codes of the symbols.

    Example of usage.
    >>> huffman = HuffmanCode((0.4, 0.15, 0.15, 0.15, 0.15))
    >>> huffman.code()
    ('1', '000', '001', '010', '011')

    >>> round(huffman.average_length(), 3)
    2.2
    >>> round(huffman.entropy(), 3)
    2.171
    """
    def __init__(self, propabilities: tuple[float]) -> None:
        self.props = propabilities
        self.huffman_code = self._encode()

    def _encode(self) -> None:
        """
        Function that encodes the symbols.
        """
        steps = []
        props_list = list(self.props)

        while len(props_list) > 2:
            new = props_list.pop() + props_list.pop()
            props_list.append(new)
            props_list.sort(key=lambda x: -x)

            steps.insert(0, props_list.index(new))

        result = ["0", "1"]
        for step in steps:
            current = result[step]
            result.extend([current + "0", current + "1"])
            result.remove(current)

        return tuple(result)

    def code(self) -> tuple[str]:
        """
        Getter for the code.
        """
        return self.huffman_code

    def average_length(self) -> float:
        """
        Average length of the code.
        """
        return sum(prop * len(code) for prop, code in zip(self.props, self.huffman_code))

    def entropy(self) -> float:
        """
        Entropy of the code.
        """
        return sum(-prop * log2(prop) for prop in self.props)


if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
