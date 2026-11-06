from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Severity = Literal["info", "warning", "major", "critical"]
FindingStatus = Literal["open", "fixed", "acknowledged"]
ReportStatus = Literal["pass", "pass_with_warnings", "needs_review", "blocked"]


class QualityFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    check_name: str
    module: str
    location: str
    text: str
    severity: Severity
    explanation: str
    suggested_fix: str
    auto_fix_available: bool = False
    status: FindingStatus = "open"
    acknowledgment_reason: str | None = None


class QualityReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    report_id: str
    campaign_reference: str
    rules_version: str
    prompt_versions: list[str] = Field(default_factory=list)
    timestamp: str
    overall_status: ReportStatus
    overall_score: float = Field(ge=0, le=100)
    module_scores: dict[str, float]
    findings: list[QualityFinding] = Field(default_factory=list)
    check_applicability: dict[str, Literal["English only", "language-aware", "skipped for this language"]] = Field(default_factory=dict)
    language_notes: list[str] = Field(default_factory=list)


class QualityCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    campaign_reference: str
    campaign: dict
    section: str | None = None


class AutoFixRequest(BaseModel):
    finding_ids: list[str]


class AcknowledgeRequest(BaseModel):
    reason: str = Field(min_length=10, max_length=500)


class ApprovalRequest(BaseModel):
    campaign_id: str
    approver: str = Field(min_length=1, max_length=100)
    report_id: str


class RevokeApprovalRequest(BaseModel):
    campaign_id: str
