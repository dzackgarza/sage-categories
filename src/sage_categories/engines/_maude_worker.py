"""Isolated Maude worker for the Sage Categories runtime.

The embedded Sage process already loads native libraries with lexer/signal globals that
conflict with the Python Maude extension.  This worker keeps Maude in a clean Python
process and accepts only JSON conversion data; all rewriting remains native Maude work.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import maude

_MODULE_SOURCE = r"""
fmod SAGE-CATEGORIES-MORPHISM-WORD is
  sorts Tok Obj Morph .
  op tz : -> Tok [ctor] .
  op ts : Tok -> Tok [ctor] .
  op oz : -> Obj [ctor] .
  op os : Obj -> Obj [ctor] .
  op id : Obj -> Morph [ctor] .
  op a : Tok Tok Obj Obj -> Morph [ctor] .
  op src : Morph -> Obj .
  op tgt : Morph -> Obj .
  op _then_ : Morph Morph -> Morph [assoc] .

  vars N M : Tok .
  vars X Y : Obj .
  vars F G : Morph .

  eq src(id(X)) = X .
  eq tgt(id(X)) = X .
  eq src(a(N, M, X, Y)) = X .
  eq tgt(a(N, M, X, Y)) = Y .
  eq src(F then G) = src(F) .
  eq tgt(F then G) = tgt(G) .

  ceq id(X) then F = F if src(F) = X .
  ceq F then id(X) = F if tgt(F) = X .
  eq a(N, M, X, Y) then a(M, N, Y, X) = id(X) .
endfm
"""

assert maude.init(), "Maude failed to initialize"
assert maude.input(_MODULE_SOURCE), "Maude rejected the morphism-word theory"
_module = maude.getModule("SAGE-CATEGORIES-MORPHISM-WORD")
assert _module is not None
_symbols = {str(symbol): symbol for symbol in _module.getSymbols()}


def _successor(zero: Any, successor: Any, index: int) -> Any:
    term = zero.makeTerm([])
    for _ in range(index):
        term = successor.makeTerm([term])
    return term


def _token(index: int) -> Any:
    return _successor(_symbols["tz"], _symbols["ts"], index)


def _object(index: int) -> Any:
    return _successor(_symbols["oz"], _symbols["os"], index)


def _term(expression: list[Any]) -> Any:
    match expression:
        case ["id", int(index)]:
            return _symbols["id"].makeTerm([_object(index)])
        case ["a", int(token), int(inverse), int(source), int(target)]:
            return _symbols["a"].makeTerm(
                [_token(token), _token(inverse), _object(source), _object(target)]
            )
        case ["then", first, second]:
            return _symbols["_then_"].makeTerm([_term(first), _term(second)])
    raise ValueError(f"invalid morphism expression {expression!r}")


def _decode_token(term: Any) -> int:
    match str(term.symbol()):
        case "tz":
            return 0
        case "ts":
            arguments = tuple(term.arguments())
            assert len(arguments) == 1
            return _decode_token(arguments[0]) + 1
    raise ValueError(f"unexpected token term {term!r}")


def _factors(term: Any) -> list[int]:
    match str(term.symbol()):
        case "id":
            return []
        case "a":
            return [_decode_token(next(iter(term.arguments())))]
        case "_then_":
            result: list[int] = []
            for argument in term.arguments():
                result.extend(_factors(argument))
            return result
    raise ValueError(f"unexpected reduced morphism term {term!r}")


def _handle(request: dict[str, Any]) -> object:
    match request["op"]:
        case "reduce":
            term = _term(request["term"])
            term.reduce()
            return _factors(term)
        case "equal":
            left, right = _term(request["left"]), _term(request["right"])
            left.reduce()
            right.reduce()
            return bool(left.equal(right))
    raise ValueError(f"unknown worker operation {request['op']!r}")


for line in sys.stdin:
    try:
        request = json.loads(line)
        response = {"ok": True, "result": _handle(request)}
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        response = {"ok": False, "error": f"{type(error).__name__}: {error}"}
    sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
    sys.stdout.flush()
