"""
Repo Adopter Router
API endpoints for Open Source package adoption system
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.repo_adopter import get_repo_adopter_service
from app import models

router = APIRouter()


@router.get("/scan-packages")
def scan_abandoned_packages(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Scan for abandoned but valuable npm packages
    """
    service = get_repo_adopter_service()
    
    packages = service.scan_abandoned_packages()
    
    return {
        "success": True,
        "packages_found": len(packages),
        "packages": [
            {
                "name": p.package_name,
                "version": p.current_version,
                "last_publish": p.last_publish_date,
                "weekly_downloads": p.weekly_downloads,
                "dependents": p.dependent_count,
                "issues": p.open_issues,
                "vulnerabilities": p.security_vulnerabilities,
                "estimated_value": p.estimated_value,
                "maintenance_effort": p.maintenance_effort,
                "monthly_potential": p.monetization_potential
            }
            for p in packages[:10]  # Top 10
        ],
        "message": f"📦 Found {len(packages)} abandoned packages with adoption potential"
    }


@router.get("/analyze/{package_name}")
def analyze_package(
    package_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Analyze specific package for adoption opportunity
    """
    service = get_repo_adopter_service()
    
    opportunity = service.analyze_adoption_opportunity(package_name)
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Package not found")
    
    return {
        "success": True,
        "opportunity_id": opportunity.opportunity_id,
        "package": {
            "name": opportunity.package.package_name,
            "version": opportunity.package.current_version,
            "downloads": opportunity.package.weekly_downloads,
            "dependents": opportunity.package.dependent_count,
            "issues": opportunity.package.open_issues,
            "vulnerabilities": opportunity.package.security_vulnerabilities,
            "outdated_deps": opportunity.package.outdated_dependencies
        },
        "analysis": opportunity.analysis_summary,
        "action_plan": opportunity.action_plan,
        "estimated_monthly_sponsors": opportunity.estimated_monthly_sponsors,
        "setup_time": opportunity.estimated_setup_time,
        "fork_command": opportunity.fork_command,
        "github_sponsors_url": opportunity.github_sponsors_url
    }


@router.get("/top-opportunities")
def get_top_opportunities(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get top adoption opportunities by value
    """
    service = get_repo_adopter_service()
    
    opportunities = service.get_top_opportunities(limit=limit)
    
    return {
        "top_opportunities": [
            {
                "id": opp.opportunity_id,
                "package_name": opp.package.package_name,
                "downloads": opp.package.weekly_downloads,
                "dependents": opp.package.dependent_count,
                "estimated_value": opp.package.estimated_value,
                "monthly_potential": opp.estimated_monthly_sponsors,
                "effort": opp.estimated_setup_time
            }
            for opp in opportunities
        ]
    }


@router.post("/adopt/{opportunity_id}")
def adopt_package(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Mark package as adopted and get action plan
    """
    service = get_repo_adopter_service()
    
    result = service.adopt_package(opportunity_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    # Add to user's balance tracking
    if result.get("estimated_monthly_revenue", 0) > 0:
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        if user:
            # Track potential (not actual until sponsors come in)
            user.notes = f"Adopted: {result['package']} - Potential: €{result['estimated_monthly_revenue']}/month"
            db.commit()
    
    return {
        "success": True,
        **result,
        "next_steps": [
            "1. Fork the repository",
            "2. Set up GitHub Sponsors account",
            "3. Fix security vulnerabilities",
            "4. Release v2.0.0",
            "5. Announce on social media",
            "6. Wait for sponsors (2-4 weeks)"
        ]
    }


@router.get("/adoption-stats")
def get_adoption_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get adoption service statistics
    """
    service = get_repo_adopter_service()
    
    stats = service.get_adoption_stats()
    
    return {
        "user_id": current_user.id,
        **stats,
        "message": "🚀 Open Source Repo Adoption - 100% Legal business model"
    }


@router.post("/autonomous-scan-and-adopt")
def autonomous_scan_and_adopt(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Full autonomous cycle:
    1. Scan for packages
    2. Analyze top 3
    3. Generate adoption plans
    """
    service = get_repo_adopter_service()
    
    # Step 1: Scan
    packages = service.scan_abandoned_packages()
    
    # Step 2: Analyze top 3
    top_packages = packages[:3]
    analyzed = []
    
    for pkg in top_packages:
        opp = service.analyze_adoption_opportunity(pkg.package_name)
        if opp:
            analyzed.append({
                "package": pkg.package_name,
                "opportunity_id": opp.opportunity_id,
                "estimated_value": pkg.estimated_value,
                "monthly_potential": opp.estimated_monthly_sponsors,
                "action_plan": opp.action_plan[:3]
            })
    
    return {
        "success": True,
        "scanned": len(packages),
        "analyzed": len(analyzed),
        "top_opportunities": analyzed,
        "message": f"🤖 Autonomous scan complete! Found {len(packages)} packages, top 3 ready for adoption",
        "recommended_next_action": "Review top opportunities and click 'adopt' on most promising one",
        "estimated_total_monthly_potential": sum(a['monthly_potential'] for a in analyzed)
    }
