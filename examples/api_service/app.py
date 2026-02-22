"""FastAPI service for AI Governance compliance checking."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import json
from datetime import datetime
import asyncio
from pathlib import Path
import aiofiles
from ai_governance_tool import ComplianceAnalyzer

app = FastAPI(
    title="AI Governance Compliance API",
    description="REST API for ISO 42001 compliance checking",
    version="1.0.0"
)

# Initialize analyzer
analyzer = ComplianceAnalyzer()

class PolicyCheck(BaseModel):
    """Policy check request model."""
    content: str
    policy_id: Optional[str] = None
    min_score: Optional[float] = 0.6
    notify_url: Optional[str] = None

class ComplianceScore(BaseModel):
    """Category compliance score."""
    score: float
    found_patterns: List[str]
    status: str

class ComplianceResult(BaseModel):
    """Compliance check result model."""
    policy_id: str
    timestamp: str
    overall_score: float
    status: str
    category_scores: Dict[str, ComplianceScore]
    report_url: Optional[str] = None

@app.post("/check", response_model=ComplianceResult)
async def check_policy(policy: PolicyCheck, background_tasks: BackgroundTasks):
    """Check a policy for compliance."""
    try:
        # Generate policy ID if not provided
        policy_id = policy.policy_id or datetime.now().strftime("%Y%m%d_%H%M%S")

        # Analyze policy
        result = analyzer.check_compliance(policy.content, min_score=policy.min_score)

        # Prepare category scores
        category_scores = {}
        for category, score in result.category_scores.items():
            patterns = [p[1] for p in result.found_patterns.get(category, [])]
            category_scores[category] = ComplianceScore(
                score=score,
                found_patterns=patterns,
                status="PASS" if score >= policy.min_score else "FAIL"
            )

        # Generate report in background
        report_path = Path(f"reports/{policy_id}_report.pdf")
        report_path.parent.mkdir(exist_ok=True)

        background_tasks.add_task(
            generate_report,
            result,
            str(report_path),
            policy.notify_url
        )

        return ComplianceResult(
            policy_id=policy_id,
            timestamp=result.timestamp,
            overall_score=result.score,
            status="PASS" if result.is_compliant else "FAIL",
            category_scores=category_scores,
            report_url=f"/reports/{policy_id}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/{policy_id}")
async def get_report(policy_id: str):
    """Get the PDF report for a policy check."""
    report_path = Path(f"reports/{policy_id}_report.pdf")
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        str(report_path),
        media_type="application/pdf",
        filename=f"compliance_report_{policy_id}.pdf"
    )

@app.get("/history")
async def get_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_score: Optional[float] = None
):
    """Get compliance check history."""
    try:
        # Read from SQLite database
        history = analyzer.get_historical_trends()

        # Filter results
        filtered = []
        for idx, timestamp in enumerate(history['timestamps']):
            score = history['overall_scores'][idx]
            if min_score and score < min_score:
                continue

            if start_date and timestamp < start_date:
                continue

            if end_date and timestamp > end_date:
                continue

            filtered.append({
                'timestamp': timestamp,
                'score': score,
                'category_scores': {
                    cat: scores[idx]
                    for cat, scores in history['category_scores'].items()
                }
            })

        return {'results': filtered}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_report(result, report_path: str, notify_url: Optional[str] = None):
    """Generate PDF report and notify if URL provided."""
    from ai_governance_tool.report import generate_pdf_report

    # Generate report
    generate_pdf_report(result, analyzer, report_path)

    # Send notification if URL provided
    if notify_url:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            await session.post(notify_url, json={
                'status': 'complete',
                'report_path': report_path,
                'timestamp': datetime.now().isoformat()
            })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)