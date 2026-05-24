"""
Belgian Business Real Setup Router
For Belgian company BE0672886525
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.real_belgian_business_setup import RealBelgianAffiliateSetup
from app import models

router = APIRouter()


@router.post("/setup-belgian-business")
def setup_real_belgian_business(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    REAL Belgian Business Setup
    Company: BE0672886525
    Phone: 0479221707
    
    WARNING: Creates REAL legal and tax obligations!
    """
    
    setup = RealBelgianAffiliateSetup()
    result = setup.run_full_setup()
    
    return {
        "success": True,
        "message": "🇧🇪 REAL Belgian Affiliate Business Setup Complete",
        "warning": "⚠️ This creates REAL tax obligations!",
        "company": result["business_entity"]["company_name"],
        "vat_number": result["business_entity"]["vat_number"],
        "phone": result["business_entity"]["phone"],
        "platforms_prepared": len(result["platforms"]),
        "platforms": {
            name: {
                "url": platform["url"],
                "type": platform["platform"]
            }
            for name, platform in result["platforms"].items()
        },
        "packages_location": result["packages_location"],
        "legal_obligations": [
            "Belgian tax declaration (annual)",
            "VAT/BTW filings (quarterly/monthly)",
            "Accounting records (7 years)",
            "Social security (if self-employed)"
        ],
        "estimated_costs": {
            "accounting": "€500-2000/year",
            "website_hosting": "€50-200/year",
            "legal_advice": "€200-500"
        },
        "timeline": {
            "setup_work": "2-3 hours",
            "approval_wait": "1-7 days",
            "first_earnings": "Month 2-3",
            "regular_income": "Month 6+"
        },
        "next_actions": result["next_steps"],
        "autonomous": False,  # Requires manual verification
        "requires_human": True,
        "real_money": True,
        "risk_level": "Medium - Real business with legal obligations"
    }


@router.get("/belgian-setup-status")
def get_belgian_setup_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get status of Belgian business setup"""
    
    import os
    
    setup_dir = "./real_belgian_setup"
    packages = []
    
    if os.path.exists(setup_dir):
        packages = [f for f in os.listdir(setup_dir) if f.endswith('.txt')]
    
    return {
        "vat_number": "BE0672886525",
        "company": "AutoDigital Solutions BV",
        "country": "Belgium",
        "packages_generated": len(packages),
        "packages": packages,
        "platforms": [
            "Amazon Associates EU",
            "ClickBank International",
            "Awin Belgium",
            "TradeTracker Belgium"
        ],
        "setup_complete": len(packages) >= 5,
        "ready_to_register": len(packages) > 0,
        "next_step": "Complete platform registrations manually"
    }


@router.get("/belgian-tax-info")
def get_belgian_tax_info(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Belgian tax obligations information"""
    
    return {
        "country": "Belgium",
        "vat_number": "BE0672886525",
        "tax_obligations": {
            "annual_tax_return": {
                "description": "Personal/Business income tax (aangifte personenbelasting)",
                "deadline": "June 30 (online)",
                "rate": "25-50% progressive",
                "required": True
            },
            "vat_btw": {
                "description": "Value Added Tax (BTW)",
                "threshold": "€25,000 revenue",
                "rate": "21% standard",
                "filing": "Monthly or quarterly",
                "required": "Above threshold"
            },
            "social_security": {
                "description": "Social contributions (RSZ/INSS)",
                "rate": "20-25% of income",
                "required": "If self-employed"
            },
            "accounting": {
                "description": "Financial record keeping",
                "retention": "7 years minimum",
                "software": "Recommended: Accountable, WinBooks"
            }
        },
        "recommended_accountants": [
            "Accountable (online, €39-79/month)",
            "Xerius (social security + accounting)",
            "Securex (full service)",
            "Local certified accountant (NIRB/IEWB)"
        ],
        "tax_office": "FOD Financiën / SPF Finances",
        "vat_office": "BTW Administratie / Administration TVA",
        "chamber_of_commerce": "Voka / Beci (for business support)"
    }
