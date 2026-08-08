"""Shared state schema for the multi-agent research graph."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class Finding(BaseModel):
    """A single researched fact, always tied to a source."""
    claim: str
    source_url: str
    source_title: str = ""


class ResearchStep(BaseModel):
    """One sub-question the Planner wants investigated."""
    question: str
    status: Literal["pending", "done"] = "pending"


class CriticVerdict(BaseModel):
    """Critic's judgement on the current draft."""
    approved: bool
    reason: str = ""
    route_to: Literal["researcher", "writer", "done"] = "done"


class GraphState(BaseModel):
    """The single object passed between every node in the graph."""
    question: str                                  # original user question
    plan: list[ResearchStep] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    draft_report: str = ""
    critic_verdict: CriticVerdict | None = None
    revision_count: int = 0
    max_revisions: int = 2                          # hard cap, per charter risk notes