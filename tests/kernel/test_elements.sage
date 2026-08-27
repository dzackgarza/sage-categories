"""Generalized elements, stages, stage comparisons, and result transport (``specs/functor.md``, "Structural inheritance").

Toy categories live only in this file (POL-TEST-006): abelian groups with the chosen stage ``Z``
(a classical element of ``A`` is a homomorphism ``Z -> A``, determined by the image of
``1``), modules over ``R = Z/2`` with the chosen stage ``R``, and the two-generator free
modules included into them.  The module-to-group functor retains the stage comparison
``Z -> U(R)``, ``1 |-> 1``; the group-to-set functor retains ``1 -> ZZ``, ``* |-> 1``.

Oracles: the definition of a generalized element and of its image under a functor
(``F`` applied to the defining morphism); the definition of the stage comparison (the
classical image is ``F(t)`` precomposed with ``G_D -> F(G_C)``); the sum in
``(Z/2)^2``; POL-CAT-062 for the category of every inherited result; POL-CAT-012 for
the construction-defect error; the classical stages ``1`` of ``Sets()`` and ``{1, [1]}``
of ``Cat()``.
"""

import functools
import itertools

import pytest
from sage.structure.coerce_dict import MonoDict

from sage_categories.all import *
from sage_categories.kernel.compiler import StructuralImageMismatch
from sage_categories.kernel.roles import ElementOfObject, MorphismOfCategory, ObjectOfCategory
from sage_categories.sets.elements import Datum
from sage_categories.sets.maps import SetMap
from sage_categories.sets.objects import SetObject


def _datum_of(carrier, point):
    """The enumeration datum of a point of a finite enumerated set."""
    return next(datum for datum in Sets().Finite().chosen_enumeration(carrier) if carrier.point(datum) is point)


# -- toy abelian groups: carrier, addition, and integer multiples on data ------------------


class ToyGroup(ObjectOfCategory):
    def __init__(self, category, carrier, add, multiple):
        ObjectOfCategory.__init__(self, category)
        self._carrier = carrier
        self._add = add
        self._multiple = multiple
        self._elements = {}

    def carrier(self) -> SetObject:
        return self._carrier

    def element(self, datum: Datum) -> ToyGroupElement:
        """The classical element ``Z -> A``, ``k |-> k . datum``."""
        if datum not in self._elements:
            groups = ToyAbelianGroups()
            hom = groups.MorphismType(Mor(groups), groups.integers(), self, Mor(Sets())(ZZ, self._carrier)(lambda k: self._multiple(k, datum)))
            self._elements[datum] = self.category().ElementType(hom)
        return self._elements[datum]

    def __repr__(self):
        return f"ToyGroup({self._carrier!r})"


class ToyGroupElement(ElementOfObject):
    def __init__(self, hom):
        ElementOfObject.__init__(self, hom)

    def __add__(self, other: ToyGroupElement) -> ToyGroupElement:
        group = self.parent()
        return group.element(group._add(_datum_of(group.carrier(), self.defining_morphism().set_map()(ZZ(int(1)))), _datum_of(group.carrier(), other.defining_morphism().set_map()(ZZ(int(1))))))

    def __repr__(self):
        return f"point of {self.parent()!r} at stage {self.stage()!r}"


class ToyGroupHom(MorphismOfCategory):
    def __init__(self, category, domain, codomain, set_map):
        MorphismOfCategory.__init__(self, category, domain, codomain)
        self._set_map = set_map

    def set_map(self) -> SetMap:
        return self._set_map

    def __repr__(self):
        return f"ToyGroupHom({self.domain()!r} -> {self.codomain()!r})"


class ToyAbelianGroupsCategory(Category):
    ObjectType = ToyGroup
    ElementType = ToyGroupElement
    MorphismType = ToyGroupHom

    def __init__(self):
        self._functors = {}
        super().__init__()
        self._integers = self.ObjectType(self, ZZ, lambda a, b: a + b, lambda k, a: k * a)
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
            self._functors["underlying_set"] = Fun(self, Sets()).Faithful()(lambda group: group.carrier(), lambda hom: hom.set_map())
        return self._functors["underlying_set"]

    def cyclic(self, modulus):
        """``Z/n`` on the carrier ``{0, ..., n - 1}``."""
        return self.ObjectType(self, Sets().Simplex(modulus - int(1)), lambda a, b: (a + b) % modulus, lambda k, a: (k * a) % modulus)

    def element_from_defining_morphism(self, hom):
        assert hom in Mor(self)
        if hom.domain() is self._integers:
            return hom.codomain().element(_datum_of(hom.codomain().carrier(), hom.set_map()(ZZ(int(1)))))
        return hom.codomain().category().ElementType(hom)

    def construct_morphism(self, domain, codomain, rule):
        return self.MorphismType(Mor(self), domain, codomain, Mor(Sets())(domain.carrier(), codomain.carrier())(rule))

    def construct_identity(self, group):
        return self.MorphismType(Mor(self), group, group, group.carrier().identity())

    def composite(self, second, first):
        assert first.codomain() is second.domain()
        return self.MorphismType(Mor(self), first.domain(), second.codomain(), second.set_map() * first.set_map())

    def __repr__(self):
        return "ToyAbelianGroups"


_GROUPS = ToyAbelianGroupsCategory()


def ToyAbelianGroups():
    return _GROUPS


# -- toy modules over R = Z/2: carriers are tuples of bits ---------------------------------


def _bits(rank):
    return Sets().Finite()(tuple(itertools.product((int(0), int(1)), repeat=rank)))


class ToyModule(ObjectOfCategory):
    def __init__(self, category, rank):
        ObjectOfCategory.__init__(self, category)
        self._rank = rank
        self._carrier = _bits(rank)
        self._elements = {}
        self._additive_group = ToyAbelianGroups().ObjectType(
            ToyAbelianGroups(),
            self._carrier,
            lambda v, w: tuple((a + b) % int(2) for a, b in zip(v, w)),
            lambda k, v: tuple((k * a) % int(2) for a in v),
        )

    def carrier(self) -> SetObject:
        return self._carrier

    def additive_group(self) -> ToyGroup:
        return self._additive_group

    def element(self, vector: Datum) -> ToyModuleElement:
        """The classical element ``R -> M``, ``r |-> r . vector``."""
        if vector not in self._elements:
            modules = ToyModules()
            hom = modules.MorphismType(Mor(modules), modules.ring(), self, Mor(Sets())(modules.ring().carrier(), self._carrier)(lambda r: tuple((r[int(0)] * a) % int(2) for a in vector)))
            self._elements[vector] = self.category().ElementType(hom)
        return self._elements[vector]

    def __repr__(self):
        return f"ToyModule(rank {self._rank})"


class ToyModuleElement(ElementOfObject):
    """No local operation: addition arrives through the additive group."""

    def __init__(self, hom):
        ElementOfObject.__init__(self, hom)

    def __repr__(self):
        return f"point of {self.parent()!r} at stage {self.stage()!r}"


class ToyLinearMap(MorphismOfCategory):
    def __init__(self, category, domain, codomain, set_map):
        MorphismOfCategory.__init__(self, category, domain, codomain)
        self._set_map = set_map

    def set_map(self) -> SetMap:
        return self._set_map

    def __repr__(self):
        return f"ToyLinearMap({self.domain()!r} -> {self.codomain()!r})"


class ToyModulesCategory(Category):
    ObjectType = ToyModule
    ElementType = ToyModuleElement
    MorphismType = ToyLinearMap

    def __init__(self):
        self._functors = {}
        super().__init__()
        self._ring = self.ObjectType(self, int(1))
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
            groups = ToyAbelianGroups()
            retained = MonoDict()

            def additive_hom(linear):
                if linear not in retained:
                    retained[linear] = groups.MorphismType(Mor(groups), linear.domain().additive_group(), linear.codomain().additive_group(), linear.set_map())
                return retained[linear]

            self._functors["additive_group"] = Fun(self, groups).Faithful()(lambda module: module.additive_group(), additive_hom)
        return self._functors["additive_group"]

    def __call__(self, rank):
        return self.ObjectType(self, rank)

    def element_from_defining_morphism(self, hom):
        assert hom in Mor(self)
        if hom.domain() is self._ring:
            return hom.codomain().element(_datum_of(hom.codomain().carrier(), hom.set_map()(self._ring.carrier().point((int(1),)))))
        return hom.codomain().category().ElementType(hom)

    def construct_morphism(self, domain, codomain, rule):
        return self.MorphismType(Mor(self), domain, codomain, Mor(Sets())(domain.carrier(), codomain.carrier())(rule))

    def construct_identity(self, module):
        return self.MorphismType(Mor(self), module, module, module.carrier().identity())

    def composite(self, second, first):
        assert first.codomain() is second.domain()
        return self.MorphismType(Mor(self), first.domain(), second.codomain(), second.set_map() * first.set_map())

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


class Rebuilt(Category):
    """A leaf whose second selected functor rebuilds the ancestor set instead of returning the retained one."""

    class ObjectType(ObjectOfCategory):
        def __init__(self, category, members):
            ObjectOfCategory.__init__(self, category)
            self._members = members
            self._carrier = Sets().Finite()(members)

    class ElementType(ElementOfObject):
        """No local operation."""

    class MorphismType(MorphismOfCategory):
        """No local operation."""

    def structure_functors(self):
        return (
            Fun(self, Sets())(lambda member: member._carrier, lambda morphism: morphism),
            Fun(self, Sets())(lambda member: Sets().Finite()(member._members), lambda morphism: morphism),
        )

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


def test_the_stage_comparison_supplies_additive_element_inheritance() -> None:
    modules, groups = ToyModules(), ToyAbelianGroups()
    additive = modules.structure_functors()[int(0)]
    plane = modules(int(2))
    first, second = plane.element((int(1), int(0))), plane.element((int(0), int(1)))

    comparison = additive.stage_comparison()
    assert comparison in Mor(groups)(groups.integers(), additive.on_object(modules.ring()))
    assert ask(comparison.set_map()(ZZ(int(3))) == modules.ring().carrier().point((int(1),))) is True
    assert additive.on_element(first).stage() is additive.on_object(modules.ring())

    total = first + second
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
    member = rebuilt.ObjectType(rebuilt, (int(1), int(2)))
    with pytest.raises(StructuralImageMismatch):
        member.cardinality()
