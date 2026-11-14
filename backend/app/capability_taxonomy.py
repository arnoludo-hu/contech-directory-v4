"""Query-side capability vocabulary. Does not modify or certify Excel data."""
import re

PATTERNS = (
    ('pile_position_verification', r'(?=.*\b(?:pile|piles|piling|foundation\s+pile)\b)(?=.*\b(?:wrong\s+location|wrong\s+position|misplac(?:ed|ement)|position(?:ing)?|locat(?:ions?|ed)|coordinates?|as[ -]?built|deviation|setting[ -]?out)\b)'),
    ('robotic_tile_layout', r'\b(?:tile\s+(?:layout|laying|setting|installation)\s+robot|robot(?:ic)?\s+tile\s+(?:layout|laying|setting|installation)|tile\s+layout\s+automation)\b'),
    ('fm_digital_twin', r'(?=.*\b(?:digital[\s-]*twins?|operational\s+twins?|asset\s+twins?)\b)(?=.*\b(?:fm|facilit(?:y|ies)\s+management|facility\s+operations|building\s+operations|maintenance)\b)'),
    ('digital_twin', r'\b(?:digital[\s-]*twins?|operational\s+twins?|asset\s+twins?)\b'),
    ('construction_safety_monitoring', r'\b(?:construction\s+(?:site\s+)?safety|site\s+safety|safety\s+monitoring|ppe\s+(?:detection|monitoring|compliance)|unsafe\s+behavio[u]?r|hazard\s+(?:detection|monitoring)|workplace\s+safety)\b'),
    ('generative_design', r'\b(?:generative\s+design|automated\s+design\s+generation|design\s+optimi[sz]ation)\b'),
    ('progress_monitoring', r'\b(?:construction\s+progress|site\s+progress|progress\s+monitoring|progress\s+tracking)\b'),
    ('quality_inspection', r'\b(?:quality\s+inspection|defect\s+detection|automated\s+qa\s*/\s*qc)\b'),
)

def identify_capability(query: str):
    for name, pattern in PATTERNS:
        if re.search(pattern, query, re.I | re.S):
            return name
    return None
