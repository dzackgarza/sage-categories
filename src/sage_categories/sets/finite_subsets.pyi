from sage_categories.cat.category import Category
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.sets.cardinals import CardinalObject
from sage_categories.sets.category import SetElement
from sage_categories.sets.maps import Rule
from sage_categories.sets.category import SetObject
__all__ = ['FiniteSubsetsObject', 'SizedSubsetsObject', 'SizedSubsetsCategory', 'FiniteSubsetsCategory', 'FinitelySupportedFunctionsObject', 'FinitelySupportedFunctionsCategory']

class FiniteSubsetsObject:

    def base_set(self) -> SetObject:
        ...

    def subset_at(self, point: SetElement) -> SetObject:
        ...

    def point_of(self, subset: SetObject) -> SetElement:
        ...

    def index(self, subset: SetObject) -> CardinalObject:
        ...

    def __getitem__(self, position: CardinalObject | int) -> SetObject:
        ...

class SizedSubsetsObject:

    def subset_cardinality(self) -> CardinalObject:
        ...

class SizedSubsetsCategory(PropertySubcategory[[Rule], []]):
    ObjectType = SizedSubsetsObject

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: Category[[Rule], []], size: int) -> None:
        ...

    def size(self) -> CardinalObject:
        ...

    def __call__(self, base_set: SetObject) -> SetObject:
        ...

class FiniteSubsetsCategory(PropertySubcategory[[Rule], []]):
    ObjectType = FiniteSubsetsObject

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        ...

    def __call__(self, base_set: SetObject) -> SetObject:
        ...

    def of_size(self, size: int, base_set: SetObject) -> SetObject:
        ...

    def retained_size(self, subsets: SetObject) -> CardinalObject:
        ...

    def subset_at(self, subsets: SetObject, point: SetElement) -> SetObject:
        ...

    def point_of(self, subsets: SetObject, subset: SetObject) -> SetElement:
        ...

    def index(self, subsets: SetObject, subset: SetObject) -> CardinalObject:
        ...

    def subset_at_position(self, subsets: SetObject, position: CardinalObject | int) -> SetObject:
        ...

class FinitelySupportedFunctionsObject:

    def index_set(self) -> SetObject:
        ...

    def value_set(self) -> SetObject:
        ...

    def basepoint(self) -> SetElement:
        ...

class FinitelySupportedFunctionsCategory(PropertySubcategory[[Rule], []]):
    ObjectType = FinitelySupportedFunctionsObject

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        ...

    def __call__(self, index_set: SetObject, basepoint: SetElement) -> SetObject:
        ...

    def retained_index_set(self, functions: SetObject) -> SetObject:
        ...
