"""Fail a D132 rule whose file globs read nothing (D174, POL-DOC-028).

Gate protocol item 1 reads the owned rules "green over `src` and `tests/kernel`" at the
revision under gate. A rule whose globs match no file is green because it read nothing,
which is not a measurement. D137 deleted five leaf packages and left nine rules globbing
them, so R1's kernel capabilities were measured over `tests/kernel` alone while the card
claimed both roots. This runs before the scan so a dead glob is a hard stop, not a
footnote in a gate record.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

RULES = Path(".ast-grep/architecture")

dead: list[str] = []
for rule_file in sorted(RULES.glob("*.yml")):
    rule = yaml.safe_load(rule_file.read_text())
    for glob in rule.get("files", []):
        if not any(Path().glob(glob)):
            dead.append(f"{rule['id']}: no file matches '{glob}'")

for line in dead:
    print(f"rule-coverage: {line}")
if dead:
    print(f"rule-coverage: {len(dead)} dead glob(s); a rule that reads nothing is not green")
    sys.exit(1)
print(f"rule-coverage: every glob of {len(list(RULES.glob('*.yml')))} rules reads at least one file")
