"""Generalized elements, stages, stage comparisons, and result transport (``specs/functor.md``, "Structural inheritance").

Toy categories live only in this file (POL-TEST-006): abelian groups with the chosen stage ``Z``
(a classical element of ``A`` is a homomorphism ``Z -> A``, determined by the image of
``1``), modules over ``R = Z/2`` with the chosen stage ``R``, and the two-generator free
modules included into them.  The module-to-group functor retains the stage comparison
``Z -> U(R)``, ``1 |-> 1``; the group-to-set functor retains ``1 -> ZZ``, ``* |-> 1``.

Each toy declares only the roles whose mathematics it introduces, and each local
constructor takes one exact typed datum (POL-KERNEL-028, POL-LEAF-047).  A selected
functor retains its object and morphism construction-input conversions; the element
conversion is derived from the morphism one (POL-FUN-002).

Oracles: the definition of a generalized element and of its image under a functor
(``F`` applied to the defining morphism); the definition of the stage comparison (the
classical image is ``F(t)`` precomposed with ``G_D -> F(G_C)``); the sum in
``(Z/2)^2``; POL-CAT-062 for the category of every inherited result; POL-CAT-012 for
the construction-defect error; the classical stages ``1`` of ``Sets()`` and ``{1, [1]}``
of ``Cat()``.
"""

import functools
import itertools
from dataclasses import dataclass, field

import pytest

from sage.structure.coerce_dict import MonoDict

from sage_categories.all import *
from sage_categories.kernel.compiler import StructuralImageMismatch
from sage_categories.kernel.construction import retained_morphism_input, retained_object_input
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory
from sage_categories.sets.category import SetMap
from sage_categories.sets.elements import Datum
from sage_categories.sets.objects import SetObject


def _datum_of(carrier, point):
    """The enumeration datum of a point of a finite enumerated set."""
    return next(datum for datum in Sets().Finite().chosen_enumeration(carrier) if carrier.point(datum) is point)


# -- toy abelian groups: carrier, addition, and integer multiples on data ------------------


@dataclass(eq=False, slots=True)
class ToyGroupData:
    """The carrier of an abelian group, its addition, and its integer multiples."""

    carrier: SetObject
    add: object
    multiple: object
    elements: dict = field(default_factory=dict)


@dataclass(frozen=True, eq=False, slots=True)
class ToyGroupHomData:
    """The underlying set map of a group homomorphism."""

    set_map: SetMap


@dataclass(eq=False, slots=True)
class ToyGroupElementData:
    """The group a classical element belongs to and the carrier datum it selects."""

    group: object
    datum: Datum


class ToyGroupDeclaration(ObjectOfCategory):
    def __init__(self, data):
        self._group_data = data
        super().__init__()

    def carrier(self) -> SetObject:
        return self._group_data.carrier

    def add(self, first: Datum, second: Datum) -> Datum:
        return self._group_data.add(first, second)

    def element(self, datum: Datum) -> object:
        """The classical element ``Z -> A``, ``k |-> k . datum``."""
        state = self._group_data
        if datum not in state.elements:
            groups = ToyAbelianGroups()
            hom = Mor(groups)(groups.integers(), self)(lambda k: state.multiple(k, datum))
            state.elements[datum] = self.category().ElementType(hom, ToyGroupElementData(self, datum))
        return state.elements[datum]

    def __repr__(self):
        return f"ToyGroup({self._group_data.carrier!r})"


class ToyGroupElementDeclaration(ElementOfObject):
    def __init__(self, data):
        self._group_element_data = data
        super().__init__()

    def __add__(self, other):
        """``x + y`` in the group this element belongs to (POL-CAT-062: the result stays there)."""
        state = self._group_element_data
        group = state.group
        return group.element(group.add(state.datum, other._group_element_data.datum))

    def __repr__(self):
        return f"point of {self.parent()!r} at stage {self.stage()!r}"


class ToyGroupHomDeclaration(MorphismOfCategory):
    def __init__(self, data):
        self._group_hom_data = data
        super().__init__()

    def set_map(self) -> SetMap:
        return self._group_hom_data.set_map

    def __repr__(self):
        return f"ToyGroupHom({self.domain()!r} -> {self.codomain()!r})"


class ToyAbelianGroupsCategory(Category):
    DeclaredObjectType = ToyGroupDeclaration
    DeclaredElementType = ToyGroupElementDeclaration
    DeclaredMorphismType = ToyGroupHomDeclaration

    def __init__(self):
        self._functors = {}
        self._generalized = MonoDict()
        super().__init__()
        self._integers = self.ObjectType(self, ToyGroupData(ZZ, lambda a, b: a + b, lambda k, a: k * a))
        # G_Sets = 1 -> U(Z) = ZZ selects 1: the stage comparison of the underlying-set functor.
        self.underlying_set_functor().retain_stage_comparison(ZZ(int(1)).defining_morphism())

    def integers(self):
        return self._integers

    def classical_stages(self):
        return (self._integers,)

    def structure_functors(self):
        return (self.underlying_set_functor(),)

    def underlying_set_functor(self):
        if "underlying_set" not in self._functors:
            underlying = Fun(self, Sets()).Faithful()(lambda group: group.carrier(), lambda hom: hom.set_map())
            underlying.retain_object_constructor_conversion(lambda source: retained_object_input(source.datum.carrier))
            underlying.retain_morphism_constructor_conversion(lambda source: retained_morphism_input(source.datum.set_map))
            self._functors["underlying_set"] = underlying
        return self._functors["underlying_set"]

    def cyclic(self, modulus):
        """``Z/n`` on the carrier ``{0, ..., n - 1}``."""
        carrier = Sets().Simplex(modulus - int(1))
        return self.ObjectType(self, ToyGroupData(carrier, lambda a, b: (a + b) % modulus, lambda k, a: (k * a) % modulus))

    def element_from_defining_morphism(self, hom):
        """The one generalized element with this defining morphism, retained (POL-CAT-066)."""
        assert hom in Mor(self)
        if hom.domain() is self._integers:
            return hom.codomain().element(_datum_of(hom.codomain().carrier(), hom.set_map()(ZZ(int(1)))))
        if hom not in self._generalized:
            self._generalized[hom] = self.ElementType(hom)
        return self._generalized[hom]

    def construct_morphism(self, domain, codomain, rule):
        set_map = Mor(Sets())(domain.carrier(), codomain.carrier())(rule)
        return self.MorphismType(Mor(self), domain, codomain, ToyGroupHomData(set_map))

    def construct_identity(self, group):
        return self.MorphismType(Mor(self), group, group, ToyGroupHomData(group.carrier().identity()))

    def composite(self, second, first):
        assert first.codomain() is second.domain()
        return self.MorphismType(Mor(self), first.domain(), second.codomain(), ToyGroupHomData(second.set_map() * first.set_map()))

    def __repr__(self):
        return "ToyAbelianGroups"


_GROUPS = ToyAbelianGroupsCategory()


def ToyAbelianGroups():
    return _GROUPS


# -- toy modules over R = Z/2: carriers are tuples of bits ---------------------------------


def _bits(rank):
    return Sets().Finite()(tuple(itertools.product((int(0), int(1)), repeat=rank)))


@dataclass(eq=False, slots=True)
class ToyModuleData:
    """The rank of a free module, its carrier, and the additive group the functor returns."""

    rank: int
    carrier: SetObject
    additive_group: object
    elements: dict = field(default_factory=dict)


@dataclass(frozen=True, eq=False, slots=True)
class ToyLinearMapData:
    """The underlying set map of a linear map and the group homomorphism it induces."""

    set_map: SetMap
    additive: object


class ToyModuleDeclaration(ObjectOfCategory):
    def __init__(self, data):
        self._module_data = data
        super().__init__()

    def carrier(self) -> SetObject:
        return self._module_data.carrier

    def additive_group(self) -> object:
        return self._module_data.additive_group

    def element(self, vector: Datum) -> object:
        """The classical element ``R -> M``, ``r |-> r . vector``."""
        state = self._module_data
        if vector not in state.elements:
            modules = ToyModules()
            hom = Mor(modules)(modules.ring(), self)(lambda r: tuple((r[int(0)] * a) % int(2) for a in vector))
            state.elements[vector] = self.category().ElementType(hom)
        return state.elements[vector]

    def __repr__(self):
        return f"ToyModule(rank {self._module_data.rank})"


class ToyModuleElementDeclaration(ElementOfObject):
    """No local operation: addition arrives through the additive group."""

    def __repr__(self):
        return f"point of {self.parent()!r} at stage {self.stage()!r}"


class ToyLinearMapDeclaration(MorphismOfCategory):
    def __init__(self, data):
        self._linear_map_data = data
        super().__init__()

    def set_map(self) -> SetMap:
        return self._linear_map_data.set_map

    def __repr__(self):
        return f"ToyLinearMap({self.domain()!r} -> {self.codomain()!r})"


class ToyModulesCategory(Category):
    DeclaredObjectType = ToyModuleDeclaration
    DeclaredElementType = ToyModuleElementDeclaration
    DeclaredMorphismType = ToyLinearMapDeclaration

    def __init__(self):
        self._functors = {}
        self._generalized = MonoDict()
        super().__init__()
        self._ring = self._module(int(1))
        groups = ToyAbelianGroups()
        # The stage comparison Z -> U(R), 1 |-> 1: the reduction homomorphism.
        self.additive_group_functor().retain_stage_comparison(Mor(groups)(groups.integers(), self._ring.additive_group())(lambda k: (k % int(2),)))

    def ring(self):
        return self._ring

    def classical_stages(self):
        return (self._ring,)

    def structure_functors(self):
        return (self.additive_group_functor(),)

    def additive_group_functor(self):
        if "additive_group" not in self._functors:
            additive = Fun(self, ToyAbelianGroups()).Faithful()(
                lambda module: module.additive_group(),
                lambda linear: linear._linear_map_data.additive,
            )
            additive.retain_object_constructor_conversion(lambda source: retained_object_input(source.datum.additive_group))
            additive.retain_morphism_constructor_conversion(lambda source: retained_morphism_input(source.datum.additive))
            self._functors["additive_group"] = additive
        return self._functors["additive_group"]

    def _module(self, rank):
        carrier = _bits(rank)
        groups = ToyAbelianGroups()
        additive_group = groups.ObjectType(
            groups,
            ToyGroupData(
                carrier,
                lambda v, w: tuple((a + b) % int(2) for a, b in zip(v, w)),
                lambda k, v: tuple((k * a) % int(2) for a in v),
            ),
        )
        return self.ObjectType(self, ToyModuleData(rank, carrier, additive_group))

    def __call__(self, rank):
        return self._module(rank)

    def element_from_defining_morphism(self, hom):
        """The one generalized element with this defining morphism, retained (POL-CAT-066)."""
        assert hom in Mor(self)
        if hom.domain() is self._ring:
            return hom.codomain().element(_datum_of(hom.codomain().carrier(), hom.set_map()(self._ring.carrier().point((int(1),)))))
        if hom not in self._generalized:
            self._generalized[hom] = self.ElementType(hom)
        return self._generalized[hom]

    def construct_morphism(self, domain, codomain, rule):
        set_map = Mor(Sets())(domain.carrier(), codomain.carrier())(rule)
        groups = ToyAbelianGroups()
        additive = groups.MorphismType(
            Mor(groups),
            domain.additive_group(),
            codomain.additive_group(),
            ToyGroupHomData(set_map),
        )
        return self.MorphismType(Mor(self), domain, codomain, ToyLinearMapData(set_map, additive))

    def construct_identity(self, module):
        return self.construct_morphism(module, module, lambda vector: vector)

    def composite(self, second, first):
        assert first.codomain() is second.domain()
        set_map = second.set_map() * first.set_map()
        groups = ToyAbelianGroups()
        additive = groups.MorphismType(
            Mor(groups),
            first.domain().additive_group(),
            second.codomain().additive_group(),
            ToyGroupHomData(set_map),
        )
        return self.MorphismType(Mor(self), first.domain(), second.codomain(), ToyLinearMapData(set_map, additive))

    def __repr__(self):
        return "ToyModules"


_MODULES = ToyModulesCategory()


def ToyModules():
    return _MODULES


@functools.cache
def _two_generator_modules():
    """The full subcategory of the two-generator free modules, declared by one inclusion; constructed once."""
    from sage_categories.cat.properties import PropertySubcategory

    return PropertySubcategory(ToyModules(), "TwoGenerator", {}, ())


@dataclass(eq=False, slots=True)
class RebuiltData:
    """The members of a rebuilt object and the carrier its first route returns."""

    members: tuple
    carrier: SetObject


class Rebuilt(Category):
    """A leaf whose second selected functor rebuilds the ancestor set instead of returning the retained one."""

    class DeclaredObjectType(ObjectOfCategory):
        def __init__(self, data):
            self._rebuilt_data = data
            super().__init__()

    class DeclaredMorphismType(MorphismOfCategory):
        def __init__(self, data):
            self._rebuilt_map_data = data
            super().__init__()

    def __init__(self):
        self._selected = {}
        super().__init__()

    def structure_functors(self):
        if "routes" not in self._selected:
            retained = Fun(self, Sets())(lambda member: member._rebuilt_data.carrier, lambda morphism: morphism._rebuilt_map_data)
            retained.retain_object_constructor_conversion(lambda source: retained_object_input(source.datum.carrier))
            retained.retain_morphism_constructor_conversion(lambda source: retained_morphism_input(source.datum))
            rebuilt = Fun(self, Sets())(
                lambda member: Sets().Finite()(member._rebuilt_data.members),
                lambda morphism: morphism._rebuilt_map_data,
            )
            rebuilt.retain_object_constructor_conversion(lambda source: retained_object_input(Sets().Finite()(source.datum.members)))
            rebuilt.retain_morphism_constructor_conversion(lambda source: retained_morphism_input(source.datum))
            self._selected["routes"] = (retained, rebuilt)
        return self._selected["routes"]

    def __call__(self, members):
        return self.ObjectType(self, RebuiltData(members, Sets().Finite()(members)))

    def __repr__(self):
        return "Rebuilt"


def _thin_functor():
    """The ordinary, unselected functor ``Posets() -> Cat()``, ``P |-> P.thin_category()``."""

    def on_morphism(monotone):
        source, target = monotone.domain().thin_category(), monotone.codomain().thin_category()
        return Fun(source, target)(
            lambda vertex: target(monotone(vertex.point())),
            lambda comparison: Mor(target)(target(monotone(comparison.domain().point())), target(monotone(comparison.codomain().point())))(),
        )

    return Fun(Posets(), Cat())(lambda poset: poset.thin_category(), on_morphism)


# -- rows -------------------------------------------------------------------------------------


def test_cat_elements_at_stage_one_select_objects_and_at_the_walking_arrow_select_morphisms() -> None:
    walking_arrow = Cat().Simplex(int(1))
    identity = Fun(Sets(), Sets()).Equivalences().identity()

    assert Cat().classical_stages() == (Cat().Terminal(), walking_arrow)
    assert Sets().stage() is Cat().Terminal()
    assert Sets().parent() is Cat()
    assert Sets().defining_morphism() in Fun(Cat().Terminal(), Cat())
    assert Sets().defining_morphism().on_object(Cat().Terminal()(int(0))) is Sets()
    assert identity.stage() is walking_arrow
    assert identity.parent() is Cat()
    assert identity.defining_morphism().on_morphism(walking_arrow.generator("0->1")) is identity

    point = Cat().element_from_defining_morphism(Sets().defining_morphism())
    assert point.stage() is Cat().Terminal()
    assert point.parent() is Cat()
    assert point.defining_morphism() is Sets().defining_morphism()


def test_a_generalized_element_retains_its_stage_defining_morphism_and_parent() -> None:
    modules = ToyModules()
    plane, line = modules(int(2)), modules.ring()
    first_coordinate = Mor(modules)(plane, line)(lambda v: (v[int(0)],))
    generalized = modules.element_from_defining_morphism(first_coordinate)

    assert generalized.stage() is plane
    assert generalized.parent() is line
    assert generalized.defining_morphism() is first_coordinate
    assert generalized.stage() is not modules.ring()

    classical = plane.element((int(1), int(0)))
    assert classical.stage() is modules.ring()
    assert classical.parent() is plane
    assert classical.defining_morphism() in Mor(modules)(modules.ring(), plane)


def test_the_derived_element_action_applies_the_morphism_action_and_induces_the_slice_functor() -> None:
    modules, groups = ToyModules(), ToyAbelianGroups()
    additive = modules.structure_functors()[int(0)]
    plane, line = modules(int(2)), modules.ring()
    first_coordinate = Mor(modules)(plane, line)(lambda v: (v[int(0)],))
    generalized = modules.element_from_defining_morphism(first_coordinate)

    image = additive.on_element(generalized)
    assert image.defining_morphism() is additive.on_morphism(first_coordinate)
    assert image.stage() is additive.on_object(plane)
    assert image.parent() is additive.on_object(generalized.parent())
    assert image.parent() is line.additive_group()
    assert image.stage() is not groups.integers()


def test_represented_concrete_structure_makes_classical_elements_the_stage_points() -> None:
    groups = ToyAbelianGroups()
    integers, cyclic = groups.integers(), groups.cyclic(int(4))
    three = cyclic.element(int(3))

    assert groups.classical_stages() == (integers,)
    assert Sets().classical_stages() == (Sets().Terminal(),)
    assert three.stage() is integers
    assert three.defining_morphism() in Mor(groups)(integers, cyclic)
    assert ask(three.defining_morphism().set_map()(ZZ(int(2))) == Sets().Simplex(int(3)).point(int(2))) is True

    hom = Mor(groups)(integers, cyclic)(lambda k: (int(3) * k) % int(4))
    assert groups.element_from_defining_morphism(hom) is three

    doubling = Mor(groups)(cyclic, cyclic)(lambda a: (int(2) * a) % int(4))
    as_element = groups.element_from_defining_morphism(doubling)
    assert as_element.stage() is cyclic
    assert as_element.stage() is not integers


def test_the_public_element_image_keeps_the_source_stage_and_the_compiler_input_shifts_it() -> None:
    """``F.on_element(t)`` is ``q = F(t)``; the classical compiler input is ``p = q . c_F`` (POL-FUN-002/035)."""
    modules, groups = ToyModules(), ToyAbelianGroups()
    additive = modules.structure_functors()[int(0)]
    plane = modules(int(2))
    first = plane.element((int(1), int(0)))

    comparison = additive.stage_comparison()
    assert comparison in Mor(groups)(groups.integers(), additive.on_object(modules.ring()))
    assert ask(comparison.set_map()(ZZ(int(3))) == modules.ring().carrier().point((int(1),))) is True

    # The public image is ``q``: its stage is ``F(G_C)``, not the target's own stage.
    image = additive.on_element(first)
    assert image.defining_morphism() is additive.on_morphism(first.defining_morphism())
    assert image.stage() is additive.on_object(modules.ring())
    assert image.stage() is not groups.integers()

    # The inherited group operation reads the classical input ``p``, whose stage is ``Z``.
    total = first + plane.element((int(0), int(1)))
    assert total.parent() is plane.additive_group()
    assert total.stage() is groups.integers()
    assert total is plane.additive_group().element((int(1), int(1)))
    assert ask(total.defining_morphism().set_map()(ZZ(int(1))) == plane.carrier().point((int(1), int(1)))) is True
    assert (first + first) is plane.additive_group().element((int(0), int(0)))


def test_the_element_path_to_sets_and_special_methods_through_a_length_two_route() -> None:
    modules = ToyModules()
    free = _two_generator_modules()
    plane = free(modules(int(2)))
    first, second = plane.element((int(1), int(0))), plane.element((int(0), int(1)))

    assert plane in free
    assert first.parent() is plane
    total = first + second
    assert total.parent() is plane.additive_group()
    assert total.stage() is ToyAbelianGroups().integers()
    # ``(1, 0) + (0, 1) = (1, 1)`` and ``(0, 1) + (0, 1) = (0, 0)`` in ``(Z/2)^2``: the
    # special method inherited over two edges returns those sums, not merely a value of
    # the additive image at the target stage.
    assert total is plane.additive_group().element((int(1), int(1)))
    assert ask(total.defining_morphism().set_map()(ZZ(int(1))) == plane.carrier().point((int(1), int(1)))) is True
    assert (second + second) is plane.additive_group().element((int(0), int(0)))

    assert hash(first) == hash(plane.carrier().point((int(1), int(0))))
    assert first in plane
    assert ask(plane.cardinality() == int(4)) is True
    assert plane.point((int(1), int(1))) is plane.carrier().point((int(1), int(1)))


def test_a_route_of_length_two_transports_one_object_element_and_morphism_to_exact_images() -> None:
    modules, groups = ToyModules(), ToyAbelianGroups()
    free = _two_generator_modules()
    inclusion = free.structure_functors()[int(0)]
    additive = modules.structure_functors()[int(0)]
    plane = free(modules(int(2)))
    swap = Mor(free)(plane, plane)(lambda v: (v[int(1)], v[int(0)]))
    first = plane.element((int(1), int(0)))

    assert additive.on_object(inclusion.on_object(plane)) is plane.additive_group()
    assert additive.on_morphism(inclusion.on_morphism(swap)).set_map() is swap.set_map()
    assert additive.on_morphism(inclusion.on_morphism(swap)) in Mor(groups)(plane.additive_group(), plane.additive_group())
    assert ask(swap(first) == plane.carrier().point((int(0), int(1)))) is True
    assert swap(first).parent() is plane.carrier()
    image = additive.on_element(inclusion.on_element(first))
    assert image.parent() is plane.additive_group()
    assert image.defining_morphism().set_map() is first.defining_morphism().set_map()


def test_product_stages_map_to_the_factor_stages_with_the_identity_comparison() -> None:
    modules, groups = ToyModules(), ToyAbelianGroups()
    product = Cat().Products()((modules, groups))
    pair = product((modules.ring(), groups.integers()))

    assert product.classical_stages() == (pair,)
    assert product.product_projection(int(0)).on_object(pair) is modules.ring()
    assert product.product_projection(int(0)).stage_comparison() is modules.ring().identity()
    assert product.product_projection(int(1)).stage_comparison() is groups.integers().identity()


def test_an_empty_local_element_role_still_exposes_the_generalized_point_interface() -> None:
    modules = ToyModules()
    plane = modules(int(2))
    element = plane.element((int(1), int(1)))

    assert element.stage() is modules.ring()
    assert element.parent() is plane
    assert element.defining_morphism() in Mor(modules)(modules.ring(), plane)
    assert element.defining_morphism().codomain() is plane


def test_an_unselected_functor_maps_generalized_points_and_contributes_no_operation() -> None:
    chain = Posets().Simplex(int(2))
    carrier = Sets().Simplex(int(2))
    thin_functor = _thin_functor()
    one = chain.element(carrier.point(int(1)))

    assert thin_functor in Fun(Posets(), Cat())
    assert all(selected is not thin_functor for selected in Posets().structure_functors())
    assert thin_functor.on_object(chain) is chain.thin_category()
    image = thin_functor.on_element(one)
    assert image.parent() is chain.thin_category()
    assert image.stage() is Posets().Terminal().thin_category()
    assert image.defining_morphism().on_object(Posets().Terminal().thin_category()(Sets().Terminal().point(()))) is chain.thin_category()(carrier.point(int(1)))
    with pytest.raises(AttributeError):
        chain.morphism_category
    with pytest.raises(AttributeError):
        chain.Products


def test_the_eager_check_raises_the_construction_defect_before_any_inherited_method_returns() -> None:
    rebuilt = Rebuilt()
    with pytest.raises(StructuralImageMismatch):
        rebuilt((int(1), int(2)))
