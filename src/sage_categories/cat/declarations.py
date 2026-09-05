"""The categories ``Cat`` declares the repository expects to exist (D80, D82).

Declaring a category and implementing it are two acts, and only the second belongs to a
leaf.  That is what lets information flow from the kernel into the leaves and never back
(D81): a kernel construction stated over ``Sets`` uses the declaration ``Cat`` holds, and
never reaches into the set implementation to obtain it.

Every declaration is a functor into ``Cat()``, and the parameter it takes is that
functor's domain.  A category with no parameter is the terminal-domain case: the point
``* -> Cat()``, whose value is a category.  ``Cat`` constructs that value when it declares
it, so it is an object of ``Cat()`` from that moment -- it takes its ordinal, it is placed,
and its three implementation classes are compiled from ``DeclaredCategory``'s
declarations, which name the three kinds and no operation on any of them.  A parameterized
family instead awaits the object and morphism actions
its implementation supplies, exactly as ``Discrete`` states them.

An implementation does not construct a second category.  It selects the identity functor
of this one as its first structure functor, which is the whole declaration, and there is
no binding field (D156; ``specs/functor.md``, "Implementing a named category")::

    class SetsCategory(Category[[Rule], []]):
        def structure_functors(self) -> tuple[Functor, ...]:
            return (End_Cat(Sets).one(), ...)


    Cat().implement(SetsCategory)

``Cat().implement`` constructs the class to read that declaration, because the structure
functors beside the identity are written against ``self`` like every other leaf's; the
construction then stops at the declaration and strengthens ``Sets`` in place to the class,
keeping its ordinal, instead of building a second category.  Until that call the
declaration is open work like any other.

The declarations below that no implementation claims are open work, and this module is
the queue to read.  It is never a check that fails a build (``AGENTS.md``, "Tests").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# ``Cat`` and the compiled ``Cat().ObjectType`` come from the module that bootstraps
# them, so this one holds the compiled class whatever imports it first.
from sage_categories.cat.functors import Cat, Category

if TYPE_CHECKING:
    from sage_categories.cat.category import CategoryOfCategories
    from sage_categories.cat.functors import Functor

__all__ = [
    "NN",
    "ZZ",
    "CategoryFamily",
    "DeclaredCategory",
    "Groupoids",
    "MagmaObjects",
    "MonoidObjects",
    "Posets",
    "RingObjects",
    "SemiringObjects",
    "Sets",
    "TotallyOrderedSets",
    "omega",
]


class DeclaredCategory(Category[[], []]):
    """A category ``Cat`` declared, before an implementation claims it (D80).

    Declaring says that the category exists and says nothing about its mathematics, so
    the three classes below name the three kinds and no operation on any of them.  That
    is the whole content of a declaration, and it is why implementing is a second act.
    ``Cat().implement`` completes the connection on this one object: the class is
    strengthened in place -- the same in-place strengthening every value receives when its
    placement improves -- and the roles are compiled again from the implementation's own
    declarations, keeping the ordinal declaration gave it.

    These three bodies are empty, and writing them is not the same as the kernel filling
    the gap.  Written, they are a statement ``Cat`` makes on its own authority about a
    category it has only declared, and the author of every role is known before and after
    ``Cat().implement``: ``Cat`` here, the implementation afterwards.  A class the kernel
    supplied is nobody's statement, and under it a category that is deliberately silent
    and one whose author forgot a declaration are the same category (POL-CAT-057).
    """

    class ObjectType:
        """An object of a category whose mathematics no implementation has stated yet."""

    class ElementType:
        """A generalized element of such an object."""

    class MorphismType:
        """A morphism between two such objects."""

    def __init__(self, name: str) -> None:
        self._name = name
        super().__init__()

    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return self._name


class CategoryFamily:
    """A parameterized family ``Cat`` declared: the functor ``domain -> Cat()`` awaiting its actions.

    ``FF`` over ``Discrete(Primes)`` and ``MonoidObjects`` over ``Cat()`` are the two
    shapes.  Applying the family is applying that functor, so a family no implementation
    claims has no category to return, and an empty one would put a category with no
    mathematics into ``Cat()``.
    """

    def __init__(self, name: str, domain: Category) -> None:
        self._name = name
        self._domain = domain
        self._functor: Functor | None = None

    def name(self) -> str:
        return self._name

    def domain(self) -> Category:
        return self._domain

    def implemented_by(self, implementation: Functor) -> None:
        from sage_categories.cat.functors import Fun

        assert implementation in Fun(self._domain, Cat()), (
            f"{implementation!r} implements the declared family {self._name!r} and is not a functor {self._domain!r} -> Cat"
        )
        self._functor = implementation

    def __call__(self, argument: CategoryOfCategories.ElementType) -> Category:
        assert self._functor is not None, (
            f"{self._name} is declared and no implementation claims it, so it has no category to return"
        )
        return self._functor.on_object(argument)

    def __repr__(self) -> str:
        return self._name


# The points: a declaration with the terminal domain, whose value is a category.
Sets: Category = Cat().declare("Sets")
Posets: Category = Cat().declare("Posets")
# ``Groupoids()``: the point of ``Cat()`` the core functor lands in.  ``cat/core.py``
# claims it and states the one arrow the documents state, its inclusion into ``Cat()``;
# groupoid theory stands behind neither (D99).
Groupoids: Category = Cat().declare("Groupoids")
TotallyOrderedSets: Category = Cat().declare("TotallyOrderedSets")

# The categories whose implementations supply distinguished arithmetic objects.
NN: Category = Cat().declare("NN")
ZZ: Category = Cat().declare("ZZ")

# ``omega = Thin(NN, natural_order)``, the sequential shape (``specs/sets.md``, "General
# limits and colimits").  Its carrier and its order are the mathematics of ``NN``, so the
# category that owns them implements this one; the kernel owns ``Thin`` and names the
# shape.
omega: Category = Cat().declare("omega")

# The construction families: functors ``Cat() -> Cat()`` carrying an ambient category to
# the category of its internal magma, monoid, semiring, and ring objects.
MagmaObjects: CategoryFamily = Cat().declare_family("MagmaObjects", Cat())
MonoidObjects: CategoryFamily = Cat().declare_family("MonoidObjects", Cat())
SemiringObjects: CategoryFamily = Cat().declare_family("SemiringObjects", Cat())
RingObjects: CategoryFamily = Cat().declare_family("RingObjects", Cat())
