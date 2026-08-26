"""Three-valued decisions.

Sage owns the unresolved truth value: ``sage.misc.unknown.Unknown`` is the only
``Unknown`` in this package (D01, POL-ASSUME-004).  A ``Decision`` is ``True``,
``False``, or that singleton.  ``UnknownClass.__bool__`` raises, so no decision is
ever used in a Boolean context by accident; every consumer compares with ``is``.
"""

from sage.misc.unknown import Unknown, UnknownClass

type Decision = bool | UnknownClass

__all__ = ["Decision", "Unknown", "UnknownClass", "decision_and", "decision_not", "decision_or"]


def decision_and(*decisions: Decision) -> Decision:
    """Kleene conjunction: ``False`` dominates, then ``Unknown``, then ``True``."""
    if any(decision is False for decision in decisions):
        return False
    if any(decision is Unknown for decision in decisions):
        return Unknown
    return True


def decision_or(*decisions: Decision) -> Decision:
    """Kleene disjunction: ``True`` dominates, then ``Unknown``, then ``False``."""
    if any(decision is True for decision in decisions):
        return True
    if any(decision is Unknown for decision in decisions):
        return Unknown
    return False


def decision_not(decision: Decision) -> Decision:
    """Kleene negation; ``Unknown`` is fixed."""
    if decision is Unknown:
        return Unknown
    return not decision
