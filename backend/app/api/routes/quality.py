from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models.stage8 import ApprovalRequest, AcknowledgeRequest, AutoFixRequest, QualityCheckRequest, RevokeApprovalRequest
from app.services.quality import apply_quality_autofix, run_quality_check

router = APIRouter(tags=["stage8"])

_campaigns: dict[str, dict] = {}
_reports: dict[str, dict] = {}
_approvals: dict[str, dict] = {}


@router.post("/campaigns/quality/check")
def check_quality(request: QualityCheckRequest):
    campaign = request.campaign
    product = campaign.get("product_input", campaign.get("product", {}))
    report = run_quality_check(product, campaign, request.campaign_reference, request.section)
    _campaigns[request.campaign_reference] = campaign
    _reports[request.campaign_reference] = report
    return report


@router.get("/campaigns/{campaign_id}/quality")
def get_quality(campaign_id: str):
    report = _reports.get(campaign_id)
    if report is None:
        raise HTTPException(status_code=404, detail={"code": "QUALITY_REPORT_NOT_FOUND", "field": "campaign_id", "message": "No quality report exists for this campaign."})
    return report


@router.post("/campaigns/quality/autofix")
def autofix(request: AutoFixRequest, campaign_reference: str = "campaign"):
    campaign = _campaigns.get(campaign_reference)
    report = _reports.get(campaign_reference)
    if campaign is None or report is None:
        raise HTTPException(status_code=404, detail={"code": "QUALITY_REPORT_NOT_FOUND", "field": "campaign_reference", "message": "Run a quality check before applying fixes."})
    fixed, diffs = apply_quality_autofix(campaign, report.findings, request.finding_ids)
    _campaigns[campaign_reference] = fixed
    return {"campaign": fixed, "diffs": diffs, "reversible": True}


@router.post("/campaigns/quality/findings/{finding_id}/acknowledge")
def acknowledge_finding(finding_id: str, request: AcknowledgeRequest, campaign_reference: str = "campaign"):
    report = _reports.get(campaign_reference)
    if report is None:
        raise HTTPException(status_code=404, detail={"code": "QUALITY_REPORT_NOT_FOUND", "field": "campaign_reference", "message": "No quality report exists."})
    for finding in report.findings:
        if finding.id == finding_id:
            finding.status = "acknowledged"
            finding.acknowledgment_reason = request.reason
            return finding
    raise HTTPException(status_code=404, detail={"code": "QUALITY_FINDING_NOT_FOUND", "field": "finding_id", "message": "Finding was not found."})


@router.post("/campaigns/quality/findings/{finding_id}/regenerate")
def regenerate_finding(finding_id: str, campaign_reference: str = "campaign"):
    report = _reports.get(campaign_reference)
    if report is None:
        raise HTTPException(status_code=404, detail={"code": "QUALITY_REPORT_NOT_FOUND", "field": "campaign_reference", "message": "No quality report exists."})
    if not any(finding.id == finding_id for finding in report.findings):
        raise HTTPException(status_code=404, detail={"code": "QUALITY_FINDING_NOT_FOUND", "field": "finding_id", "message": "Finding was not found."})
    return {"finding_id": finding_id, "action": "regenerate_section", "constraint_added": True, "attempts_remaining": 0}


@router.post("/campaigns/approve")
def approve_campaign(request: ApprovalRequest):
    report = _reports.get(request.campaign_id)
    if report is None:
        raise HTTPException(status_code=404, detail={"code": "QUALITY_REPORT_NOT_FOUND", "field": "campaign_id", "message": "Run a quality check before approval."})
    if report.report_id != request.report_id:
        raise HTTPException(status_code=409, detail={"code": "QUALITY_REPORT_OUTDATED", "field": "report_id", "message": "Approve the latest quality report."})
    if any(finding.status == "open" and finding.severity == "critical" for finding in report.findings):
        raise HTTPException(status_code=409, detail={"code": "CAMPAIGN_CRITICAL_FINDINGS", "field": "approval", "message": "Critical findings must be fixed before approval."})
    open_major = [finding for finding in report.findings if finding.status == "open" and finding.severity == "major"]
    if open_major:
        raise HTTPException(status_code=409, detail={"code": "CAMPAIGN_MAJOR_FINDINGS", "field": "approval", "message": "Major findings must be fixed or acknowledged with a reason."})
    _approvals[request.campaign_id] = {"status": "approved", "approved_by": request.approver, "approved_at": datetime.now(timezone.utc).isoformat(), "report_id": request.report_id, "export_allowed": True}
    return _approvals[request.campaign_id]


@router.post("/campaigns/approval/revoke")
def revoke_approval(request: RevokeApprovalRequest):
    approval = _approvals.pop(request.campaign_id, None)
    if approval is None:
        raise HTTPException(status_code=404, detail={"code": "CAMPAIGN_APPROVAL_NOT_FOUND", "field": "campaign_id", "message": "Campaign is not approved."})
    return {"status": "draft", "campaign_id": request.campaign_id, "export_allowed": False}


@router.get("/config/quality-rules")
def quality_rules_config():
    from app.services.quality_rules import load_quality_rules
    rules = load_quality_rules()
    return {"rules_version": rules["rules_version"], "starting_version_note": rules["starting_version_note"], "lists": {key: rules[key] for key in rules if isinstance(rules[key], list)}}
