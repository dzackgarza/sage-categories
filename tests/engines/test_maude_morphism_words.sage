"""Maude owns generic formal morphism reduction and equality."""

from sage_categories.all import Category, Mor, ask


class FormalCategory(Category):
    class ObjectType:
        def __init__(self, label):
            self.label = label

    class ElementType:
        pass

    class MorphismType:
        pass

    def __init__(self):
        self._named_objects = {}
        super().__init__()

    def __call__(self, label):
        if label not in self._named_objects:
            self._named_objects[label] = self.ObjectType(label)
        return self._named_objects[label]


def test_maude_reduces_generic_morphism_terms() -> None:
    category = FormalCategory()
    a, b, c, d = (category(label) for label in "abcd")
    f = Mor(category)(a, b)()
    g = Mor(category)(b, c)()
    h = Mor(category)(c, d)()

    left = h * (g * f)
    right = (h * g) * f
    assert left.word() == (f, g, h)
    assert right.word() == (f, g, h)
    assert ask(left == right) is True

    identity = Mor(category)(a, a).one()
    formal_with_identity = category.composite(f, identity)
    assert formal_with_identity.word() == (f,)

    inverse = Mor(category)(b, a)()
    category.retain_inverses(f, inverse)
    cancelled = inverse * f
    assert cancelled.word() == ()

    k = Mor(category)(a, d)()
    assert (k * cancelled).word() == (k,)

    unrelated_reverse = Mor(category)(b, a)()
    assert category.composite(unrelated_reverse, f).word() == (f, unrelated_reverse)


test_maude_reduces_generic_morphism_terms()
