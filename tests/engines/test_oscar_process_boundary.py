"""OSCAR runs outside the package-global Catlab Julia process."""

from __future__ import annotations

import importlib.util
import json
import sys
import tomllib
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parents[2]
ENGINE = ROOT / "src/sage_categories/engines"


def _julia_bridge() -> ModuleType:
    path = ENGINE / "julia_bridge.py"
    spec = importlib.util.spec_from_file_location("julia_bridge_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_oscar_project_is_disjoint_from_catlab_project() -> None:
    global_project = json.loads((ROOT / "src/sage_categories/juliapkg.json").read_text())
    oscar_project = tomllib.loads((ENGINE / "OscarProject.toml").read_text())

    global_packages = set(global_project["packages"])
    assert global_packages == {"Catlab", "GATlab"}
    assert "Oscar" not in global_packages

    oscar_packages = set(oscar_project["deps"])
    assert oscar_packages == {"JSON", "Oscar"}
    assert "Catlab" not in oscar_packages
    assert "GATlab" not in oscar_packages
    assert oscar_project["compat"]["julia"] == "=1.12.7"
    assert oscar_project["compat"]["Oscar"] == "=1.8.2"


def test_oscar_executable_lookup_does_not_resolve_catlab_project() -> None:
    bridge = _julia_bridge()
    executable = Path(bridge._oscar_julia())
    assert executable.name == "julia"
    assert executable.is_file()


def test_oscar_handles_belong_to_one_worker() -> None:
    bridge = _julia_bridge()
    first_worker = object.__new__(bridge._OscarWorker)
    second_worker = object.__new__(bridge._OscarWorker)
    handle = bridge.OscarHandle(first_worker, 7)

    assert bridge._encode_oscar(first_worker, handle) == {"__oscar_handle__": 7}
    decoded = bridge._decode_oscar(first_worker, {"__oscar_handle__": 7})
    assert isinstance(decoded, bridge.OscarHandle)
    assert decoded._worker is first_worker
    assert decoded.index == 7

    with pytest.raises(AssertionError):
        bridge._encode_oscar(second_worker, handle)


def test_oscar_worker_executes_without_loading_oscar_into_catlab() -> None:
    bridge = _julia_bridge()
    main = bridge._main()
    bridge.catlab_bridge()
    assert bool(main.seval("isdefined(Main, :SageCategoriesBridge)"))
    assert not bool(main.seval("isdefined(Main, :Oscar)"))

    assert bridge.oscar_bridge().text("version") == "1.8.2"

    assert not bool(main.seval("isdefined(Main, :Oscar)"))
