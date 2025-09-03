import string
from typing import Dict, Callable


DEFAULT_ALPHABET = string.digits + string.ascii_letters



class Base62:
    """
    Base62 encoder/decoder.
    """
    

    def __init__(self, alphabet: str = DEFAULT_ALPHABET) -> None:
        if len(set(alphabet)) != len(alphabet):
            raise ValueError("Alphabet must contain unique characters.")
        
        if len(alphabet) < 2:
            raise ValueError("Alphabet must have at least two characters.")
        
        self.alphabet: str = alphabet
        self.base: int = len(alphabet)
        self._index: Dict[str, int] = {ch: i for i, ch in enumerate(alphabet)}

    def encode(self, num: int) -> str:
        """Encode a non-negative integer to a base-N string (N=len(alphabet))."""
        if not isinstance(num, int):
            raise TypeError("num must be an int.")
        
        if num < 0:
            raise ValueError("num must be non-negative.")
        
        if num == 0:
            return self.alphabet[0]

        digits = []
        n = num
        while n > 0:
            n, rem = divmod(n, self.base)
            digits.append(self.alphabet[rem])
        return "".join(reversed(digits))

    def decode(self, s: str) -> int:
        """Decode a base-N string (N=len(alphabet)) into a non-negative integer."""
        if not isinstance(s, str):
            raise TypeError("s must be a str.")
        if not s:
            raise ValueError("s must be a non-empty string.")

        n = 0
        for ch in s:
            try:
                val = self._index[ch]
            except KeyError as e:
                raise ValueError(f"Invalid character for this alphabet: {ch!r}") from e
            n = n * self.base + val
        return n



_default_b62 = Base62()

encoder: Callable[[int], str] = _default_b62.encode
decoder: Callable[[str], int] = _default_b62.decode
