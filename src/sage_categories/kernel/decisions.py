"""What ``ask`` returns.

Sage owns the unresolved truth value: ``sage.misc.unknown.Unknown`` is the only
``Unknown`` in this package (POL-ASSUME-004).  A ``Decision`` is ``True``, ``False``,
or that singleton, and it exists because ``ask`` has to terminate in a value a caller
can branch on.  It carries no logic of its own: propositions compose under SymPy's
boolean algebra through ``kernel/predicates.py`` and ``ask`` decides the result once.

``UnknownClass.__bool__`` raises, so no decision is ever used in a Boolean context by
accident; every consumer compares with ``is``.
"""

from sage.misc.unknown import Unknown, UnknownClass

type Decision = bool | UnknownClass

__all__ = ["Decision", "Unknown", "UnknownClass"]
