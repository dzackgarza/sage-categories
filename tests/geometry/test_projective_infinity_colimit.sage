"""The full projective-space sequence retains its CW topological colimit."""

from sage_categories.all import ask
from sage_categories.geometry import complex_projective_point, projective_infinity


def test_projective_infinity_retains_arbitrary_stages_and_mediator() -> None:
    presentation = projective_infinity()
    low = presentation.finite_skeleton(2)
    high = presentation.finite_skeleton(37)

    assert low.stage == 2 and low.cells() == (0, 2, 4)
    assert high.stage == 37 and high.cells()[-1] == 74
    assert low.space is not presentation.space
    assert high.space is not presentation.space

    low_inclusion = presentation.structure_map(2)
    high_inclusion = presentation.structure_map(37)
    assert low_inclusion.domain() is low.space and low_inclusion.codomain() is presentation.space
    assert high_inclusion.domain() is high.space and high_inclusion.codomain() is presentation.space

    conjugation = presentation.complex_conjugation()
    assert conjugation.domain() is presentation.space and conjugation.codomain() is presentation.space

    stage_point = low.space.carrier().point(complex_projective_point(1, 1j, 2))
    conjugated_stage = low.complex_conjugation()(stage_point)
    assert conjugated_stage.datum() != stage_point.datum()
    assert ask(
        conjugation(low_inclusion(stage_point))
        == low_inclusion(conjugated_stage)
    ) is True

    later_point = high.space.carrier().point(
        complex_projective_point(1, 1j, *(0 for _ in range(36)))
    )
    assert ask(
        conjugation(high_inclusion(later_point))
        == high_inclusion(high.complex_conjugation()(later_point))
    ) is True


test_projective_infinity_retains_arbitrary_stages_and_mediator()
