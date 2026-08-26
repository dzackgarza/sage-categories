"""Canonical-image tables keyed by identity.

Every canonical cache is a ``sage.structure.coerce_dict`` dictionary: keys are
compared with ``is``, held weakly, and values strongly (D12).  No cache ever calls
``__eq__`` or ``__hash__`` of an owned value.  One table per role; a key is
``(key1, key2, target category)``: objects ``(X, X, D)``, elements
``(parent, element, D)``, morphisms ``(f, f, D)`` (POL-CAT-066).

``MonoDict`` silently fails for keys that do not support weak references
(integers, strings); only owned values are ever used as its keys.
"""

from sage.structure.coerce_dict import MonoDict, TripleDict

from sage_categories.kernel.roles import Role

__all__ = ["MonoDict", "TripleDict", "canonical_images"]

canonical_images: dict[Role, TripleDict] = {role: TripleDict(weak_values=False) for role in Role}
