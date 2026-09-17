from collections.abc import Sequence
from sage.structure.sage_object import SageObject
from sage_categories.cat.calculus import binary_product_data as binary_product_data
from sage_categories.cat.monoidal import Cartesian as Cartesian
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.structured_objects import Groups as Groups, Magmas as Magmas, Monoids as Monoids, PointedMagmas as PointedMagmas
from sage_categories.kernel.refinement import refine as refine
from sage_categories.sets import Sets as Sets
type GroupWord = tuple[int, ...]

class GroupPresentation(SageObject):

    def __init__(self, generator_names: Sequence[str], relations: Sequence[GroupWord]) -> None:
        ...

    def generator_names(self) -> tuple[str, ...]:
        ...

    def relation_words(self) -> tuple[GroupWord, ...]:
        ...

    def free_group(self):
        ...

    def relation_group(self):
        ...

    def group(self):
        ...

    def free_generators(self):
        ...

    def generators(self):
        ...

    def relation_arrow(self):
        ...

    def trivial_relation_arrow(self):
        ...

    def quotient_morphism(self):
        ...

    def relation_images(self):
        ...

    def evaluate_word(self, word: GroupWord):
        ...

    def factor(self, target, generator_images):
        ...

def presented_group(generator_names: Sequence[str], relations: Sequence[GroupWord]=()) -> GroupPresentation:
    ...
