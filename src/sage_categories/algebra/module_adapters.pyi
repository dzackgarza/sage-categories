from sage_categories.cat.modules import ModuleCategory

__all__ = ["install_sage_module_adapter", "sage_module_from_engine"]

def sage_module_from_engine(
    modules: ModuleCategory, engine_module: object
) -> ModuleCategory.ObjectType: ...
def install_sage_module_adapter() -> None: ...
