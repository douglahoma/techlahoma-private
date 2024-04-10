#!/usr/bin/python3

from random import SystemRandom

class SecretKey(bytes):

    def __new__(cls, length=49):
        """Set up so that the secret key can be created using an abbreviated
        syntax of just 'SecretKey()' or 'SecretKey(YOUR_LENGTH_HERE)' -- uses
        49 as a default length if none is given."""
        return (
            super().__new__(
                cls, cls.generate_secret_key(length)
            )
        )

    @classmethod
    def generate_secret_key(cls, length=49) -> bytes:
        """What is ultimately the real function buried under all of this
        syntactic sugar. Generates a random(ish) -- it has to exclude certain
        characters -- string of the specified number of characters."""
        rng = SystemRandom()
        charset = cls.populate_charset()

        return "".join(
            rng.choice(charset) for x in range(length)
        ).encode()

    @staticmethod
    def populate_charset() -> tuple:
        """We need to make sure to weed out certain problematic characters
        like parentheses, brackets, and curly braces."""
        return tuple(
            chr(z) for z in [
                *[x for x in range(42, 91)],
                *[y for y in range(94, 123)]
            ]
        )

if __name__ == "__main__":
    """When invoked directly the script just prints out the default forty-nine
    character long secret key."""
    print(SecretKey())
