from app.universal_evidence import capability_for_query, eligible_evidence, unrecognised_query_eligible
from app.excel_api import render, Session
from app.interpreter import fallback

def test_thermal_insulation_rejects_unrelated_products():
    for name in ('Millipede','Giken','Evercam'):
        row={'solution':name,'summary':'construction monitoring and energy performance', 'source_use_cases':'digital management','technologies':['computer vision']}
        assert not eligible_evidence(row,'thermal_insulation')

def test_thermal_insulation_accepts_explicit_solution_evidence():
    assert eligible_evidence({'summary':'Aerogel insulation coating with reduced thermal conductivity'},'thermal_insulation')
    assert not eligible_evidence({'summary':'Does not provide thermal insulation; offers thermal imaging only'},'thermal_insulation')

def test_unrecognised_query_not_generic_keyword_overlap():
    row={'summary':'Digital energy monitoring for construction projects'}
    assert not unrecognised_query_eligible(row,'thermal performance insulation materials')
    assert unrecognised_query_eligible({'summary':'Automated facade crack detection and reporting'},'facade crack detection')

def test_integration_no_false_thermal_results():
    result=render(Session(),fallback('thermal insulation solutions'),1,10)
    assert result.total_solutions==0

def test_attribute_search_preserved():
    result=render(Session(),fallback('which vendors have PSG pre-approved solutions'),1,100)
    assert result.total_solutions==23

def test_safety_search_preserved():
    result=render(Session(),fallback('safety monitoring'),1,100)
    assert result.total_solutions==5

def test_robotic_layout_preserved():
    result=render(Session(),fallback('concrete layout robot'),1,100)
    assert result.total_solutions==0
