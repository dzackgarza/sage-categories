"""Maude-backed typed reduction of generic owned morphism expressions.

The Sage process maps retained owned objects and arrows to opaque integer tokens.  A
persistent clean-Python worker constructs native Maude terms, performs associativity,
identity, inverse cancellation, and equality reduction, and returns only token indices.
This process boundary avoids native lexer/signal collisions between Maude and libraries
already loaded by Sage; it is not a secondary evaluator.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from functools import cache
from pathlib import Path
from threading import Lock
from typing import Any

__all__ = ["equal_morphisms", "reduced_word"]


def _worker_path() -> Path:
    return Path(__file__).with_name("_maude_worker.py")


def _local_python() -> Path:
    return Path(__file__).resolve().parents[3] / ".venv" / "bin" / "python"


def _has_maude(executable: Path) -> bool:
    if not executable.is_file():
        return False
    result = subprocess.run(
        [str(executable), "-c", "import maude"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def _worker_command() -> list[str]:
    match os.environ.get("SAGE_CATEGORIES_MAUDE_PYTHON"):
        case str(executable) if executable:
            return [executable, str(_worker_path())]
        case _:
            local = _local_python()
            if _has_maude(local):
                return [str(local), str(_worker_path())]
            uv = shutil.which("uv")
            assert uv is not None, (
                "Maude execution requires either SAGE_CATEGORIES_MAUDE_PYTHON, "
                "a project .venv containing maude, or uv"
            )
            return [
                uv,
                "run",
                "--no-project",
                "--python",
                "3.14",
                "--with",
                "maude>=1.6,<2",
                "python",
                str(_worker_path()),
            ]


class _Worker:
    def __init__(self) -> None:
        self._process = subprocess.Popen(
            _worker_command(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        assert self._process.stdin is not None
        assert self._process.stdout is not None
        self._lock = Lock()

    def request(self, operation: str, **payload: object) -> object:
        request = {"op": operation, **payload}
        with self._lock:
            assert self._process.poll() is None, (
                "the Maude worker terminated unexpectedly"
            )
            self._process.stdin.write(json.dumps(request, separators=(",", ":")) + "\n")
            self._process.stdin.flush()
            line = self._process.stdout.readline()
        assert line, "the Maude worker returned no response"
        response = json.loads(line)
        assert response["ok"] is True, response["error"]
        return response["result"]


@cache
def _worker() -> _Worker:
    return _Worker()


class _Encoding:
    """One identity-preserving conversion context for a native equality/reduction."""

    def __init__(self) -> None:
        self._tokens: dict[int, tuple[object, int]] = {}
        self._token_values: list[object | None] = []
        self._ghost_tokens: dict[int, int] = {}
        self._objects: dict[int, tuple[object, int]] = {}

    def _object_index(self, value: object) -> int:
        identifier = id(value)
        match identifier in self._objects:
            case True:
                retained, index = self._objects[identifier]
                assert retained is value
                return index
            case False:
                index = len(self._objects)
                self._objects[identifier] = (value, index)
                return index

    def _token_index(self, value: object) -> int:
        identifier = id(value)
        match identifier in self._tokens:
            case True:
                retained, index = self._tokens[identifier]
                assert retained is value
                return index
            case False:
                index = len(self._token_values)
                self._tokens[identifier] = (value, index)
                self._token_values.append(value)
                return index

    def _ghost_token_index(self, value: object) -> int:
        identifier = id(value)
        match identifier in self._ghost_tokens:
            case True:
                return self._ghost_tokens[identifier]
            case False:
                index = len(self._token_values)
                self._ghost_tokens[identifier] = index
                self._token_values.append(None)
                return index

    def expression(self, morphism: object) -> list[Any]:
        """Convert retained structure to native input without reducing it in Python."""
        match morphism.is_composite():
            case True:
                first, second = morphism.factors()
                return ["then", self.expression(first), self.expression(second)]
            case False:
                base = morphism.base_category()
                from sage_categories.kernel.refinement import is_placed

                match is_placed(morphism, base.morphism_category(1).Identity()):
                    case True:
                        return ["id", self._object_index(morphism.domain())]
                    case False:
                        token = self._token_index(morphism)
                        inverse = base.retained_inverse(morphism)
                        match inverse:
                            case None:
                                inverse_token = self._ghost_token_index(morphism)
                            case _:
                                inverse_token = self._token_index(inverse)
                        return [
                            "a",
                            token,
                            inverse_token,
                            self._object_index(morphism.domain()),
                            self._object_index(morphism.codomain()),
                        ]

    def factors(self, indices: object) -> tuple[object, ...]:
        assert isinstance(indices, list)
        result: list[object] = []
        for index in indices:
            assert isinstance(index, int)
            value = self._token_values[index]
            assert value is not None, "Maude cannot reconstruct a ghost inverse token"
            result.append(value)
        return tuple(result)


def reduced_word(morphism: object) -> tuple[object, ...]:
    """Return exact owned atomic factors of Maude's reduced typed expression."""
    encoding = _Encoding()
    result = _worker().request("reduce", term=encoding.expression(morphism))
    return encoding.factors(result)


def equal_morphisms(first: object, second: object) -> bool:
    """Whether Maude's reductions of two endpoint-compatible expressions coincide."""
    encoding = _Encoding()
    result = _worker().request(
        "equal",
        left=encoding.expression(first),
        right=encoding.expression(second),
    )
    assert isinstance(result, bool)
    return result
