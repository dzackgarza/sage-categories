from pathlib import Path

__all__ = ["generate_stubs"]

def generate_stubs(package: str, output_directory: Path) -> tuple[Path, ...]: ...
