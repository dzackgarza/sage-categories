import ast
from _typeshed import Incomplete
from pathlib import Path
__all__ = ['generate_stubs']

def generate_stubs(package: str, output_directory: Path) -> tuple[Path, ...]:
    ...

class _QualifiedClass:
    node: Incomplete
    name: Incomplete

    def __init__(self, node: ast.ClassDef, name: str) -> None:
        ...
