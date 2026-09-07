# Static class projection continuation

Continuation of [the remediation cutoff](remediation-handoff.md), owned by
[#45](https://github.com/dzackgarza/sage-categories/issues/45) and
`PLAN-mypy-static-projection-remediation`.

## Exact pending claim

Source checkpoint `856a3dc` contains an unfinished generator patch and the public
consumer [`category_morphism_parameters.py`](../tests/static/category_morphism_parameters.py).
The patch explicitly binds free ParamSpecs in class assignment aliases. Fresh
package projection still fails. Generated `.pyi` changes remain unpublished.

Preserve every `assert_type` in the consumer. Its required inferred results are:

| Input expression | Exact result |
| --- | --- |
| `Mor(C)` for `C: Category[[str], [int]]` | `MorphismCategory[[str], [int]]` |
| `Mor(C)(A, B)` | `FixedEndpointCategory[[str], [int]]` |
| `Mor(C)(A, B)("arrow")` | `MorphismCategory.ObjectType` |
| `Mor(0, C)` | `Category[[str], [int]]` |
| `Mor(1, C)` | `MorphismCategory[[str], [int]]` |
| `Mor(2, C)` | `MorphismCategory[[int], []]` |
| `Mor(PointCategory(member))` | `MorphismCategory[[], []]` |
| `Mor(DeclaredCategory("C"))` | `MorphismCategory[[], []]` |
| `Mor(C)` for `C: CategoryOfCategories.ObjectType[[str], [int]]` | `MorphismCategory[[str], [int]]` |

These are inferred results, rather than annotations imposed on output variables.
This specimen addresses one slice of #45. Exact functor endpoints, same-value
refinement, parameter-dependent bases, and typed dependencies retain their
separate obligations in the owning plan. #44 also needs static separation of the
acting category M and acted-on category C.

## Current source and observed failure

Owner: `src/sage_categories/kernel/stub_generator.py`.

`_generate_stubs` reads source and generated-stub ASTs. The new
`_project_paramspec_class_aliases` finds source classes whose parameters are
ParamSpecs. It changes assignment aliases to explicit subscriptions with free
ParamSpecs, including the nested `CategoryOfCategories.ObjectType` alias.
`_project_provider_bases` still projects retained compiler provider relations.

The original bare class alias loses the free ParamSpecs in mypy's alias analysis.
`Category[[str], [int]]` then produces an invalid bracketed type expression, and
the fixed-hom and nullary results lose their required parameters. Explicit free
ParamSpecs address that isolated alias case.

The fresh full package exposes a different static dependency:

```python
class CategoryDeclaration[**P, **Q](CategoryOfCategories.ElementType):
    ...


class CategoryOfCategories(CategoryDeclaration[[], []]):
    class ElementType:
        ...
```

The runtime relation need not contain an inheritance cycle. The nested static
declaration makes a base depend on a member of its subclass's unresolved
namespace. The full configured consumer reports missing category symbols and
cyclic definitions, then an internal mypy failure:

```text
AssertionError: Must not defer during final iteration
```

The first internal error in the inspected projection was at `cat/functors.pyi:13`.
The final traceback reached `mypy/semanal.py:7306`. Treat these locations as
locators for the recorded runtime version, not stable line contracts.

## Next repair: retain class identity in the static representation

The recommended representation has standalone mypy evidence. Its integration in
the real generator and configured plugin remains unimplemented.

1. Hoist the actual generated declaration body for the nested element class to
   a private top-level class. Preserve its methods and exact bases.
2. Point base lists directly to that declaration where nesting creates the
   lexical cycle.
3. Retain the public nested name by an import re-export of the same class.
4. Project source class aliases, including `Category` and
   `CategoryOfCategories.ObjectType`, as class import re-exports.
5. Derive these relations from source declarations and the retained compiler
   relation. Regenerate a complete fresh projection and run the original consumer.

An import re-export keeps the underlying class `TypeInfo`. An assignment alias
can instead create a `TypeAlias`. The configured plugin's `_lookup_typeinfo`
currently requires `TypeInfo`, so this distinction is part of the dependency
interlock. Inspect any remaining real plugin failure before changing that
interface.

The following standalone representation retains both generic aliases. In a file
named `sage_category_import_alias.py`:

```python
from typing import assert_type


class Declaration[**P, **Q]:
    def construct(self, *args: P.args, **kwargs: P.kwargs) -> int:
        return 1


from sage_category_import_alias import Declaration as Category


class Nullary(Category[[], []]):
    pass


class Owner:
    from sage_category_import_alias import Declaration as ObjectType


def consumer(category: Category[[str], []]) -> None:
    assert_type(category.construct("word"), int)


def role_consumer(category: Owner.ObjectType[[str], [int]]) -> None:
    assert_type(category.construct("word"), int)
```

The nested declaration can retain its public identity as follows. In a file named
`sage_category_hoisted_projection.py`:

```python
class _ElementType:
    pass


class CategoryDeclaration[**P, **Q](_ElementType):
    pass


class CategoryOfCategories(CategoryDeclaration[[], []]):
    from sage_category_hoisted_projection import _ElementType as ElementType


def point(category: CategoryDeclaration[[], []]) -> CategoryOfCategories.ElementType:
    return category
```

These dependency experiments establish admissible representations in mypy 2.0.0
on Python 3.14. They do not establish the repository's provider graph or full
static contract. The cutoff files are also retained locally at `/tmp/` under
those two basenames.

## Reproduce the complete projection

Use the research Sage environment. Its interpreter is
`/home/dzack/gitclones/sage-dev-allopts/.venv/bin/python`. The configured mypy file
is `/home/dzack/ai-review-ci/tool-configs/mypy-sage.ini`, with plugin
`sage_mypy_category_plugin.plugin`.

The installed plugin source is under that environment's
`lib/python3.14/site-packages/sage_mypy_category_plugin/plugin.py`.
Read it as dependency evidence; changes belong to its owning project. Its
`_lookup_typeinfo` and provider-MRO hook are the immediate consumers of the
generated class relation.

The cutoff generator exercise used this script:

```python
from pathlib import Path
from shutil import copytree, ignore_patterns
from tempfile import mkdtemp

from sage_categories.kernel.stub_generator import generate_stubs

source = Path("src/sage_categories").resolve()
projection_root = Path(mkdtemp(prefix="sage-category-parameters-"))
projection = projection_root / "sage_categories"
copytree(source, projection, ignore=ignore_patterns("*.pyi", "__pycache__"))
generate_stubs("sage_categories", projection)
print(projection_root, flush=True)
```

The local script is `/tmp/project_category_parameters.py`. Run it using:

```bash
sage -c 'exec(open("/tmp/project_category_parameters.py").read())'
```

Read the printed directory, then use that exact directory as the first MYPYPATH
entry. For the recorded cutoff output, the focused public command is:

```bash
MYPYPATH=/tmp/sage-category-parameters-sbsj4xwk:/home/dzack/ai-review-ci/typings sage -c 'from mypy.api import run; output,error,status=run(["--config-file","/home/dzack/ai-review-ci/tool-configs/mypy-sage.ini","--no-incremental","--follow-imports=silent","tests/static/category_morphism_parameters.py"]); print(output); print(error); raise SystemExit(status)'
```

That temporary output predates the final source checkpoint. Generate fresh output
after the repair. `--follow-imports=silent` limits imported-module diagnostics for
this consumer; it preserves their types and the configured plugin. Aggregate QC
remains with the normal hooks.

## Interfaces to preserve

Inspect generated declarations against their complete source owners before
publishing them. The earlier fresh projection exposed these current interfaces:

- `CategoryDeclaration.point_morphism`, `closed_roots`, and Cat's `Concrete`
  predicate;
- the compiler-derived `CategoryOfCategories.ElementType` provider bases;
- `AxiomLayer.application_axiom` and `install_subclass_applications`;
- `Axiom.inverse_image`, `InverseImageAxiom`, and `ConstructionFamily`;
- `realize_implementation_class` and the declaration parameter of
  `_RuntimeImplementationCategory`;
- module categories, supplied actions, scalar endofunctors, carrier and
  forgetful functors, transport, and restriction.

The full projection also touches algebra, order, sets, universal constructions,
and exports. A generator completion does not establish semantic preservation of
those interfaces. Publish the source-derived result after its owned consumer and
dependency checks; retain the original mathematical declarations and exact types.

The original generic-alias reference is the mypy documentation:
[Generic type aliases](https://mypy.readthedocs.io/en/stable/generics.html#generic-type-aliases).
The installed source analysis and standalone examples above distinguish its
class-identity consequences for this repository.
