from _typeshed import Incomplete
__all__ = ['WordRewriter']

class WordRewriter:
    confluent: Incomplete

    def __init__(self, alphabet_size: int, equations: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]) -> None:
        ...

    def reduce(self, letters: tuple[int, ...]) -> tuple[int, ...]:
        ...

    def finite(self) -> bool:
        ...
