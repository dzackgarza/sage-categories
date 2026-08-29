# sage-categories

`sage-categories` is a package-owned categorical framework for Sage-based mathematics.
It uses explicit categories, functors, and universal constructions as its reuse model.
Sage and other computation systems remain private engines.

The public API is not stable. The current work completes the foundation before any production leaf.

## Public import

```python
from sage_categories.all import *
```

This import selects the package-owned mathematical universe.
Public operations on owned inputs return owned mathematical values.

## Documentation map

| Subject | Owner |
| --- | --- |
| Mathematical decisions and supersession | [`specs/decisions.md`](specs/decisions.md) |
| `Cat`, `Mor`, `Fun`, functor actions, and selected structure functors | [`specs/functor.md`](specs/functor.md) |
| Private Sage compiler and runtime | [`specs/resolution.md`](specs/resolution.md) |
| Leaf and computation-engine boundary | [`specs/leaves.md`](specs/leaves.md) |
| Property categories, inverse images, and refinement | [`specs/property-refinement.md`](specs/property-refinement.md) |
| Propositions, typed queries, and `ask()` | [`specs/undecidable-properties.md`](specs/undecidable-properties.md) |
| Compact review policies | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Agent workflow and current scope | [`AGENTS.md`](AGENTS.md) |

Category specifications under [`specs/`](specs/) state their local mathematics and link to these owners.
