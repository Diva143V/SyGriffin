from griffin.bio.scoring import binding_score_from_ic50, composite_score


def test_binding_score_normalization():
    assert binding_score_from_ic50(40) == 1.0
    assert binding_score_from_ic50(120) == 0.85
    assert binding_score_from_ic50(400) == 0.65
    assert binding_score_from_ic50(800) == 0.35
    assert binding_score_from_ic50(1200) == 0.10


def test_weak_binder_composite_cap():
    assert composite_score(0.10, 1.0, 1.0, 1.0) <= 0.50
