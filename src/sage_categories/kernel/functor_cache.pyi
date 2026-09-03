from collections.abc import Callable as Callable
from sage_categories.kernel.roles import MorphismOfCategory as MorphismOfCategory, ObjectOfCategory as ObjectOfCategory
from sage_categories.kernel.sage_runtime import MonoDict as MonoDict, TripleDict as TripleDict

class FunctorImageCache:

    def __init__(self) -> None:
        ...

    def object_image(self, source: ObjectOfCategory, construct: Callable[[ObjectOfCategory], ObjectOfCategory]) -> ObjectOfCategory:
        ...

    def morphism_image(self, source: MorphismOfCategory, on_object: Callable[[ObjectOfCategory], ObjectOfCategory], construct: Callable[[MorphismOfCategory], MorphismOfCategory]) -> MorphismOfCategory:
        ...
