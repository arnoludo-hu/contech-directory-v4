"""Compatibility adapter for the evidence-based capability validator."""
from .relevance_validator import identify, assess, solution_text

def specific_intent(query):
    return identify(query)

def capability_text(row):
    return solution_text(row)

def eligible(row, intent):
    return assess(row,intent).status == 'eligible'
