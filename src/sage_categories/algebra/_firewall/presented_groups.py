"""Private Sage/GAP execution boundary for finitely presented groups."""

from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass

from sage.groups.free_group import FreeGroup
from sage.structure.element import Element

type GroupWord = tuple[int, ...]


@dataclass(slots=True)
class _NativePresentation:
    free: object
    relations: object
    quotient: object
    relation_map: object
    trivial_relation_map: object
    quotient_map: object


_presentations: dict[object, _NativePresentation] = {}


def prepare(owner: object, names: tuple[str, ...], relation_words: tuple[GroupWord, ...]) -> None:
    free = FreeGroup(names)
    native_relations = tuple(free(tuple(int(letter) for letter in word)) for word in relation_words)
    quotient = free / native_relations
    relation_free = FreeGroup(tuple(f"r{index}" for index in range(len(native_relations))))
    _presentations[owner] = _NativePresentation(
        free,
        relation_free,
        quotient,
        relation_free.hom(native_relations, free),
        relation_free.hom([free.one() for _ in native_relations], free),
        free.hom(tuple(quotient.gens()), quotient),
    )


def _engine(owner: object, role: str):
    record = _presentations[owner]
    match role:
        case "free":
            return record.free
        case "relations":
            return record.relations
        case "quotient":
            return record.quotient
        case _:
            raise AssertionError(f"unknown presented-group role {role!r}")


def is_member(owner: object, role: str, value: object) -> bool:
    return isinstance(value, Element) and value.parent() is _engine(owner, role)


def multiply(left: Hashable, right: Hashable) -> Hashable:
    return left * right


def one(owner: object, role: str) -> Hashable:
    return _engine(owner, role).one()


def inverse_product(first: Hashable, second: Hashable) -> tuple[Hashable, Hashable]:
    return first, first ** -1 * second


def native_map(owner: object, role: str):
    record = _presentations[owner]
    match role:
        case "relations":
            return record.relation_map
        case "trivial-relations":
            return record.trivial_relation_map
        case "quotient":
            return record.quotient_map
        case _:
            raise AssertionError(f"unknown presented-group map {role!r}")


def apply_map(mapping: object, value: Hashable) -> Hashable:
    return mapping(value)


def generators(owner: object, role: str) -> tuple[Hashable, ...]:
    return tuple(_engine(owner, role).gens())


def evaluate_word(owner: object, role: str, word: GroupWord) -> Hashable:
    return _engine(owner, role)(tuple(int(letter) for letter in word))


def factor_map(owner: object, images: tuple[Hashable, ...]):
    if not images or not isinstance(images[0], Element):
        raise ValueError("presentation factorization requires a native Sage/GAP target group")
    target_engine = images[0].parent()
    if any(not isinstance(image, Element) or image.parent() is not target_engine for image in images):
        raise ValueError("presentation generator images must share one native target group")
    return _presentations[owner].quotient.hom(images, target_engine)


def representation(owner: object) -> str:
    return repr(_presentations[owner].quotient)
