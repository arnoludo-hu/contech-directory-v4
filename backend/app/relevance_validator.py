"""Evidence-first capability validation for solution discovery.

This module does not modify source data or infer official verification.
Unrecognised specific operational requests fail closed rather than selecting
unrelated top-k results. Attribute-only browsing is handled elsewhere.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Assessment:
    status: str  # eligible, unknown, ineligible
    reason: str

# Positive, task-specific evidence. Each tuple is an AND of independent
# evidence families. Multiple tuples are OR alternatives.
EVIDENCE = {
    'robotic_layout': [
        (r'\b(?:robot|robotic|robotics|autonomous\s+(?:machine|equipment))\b',
         r'\b(?:construction\s+layout|layout\s+marking|floor\s+marking|setting[ -]?out|stakeout|marking\s+robot|layout\s+robot)\b')],
    'robotic_tile_layout': [
        (r'\b(?:robot|robotic|robotics)\b',
         r'\b(?:tile\s+(?:layout|setting|laying|placement|installation)|(?:install|place|lay|set)\s+tiles)\b')],
    'fm_digital_twin': [
        (r'\b(?:digital[ -]?twins?|operational\s+twins?|asset\s+twins?)\b',
         r'\b(?:facilit(?:y|ies)\s+management|facility\s+operations|building\s+operations|maintenance|\bfm\b|\bbms\b)')],
    'digital_twin': [(r'\b(?:digital[ -]?twins?|operational\s+twins?|asset\s+twins?)\b',)],
    'construction_safety_monitoring': [(r'\b(?:site\s+safety|construction\s+safety|safety\s+monitoring|ppe\s+(?:detection|monitoring|compliance)|unsafe\s+behavio[u]?r|hazard\s+(?:detection|monitoring)|safety\s+analytics|safety\s+inspections?|safety\s+compliance\s+monitoring|digital\s+safety\s+planning\s+and\s+management|safety\s+management|safety\s+manag(?:e)?ment)\b',)],
    'ppe_detection': [(r'\b(?:ppe\s+(?:detection|monitoring|compliance)|personal\s+protective\s+equipment\s+(?:detection|monitoring|compliance))\b',)],
    'generative_design': [(r'\b(?:generative\s+design|automated\s+design\s+generation|design\s+optimi[sz]ation)\b',)],
    'progress_monitoring': [(r'\b(?:progress\s+monitoring|progress\s+tracking|site\s+progress|construction\s+progress)\b',)],
    'quality_inspection': [(r'\b(?:quality\s+inspection|defect\s+detection|automated\s+inspection|visual\s+inspection)\b',)],
    'pile_position_verification': [(r'\b(?:pile|piles|piling)\b',r'\b(?:coordinate|survey|position|location|as[ -]?built)\b',r'\b(?:design\s+compar|deviation|verification|misplac|wrong\s+location)')],
    'quantity_takeoff': [(r'\b(?:quantity\s+take[ -]?off|automated\s+measurement|material\s+quantification)\b',)],
    'predictive_maintenance': [(r'\b(?:predictive\s+maintenance|condition[ -]?based\s+maintenance|failure\s+prediction)\b',)],
}

NEGATION = re.compile(r'\b(?:does\s+not|do\s+not|not\s+supported|without|no)\b',re.I)

def solution_text(row: dict) -> str:
    fields = ('summary','source_use_cases','source_technology','source_category','material_ai_description')
    values = [str(row.get(k) or '') for k in fields]
    for k in ('use_cases','technologies'):
        v=row.get(k) or []
        values.extend(map(str,v if isinstance(v,list) else [v]))
    return ' '.join(values).lower()

def assess(row: dict, capability: str) -> Assessment:
    text=solution_text(row)
    patterns=EVIDENCE.get(capability)
    if not patterns:
        return Assessment('unknown','Capability is not yet mapped to an evidence rule')
    for alternative in patterns:
        matches=[re.search(p,text,re.I) for p in alternative]
        if all(matches):
            # Avoid using explicit negative claims as evidence. This conservative
            # window is imperfect: manual review remains needed for nuanced prose.
            if any(NEGATION.search(text[max(0,m.start()-35):m.start()]) for m in matches if m):
                continue
            return Assessment('eligible','Recorded solution-level capability evidence')
    return Assessment('unknown','Insufficient recorded evidence of mandatory capability')

# The parser is deliberately phrase-aware. Generic browsing queries must
# return None so their structured filters remain authoritative.
INTENT_PATTERNS = [
 ('pile_position_verification',r'(?=.*\b(?:pile|piles|piling)\b)(?=.*\b(?:wrong|misplac|position|locat|coordinat|deviat|as[ -]?built)\b)'),
 ('robotic_tile_layout',r'(?=.*\b(?:tile|tiles)\b)(?=.*\b(?:robot|robotic)\b)'),
 ('robotic_layout',r'(?=.*\b(?:robot|robots|robotic)\b)(?=.*\b(?:layout|marking|setting[ -]?out|stakeout)\b)'),
 ('fm_digital_twin',r'(?=.*\b(?:digital[ -]?twins?|operational\s+twins?|asset\s+twins?)\b)(?=.*\b(?:fm|facilit|maintenance|building\s+operations)\b)'),
 ('digital_twin',r'\b(?:digital[ -]?twins?|operational\s+twins?|asset\s+twins?)\b'),
 ('construction_safety_monitoring',r'\b(?:construction\s+(?:site\s+)?safety|site\s+safety|safety\s+monitoring|ppe\s+detection|unsafe\s+behavio[u]?r|hazard\s+detection)\b'),
 ('generative_design',r'\b(?:generative\s+design|design\s+optimi[sz]ation|automated\s+design\s+generation)\b'),
 ('progress_monitoring',r'\b(?:progress\s+monitoring|progress\s+tracking|construction\s+progress|site\s+progress)\b'),
 ('quality_inspection',r'\b(?:quality\s+inspection|defect\s+detection|automated\s+inspection)\b'),
 ('quantity_takeoff',r'\b(?:quantity\s+take[ -]?off|automated\s+quantity\s+measurement)\b'),
 ('predictive_maintenance',r'\b(?:predictive\s+maintenance|failure\s+prediction)\b'),
]

def identify(query: str) -> Optional[str]:
    for name,pattern in INTENT_PATTERNS:
        if re.search(pattern,query,re.I|re.S):
            return name
    return None
