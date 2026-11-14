from app.relevance_validator import identify, assess

def test_robotic_layout_query_variants():
    for q in ('concrete layout robot','floor layout marking robot','robotic setting-out'):
        assert identify(q)=='robotic_layout'

def test_tile_is_more_specific():
    assert identify('tile layout robot')=='robotic_tile_layout'

def test_cupix_style_record_not_robot():
    row={'summary':'3D reality capture and spatial site documentation', 'use_cases':['Progress monitoring'], 'technologies':['Computer vision']}
    assert assess(row,'robotic_layout').status=='unknown'

def test_real_robot_evidence():
    row={'summary':'Physical robotic construction layout marking on concrete floors'}
    assert assess(row,'robotic_layout').status=='eligible'

def test_digital_contract_not_twin():
    assert assess({'summary':'Digital contract management platform'},'fm_digital_twin').status=='unknown'

def test_fm_twin_evidence():
    assert assess({'summary':'Operational digital twin for facility management'},'fm_digital_twin').status=='eligible'

def test_safety_synonym():
    assert identify('Construction Site Safety Monitoring')=='construction_safety_monitoring'
    assert assess({'use_cases':['PPE detection']},'construction_safety_monitoring').status=='eligible'

def test_generic_browse_not_gated():
    assert identify('Which vendors have PSG pre-approved solutions?') is None
    assert identify('List all solutions') is None
