from collections.abc import Iterable
from sage.combinat.posets.posets import FinitePoset as SagePoset
from sage.rings.integer import Integer
from sage_categories.posets.category import Poset, PosetElement
from sage_categories.sets.elements import Datum
from sage_categories.sets.objects import MembershipRule
__all__ = ['sage_poset', 'datum', 'data', 'element', 'selecting', 'count']

def sage_poset(poset: Poset) -> SagePoset:
    ...

def datum(poset: Poset, member: PosetElement) -> Datum:
    ...

def data(poset: Poset, members: Poset) -> tuple[Datum, ...]:
    ...

def element(poset: Poset, value: Datum) -> PosetElement:
    ...

def selecting(data: Iterable[Datum]) -> MembershipRule:
    ...

def count(value: Integer) -> int:
    ...
