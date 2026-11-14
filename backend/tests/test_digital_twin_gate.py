from fastapi.testclient import TestClient
from app.excel_api import app
from app.capability_gate import eligible, specific_intent

client=TestClient(app)

def test_specific_intent():
    assert specific_intent('FM Digital twin tools')=='fm_digital_twin'
    assert specific_intent('building digital twins')=='digital_twin'
    assert specific_intent('digital contract management') is None

def test_generic_digital_is_not_twin():
    row={'summary':'digital contract management','source_use_cases':'digital contract management','source_technology':'collaborative contracting','use_cases':[],'technologies':[]}
    assert not eligible(row,'digital_twin')

def test_fm_requires_both_capabilities():
    row={'summary':'digital twin for construction progress','source_use_cases':'','source_technology':'','use_cases':[],'technologies':[]}
    assert eligible(row,'digital_twin')
    assert not eligible(row,'fm_digital_twin')
    row['summary']='Digital twin for facility management and building operations'
    assert eligible(row,'fm_digital_twin')

def test_live_search_excludes_unrelated_contract_management():
    result=client.post('/api/v1/search',json={'message':'FM Digital twin tools'}).json()
    assert 'matches' in result
    assert all('Digital Beehive' not in m['solution'] for m in result['matches'])

def test_psg_search_unchanged():
    result=client.post('/api/v1/search',json={'message':'Which vendors have PSG pre-approved solutions?'}).json()
    assert result['total_solutions']==23
