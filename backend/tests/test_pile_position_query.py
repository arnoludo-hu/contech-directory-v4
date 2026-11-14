from app.capability_taxonomy import identify_capability
from app.capability_gate import eligible

def test_pile_query_interpretation():
    assert identify_capability("a AI vision solution that can detect when piles are done at wrong locations") == "pile_position_verification"

def test_generic_progress_not_eligible():
    assert not eligible({"summary":"AI site progress monitoring and image analytics"}, "pile_position_verification")

def test_pile_detection_alone_not_eligible():
    assert not eligible({"summary":"AI detects piles in images"}, "pile_position_verification")

def test_explicit_pile_coordinate_verification_eligible():
    assert eligible({"summary":"Pile survey coordinates and as-built position verification against design coordinates"}, "pile_position_verification")
