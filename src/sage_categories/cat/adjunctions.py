"""Selected adjunction and equivalence data (D106).

``Adjunctions(F, G)`` retains the unit and counit of adjunctions with fixed
left adjoint ``F`` and right adjoint ``G``.  ``Equivalences(C, D)`` retains a
forward functor, an inverse functor, and an invertible unit and counit.  These
categories own selected data.  The corresponding functor property categories
state existence properties and retain none of this data.
"""

from __future__ import annotations

from dataclasses import dataclass

from sympy import ask as sympy_ask

from sage_categories.cat.category import Category, CategoryOfCategories
from sage_categories.cat.functors import Cat, Fun, Functor, NaturalTransformation
from sage_categories.cat.predicates import Decision, Proposition, Unknown, ask, register_handler
from sage_categories.kernel.construction import retained_objects
from sage_categories.kernel.refinement import refine
from sage_categories.kernel.retention import identity_key
from sage_categories.kernel.sage_runtime import cached_function, cached_method

__all__ = [
    "Adjunctions",
    "AdjunctionsCategory",
    "Equivalences",
    "EquivalencesCategory",
]


@dataclass(frozen=True, eq=False, slots=True)
class AdjunctionData:
    """The unit and counit retained by one adjunction."""

    forward: Functor
    inverse: Functor
    unit: NaturalTransformation
    counit: NaturalTransformation


@dataclass(frozen=True, eq=False, slots=True)
class AdjunctionMorphismData:
    """The compatible endotransformations of the two fixed adjoints."""

    forward: NaturalTransformation
    inverse: NaturalTransformation


@dataclass(frozen=True, eq=False, slots=True)
class EquivalenceData:
    """The functors and natural isomorphisms retained by one equivalence."""

    forward: Functor
    inverse: Functor
    unit: NaturalTransformation
    counit: NaturalTransformation


@dataclass(frozen=True, eq=False, slots=True)
class EquivalenceMorphismData:
    """The natural transformation represented by one equivalence morphism."""

    transformation: NaturalTransformation


class AdjunctionsCategory(Category[[NaturalTransformation, NaturalTransformation], []]):
    """``Adjunctions(F, G)`` for fixed ``F: C -> D`` and ``G: D -> C``."""

    class ObjectType:
        """Selected unit and counit data satisfying the triangle identities."""

        def __init__(self, data: AdjunctionData) -> None:
            self._adjunction_forward = data.forward
            self._adjunction_inverse = data.inverse
            self._adjunction_unit = data.unit
            self._adjunction_counit = data.counit

        def forward(self) -> Functor:
            return self._adjunction_forward

        def inverse(self) -> Functor:
            return self._adjunction_inverse

        def unit(self) -> NaturalTransformation:
            """``Id_C => G F``."""
            return self._adjunction_unit

        def counit(self) -> NaturalTransformation:
            """``F G => Id_D``."""
            return self._adjunction_counit

        def __repr__(self) -> str:
            return f"Adjunction({self.forward()!r}, {self.inverse()!r})"

    class ElementType:
        """A generalized element of selected adjunction data."""

    class MorphismType:
        """Compatible endotransformations of the two fixed adjoints."""

        def __init__(self, data: AdjunctionMorphismData) -> None:
            self._adjunction_forward_transformation = data.forward
            self._adjunction_inverse_transformation = data.inverse

        def forward_transformation(self) -> NaturalTransformation:
            return self._adjunction_forward_transformation

        def inverse_transformation(self) -> NaturalTransformation:
            return self._adjunction_inverse_transformation

    def __init__(self, forward: Functor, inverse: Functor) -> None:
        assert forward in Fun and inverse in Fun
        assert forward.domain() is inverse.codomain() and forward.codomain() is inverse.domain(), (
            f"{forward!r} and {inverse!r} do not have opposite endpoints"
        )
        self._forward = forward
        self._inverse = inverse
        super().__init__()
        register_handler(self._equality, self._equal)

    def forward(self) -> Functor:
        return self._forward

    def inverse(self) -> Functor:
        return self._inverse

    def source_category(self) -> Category:
        return self._forward.domain()

    def target_category(self) -> Category:
        return self._forward.codomain()

    def _equal(
        self,
        first: CategoryOfCategories.ElementType,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        if first in self and candidate in self:
            return sympy_ask(
                (first.unit() == candidate.unit())
                & (first.counit() == candidate.counit()),
                assumptions,
            )
        morphisms = self.morphism_category(1)
        if first in morphisms and candidate in morphisms:
            return sympy_ask(
                (first.forward_transformation() == candidate.forward_transformation())
                & (first.inverse_transformation() == candidate.inverse_transformation()),
                assumptions,
            )
        return None

    @cached_method(key=identity_key)
    def __call__(
        self,
        unit: NaturalTransformation,
        counit: NaturalTransformation,
    ) -> AdjunctionsCategory.ObjectType:
        """Select the adjunction with the supplied unit and counit."""
        source, target = self.source_category(), self.target_category()
        source_endofunctors = Fun(source, source)
        target_endofunctors = Fun(target, target)
        forward_functors = Fun(source, target)
        inverse_functors = Fun(target, source)

        assert unit.domain() is source_endofunctors.one()
        assert unit.codomain() is self._inverse * self._forward
        assert counit.domain() is self._forward * self._inverse
        assert counit.codomain() is target_endofunctors.one()

        forward_triangle = counit.whisker_right(self._forward) * unit.whisker_left(self._forward)
        inverse_triangle = counit.whisker_left(self._inverse) * unit.whisker_right(self._inverse)
        assert ask(
            forward_triangle
            == forward_functors.morphism_category(1)(self._forward, self._forward).one()
        ) is not False, "the unit and counit fail the triangle identity on the forward functor"
        assert ask(
            inverse_triangle
            == inverse_functors.morphism_category(1)(self._inverse, self._inverse).one()
        ) is not False, "the unit and counit fail the triangle identity on the inverse functor"

        return self.ObjectType(data=AdjunctionData(self._forward, self._inverse, unit, counit))

    def construct_morphism(
        self,
        source: AdjunctionsCategory.ObjectType,
        target: AdjunctionsCategory.ObjectType,
        forward: NaturalTransformation,
        inverse: NaturalTransformation,
    ) -> AdjunctionsCategory.MorphismType:
        """Construct a compatible pair of endotransformations of ``F`` and ``G``."""
        assert source in self and target in self
        forward_functors = Fun(self.source_category(), self.target_category())
        inverse_functors = Fun(self.target_category(), self.source_category())
        assert forward in forward_functors.morphism_category(1)(self._forward, self._forward)
        assert inverse in inverse_functors.morphism_category(1)(self._inverse, self._inverse)

        unit_transport = Cat().horizontal_composite(inverse, forward) * source.unit()
        counit_transport = target.counit() * Cat().horizontal_composite(forward, inverse)
        assert ask(unit_transport == target.unit()) is not False, (
            "the endotransformations are not compatible with the units"
        )
        assert ask(counit_transport == source.counit()) is not False, (
            "the endotransformations are not compatible with the counits"
        )
        return self.MorphismType(
            domain=source,
            codomain=target,
            data=AdjunctionMorphismData(forward, inverse),
        )

    def construct_identity(
        self,
        member_object: AdjunctionsCategory.ObjectType,
    ) -> AdjunctionsCategory.MorphismType:
        forward_identity = Fun(self.source_category(), self.target_category()).morphism_category(1)(
            self._forward,
            self._forward,
        ).one()
        inverse_identity = Fun(self.target_category(), self.source_category()).morphism_category(1)(
            self._inverse,
            self._inverse,
        ).one()
        return self.construct_morphism(
            member_object,
            member_object,
            forward_identity,
            inverse_identity,
        )

    def composite(
        self,
        second: AdjunctionsCategory.MorphismType,
        first: AdjunctionsCategory.MorphismType,
    ) -> AdjunctionsCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.construct_morphism(
            first.domain(),
            second.codomain(),
            second.forward_transformation() * first.forward_transformation(),
            second.inverse_transformation() * first.inverse_transformation(),
        )

    def _chosen_inhabitation(self) -> Decision:
        return True if retained_objects(self) else Unknown

    def __repr__(self) -> str:
        return f"Adjunctions({self._forward!r}, {self._inverse!r})"


class EquivalencesCategory(Category[[NaturalTransformation], []]):
    """``Equivalences(C, D)``: selected equivalence data from ``C`` to ``D``."""

    class ObjectType:
        """A forward functor, inverse functor, unit, and counit natural isomorphisms."""

        def __init__(self, data: EquivalenceData) -> None:
            self._equivalence_forward = data.forward
            self._equivalence_inverse = data.inverse
            self._equivalence_unit = data.unit
            self._equivalence_counit = data.counit

        def forward(self) -> Functor:
            return self._equivalence_forward

        def inverse(self) -> Functor:
            return self._equivalence_inverse

        def unit(self) -> NaturalTransformation:
            """The natural isomorphism ``Id_C => G F``."""
            return self._equivalence_unit

        def counit(self) -> NaturalTransformation:
            """The natural isomorphism ``F G => Id_D``."""
            return self._equivalence_counit

        def adjunction(self) -> AdjunctionsCategory.ObjectType:
            return Adjunctions(self.forward(), self.inverse())(self.unit(), self.counit())

        def __repr__(self) -> str:
            return f"Equivalence({self.forward()!r}, {self.inverse()!r})"

    class ElementType:
        """A generalized element of selected equivalence data."""

    class MorphismType:
        """A natural transformation between the selected forward functors."""

        def __init__(self, data: EquivalenceMorphismData) -> None:
            self._equivalence_transformation = data.transformation

        def transformation(self) -> NaturalTransformation:
            return self._equivalence_transformation

    def __init__(self, source: Category, target: Category) -> None:
        assert source in Cat() and target in Cat()
        self._source = source
        self._target = target
        super().__init__()
        register_handler(self._equality, self._equal)

    def source_category(self) -> Category:
        return self._source

    def target_category(self) -> Category:
        return self._target

    def _equal(
        self,
        first: CategoryOfCategories.ElementType,
        candidate: CategoryOfCategories.ElementType,
        assumptions: Proposition,
    ) -> bool | None:
        if first in self and candidate in self:
            return sympy_ask(
                (first.forward() == candidate.forward())
                & (first.inverse() == candidate.inverse())
                & (first.unit() == candidate.unit())
                & (first.counit() == candidate.counit()),
                assumptions,
            )
        morphisms = self.morphism_category(1)
        if first in morphisms and candidate in morphisms:
            return sympy_ask(
                first.transformation() == candidate.transformation(),
                assumptions,
            )
        return None

    @cached_method(key=identity_key)
    def __call__(
        self,
        forward: Functor,
        inverse: Functor,
        unit: NaturalTransformation,
        counit: NaturalTransformation,
    ) -> EquivalencesCategory.ObjectType:
        """Select an equivalence and retain its adjoint-equivalence data."""
        forward_functors = Fun(self._source, self._target)
        inverse_functors = Fun(self._target, self._source)
        assert forward in forward_functors and inverse in inverse_functors

        Adjunctions(forward, inverse)(unit, counit)
        refine(unit, unit.base_category().morphism_category(1).Isomorphisms())
        refine(counit, counit.base_category().morphism_category(1).Isomorphisms())
        refine(forward, forward_functors.Equivalences())
        refine(inverse, inverse_functors.Equivalences())

        return self.ObjectType(data=EquivalenceData(forward, inverse, unit, counit))

    def construct_morphism(
        self,
        source: EquivalencesCategory.ObjectType,
        target: EquivalencesCategory.ObjectType,
        transformation: NaturalTransformation,
    ) -> EquivalencesCategory.MorphismType:
        """Construct the morphism represented by a transformation of forward functors."""
        assert source in self and target in self
        assert transformation in Fun(self._source, self._target).morphism_category(1)(
            source.forward(),
            target.forward(),
        )
        return self.MorphismType(
            domain=source,
            codomain=target,
            data=EquivalenceMorphismData(transformation),
        )

    def construct_identity(
        self,
        member_object: EquivalencesCategory.ObjectType,
    ) -> EquivalencesCategory.MorphismType:
        identity = Fun(self._source, self._target).morphism_category(1)(
            member_object.forward(),
            member_object.forward(),
        ).one()
        return self.construct_morphism(member_object, member_object, identity)

    def composite(
        self,
        second: EquivalencesCategory.MorphismType,
        first: EquivalencesCategory.MorphismType,
    ) -> EquivalencesCategory.MorphismType:
        assert first.codomain() is second.domain()
        return self.construct_morphism(
            first.domain(),
            second.codomain(),
            second.transformation() * first.transformation(),
        )

    @cached_method
    def forward_projection(self) -> Functor:
        """The retained functor ``Equivalences(C, D) -> Fun(C, D)``."""
        return Fun(self, Fun(self._source, self._target))(
            lambda equivalence: equivalence.forward(),
            lambda morphism: morphism.transformation(),
        )

    def _chosen_inhabitation(self) -> Decision:
        return True if retained_objects(self) else Unknown

    def __repr__(self) -> str:
        return f"Equivalences({self._source!r}, {self._target!r})"


@cached_function(key=identity_key)
def Adjunctions(forward: Functor, inverse: Functor) -> AdjunctionsCategory:
    """Return the retained category of adjunction data for ``forward`` and ``inverse``."""
    return AdjunctionsCategory(forward, inverse)


@cached_function(key=identity_key)
def Equivalences(source: Category, target: Category) -> EquivalencesCategory:
    """Return the retained category of equivalence data from ``source`` to ``target``."""
    return EquivalencesCategory(source, target)
