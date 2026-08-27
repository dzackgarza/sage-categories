"""Minimal leaf for the property category ``Sets().Finite()``.

See ``specs/functor.md`` for structural-functor declarations.

The leaf constructs the finiteness proposition. A private set backend decides only its
supported semantic cases. The property category binds that backend after its declaration.
The predicate kernel owns ``ask()``, ``assume()``, proposition ``.assume()``, and positive
same-object refinement.
"""

from __future__ import annotations


class SetsCategory(Category):
    class DeclaredObjectType(Implementation):
        def is_finite(self) -> Proposition:
            """Return the finite-set membership proposition."""
            return Sets().Finite().membership_proposition(self)

    class DeclaredElementType(Implementation):
        pass

    class DeclaredMorphismType(Implementation):
        pass

    class Finite(Category):
        """The full property subcategory of finite sets."""

        def structure_functors(self) -> tuple[Cat().MorphismType, ...]:
            """Select the inclusion that supplies the inherited set implementation.

            This tuple is not a list of all functors from finite sets.
            The full-subcategory construction supplies its maps and constructs it in
            the fixed-endpoint functor category. Other functors remain in ``Fun``.
            """
            # Same-object refinement preserves the initialized ambient role data.
            return (Fun(self, Sets()).FullyFaithful().inclusion(),)

        def membership_proposition(
            self,
            X: SetObject,
        ) -> Proposition:
            """Return the proposition that ``X`` has finite cardinality."""
            return self.applied_predicate(
                X,
                definition=X.cardinality() < ALEPH_ZERO,
            )

        class DeclaredObjectType(Implementation):
            """Implement only the operations introduced by known finiteness.

            Same-object refinement keeps the set state already initialized by the
            compiled ambient role.
            """

            def cardinality_parity(self) -> Proposition:
                """Return the proposition that the cardinality is even."""
                return self.cardinality() % 2 == 0

        class DeclaredElementType(Implementation):
            pass

        class DeclaredMorphismType(Implementation):
            pass


_SETS = SetsCategory()
SetObject = _SETS.ObjectType
SetElement = _SETS.ElementType
SetMorphism = _SETS.MorphismType
FiniteSet = _SETS.Finite().ObjectType
FiniteSetElement = _SETS.Finite().ElementType
FiniteSetMorphism = _SETS.Finite().MorphismType


def Sets() -> SetsCategory:
    return _SETS


def decide_finiteness(X: SetObject) -> Decision:
    """Return an exact decision for the supported private-backend cases.

    Put this entry point and its engine calls in a private set-computation module in the
    implementation. Replace these pattern names with the owned semantic constructions.
    """
    match X:
        case ExplicitFiniteSet():
            return True
        case ExplicitInfiniteSet():
            return False
        case _:
            return Unknown


Sets().Finite().register_exact_handler(
    SetObject,
    decide_finiteness,
)


# All public routes use the proposition returned by ``X.is_finite()``:
#
# proposition = X.is_finite()
# ask(proposition)       # Decide from placement, assumptions, or exact handlers.
# assume(proposition)    # Assert and refine in the active mathematical context.
# proposition.assume()   # The equivalent proposition-owned assumption spelling.
