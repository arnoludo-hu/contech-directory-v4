"""Conservative evidence screening for previously unrecognised capability queries.

Never upgrades marketing similarity into independently verified capability.  This
module uses solution-level imported text, not company names or web links.
"""
import re
from .relevance_validator import solution_text, assess, identify

STOP = set('a an the for with of in on to from find show which what who is are i need want solutions solution tools tool ai powered based vendors vendor companies company startup startups construction building technology technologies system systems software platform platforms using use can that provide providing looking'.split())
ATTRIBUTE = re.compile(r'\b(?:psg|pre[ -]?approved|reseller|local (?:entity|presence|support)|singapore presence|series\s+[a-f]|seed|funding|from (?:australia|japan|singapore|china|usa|us)|overseas|list all|how many|compare)\b', re.I)
NEGATED = re.compile(r'\b(?:no|not|without|does not|cannot|doesn.t|lacks)\b', re.I)

# Concept-level phrases that require functionality, not adjacent industries.
THERMAL = re.compile(r'\b(?:thermal\s+insulat(?:ion|ing|or)|heat\s+insulat(?:ion|ing)|insulat(?:ing|ion)\s+(?:coating|paint|panel|material)|aerogel\s+(?:insulat(?:ion|ing)|coating)|thermal\s+resistan(?:ce|t)|low\s+thermal\s+conductivity|insulat(?:ed|ing)\s+panels?)\b', re.I)
THERMAL_QUERY = re.compile(r'\b(?:thermal|heat)\s+insulat(?:ion|ing|or)\b|\binsulat(?:ion|ing)\s+(?:material|coating|panel|paint|solution)', re.I)


def capability_for_query(query):
    if THERMAL_QUERY.search(query):
        return 'thermal_insulation'
    return identify(query)


def eligible_evidence(row, capability):
    if capability == 'thermal_insulation':
        text = solution_text(row)
        for match in THERMAL.finditer(text):
            if not NEGATED.search(text[max(0, match.start()-45):match.start()]):
                return True
        return False
    return assess(row, capability).status == 'eligible'


def unrecognised_query_eligible(row, query):
    """Fail closed for unfamiliar capability requests unless a meaningful phrase is recorded.

    This fallback is intentionally conservative; records with thin descriptions
    may be missed and should be reviewed rather than asserted as matches.
    """
    text = solution_text(row)
    words = [w for w in re.findall(r'[a-z0-9]+', query.lower()) if len(w) > 2 and w not in STOP]
    if not words:
        return False
    # Require a distinctive multiword phrase, never just a shared generic token.
    if len(words) >= 2:
        for n in (3, 2):
            for i in range(len(words)-n+1):
                phrase = r'\b' + r'\W+'.join(map(re.escape, words[i:i+n])) + r'\b'
                for match in re.finditer(phrase, text):
                    if not NEGATED.search(text[max(0,match.start()-45):match.start()]):
                        return True
    return False


def should_screen_unrecognised(plan):
    # Hard attribute filters are authoritative and must never be lost to an
    # unrelated capability screen. Browse/count/compare remain exact.
    return bool(plan.problem.strip() and not plan.hard and plan.intent == 'discover')
