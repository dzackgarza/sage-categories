"""OSCAR runs outside the package-global Catlab Julia process."""

from __future__ import annotations

import json
import tomllib
from importlib import import_module
from pathlib import Path

from sage_categories.engines import oscar
from sage_categories.engines.julia_bridge import catlab_bridge

ROOT = Path(__file__).parents[2]
ENGINE = ROOT / "src/sage_categories/engines"


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


def test_oscar_worker_executes_without_loading_oscar_into_catlab() -> None:
    catlab_bridge()
    main = import_module("juliacall").Main
    assert bool(main.seval("isdefined(Main, :SageCategoriesBridge)"))
    assert not bool(main.seval("isdefined(Main, :Oscar)"))

    assert oscar.version() == "1.8.2"
    field = oscar.prime_field(5)
    one = oscar.ring_one(field)
    assert oscar.ring_contains(field, one)
    assert oscar.same_native(one, one)

    assert not bool(main.seval("isdefined(Main, :Oscar)"))
