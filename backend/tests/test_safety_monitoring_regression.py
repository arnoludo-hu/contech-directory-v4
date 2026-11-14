"""Safety monitoring regression checks against the shipped Excel v4 workbook."""
from app.models import SearchRequest
from app.excel_api import search
from app.relevance_validator import assess, identify


def test_source_safety_taxonomy_accepted():
    for category in (
        'Digital Safety Planning and Management',
        'Safety compliance monitoring',
        'Safety management',
        'Safety monitoring',
        'PPE detection',
    ):
        assert assess({'use_cases': [category]}, 'construction_safety_monitoring').status == 'eligible'


def test_generic_video_analytics_not_automatically_safety():
    assert assess({'use_cases': ['Video analytics'], 'summary': 'Site progress tracking'}, 'construction_safety_monitoring').status != 'eligible'


def test_safety_queries_return_matching_solutions():
    for query in ('safety monitoring', 'Construction Site Safety Monitoring'):
        assert identify(query) == 'construction_safety_monitoring'
        result = search(SearchRequest(message=query))
        assert result.total_solutions > 0
        assert all(m.solution_id for m in result.matches)


def test_structured_psg_unaffected():
    result = search(SearchRequest(message='Which vendors have PSG pre-approved solutions?'))
    assert result.total_solutions == 23
