from sage_categories.cat.adjunctions import Adjunctions as Adjunctions, Equivalences as Equivalences
from sage_categories.cat.category import Category as Category
from sage_categories.cat.cones import cones as Cones, limit_cones as LimitCones
from sage_categories.cat.declarations import MagmaObjects as MagmaObjects, MonoidObjects as MonoidObjects, NN as NN, Posets as Posets, RingObjects as RingObjects, SemiringObjects as SemiringObjects, Sets as Sets, TotallyOrderedSets as TotallyOrderedSets, ZZ as ZZ, omega as omega
from sage_categories.cat.category import Cat as Cat
from sage_categories.cat.functors import Fun as Fun
from sage_categories.cat.morphisms import Mor as Mor
from sage_categories.cat.opposites import Op as Op
from sage_categories.cat.predicates import Decision as Decision, Predicate as Predicate, Unknown as Unknown, UnknownClass as UnknownClass, ask as ask, assume as assume, retract as retract
from sage_categories.cat.shapes import Discrete as Discrete, Thin as Thin
from sage_categories.cat.total_cones import total_cones as TotalCones
__all__ = ['Category', 'NN', 'ZZ', 'MagmaObjects', 'MonoidObjects', 'Posets', 'RingObjects', 'SemiringObjects', 'Sets', 'TotallyOrderedSets', 'omega', 'Cat', 'Fun', 'Mor', 'Adjunctions', 'Equivalences', 'Cones', 'LimitCones', 'Op', 'TotalCones', 'Discrete', 'Thin', 'Decision', 'Unknown', 'UnknownClass', 'Predicate', 'ask', 'assume', 'retract', '__version__', 'version']
__version__: str

def version() -> str:
    ...
