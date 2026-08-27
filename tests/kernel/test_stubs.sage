"""The static projection: the generator, the committed stubs, and a downstream declaration.

The propositions here are about a type checker's reading of the compiled surface,
so each specimen is a file mypy checks.  ``--follow-imports=silent`` keeps the
verdict about the specimen's own expressions: the modules it imports supply types
and report nothing of their own.

Toy categories live only in this file (POL-TEST-006); the two here are written into
a temporary directory because the generator's unit is a module, and because a
declaration that must fail generation cannot share a module with one that must not.
"""

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import sage_categories
from sage_categories.kernel.stubs import StubGenerationError, generate_stubs

SOURCE = Path(sage_categories.__file__).resolve().parents[1]
PACKAGE = SOURCE / "sage_categories"


def check(target, *search):
    """The diagnostics mypy reports for one file, its imports supplying types only."""
    environment = dict(os.environ)
    environment["MYPYPATH"] = os.pathsep.join(str(directory) for directory in (*search, SOURCE))
    finished = subprocess.run(
        [sys.executable, "-m", "mypy", "--follow-imports=silent", "--no-incremental", "--no-color-output", str(target)],
        capture_output=True,
        text=True,
        cwd=target.parent,
        env=environment,
    )
    return finished.stdout


def write(directory, name, body):
    """One module of a generation set, written where the generator can import it."""
    path = directory / f"{name}.py"
    path.write_text(textwrap.dedent(body))
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))
    return path


# ``Carrier()`` owns an addition on its generalized elements and returns ``Self``;
# ``Additive()`` declares one inclusion into it and no element class of its own.  The
# sum of two elements of ``Additive()`` is therefore an inherited operation whose
# result is the receiver's role, which is what the third specimen reads.

DOWNSTREAM = '''
    """A downstream declaration: an addition owned upstream, inherited downstream."""

    from __future__ import annotations

    from typing import Self

    from sage_categories.cat.category import Category
    from sage_categories.cat.functors import Fun, Functor
    from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory


    class CarrierObject(ObjectOfCategory):
        """The carrier of the addition."""


    class CarrierElement(ElementOfObject):
        """A residue modulo three, as a generalized element of the carrier."""

        def __init__(self, residue: int) -> None:
            self._residue = residue
            super().__init__()

        def residue(self) -> int:
            """The residue this element names."""
            return self._residue

        def __add__(self, other: Self) -> Self:
            """The sum in the cyclic group of order three."""
            return self.parent().category().element(self.residue() + other.residue())


    class CarrierMorphism(MorphismOfCategory):
        """Translation by a residue: the morphisms of the one-object category are the residues."""

        def __init__(self, residue: int) -> None:
            self._residue = residue
            super().__init__()


    class CarrierCategory(Category[[], []]):
        """The upstream category: the cyclic group of order three as a one-object category."""

        DeclaredObjectType = CarrierObject
        DeclaredElementType = CarrierElement
        DeclaredMorphismType = CarrierMorphism

        def __init__(self) -> None:
            super().__init__()
            self._carrier = self.ObjectType(self)
            self._translations: dict[int, CarrierMorphism] = {}
            self._residues: dict[int, CarrierElement] = {}

        def carrier(self) -> CarrierObject:
            """The sole object."""
            return self._carrier

        def translation(self, residue: int) -> CarrierMorphism:
            """Translation by the given residue, retained once."""
            reduced = residue % 3
            if reduced not in self._translations:
                self._translations[reduced] = self.MorphismType(self.morphism_category(1), self._carrier, self._carrier, reduced)
            return self._translations[reduced]

        def element(self, residue: int) -> CarrierElement:
            """The element of the given residue: the translation by it, with the carrier as domain."""
            reduced = residue % 3
            if reduced not in self._residues:
                self._residues[reduced] = self.ElementType(self.translation(reduced), reduced)
            return self._residues[reduced]

        def construct_identity(self, member_object: ObjectOfCategory) -> CarrierMorphism:
            """The identity of the carrier: translation by zero."""
            return self.translation(0)

        def __repr__(self) -> str:
            return "Carrier"


    class AdditiveObject(ObjectOfCategory):
        """No local operation: the downstream carrier is the upstream one."""


    class AdditiveElement(ElementOfObject):
        """No local operation: the addition is inherited."""


    class AdditiveMorphism(MorphismOfCategory):
        """No local operation."""


    class AdditiveCategory(Category[[], []]):
        """The downstream category: one inclusion, and no operation of its own."""

        DeclaredObjectType = AdditiveObject
        DeclaredElementType = AdditiveElement
        DeclaredMorphismType = AdditiveMorphism

        def structure_functors(self) -> tuple[Functor, ...]:
            """The inclusion into the carrier category."""
            return (Fun(self, Carrier()).Monomorphisms().Isofibrations().Full()(),)

        def __repr__(self) -> str:
            return "Additive"


    def Carrier() -> CarrierCategory:
        """The upstream category."""
        return _CARRIER


    def Additive() -> AdditiveCategory:
        """The downstream category."""
        return _ADDITIVE


    _CARRIER = CarrierCategory()
    _ADDITIVE = AdditiveCategory()
'''

BROAD = '''
    """A declaration whose parameter is a union of two mathematical roles."""

    from __future__ import annotations

    from sage_categories.cat.category import Category
    from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory


    class BroadObject(ObjectOfCategory):
        """The object role, with one erased parameter."""

        def erased(self, value: BroadObject | BroadMorphism) -> BroadObject:
            """A parameter that is either an object or a morphism."""
            return self


    class BroadElement(ElementOfObject):
        """No local operation."""


    class BroadMorphism(MorphismOfCategory):
        """No local operation."""


    class BroadCategory(Category[[], []]):
        """A category whose object declaration erases a role."""

        DeclaredObjectType = BroadObject
        DeclaredElementType = BroadElement
        DeclaredMorphismType = BroadMorphism

        def __repr__(self) -> str:
            return "Broad"


    _BROAD = BroadCategory()
'''

COMMITTED_SPECIMEN = '''
    from typing import assert_type

    from sage_categories.kernel.decisions import UnknownClass
    from sage_categories.sets.cardinals import CardinalObject
    from sage_categories.sets.category import SetMap, Sets, Sets_Finite_MorphismType


    def cardinality_of_a_finite_set(members: tuple[int, ...]) -> None:
        assert_type(Sets().Finite()(members).cardinality(), CardinalObject | UnknownClass)


    def composite_with_a_finite_set_map(set_map: SetMap, finite: Sets_Finite_MorphismType) -> None:
        assert_type(Sets().composite(set_map, finite), SetMap)
        assert_type(Sets().MorphismType, type[SetMap])
'''

DOWNSTREAM_SPECIMEN = '''
    from typing import assert_type

    from downstream import Additive, AdditiveElement


    def sum_of_two_elements(first: AdditiveElement, second: AdditiveElement) -> None:
        assert_type(first + second, AdditiveElement)
        assert_type(Additive().ElementType, type[AdditiveElement])
'''


def test_the_committed_stubs_are_the_projection_of_the_live_declarations(tmp_path):
    """A committed stub is a derived artifact: regenerating it changes nothing (POL-TYPE-026)."""
    regenerated = {stub.relative_to(tmp_path): stub.read_text() for stub in generate_stubs((PACKAGE,), tmp_path)}
    committed = {stub.relative_to(SOURCE): stub.read_text() for stub in sorted(PACKAGE.rglob("*.pyi"))}
    assert set(regenerated) == set(committed)
    assert regenerated == committed


def test_a_finite_set_cardinality_and_a_set_composite_type_against_the_committed_stubs(tmp_path):
    """``Sets().Finite()(...).cardinality()`` is a cardinal or ``Unknown``; a composite is ``Sets().MorphismType``."""
    specimen = write(tmp_path, "committed_specimen", COMMITTED_SPECIMEN)
    assert "Success" in check(specimen), check(specimen)


def test_a_sum_on_a_downstream_category_types_as_that_category_element_type(tmp_path):
    """The generator on a declaration outside the package: the inherited sum is the downstream element role."""
    module = write(tmp_path, "downstream", DOWNSTREAM)
    (stub,) = generate_stubs((module,))
    assert stub == module.with_suffix(".pyi")
    specimen = write(tmp_path, "downstream_specimen", DOWNSTREAM_SPECIMEN)
    assert "Success" in check(specimen, tmp_path), check(specimen, tmp_path)


def test_the_inherited_sum_is_the_downstream_element_role_at_runtime(tmp_path):
    """The addition the stub states is the one the compiler installs: two and two are one modulo three.

    The stub says ``AdditiveElement(CarrierElement)`` because a declaration's name is
    the name of the compiled role.  At runtime the two compiled classes stand in that
    relation; the declarations themselves are copied into them and are not their bases.
    """
    write(tmp_path, "downstream_runtime", DOWNSTREAM)
    import downstream_runtime

    assert (downstream_runtime.Carrier().element(2) + downstream_runtime.Carrier().element(2)).residue() == 1
    assert issubclass(downstream_runtime.Additive().ElementType, downstream_runtime.Carrier().ElementType)


def test_a_union_of_two_roles_fails_generation_at_its_declaration(tmp_path):
    """A parameter that is either an object or a morphism is type erasure, and the stub would state it (POL-TYPE-029)."""
    module = write(tmp_path, "broad", BROAD)
    with pytest.raises(StubGenerationError) as failure:
        generate_stubs((module,))
    assert "Broad.ObjectType.erased" in str(failure.value)
    assert "union of several mathematical roles" in str(failure.value)
