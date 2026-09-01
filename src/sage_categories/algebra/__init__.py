"""Internal algebraic structures in an ambient category (``specs/magmas-monoids-semirings.md``, ``specs/rings.md``, ``specs/modules.md``)."""

from sage_categories.algebra.groups import GroupPresentation, Groups, GroupsCategory
from sage_categories.algebra.magmas import Magmas, MagmasCategory
from sage_categories.algebra.modules import ModulePresentation, Modules, ModulesCategory
from sage_categories.algebra.monoids import Monoids, MonoidsCategory
from sage_categories.algebra.rings import Rings, RingsCategory
from sage_categories.algebra.semirings import Semirings, SemiringsCategory

__all__ = [
    "GroupPresentation",
    "Groups",
    "GroupsCategory",
    "Magmas",
    "MagmasCategory",
    "ModulePresentation",
    "Modules",
    "ModulesCategory",
    "Monoids",
    "MonoidsCategory",
    "Rings",
    "RingsCategory",
    "Semirings",
    "SemiringsCategory",
]
