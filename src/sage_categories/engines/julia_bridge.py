"""Private Julia process boundaries for Catlab/GATlab and OSCAR."""

from __future__ import annotations

import atexit
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from functools import cache
from importlib import import_module
from numbers import Integral
from pathlib import Path
from threading import Lock
from typing import Any

__all__ = ["catlab_bridge", "oscar_bridge"]


def _bridge_source(name: str) -> Path:
    return Path(__file__).with_name(name)


@cache
def _main() -> Any:
    juliacall = import_module("juliacall")
    return juliacall.Main


@cache
def catlab_bridge() -> Any:
    """Load the pinned Catlab/GATlab bridge through JuliaCall exactly once."""
    main = _main()
    main.include(str(_bridge_source("SageCategoriesBridge.jl")))
    return main.SageCategoriesBridge


@dataclass(frozen=True, eq=False, slots=True)
class OscarHandle:
    """Opaque identity of one OSCAR value owned by the isolated Julia worker."""

    _worker: _OscarWorker
    index: int


def _oscar_cache_directory() -> Path:
    root = Path(os.environ["XDG_CACHE_HOME"]) if "XDG_CACHE_HOME" in os.environ else Path.home() / ".cache"
    return root / "sage-categories" / "oscar-1.8.2"


def _oscar_project() -> Path:
    """Materialize the pinned OSCAR project outside the source checkout."""
    directory = _oscar_cache_directory()
    directory.mkdir(parents=True, exist_ok=True)
    source = _bridge_source("OscarProject.toml")
    target = directory / "Project.toml"
    content = source.read_text(encoding="utf-8")
    if not target.exists() or target.read_text(encoding="utf-8") != content:
        target.write_text(content, encoding="utf-8")
        manifest = directory / "Manifest.toml"
        if manifest.exists():
            manifest.unlink()
    return directory


def _oscar_julia() -> str:
    """Return an available Julia 1.12.7 without resolving the Catlab project."""
    configured = os.environ.get("SAGE_CATEGORIES_OSCAR_JULIA")
    candidates = (
        configured,
        os.environ.get("PYTHON_JULIAPKG_EXE"),
        str(Path(sys.prefix) / "julia_env/pyjuliapkg/install/bin/julia"),
        str(Path.home() / ".julia/environments/pyjuliapkg/pyjuliapkg/install/bin/julia"),
        shutil.which("julia"),
    )
    for candidate in candidates:
        if not candidate or not Path(candidate).is_file():
            continue
        result = subprocess.run(
            [candidate, "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "julia version 1.12.7":
            return candidate
    raise RuntimeError("OSCAR requires Julia 1.12.7; set SAGE_CATEGORIES_OSCAR_JULIA to its executable")


def _encode_oscar(worker: _OscarWorker, value: object) -> object:
    match value:
        case OscarHandle() as handle:
            assert handle._worker is worker, "OSCAR handles belong to one worker process"
            return {"__oscar_handle__": handle.index}
        case tuple() | list():
            return [_encode_oscar(worker, part) for part in value]
        case dict():
            return {str(key): _encode_oscar(worker, part) for key, part in value.items()}
        case None | bool() | int() | float() | str():
            return value
        case Integral():
            return int(value)
    raise TypeError(f"OSCAR worker input is not JSON-convertible: {type(value)!r}")


def _decode_oscar(worker: _OscarWorker, value: object) -> object:
    if isinstance(value, dict):
        if set(value) == {"__oscar_handle__"}:
            index = value["__oscar_handle__"]
            assert isinstance(index, int)
            return OscarHandle(worker, index)
        return {key: _decode_oscar(worker, part) for key, part in value.items()}
    if isinstance(value, list):
        return tuple(_decode_oscar(worker, part) for part in value)
    return value


class _OscarWorker:
    def __init__(self) -> None:
        cache_directory = _oscar_cache_directory()
        cache_directory.mkdir(parents=True, exist_ok=True)
        self._stderr_path = cache_directory / "worker.stderr.log"
        self._stderr = self._stderr_path.open("a", encoding="utf-8")
        self._process = subprocess.Popen(
            [
                _oscar_julia(),
                "--startup-file=no",
                "--history-file=no",
                f"--project={_oscar_project()}",
                str(_bridge_source("OscarWorker.jl")),
                str(_bridge_source("OscarBridge.jl")),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self._stderr,
            text=True,
            bufsize=1,
        )
        stdin = self._process.stdin
        stdout = self._process.stdout
        assert stdin is not None
        assert stdout is not None
        self._stdin = stdin
        self._stdout = stdout
        self._lock = Lock()
        atexit.register(self.close)

    def close(self) -> None:
        if self._process.poll() is None:
            self._process.terminate()
        self._stderr.close()

    def request(self, operation: str, *arguments: object) -> object:
        request = {
            "op": operation,
            "args": [_encode_oscar(self, argument) for argument in arguments],
        }
        with self._lock:
            assert self._process.poll() is None, f"the OSCAR worker terminated unexpectedly; see {self._stderr_path}"
            self._stdin.write(json.dumps(request, separators=(",", ":")) + "\n")
            self._stdin.flush()
            line = self._stdout.readline()
        assert line, f"the OSCAR worker returned no response; see {self._stderr_path}"
        response = json.loads(line)
        assert response["ok"] is True, response["error"]
        return _decode_oscar(self, response["result"])


class _OscarBridge:
    def __init__(self) -> None:
        self._worker = _OscarWorker()

    def handle(self, operation: str, *arguments: object) -> OscarHandle:
        result = self._worker.request(operation, *arguments)
        assert isinstance(result, OscarHandle)
        return result

    def pair(self, operation: str, *arguments: object) -> tuple[OscarHandle, OscarHandle]:
        result = self._worker.request(operation, *arguments)
        assert isinstance(result, tuple) and len(result) == 2
        first, second = result
        assert isinstance(first, OscarHandle) and isinstance(second, OscarHandle)
        return first, second

    def handle_and_handles(self, operation: str, *arguments: object) -> tuple[OscarHandle, tuple[OscarHandle, ...]]:
        result = self._worker.request(operation, *arguments)
        assert isinstance(result, tuple) and len(result) == 2
        first, remaining = result
        assert isinstance(first, OscarHandle)
        assert isinstance(remaining, tuple) and all(isinstance(value, OscarHandle) for value in remaining)
        return first, remaining

    def handles(self, operation: str, *arguments: object) -> tuple[OscarHandle, ...]:
        result = self._worker.request(operation, *arguments)
        assert isinstance(result, tuple) and all(isinstance(value, OscarHandle) for value in result)
        return result

    def boolean(self, operation: str, *arguments: object) -> bool:
        result = self._worker.request(operation, *arguments)
        assert isinstance(result, bool)
        return result

    def text(self, operation: str, *arguments: object) -> str:
        result = self._worker.request(operation, *arguments)
        assert isinstance(result, str)
        return result


@cache
def oscar_bridge() -> _OscarBridge:
    """Return the OSCAR proxy backed by its dedicated Julia process/project."""
    return _OscarBridge()
