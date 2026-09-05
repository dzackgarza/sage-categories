import sage_categories
from _typeshed import Incomplete
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from sage_categories.cat.canonical import FinitePresentedCategory
from sage_categories.cat.declarations import CategoryFamily
from sage_categories.cat.functors import Functor, FunctorsCategory, NaturalTransformation
from sage_categories.cat.morphisms import MorphismCategory
from sage_categories.cat.points import PointCategory
from sage_categories.cat.predicates import AppliedQuery, Predicate, Proposition, UnknownClass
from sage_categories.kernel.sage_runtime import Integer
from typing import Literal, overload
__all__ = ['OnObject', 'OnMorphism', 'Assignment', 'member', 'Category', 'CategoryOfCategories', 'Cat']
type OnObject = Callable[[CategoryOfCategories.ElementType], CategoryOfCategories.ElementType]
type OnMorphism = Callable[['MorphismCategory.ObjectType'], 'MorphismCategory.ObjectType']
type Assignment = Callable[[CategoryOfCategories.ElementType], 'MorphismCategory.ObjectType']

class _MemberPredicate(Predicate):
    name: str
member: Predicate

class CategoryDeclaration[**MorphismData, **TwoMorphismData](sage_categories.kernel.roles.ObjectOfCategory):

    def __init__(self, data: None=None) -> None:
        ...

    def is_discrete(self) -> bool:
        ...

    def construction_owner(self) -> Category:
        ...

    def subobjects_type(self) -> type:
        ...

    def __init_subclass__(cls) -> None:
        ...

    def __mul__(self, other: Category) -> Category:
        ...

    def __add__(self, other: Category) -> Category:
        ...

    def __pow__(self, exponent: Category) -> Category:
        ...

    def op(self) -> Category:
        ...

    def universe(self) -> CategoryOfCategories:
        ...

    def ordinal(self) -> int:
        ...

    def recompile(self) -> None:
        ...

    def structure_functors(self) -> tuple[Functor, ...]:
        ...

    def selected_functors(self) -> tuple[Functor, ...]:
        ...

    def retain_datum[Datum](self, value: CategoryOfCategories.ElementType, datum: Datum) -> None:
        ...

    def retained_datum[Datum](self, value: CategoryOfCategories.ElementType) -> Datum:
        ...

    def has_ambient(self) -> bool:
        ...

    def has_full_ambient(self) -> bool:
        ...

    def ambient(self) -> Category[MorphismData, TwoMorphismData]:
        ...

    def subcategory_monomorphism(self) -> Functor:
        ...

    def equality(self) -> Predicate:
        ...

    def owns_equality(self) -> bool:
        ...

    def membership_proposition(self, candidate: CategoryOfCategories.ElementType) -> Proposition:
        ...

    def __contains__(self, candidate: CategoryOfCategories.ElementType | int) -> bool:
        ...

    @overload
    def morphism_category(self, level: Literal[0]) -> Category[MorphismData, TwoMorphismData]:
        ...

    @overload
    def morphism_category(self, level: Literal[1]) -> MorphismCategory[MorphismData, TwoMorphismData]:
        ...

    @overload
    def morphism_category(self, level: Literal[2]) -> MorphismCategory[TwoMorphismData, []]:
        ...

    @overload
    def morphism_category(self, level: int | Integer) -> MorphismCategory[[], []]:
        ...

    def morphism_category_type(self) -> type[MorphismCategory[MorphismData, TwoMorphismData]]:
        ...

    def base_category(self) -> Category:
        ...

    def retained_inverse(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType | None:
        ...

    def retain_inverses(self, forward: MorphismCategory.ObjectType, backward: MorphismCategory.ObjectType) -> None:
        ...

    def compose_morphisms(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def inverse_morphism(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def element_from_defining_morphism(self, defining_morphism: MorphismCategory.ObjectType) -> CategoryOfCategories.ElementType:
        ...

    def construct_morphism(self, domain: CategoryOfCategories.ElementType, codomain: CategoryOfCategories.ElementType, *args: MorphismData.args, **kwargs: MorphismData.kwargs) -> MorphismCategory.ObjectType:
        ...

    def construct_identity(self, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def composite(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def identity_two_morphism(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def compose_two_morphisms(self, second: MorphismCategory.ObjectType, first: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
        ...

    def construct_two_morphism(self, first: MorphismCategory.ObjectType, second: MorphismCategory.ObjectType, *args: TwoMorphismData.args, **kwargs: TwoMorphismData.kwargs) -> MorphismCategory.ObjectType:
        ...

    def Terminal(self) -> CategoryOfCategories.ElementType:
        ...

    def point_functor(self, member_object: CategoryOfCategories.ElementType) -> Functor:
        ...

    def Point(self) -> Functor:
        ...

    def arrow_functor(self, morphism: MorphismCategory.ObjectType) -> Functor:
        ...
    Products: Incomplete
    Coproducts: Incomplete
    Limits: Incomplete
    Colimits: Incomplete
    EssentialImage: Incomplete

    def Pullbacks(self) -> Category:
        ...

    def Pushouts(self) -> Category:
        ...

    def Equalizers(self) -> Category:
        ...

    def Coequalizers(self) -> Category:
        ...

    def StrictImage(self, functor: Functor) -> Category:
        ...

    def FullImage(self, functor: Functor) -> Category:
        ...

    def limit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...

    def presenting_diagrams(self, constructed: CategoryOfCategories.ElementType) -> tuple[Functor, ...]:
        ...

    def SliceOver(self, member_object: CategoryOfCategories.ElementType) -> Category:
        ...

    def CosliceUnder(self, member_object: CategoryOfCategories.ElementType) -> Category:
        ...

    def Subobjects(self, member_object: CategoryOfCategories.ElementType) -> Category:
        ...

    def Superobjects(self, member_object: CategoryOfCategories.ElementType) -> Category:
        ...

    def CoveringObjects(self, member_object: CategoryOfCategories.ElementType) -> Category:
        ...

    def CoveredObjects(self, member_object: CategoryOfCategories.ElementType) -> Category:
        ...

    def Core(self) -> Category:
        ...

    def object_set(self) -> CategoryOfCategories.ElementType:
        ...

    def object_at(self, point: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def object_point(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def morphism_set(self) -> AppliedQuery:
        ...

    def morphism_at(self, point: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
        ...

    def generating_morphisms(self) -> tuple[MorphismCategory.ObjectType, ...] | UnknownClass:
        ...

    def biproduct(self, first: CategoryOfCategories.ElementType, second: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def exponential(self, exponent: CategoryOfCategories.ElementType, base: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def name(self) -> str:
        ...

    def narrowing_base(self) -> Category[MorphismData, TwoMorphismData]:
        ...

    def narrowing_roots(self) -> tuple[Category[MorphismData, TwoMorphismData], ...]:
        ...

    def intersection(self, roots: tuple[Category[MorphismData, TwoMorphismData], ...]) -> Category[MorphismData, TwoMorphismData]:
        ...

    def property_subcategory(self, property_category: Category[MorphismData, TwoMorphismData]) -> Category[MorphismData, TwoMorphismData]:
        ...

    def __getattr__(self, name: str) -> Callable[..., Category[MorphismData, TwoMorphismData]]:
        ...

    def narrowing_type(self) -> type[Category[MorphismData, TwoMorphismData]]:
        ...
Category = CategoryDeclaration
type LiftRule = Callable[[MorphismCategory.ObjectType, CategoryOfCategories.ElementType], MorphismCategory.ObjectType]

@dataclass(frozen=True, eq=False, slots=True)
class FunctorData:
    on_object: OnObject
    on_morphism: OnMorphism

class CategoryOfCategories(CategoryDeclaration[[OnObject, OnMorphism], [Assignment]]):
    ObjectType = CategoryDeclaration
    Inhabited: Incomplete
    Empty: Incomplete

    class ElementType:

        def parent(self) -> CategoryOfCategories.ElementType:
            ...

        def defining_morphism(self) -> MorphismCategory.ObjectType:
            ...

        def category(self) -> Category:
            ...

        def __eq__(self, candidate: CategoryOfCategories.ElementType | int) -> Predicate:
            ...

        def __ne__(self, candidate: CategoryOfCategories.ElementType | int) -> Proposition:
            ...

        def __hash__(self) -> int:
            ...

        def __mul__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

        def __add__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

        def __matmul__(self, other: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

        def __pow__(self, exponent: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

        def diagram(self) -> Functor:
            ...

        def index_category(self) -> Category:
            ...

        def projection(self, index: CategoryOfCategories.ElementType | int) -> MorphismCategory.ObjectType:
            ...

        def universal_morphism(self, candidate: NaturalTransformation) -> MorphismCategory.ObjectType:
            ...

    class MorphismType(sage_categories.kernel.roles.MorphismOfCategory, sage_categories.cat.morphisms.MorphismCategory.ObjectType):

        def __init__(self, data: FunctorData) -> None:
            ...

        def on_object(self, member_object: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

        def on_morphism(self, morphism: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            ...

        def on_element(self, element: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

        def __call__(self, value: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
            ...

        def inverse_image(self, subcategory: Category) -> Category:
            ...

        def base_change(self, defining_functor: Functor) -> Functor:
            ...

        def restrict(self, source: Category, target: Category) -> Functor:
            ...

        def op(self) -> Functor:
            ...

        def Fiber(self, member_object: CategoryOfCategories.ElementType) -> Category:
            ...

        def retain_terminal_comparison(self, comparison: MorphismCategory.ObjectType) -> None:
            ...

        def terminal_comparison(self) -> MorphismCategory.ObjectType:
            ...

        def after_terminal_comparison(self, image: MorphismCategory.ObjectType, defining: MorphismCategory.ObjectType) -> MorphismCategory.ObjectType:
            ...

        def retain_cartesian_lifts(self, rule: LiftRule) -> None:
            ...

        def retain_cocartesian_lifts(self, rule: LiftRule) -> None:
            ...

        def cartesian_lift(self, morphism: MorphismCategory.ObjectType, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            ...

        def cocartesian_lift(self, morphism: MorphismCategory.ObjectType, member_object: CategoryOfCategories.ElementType) -> MorphismCategory.ObjectType:
            ...

    def __init__(self) -> None:
        ...

    def declare(self, name: str) -> Category:
        ...

    def declare_family(self, name: str, domain: Category) -> CategoryFamily:
        ...

    def declarations(self) -> dict[str, Category | CategoryFamily]:
        ...

    def open_declaration(self, declared: Category | CategoryFamily) -> str | None:
        ...

    def implementation(self, name: str) -> type[Category] | None:
        ...

    def implement(self, implementation: type[Category]) -> None:
        ...

    def morphism_category_type(self) -> type[FunctorsCategory]:
        ...

    def construct_morphism(self, domain: Category, codomain: Category, on_object: OnObject, on_morphism: OnMorphism) -> Functor:
        ...

    def construct_identity(self, category: Category) -> Functor:
        ...

    def composite(self, second: Functor, first: Functor) -> Functor:
        ...

    def construct_two_morphism(self, source: CategoryOfCategories.ElementType, target: CategoryOfCategories.ElementType, assignment: Assignment, source_functor: Functor | None=None, target_functor: Functor | None=None) -> NaturalTransformation:
        ...

    def identity_two_morphism(self, member_object: CategoryOfCategories.ElementType) -> NaturalTransformation:
        ...

    def compose_two_morphisms(self, second: NaturalTransformation, first: NaturalTransformation) -> NaturalTransformation:
        ...

    def whisker_left(self, functor: Functor, transformation: NaturalTransformation) -> NaturalTransformation:
        ...

    def whisker_right(self, transformation: NaturalTransformation, functor: Functor) -> NaturalTransformation:
        ...

    def horizontal_composite(self, second: NaturalTransformation, first: NaturalTransformation) -> NaturalTransformation:
        ...

    def limit_construction(self, shape: Category) -> Callable[[Functor], CategoryOfCategories.ElementType]:
        ...

    def exponential(self, exponent: Category, base: Category) -> Category:
        ...

    def Comma(self, first: Functor, second: Functor) -> Category:
        ...

    def postcompose(self, functor: Functor, diagram: CategoryOfCategories.ElementType) -> CategoryOfCategories.ElementType:
        ...

    def exponential_on_morphism(self, exponent: Category, functor: Functor) -> Functor:
        ...

    def __call__(self, labels: tuple[Hashable, ...], generators: tuple[tuple[str, Hashable, Hashable], ...], relations: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]) -> FinitePresentedCategory:
        ...

    def Initial(self) -> FinitePresentedCategory:
        ...

    def Terminal(self) -> FinitePresentedCategory:
        ...

    def Point(self, member: CategoryOfCategories.ElementType) -> PointCategory:
        ...

    def Simplex(self, dimension: int | Integer) -> FinitePresentedCategory:
        ...

    def Boundary(self, dimension: int | Integer) -> FinitePresentedCategory:
        ...

    def Horn(self, dimension: int, omitted_face: int) -> FinitePresentedCategory:
        ...

    def WalkingIsomorphism(self) -> FinitePresentedCategory:
        ...

    def WalkingSpan(self) -> FinitePresentedCategory:
        ...

    def WalkingCospan(self) -> FinitePresentedCategory:
        ...

    def WalkingParallelPair(self) -> FinitePresentedCategory:
        ...

    def element_from_defining_morphism(self, defining_functor: Functor) -> CategoryOfCategories.ElementType:
        ...

def Cat() -> CategoryOfCategories:
    ...
