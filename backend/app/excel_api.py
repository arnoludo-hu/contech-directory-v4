"""Excel-only FastAPI backend. All records are staging/unverified."""
from __future__ import annotations
import os,re,math
from collections import Counter
from threading import RLock
from uuid import uuid4
from difflib import SequenceMatcher
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from .models import QueryPlan,SearchRequest,SearchResponse,Match,FilterGroup,Predicate
from .interpreter import interpret
from .state import merge
from .excel_store import ExcelStore,code
from .explanations import explain
from .universal_evidence import capability_for_query, eligible_evidence, unrecognised_query_eligible, should_screen_unrecognised
from fastapi.responses import JSONResponse

_semantic_model=None
def semantic_model():
    global _semantic_model
    if os.getenv("ENABLE_LOCAL_EMBEDDINGS","false").lower()!="true":return None
    if _semantic_model is None:
        from sentence_transformers import SentenceTransformer
        _semantic_model=SentenceTransformer(os.getenv("EMBEDDING_MODEL","sentence-transformers/all-MiniLM-L6-v2"))
    return _semantic_model

app=FastAPI(title='ConTech Excel Search API (staging)',version='1.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:3000','http://127.0.0.1:3000'],allow_methods=['GET','POST'],allow_headers=['*'])
store=ExcelStore()
_sessions={};_lock=RLock()
class Session:
    def __init__(self):self.id=str(uuid4());self.plan=QueryPlan();self.last_ids=[];self.last_query='';self.snapshot=[]
class FilterRequest(BaseModel):
    session_id:str|None=None
    filters:dict[str,str]=Field(default_factory=dict)
    page:int=Field(default=1,ge=1)
    page_size:int=Field(default=10,ge=1,le=100)

def session(sid):
    with _lock:
        if sid:
            if sid not in _sessions:raise HTTPException(404,'Conversation expired or server restarted; start a new search')
            return _sessions[sid]
        s=Session();_sessions[s.id]=s;return s

def tokenize(s):return set(re.findall(r'[a-z0-9]+',str(s or '').lower()))-{'the','for','and','with','show','find','solutions','vendors','ai','which','are','there','some','me','tools','need','want'}
def relevance(row,problem):
    if not problem:return 0.0
    q=tokenize(problem)
    if not q:return 0.0
    content=' '.join(str(x or '') for x in [row['company'],row['solution'],row['summary'],row['source_category'],row['source_use_cases'],*row['technologies'],*row['use_cases']])
    tokens=tokenize(content)
    overlap=len(q&tokens)/max(1,len(q))
    fuzzy=max(SequenceMatcher(None,code(problem),code(row['company'])).ratio(),SequenceMatcher(None,code(problem),code(row['solution'])).ratio())
    return min(100,round(100*(0.85*overlap+0.15*fuzzy),1))

def score_rows(rows,plan):
    # Stable deterministic fallback, no external embedding download required.
    scored=[]
    model=semantic_model() if plan.problem else None
    vector_scores={}
    if model and rows:
        texts=[' '.join(str(v or '') for v in [r['solution'],r['summary'],r['source_category'],r['source_use_cases'],*r['use_cases'],*r['technologies']]) for r in rows]
        embeddings=model.encode([plan.problem,*texts],normalize_embeddings=True)
        for r,vec in zip(rows,embeddings[1:]):
            vector_scores[r['solution_id']]=max(0.0,float(embeddings[0] @ vec))*100
    for r in rows:
        lexical=relevance(r,plan.problem)
        s=round(0.65*vector_scores[r['solution_id']]+0.35*lexical,1) if model else lexical
        scored.append((s,r))
    return sorted(scored,key=lambda x:(-x[0],x[1]['company'].casefold(),x[1]['solution_id']))

def explicit_no_sg_presence(row):
    """Only an explicit source No can establish absence of the *recorded* entity/reseller.

    Missing, unknown, and blank values are never interpreted as No.
    This does NOT establish absence of all Singapore technical support.
    """
    raw = str(row.get('local_presence_claim') or '').strip().casefold()
    return raw in {'no', 'false', 'n', '0'}


def _negative_presence_requested(plan):
    return any(
        p.field == 'singapore_presence_recorded'
        and p.op == 'eq'
        and any(str(v).casefold() in ('false', 'no') for v in p.values)
        for group in plan.hard for p in group.any_of
    )


def _without_negative_presence(groups):
    """Keep unrelated OR alternatives; only remove the explicit negative predicate."""
    remaining = []
    for group in groups:
