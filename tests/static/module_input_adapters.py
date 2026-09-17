"""Static consumer for the native ordinary-module input adapter."""

from typing import assert_type

from sage_categories.algebra.module_adapters import sage_module_from_engine
from sage_categories.cat.modules import ModuleCategory


def module_input_adapter_types(
    modules: ModuleCategory,
    engine_module: object,
) -> None:
    assert_type(
        sage_module_from_engine(modules, engine_module),
        ModuleCategory.ObjectType,
    )
