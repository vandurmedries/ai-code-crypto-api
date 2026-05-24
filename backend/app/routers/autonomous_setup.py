"""
Autonomous Platform Setup Router
API endpoints for fully autonomous account creation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.autonomous_platform_setup import get_autonomous_setup
from app import models

router = APIRouter()


@router.post("/setup-all")
def setup_all_platforms(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    FULLY AUTONOMOUS: Setup all affiliate platform accounts
    Creates business entity, generates applications, prepares verification
    """
    setup = get_autonomous_setup()
    
    result = setup.setup_all_platforms()
    
    return {
        "success": True,
        "message": "🤖 Autonomous platform setup initiated!",
        "business_created": result["business_entity"],
        "accounts_prepared": result["accounts_created"],
        "status": "ready_for_verification",
        "packages_location": "./platform_accounts/",
        "next_action": "HUMAN_VERIFICATION_REQUIRED",
        "instructions": [
            "1. Check ./platform_accounts/ directory",
            "2. Open MASTER_SETUP_GUIDE.txt",
            "3. Complete each application manually",
            "4. Wait for approvals (1-7 days)",
            "5. Once approved, system takes over automatically"
        ],
        "accounts": result["accounts"],
        "timeline": {
            "manual_work": "2-4 hours",
            "approval_wait": "1-7 days",
            "automation_start": "After all approvals"
        },
        "autonomous": True,
        "requires_human": True,
        "estimated_first_earnings": "$100-500 in month 2-3"
    }


@router.get("/setup-status")
def get_setup_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get autonomous setup status"""
    setup = get_autonomous_setup()
    
    status = setup.get_setup_status()
    
    return {
        "user_id": current_user.id,
        **status,
        "ready_to_earn": all(a["status"] == "completed" for a in status["accounts"].values()) if status["accounts"] else False
    }


@router.post("/verify-account/{platform}")
def verify_platform_account(
    platform: str,
    api_key: str = None,
    api_secret: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    After manual verification, add API keys to enable automation
    """
    setup = get_autonomous_setup()
    
    if platform not in setup.accounts:
        raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
    
    account = setup.accounts[platform]
    
    # Update with real API credentials
    if api_key:
        account.api_key = api_key
    if api_secret:
        account.api_secret = api_secret
    
    account.status = "completed"
    account.verified_at = datetime.utcnow().isoformat()
    
    return {
        "success": True,
        "platform": platform,
        "status": "verified",
        "automation_ready": account.api_key is not None,
        "message": f"✅ {platform} verified! Automation enabled."
    }


@router.get("/packages")
def get_setup_packages(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all generated setup packages"""
    import os
    
    packages_dir = "./platform_accounts"
    packages = []
    
    if os.path.exists(packages_dir):
        for filename in os.listdir(packages_dir):
            if filename.endswith('.txt') or filename.endswith('.json'):
                filepath = os.path.join(packages_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()[:500]  # Preview
                packages.append({
                    "filename": filename,
                    "preview": content,
                    "full_path": filepath
                })
    
    return {
        "total_packages": len(packages),
        "packages": packages
    }
