# Glossary

Every technical term used in permanent documentation has a row here (`POL-MATH-050`).

A row is complete when it carries one of:

- **cited** — an inspected external source with an exact locator: theorem, definition,
  section, page, tag, or stable link;
- **defined** — one plain-English definition, and the file and heading that states it;
- **removed** — the phrase to write instead.

Writing a term with no complete row is the defect. The repair is to complete the row, or
to rewrite the sentence without the term. Do not ask whether a term was invented; look it
up here.

Presence of a term in this repository's source, tests, plans, reports, or earlier policy
rows is not evidence that it has a meaning, and is never the content of a row
(`POL-MATH-051`). When no external source names the thing and no plain definition fits it,
the thing is an implementation artifact: report the missing construction and open no row
(`POL-MATH-052`).

A plain descriptive phrase is not a term and needs no row (`POL-MATH-053`). "The class
compiled for objects of `C`" is admissible as written; "the object role" is a term.

The removed rows keep their words on purpose. They are the check: a removed term must not
appear in permanent documentation, and the row states what replaces it.

## Removed

| Term | Write instead | Reference |
| --- | --- | --- |
| `carrier` | the underlying object, or the underlying set, with the functor that produces it named | `POL-MATH-046` |
| `receiver` | the value the operation applies to | `POL-MATH-047` |
| `role`, for a Python class | the compiled class; or name it, `C.ObjectType` | `POL-MATH-048` |
| `role`, for a mathematical kind | the exact mathematical type | `POL-MATH-048` |
| `canonical image` | the image `F.on_object(x)` under a named functor `F` | `POL-CAT-096` |
| `structural_image` | nothing replaces it; a category has no image operation | `POL-CAT-096` |
| `this_object` | nothing replaces it; it states no proposition | `POL-MATH-047` |
| `DeclaredObjectType`, `DeclaredElementType`, `DeclaredMorphismType` | `ObjectType`, `ElementType`, `MorphismType` | `POL-KERNEL-028` |

One name exists per mathematical kind. A category writes `ObjectType` and the kernel
compiles that same class, as Sage compiles a written `ParentMethods` into a dynamic class
without a second name. The two-name split in source names no mathematical object and has
no external source, so it is an implementation artifact (`POL-MATH-052`); removing it is
kernel work, and the source keeps the names until then (`POL-MATH-049`).

Source occurrences of a removed term stay until the model that produced them is repaired
(`POL-MATH-049`). This section governs permanent documentation.

## Open

These terms are in use and have no complete row. Each is either completed or removed.

| Term | Why it is open |
| --- | --- |
| structural functor | `structure_functors()` selects it, but no source or single definition states what "structural" adds to "functor" |
| leaf category | used throughout as the opposite of kernel; needs one definition or a plainer phrase |
| construction input | described across `POL-KERNEL-029` and `POL-LEAF-047`; needs one definition |
| route | a composite of selected functors; either cite "composite" and use it, or define |
| transport | overlaps transport of structure along an isomorphism, which is not the sense used |
| descendant | a category with a selected functor to another; needs a definition or a plainer phrase |
| stage | appears in `ObjectStageIdentity` and `ArrowStageIdentity` with no stated meaning |
| firewall | metaphor for the implementation class boundary in `POL-LEAF-041` |

## Cited

| Term | Source |
| --- | --- |
| separator | open |
| replete | open |
| generalized element | open |

Each source cell above is open work. Fill it by inspecting the source (`POL-MATH-040`), or
remove the term.
