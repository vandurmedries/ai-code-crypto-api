"""
Real Coding Agency Router
Integrates real freelance APIs (Upwork, Fiverr, Toptal) and A2A protocol
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import os

from app.database import get_db
from app.services.auth import get_current_active_user
from app import models

# Real API imports
from app.services.real_freelance_apis import get_freelance_aggregator
from app.services.google_a2a_protocol import A2ACodingAgent, get_all_a2a_agents, register_a2a_agent
from app.services.real_blockchain_wallet import get_real_wallet_manager

# Selenium automation imports
from app.services.selenium_automation import get_selenium_automation
from app.services.job_scraper import get_job_scraper, ScrapedJob
from app.services.auto_apply import get_auto_apply_manager, UserProfile

router = APIRouter(prefix="/real-agency", tags=["real-coding-agency"])

# Initialize the real coding agent
_real_coding_agent: Optional[A2ACodingAgent] = None

def get_real_coding_agent() -> A2ACodingAgent:
    """Get or create the real A2A coding agent"""
    global _real_coding_agent
    if _real_coding_agent is None:
        base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        _real_coding_agent = A2ACodingAgent(
            url=f"{base_url}/real-agency",
            provider_name="AI Earning Platform"
        )
        register_a2a_agent(_real_coding_agent)
    return _real_coding_agent


@router.get("/platforms/status")
def get_platforms_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get status of all freelance platform integrations"""
    aggregator = get_freelance_aggregator()
    
    status = aggregator.get_all_platforms_status()
    
    return {
        "authenticated": current_user.id,
        "platforms": status,
        "setup_instructions": {
            "upwork": {
                "url": "https://developers.upwork.com/",
                "required_env": ["UPWORK_CLIENT_ID", "UPWORK_CLIENT_SECRET", "UPWORK_ACCESS_TOKEN"],
                "note": "OAuth 2.0 flow required for authentication"
            },
            "fiverr": {
                "url": "https://developers.fiverr.com/",
                "required_env": ["FIVERR_API_KEY"],
                "note": "Seller API for managing gigs and orders"
            },
            "toptal": {
                "url": "https://www.toptal.com/",
                "required_env": ["TOPTAL_API_KEY"],
                "note": "Requires talent application and approval first"
            }
        }
    }


@router.post("/platforms/setup-guide")
def get_setup_guide(
    platform: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get detailed setup guide for a specific platform"""
    
    guides = {
        "upwork": {
            "steps": [
                "1. Create Upwork account at https://www.upwork.com/",
                "2. Go to https://developers.upwork.com/ and create a new app",
                "3. Complete your freelancer profile with skills and portfolio",
                "4. Get your Client ID and Client Secret from the developer console",
                "5. Complete OAuth flow to obtain Access Token and Refresh Token",
                "6. Set environment variables: export UPWORK_CLIENT_ID='xxx'",
                "7. Restart the backend server"
            ],
            "oauth_flow": {
                "authorization_url": "/real-agency/upwork/auth-url",
                "callback_handler": "/real-agency/upwork/callback",
                "description": "User must authorize the application to access their Upwork account"
            },
            "pricing": "10% freelancer fee on earnings",
            "timeline": "Profile approval: 1-3 days. First job: 1-4 weeks typically.",
            "earning_potential": "$50-300/hour for developers"
        },
        "fiverr": {
            "steps": [
                "1. Create Fiverr account at https://www.fiverr.com/",
                "2. Apply for API access at https://developers.fiverr.com/",
                "3. Create seller profile and publish gigs (services)",
                "4. Wait for API key approval (can take weeks)",
                "5. Once approved, get API key from developer dashboard",
                "6. Set environment variable: export FIVERR_API_KEY='xxx'",
                "7. Restart the backend server"
            ],
            "pricing": "20% platform fee on all orders",
            "timeline": "Gig approval: 24-48 hours. First order: 1-8 weeks.",
            "earning_potential": "$50-500 per gig for development services"
        },
        "toptal": {
            "steps": [
                "1. Apply at https://www.toptal.com/developers",
                "2. Complete screening process (language, personality, technical)",
                "3. Pass technical interview with senior developer",
                "4. Complete test project (1-3 weeks unpaid)",
                "5. Once accepted, request API access from Toptal support",
                "6. Get API key and set: export TOPTAL_API_KEY='xxx'",
                "7. Restart the backend server"
            ],
            "pricing": "Hourly rates set by you (typically $60-200/hr)",
            "timeline": "Vetting process: 2-8 weeks. First client: 1-4 weeks after acceptance.",
            "earning_potential": "$60-250/hour for vetted developers",
            "note": "Most exclusive platform - only top 3% accepted"
        }
    }
    
    if platform not in guides:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {platform}")
    
    return {
        "platform": platform,
        **guides[platform]
    }


@router.get("/jobs/search")
def search_real_jobs(
    query: str = "python",
    min_budget: float = 100,
    skills: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Search for real jobs across all connected platforms
    Returns actual job listings from Upwork, Fiverr, Toptal
    """
    aggregator = get_freelance_aggregator()
    
    # Check if any platforms are authenticated
    status = aggregator.get_all_platforms_status()
    any_authenticated = any(s["authenticated"] for s in status.values())
    
    if not any_authenticated:
        return {
            "error": "No platforms authenticated",
            "message": "Please configure at least one freelance platform first",
            "setup_url": "/real-agency/platforms/status",
            "note": "This requires real API credentials from Upwork, Fiverr, or Toptal"
        }
    
    # Parse skills
    skill_list = skills.split(",") if skills else ["python", "fastapi", "react"]
    
    # Search all platforms
    results = aggregator.search_all_jobs(
        query=query,
        skills=skill_list,
        min_budget=min_budget
    )
    
    # Convert to serializable format
    jobs_by_platform = {}
    total_jobs = 0
    
    for platform, jobs in results.items():
        if platform == "errors":
            continue
            
        serializable_jobs = []
        for job in jobs:
            if hasattr(job, '__dataclass_fields__'):
                # It's a FreelanceJob dataclass
                serializable_jobs.append({
                    "job_id": job.job_id,
                    "title": job.title,
                    "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
                    "platform": job.platform,
                    "budget_type": job.budget_type,
                    "budget_min": job.budget_min,
                    "budget_max": job.budget_max,
                    "hourly_rate": job.hourly_rate,
                    "skills_required": job.skills_required[:5],
                    "proposals_count": job.proposals_count,
                    "is_verified": job.is_verified,
                    "url": job.url,
                    "posted_at": job.posted_at.isoformat() if hasattr(job.posted_at, 'isoformat') else str(job.posted_at)
                })
            else:
                # It's already a dict (from Fiverr buyer requests)
                serializable_jobs.append(job)
        
        jobs_by_platform[platform] = serializable_jobs
        total_jobs += len(serializable_jobs)
    
    return {
        "query": query,
        "min_budget": min_budget,
        "skills": skill_list,
        "total_jobs_found": total_jobs,
        "platforms_searched": list(jobs_by_platform.keys()),
        "jobs_by_platform": jobs_by_platform,
        "errors": results.get("errors", [])
    }


@router.get("/jobs/best-opportunities")
def get_best_opportunities(
    min_budget: float = 500,
    required_skills: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get the best job opportunities ranked by score and client quality"""
    aggregator = get_freelance_aggregator()
    
    # Check authentication
    status = aggregator.get_all_platforms_status()
    any_authenticated = any(s["authenticated"] for s in status.values())
    
    if not any_authenticated:
        return {
            "error": "No platforms authenticated",
            "message": "Configure freelance APIs to see real opportunities"
        }
    
    # Parse skills
    skills_list = required_skills.split(",") if required_skills else None
    
    opportunities = aggregator.get_best_opportunities(
        min_budget=min_budget,
        required_skills=skills_list
    )
    
    return {
        "opportunities": [
            {
                "title": opp["job"].title,
                "platform": opp["platform"],
                "budget": f"${opp['job'].budget_min}-${opp['job'].budget_max}",
                "hourly_rate": opp["job"].hourly_rate,
                "score": opp["score"],
                "competition": opp["competition_level"],
                "skills": opp["job"].skills_required[:5],
                "url": opp["job"].url,
                "client_verified": opp["job"].is_verified,
                "proposals_count": opp["job"].proposals_count
            }
            for opp in opportunities
        ],
        "count": len(opportunities),
        "filters": {
            "min_budget": min_budget,
            "required_skills": skills_list
        }
    }


@router.post("/proposals/submit")
def submit_proposal(
    job_id: str = Body(...),
    platform: str = Body(...),
    cover_letter: str = Body(...),
    proposed_rate: float = Body(...),
    auto_discover: bool = Body(False),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Submit a proposal to a real job
    Or auto-discover and submit to best matches
    """
    aggregator = get_freelance_aggregator()
    
    if auto_discover:
        # Auto-find and submit to best matches
        results = aggregator.submit_proposal_to_best_matches(auto_submit=True)
        
        # Track in database
        total_submitted = len([r for r in results if r.get("success")])
        
        return {
            "mode": "auto_discover",
            "proposals_submitted": total_submitted,
            "results": results,
            "message": f"Auto-submitted {total_submitted} proposals to best matches"
        }
    else:
        # Submit to specific job
        if platform == "upwork":
            result = aggregator.upwork.submit_proposal(
                job_id=job_id,
                cover_letter=cover_letter,
                proposed_rate=proposed_rate
            )
        elif platform == "toptal":
            result = aggregator.toptal.submit_application(
                job_id=job_id,
                message=cover_letter
            )
        else:
            return {"error": f"Platform {platform} not supported for direct submission"}
        
        return {
            "mode": "direct_submit",
            "platform": platform,
            "job_id": job_id,
            "result": result,
            "note": "This submits a real proposal to a real job posting"
        }


@router.get("/earnings/summary")
def get_earnings_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get real earnings summary from all platforms"""
    aggregator = get_freelance_aggregator()
    
    summary = aggregator.get_earnings_summary()
    
    return {
        "user_id": current_user.id,
        **summary,
        "note": "Real earnings from connected platforms. May be 0 if no jobs completed yet."
    }


# A2A Protocol Endpoints

@router.post("/a2a")
def a2a_protocol_handler(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    A2A Protocol Endpoint
    Handles incoming agent-to-agent requests per Google A2A specification
    """
    agent = get_real_coding_agent()
    
    response = agent.process_request(request)
    
    return response


@router.get("/a2a/agent-card")
def get_a2a_agent_card():
    """Get A2A Agent Card for discovery by other agents"""
    agent = get_real_coding_agent()
    
    return agent.get_agent_card().to_dict()


@router.get("/a2a/discover")
def discover_other_agents(
    directory_url: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Discover other A2A agents from a directory service"""
    agent = get_real_coding_agent()
    
    # Use default directory if none provided
    directory = directory_url or os.getenv("A2A_DIRECTORY_URL", "http://localhost:8000/a2a-directory")
    
    discovered = agent.discover_agents(directory)
    
    return {
        "directory": directory,
        "agents_discovered": len(discovered),
        "agents": [
            {
                "name": a.name,
                "description": a.description[:100] + "...",
                "url": a.url,
                "provider": a.provider,
                "skills_count": len(a.skills)
            }
            for a in discovered
        ]
    }


@router.post("/a2a/send-task")
def send_task_to_agent(
    agent_url: str = Body(...),
    message: str = Body(...),
    skill_hint: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Send a task to another A2A agent"""
    agent = get_real_coding_agent()
    
    result = agent.send_task_to_agent(
        agent_url=agent_url,
        message=message,
        skill_hint=skill_hint
    )
    
    return {
        "sender_agent": agent.name,
        "target_agent_url": agent_url,
        "message_sent": message[:100] + "...",
        "response": result,
        "protocol": "Google A2A"
    }


# Blockchain Wallet Integration

@router.post("/wallet/add")
def add_real_wallet(
    currency: str = Body(...),  # BTC or ETH
    address: str = Body(...),
    wallet_label: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Add a real crypto wallet address to track
    Requires real blockchain API keys (BlockCypher, Etherscan)
    """
    wallet_mgr = get_real_wallet_manager()
    
    wallet_id = f"{current_user.id}_{currency}_{address[:8]}"
    
    wallet = wallet_mgr.add_existing_wallet(
        wallet_id=wallet_id,
        currency=currency,
        address=address,
        beneficiary_email=current_user.email
    )
    
    # Check for API keys
    has_blockcypher = bool(os.getenv("BLOCKCYPHER_API_TOKEN"))
    has_etherscan = bool(os.getenv("ETHERSCAN_API_KEY"))
    
    return {
        "wallet_added": True,
        "wallet_id": wallet_id,
        "currency": currency,
        "address": address,
        "current_balance": wallet.balance,
        "api_status": {
            "blockcypher_configured": has_blockcypher,
            "etherscan_configured": has_etherscan,
            "note": "Set BLOCKCYPHER_API_TOKEN and ETHERSCAN_API_KEY for real balance lookups"
        },
        "refresh_endpoint": f"/real-agency/wallet/{wallet_id}/refresh"
    }


@router.get("/wallet/{wallet_id}/refresh")
def refresh_wallet_balance(
    wallet_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Refresh wallet balance from the blockchain"""
    wallet_mgr = get_real_wallet_manager()
    
    wallet = wallet_mgr.refresh_wallet_balance(wallet_id)
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    return {
        "wallet_id": wallet_id,
        "currency": wallet.currency,
        "address": wallet.address,
        "balance": wallet.balance,
        "balance_raw": wallet.balance_wei_or_sat,
        "total_received": wallet.total_received,
        "total_sent": wallet.total_sent,
        "transaction_count": wallet.transaction_count,
        "last_updated": wallet.last_updated
    }


@router.get("/wallet/{wallet_id}/transactions")
def get_wallet_transactions(
    wallet_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get real blockchain transactions for a wallet"""
    wallet_mgr = get_real_wallet_manager()
    
    transactions = wallet_mgr.get_wallet_transactions(wallet_id)
    
    return {
        "wallet_id": wallet_id,
        "transactions": transactions,
        "count": len(transactions)
    }


@router.get("/wallets/summary")
def get_all_wallets_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get summary of all tracked wallets with real balances"""
    wallet_mgr = get_real_wallet_manager()
    
    summary = wallet_mgr.get_all_balances()
    
    return {
        "user_id": current_user.id,
        **summary
    }


# Combined Workflow

@router.post("/auto-earn-cycle")
def run_real_auto_earn_cycle(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Run one autonomous earning cycle with REAL integrations:
    1. Search for real jobs across platforms
    2. Find best opportunities
    3. Check wallet balances
    4. Return actionable opportunities
    """
    aggregator = get_freelance_aggregator()
    wallet_mgr = get_real_wallet_manager()
    
    results = {
        "jobs_found": 0,
        "opportunities": [],
        "wallets_summary": {},
        "recommendations": []
    }
    
    # Step 1: Search for jobs if platforms connected
    try:
        job_results = aggregator.search_all_jobs(min_budget=100)
        for platform, jobs in job_results.items():
            if platform != "errors":
                results["jobs_found"] += len(jobs)
    except Exception as e:
        results["job_search_error"] = str(e)
    
    # Step 2: Get best opportunities
    try:
        opportunities = aggregator.get_best_opportunities(min_budget=500)
        results["opportunities"] = [
            {
                "title": opp["job"].title,
                "platform": opp["platform"],
                "budget": f"${opp['job'].budget_min}-${opp['job'].budget_max}",
                "url": opp["job"].url,
                "score": opp["score"]
            }
            for opp in opportunities[:5]
        ]
    except Exception as e:
        results["opportunities_error"] = str(e)
    
    # Step 3: Check wallet balances
    try:
        results["wallets_summary"] = wallet_mgr.get_all_balances()
    except Exception as e:
        results["wallet_error"] = str(e)
    
    # Step 4: Generate recommendations
    recommendations = []
    
    if results["jobs_found"] == 0:
        recommendations.append({
            "priority": "high",
            "action": "Setup freelance platforms",
            "details": "No jobs found. Configure Upwork, Fiverr, or Toptal APIs to access real opportunities.",
            "url": "/real-agency/platforms/status"
        })
    
    if results["opportunities"]:
        best = results["opportunities"][0]
        recommendations.append({
            "priority": "high",
            "action": "Apply to best opportunity",
            "details": f"Apply to '{best['title']}' on {best['platform']} - Budget: {best['budget']}",
            "url": best["url"]
        })
    
    if not results["wallets_summary"].get("wallets"):
        recommendations.append({
            "priority": "medium",
            "action": "Add crypto wallet",
            "details": "Add BTC or ETH wallet to track real earnings",
            "url": "/real-agency/wallet/add"
        })
    
    results["recommendations"] = recommendations
    
    return {
        "cycle_completed": True,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        **results
    }


# ============================================================================
# SELENIUM AUTOMATION ENDPOINTS
# ============================================================================

@router.post("/selenium/screenshot")
def take_screenshot(
    url: str = Body(...),
    full_page: bool = Body(False),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Take automated screenshot of any website (Use Case #6)"""
    selenium = get_selenium_automation(headless=True)
    
    try:
        result = selenium.take_screenshot(url=url, full_page=full_page)
        
        return {
            "success": result.success,
            "message": result.message,
            "screenshot_path": result.screenshot_path,
            "url": url,
            "full_page": full_page,
            "timestamp": result.timestamp
        }
    finally:
        selenium.close()


@router.post("/selenium/website-check")
def check_website_status(
    url: str = Body(...),
    expected_content: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Check website status like a bot (Use Case #7)"""
    selenium = get_selenium_automation(headless=True)
    
    try:
        result = selenium.check_website_status(
            url=url,
            expected_content=expected_content
        )
        
        return {
            "success": result.success,
            "message": result.message,
            "is_up": result.data.get("is_up"),
            "load_time_seconds": result.data.get("load_time_seconds"),
            "errors_detected": result.data.get("errors_detected"),
            "page_title": result.data.get("page_title"),
            "screenshot_path": result.screenshot_path,
            "timestamp": result.timestamp
        }
    finally:
        selenium.close()


@router.post("/selenium/google-search")
def google_search(
    query: str = Body(...),
    result_count: int = Body(10),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Automate Google search (Use Case #8)"""
    selenium = get_selenium_automation(headless=True)
    
    try:
        result = selenium.google_search(
            query=query,
            result_count=result_count
        )
        
        return {
            "success": result.success,
            "query": query,
            "results_count": result.data.get("results_count"),
            "results": result.data.get("results", []),
            "timestamp": result.timestamp
        }
    finally:
        selenium.close()


@router.post("/selenium/scrape-prices")
def scrape_prices(
    url: str = Body(...),
    price_selector: str = Body(...),
    name_selector: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Scrape prices without API (Use Case #5)"""
    selenium = get_selenium_automation(headless=True)
    
    try:
        result = selenium.scrape_prices(
            url=url,
            price_selector=price_selector,
            name_selector=name_selector
        )
        
        return {
            "success": result.success,
            "products_found": result.data.get("products_found"),
            "products": result.data.get("products", []),
            "timestamp": result.timestamp
        }
    finally:
        selenium.close()


# ============================================================================
# JOB SCRAPING ENDPOINTS (Platforms Without APIs)
# ============================================================================

@router.get("/jobs/scrape")
def scrape_jobs_from_platforms(
    query: str = "python developer",
    sources: str = "all",  # comma-separated: linkedin,indeed,weworkremotely,remoteco
    remote_only: bool = True,
    max_per_source: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Scrape jobs from platforms without APIs using Selenium
    - LinkedIn Jobs
    - Indeed
    - We Work Remotely
    - Remote.co
    """
    scraper = get_job_scraper()
    
    try:
        # Parse sources
        source_list = sources.split(",") if sources != "all" else ["linkedin", "indeed", "weworkremotely", "remoteco"]
        
        all_jobs = {}
        total_jobs = 0
        
        for source in source_list:
            try:
                if source == "linkedin":
                    from app.services.job_scraper import LinkedInJobScraper
                    s = LinkedInJobScraper(scraper.selenium)
                    jobs = s.search_jobs(keywords=query, remote=remote_only, max_results=max_per_source)
                elif source == "indeed":
                    from app.services.job_scraper import IndeedJobScraper
                    s = IndeedJobScraper(scraper.selenium)
                    jobs = s.search_jobs(query=query, remote=remote_only, max_results=max_per_source)
                elif source == "weworkremotely":
                    from app.services.job_scraper import WeWorkRemotelyScraper
                    s = WeWorkRemotelyScraper(scraper.selenium)
                    jobs = s.search_jobs(category="programming", max_results=max_per_source)
                elif source == "remoteco":
                    from app.services.job_scraper import RemoteCoScraper
                    s = RemoteCoScraper(scraper.selenium)
                    jobs = s.search_jobs(category="developer", max_results=max_per_source)
                else:
                    continue
                
                # Convert to serializable format
                all_jobs[source] = [
                    {
                        "title": job.title,
                        "company": job.company,
                        "location": job.location,
                        "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
                        "url": job.url,
                        "platform": job.platform,
                        "salary": job.salary,
                        "remote": job.remote,
                        "posted_date": job.posted_date,
                        "scraped_at": job.scraped_at
                    }
                    for job in jobs
                ]
                total_jobs += len(jobs)
                
            except Exception as e:
                all_jobs[source] = {"error": str(e)}
        
        return {
            "query": query,
            "sources_searched": source_list,
            "total_jobs_found": total_jobs,
            "jobs_by_source": all_jobs,
            "note": "These are real jobs scraped from live websites using Selenium"
        }
        
    finally:
        scraper.close()


@router.get("/jobs/scrape/best-opportunities")
def get_scraped_best_opportunities(
    query: str = "python developer",
    min_salary: Optional[str] = Body(None),
    remote_only: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get best opportunities from scraped jobs with AI scoring"""
    scraper = get_job_scraper()
    
    try:
        opportunities = scraper.get_best_opportunities(
            query=query,
            min_salary=min_salary,
            remote_only=remote_only
        )
        
        return {
            "query": query,
            "opportunities_count": len(opportunities),
            "opportunities": [
                {
                    "title": opp["job"]["title"],
                    "company": opp["job"]["company"],
                    "location": opp["job"]["location"],
                    "source": opp["source"],
                    "score": opp["score"],
                    "match_reasons": opp["match_reasons"],
                    "estimated_quality": opp["estimated_quality"],
                    "salary": opp["job"]["salary"],
                    "url": opp["job"]["url"]
                }
                for opp in opportunities[:20]
            ],
            "note": "Scored based on remote work, salary transparency, company reputation, and title relevance"
        }
        
    finally:
        scraper.close()


# ============================================================================
# AUTO-APPLY ENDPOINTS
# ============================================================================

@router.post("/apply/auto-fill")
def auto_apply_to_job(
    job_url: str = Body(...),
    profile: Dict[str, Any] = Body(...),
    platform: Optional[str] = Body(None),  # linkedin, indeed, or generic
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Auto-fill and submit job application using Selenium
    Works with LinkedIn Easy Apply, Indeed Apply, and generic forms
    
    Required profile fields:
    - first_name, last_name, email
    - Optional: phone, linkedin_url, resume_path, summary, skills
    """
    auto_apply = get_auto_apply_manager()
    
    try:
        # Create user profile
        user_profile = UserProfile(profile)
        
        # Apply to job
        result = auto_apply.apply_to_job(
            job_url=job_url,
            profile=user_profile,
            platform=platform
        )
        
        return {
            "success": result.success,
            "platform": result.platform,
            "job_url": result.job_url,
            "message": result.message,
            "fields_filled": result.form_fields_filled,
            "errors": result.errors,
            "screenshot_path": result.screenshot_path,
            "submitted_at": result.submitted_at,
            "warning": "This submits REAL applications to REAL job postings. Review carefully before using."
        }
        
    finally:
        pass  # Keep selenium open for potential bulk apply


@router.post("/apply/bulk")
def bulk_apply_to_jobs(
    job_urls: List[str] = Body(...),
    profile: Dict[str, Any] = Body(...),
    delay_seconds: int = Body(30),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Apply to multiple jobs automatically with delay between applications
    
    WARNING: This submits REAL applications. Use with caution.
    """
    auto_apply = get_auto_apply_manager()
    
    try:
        user_profile = UserProfile(profile)
        
        results = auto_apply.bulk_apply(
            job_urls=job_urls,
            profile=user_profile,
            delay_between=delay_seconds
        )
        
        successful = sum(1 for r in results if r.success)
        
        return {
            "total_jobs": len(job_urls),
            "successful": successful,
            "failed": len(job_urls) - successful,
            "results": [
                {
                    "success": r.success,
                    "platform": r.platform,
                    "job_url": r.job_url,
                    "message": r.message
                }
                for r in results
            ],
            "stats": auto_apply.get_application_stats(),
            "warning": f"Submitted {successful} REAL job applications. These are actual applications to real companies."
        }
        
    finally:
        auto_apply.close()


@router.get("/apply/stats")
def get_application_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get statistics on auto-applied jobs"""
    auto_apply = get_auto_apply_manager()
    
    return {
        "user_id": current_user.id,
        **auto_apply.get_application_stats()
    }


# ============================================================================
# MONITORING & UTILITIES
# ============================================================================

@router.post("/monitor/website")
def monitor_website(
    url: str = Body(...),
    check_interval_hours: int = Body(24),
    expected_content: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Schedule website monitoring (Use Case #7)
    Can be scheduled with cron or APScheduler to run periodically
    """
    selenium = get_selenium_automation(headless=True)
    
    try:
        result = selenium.check_website_status(
            url=url,
            expected_content=expected_content
        )
        
        # This would typically save to a monitoring table in production
        return {
            "url": url,
            "status": "up" if result.success else "down",
            "load_time_seconds": result.data.get("load_time_seconds"),
            "errors": result.data.get("errors_detected"),
            "screenshot": result.screenshot_path,
            "check_completed_at": result.timestamp,
            "next_check_scheduled": f"In {check_interval_hours} hours",
            "note": "For continuous monitoring, schedule this endpoint with APScheduler or cron"
        }
        
    finally:
        selenium.close()


@router.post("/utils/auto-login")
def auto_login_to_website(
    url: str = Body(...),
    username: str = Body(...),
    password: str = Body(...),
    username_selector: str = Body("#username"),
    password_selector: str = Body("#password"),
    submit_selector: str = Body("#submit"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Auto-login to any website (Use Case #1)
    Useful for keeping sessions active on freelance platforms
    """
    selenium = get_selenium_automation(headless=False)  # Visible for captcha handling
    
    try:
        result = selenium.auto_login(
            url=url,
            username=username,
            password=password,
            username_selector=username_selector,
            password_selector=password_selector,
            submit_selector=submit_selector
        )
        
        return {
            "success": result.success,
            "message": result.message,
            "url_after_login": result.data.get("url_after"),
            "screenshot": result.screenshot_path,
            "timestamp": result.timestamp,
            "warning": "Credentials are used immediately and not stored. Use with caution."
        }
        
    finally:
        selenium.close()
