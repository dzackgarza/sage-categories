# sage-categories

`sage-categories` is a package-owned categorical framework for Sage-based mathematics.
It uses explicit categories, functors, and universal constructions as its reuse model.
Sage and other computation systems remain private engines.

The public API is not stable.
[System architecture](specs/system.md) describes the mathematical foundation and production order.

## Public import

```python
from sage_categories.all import *
```

This import selects the package-owned mathematical universe.
Public operations return owned mathematical values or authorized SymPy proposition expressions.

## Consumer revisions

External Git consumers must pin a full commit SHA that is already reachable from this repository's published `origin` refs.
A commit that exists only in a local checkout is not a published artifact, even when another local project can see it.
There is no automatic publication cadence: pushing or merging a branch is an explicit repository-owner action after the applicable push gate, and an agent work unit does not publish history merely to make a downstream pin resolve.

Before changing a consumer pin, verify that the selected SHA is present on the remote.
If required work exists only locally, record the consumer as blocked on repository owner `dzackgarza` choosing either to publish the relevant branch/history or to select another already-published revision.
Do not replace the declared Git dependency with a filesystem path to bypass that publication decision.

## Documentation map

| Subject | Owner |
| --- | --- |
| System layers and dependency order | [`specs/system.md`](specs/system.md) |
| Mathematical decisions and supersession | [`specs/decisions.md`](specs/decisions.md) |
| `Cat`, `Mor`, `Fun`, functor actions, and selected structure functors | [`specs/functor.md`](specs/functor.md) |
| Private Sage compiler and runtime | [`specs/resolution.md`](specs/resolution.md) |
| Leaf and computation-engine boundary | [`specs/leaves.md`](specs/leaves.md) |
| Leaf consumer contracts and public-name distinctions | [`specs/leaf-scaffolding.md`](specs/leaf-scaffolding.md) |
| Bimodule actions and relative tensor products | [`specs/bimodules.md`](specs/bimodules.md) |
| Schemes, affine presentations, and gluing | [`specs/schemes.md`](specs/schemes.md) |
| Property categories, inverse images, and refinement | [`specs/property-refinement.md`](specs/property-refinement.md) |
| Propositions, typed queries, and `ask()` | [`specs/undecidable-properties.md`](specs/undecidable-properties.md) |
| Compact review policies | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Governing remediation plan | [Agent-memory retrieval and historical locators](docs/remediation-handoff.md) |
| Agent workflow | [`AGENTS.md`](AGENTS.md) |

Category specifications under [`specs/`](specs/) state their local mathematics and link to these owners.
