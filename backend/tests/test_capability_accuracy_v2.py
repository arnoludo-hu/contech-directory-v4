from fastapi.testclient import TestClient
from app.excel_api import app
from app.capability_gate import eligible, specific_intent

client = TestClient(app)

def row(text):
    return dict(summary=text, source_use_cases='', source_technology='', source_category='', use_cases=[], technologies=[])

def test_tile_robot_requires_both():
    assert specific_intent('tile layout robot') == 'robotic_tile_layout'
    assert not eligible(row('AI generated office layout'), 'robotic_tile_layout')
    assert not eligible(row('Reality capture progress analytics'), 'robotic_tile_layout')
    assert eligible(row('Robotic tile installation on construction sites'), 'robotic_tile_layout')

def test_digital_twin_distinction():
    assert specific_intent('FM digital twin tools') == 'fm_digital_twin'
    assert not eligible(row('Digital contract management'), 'fm_digital_twin')
    assert not eligible(row('Digital twin for construction'), 'fm_digital_twin')
    assert eligible(row('Digital twin for building operations'), 'fm_digital_twin')

def test_safety_aliases_and_eligibility():
    assert specific_intent('Construction Site Safety Monitoring') == 'construction_safety_monitoring'
    assert specific_intent('PPE detection') == 'construction_safety_monitoring'
    assert eligible(row('Site safety monitoring using cameras'), 'construction_safety_monitoring')
    assert not eligible(row('Contract safety clauses'), 'construction_safety_monitoring')

def test_api_no_unrelated_tile_results():
    result = client.post('/api/v1/search', json={'message':'tile layout robot'})
    assert result.status_code == 200
    names = {m['company'].lower() for m in result.json()['matches']}
    assert not names.intersection({'laiout','podium','cupix'})

def test_structured_queries_unaffected():
    response = client.post('/api/v1/search', json={'message':'Which vendors have PSG pre-approved solutions?'})
    assert response.status_code == 200
    assert response.json()['total_solutions'] == 23
