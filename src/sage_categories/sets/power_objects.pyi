from sage_categories.cat.category import Category
from sage_categories.cat.properties import PropertySubcategory
from sage_categories.sets.category import SetMap
from sage_categories.sets.category import SetElement
from sage_categories.sets.maps import Rule
from sage_categories.sets.objects import MembershipRule
from sage_categories.sets.category import SetObject
__all__ = ['PowerObjectsCategory']

class PowerObject:

    def base_set(self) -> SetObject:
        ...

    def from_predicate(self, predicate: MembershipRule) -> SetObject:
        ...

    def from_characteristic_morphism(self, characteristic: SetMap) -> SetObject:
        ...

    def subset_named_by(self, point: SetElement) -> SetObject:
        ...

    def top(self) -> SetObject:
        ...

    def bottom(self) -> SetObject:
        ...

    def inverse_image_morphism(self, set_map: SetMap) -> SetMap:
        ...

    def direct_image_morphism(self, set_map: SetMap) -> SetMap:
        ...

class PowerObjectsCategory(PropertySubcategory[[Rule], []]):
    ObjectType = PowerObject

    class ElementType:
        ...

    class MorphismType:
        ...

    def __init__(self, ambient: Category[[Rule], []]) -> None:
        ...

    def __call__(self, base_set: SetObject) -> SetObject:
        ...

    def subset_of_characteristic_morphism(self, power: SetObject, characteristic: SetMap) -> SetObject:
        ...

    def extreme_subset(self, power: SetObject, whole: bool) -> SetObject:
        ...

    def inverse_image_morphism(self, power: SetObject, set_map: SetMap) -> SetMap:
        ...

    def direct_image_morphism(self, power: SetObject, set_map: SetMap) -> SetMap:
        ...
