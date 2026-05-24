"""
Real Freelance API Integrations
Upwork, Fiverr, Toptal API clients for finding real coding jobs
"""

import os
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger('RealFreelanceAPIs')


@dataclass
class FreelanceJob:
    """Represents a real freelance job opportunity"""
    job_id: str
    platform: str  # upwork, fiverr, toptal
    title: str
    description: str
    budget_type: str  # fixed, hourly
    budget_min: float
    budget_max: float
    hourly_rate: Optional[float]
    skills_required: List[str]
    client_info: Dict[str, Any]
    posted_at: datetime
    proposals_count: int
    status: str  # open, closed
    url: str
    is_verified: bool


@dataclass
class FreelanceProposal:
    """A proposal submitted to a freelance job"""
    proposal_id: str
    job_id: str
    platform: str
    cover_letter: str
    proposed_rate: float
    proposed_duration: str
    status: str  # submitted, shortlisted, hired, rejected
    submitted_at: datetime
    milestones: List[Dict[str, Any]]


class UpworkAPIClient:
    """
    Upwork API Client (OAuth 2.0)
    Docs: https://developers.upwork.com/
    
    Required OAuth flow:
    1. Get client_id and client_secret from Upwork Developer Console
    2. User authorizes app, get authorization code
    3. Exchange code for access_token and refresh_token
    4. Use access_token for API calls
    """
    
    BASE_URL = "https://www.upwork.com/api"
    AUTH_URL = "https://www.upwork.com/ab/account-security/oauth2/authorize"
    TOKEN_URL = "https://www.upwork.com/api/v3/oauth2/token"
    
    def __init__(self):
        self.client_id = os.getenv("UPWORK_CLIENT_ID")
        self.client_secret = os.getenv("UPWORK_CLIENT_SECRET")
        self.access_token = os.getenv("UPWORK_ACCESS_TOKEN")
        self.refresh_token = os.getenv("UPWORK_REFRESH_TOKEN")
        self.session = requests.Session()
        
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}",
                "User-Agent": "AI-Earning-Platform/1.0"
            })
    
    def is_authenticated(self) -> bool:
        """Check if API client has valid credentials"""
        return bool(self.access_token and self.client_id)
    
    def get_authorization_url(self, redirect_uri: str, state: str = "") -> str:
        """Generate OAuth authorization URL for user to approve access"""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": "read write"
        }
        from urllib.parse import urlencode
        return f"{self.AUTH_URL}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            auth = (self.client_id, self.client_secret)
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri
            }
            
            response = self.session.post(self.TOKEN_URL, auth=auth, data=data, timeout=30)
            response.raise_for_status()
            tokens = response.json()
            
            # Update tokens
            self.access_token = tokens.get("access_token")
            self.refresh_token = tokens.get("refresh_token")
            
            # Update session headers
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
            
            logger.info("✅ Upwork OAuth tokens obtained successfully")
            return tokens
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Upwork OAuth error: {e}")
            return {"error": str(e)}
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh expired access token"""
        try:
            auth = (self.client_id, self.client_secret)
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
            
            response = self.session.post(self.TOKEN_URL, auth=auth, data=data, timeout=30)
            response.raise_for_status()
            tokens = response.json()
            
            self.access_token = tokens.get("access_token")
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
            
            return tokens
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Upwork token refresh error: {e}")
            return {"error": str(e)}
    
    def search_jobs(self, query: str = "python", skills: List[str] = None, 
                   budget_min: float = None, category: str = "Web, Mobile & Software Dev",
                   page: int = 0, per_page: int = 10) -> List[FreelanceJob]:
        """
        Search for jobs on Upwork
        
        API Endpoint: GET /api/profiles/v2/search/jobs
        """
        if not self.is_authenticated():
            logger.error("Upwork API not authenticated. Complete OAuth flow first.")
            return []
        
        try:
            url = f"{self.BASE_URL}/profiles/v2/search/jobs"
            
            params = {
                "q": query,
                "category": category,
                "page": page,
                "per_page": per_page
            }
            
            if skills:
                params["skills"] = ",".join(skills)
            if budget_min:
                params["budget_min"] = budget_min
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 401:
                # Token expired, try to refresh
                self.refresh_access_token()
                response = self.session.get(url, params=params, timeout=30)
            
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job_data in data.get("jobs", []):
                budget = job_data.get("budget", {})
                client = job_data.get("client", {})
                
                job = FreelanceJob(
                    job_id=job_data.get("id"),
                    platform="upwork",
                    title=job_data.get("title", ""),
                    description=job_data.get("description", "")[:500] + "...",
                    budget_type=budget.get("type", "fixed"),
                    budget_min=budget.get("minimum", 0),
                    budget_max=budget.get("maximum", 0),
                    hourly_rate=None if budget.get("type") == "fixed" else budget.get("amount", 0),
                    skills_required=job_data.get("skills", []),
                    client_info={
                        "name": client.get("name", "Hidden"),
                        "rating": client.get("rating", 0),
                        "total_spent": client.get("total_spent", 0),
                        "country": client.get("country", "Unknown")
                    },
                    posted_at=datetime.fromtimestamp(job_data.get("posted_on", 0)),
                    proposals_count=job_data.get("proposals_count", 0),
                    status=job_data.get("status", "open"),
                    url=f"https://www.upwork.com/jobs/{job_data.get('id')}",
                    is_verified=client.get("payment_verified", False)
                )
                jobs.append(job)
            
            logger.info(f"✅ Found {len(jobs)} Upwork jobs for query: {query}")
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Upwork API error: {e}")
            return []
    
    def submit_proposal(self, job_id: str, cover_letter: str, 
                       proposed_rate: float, milestones: List[Dict] = None) -> Dict[str, Any]:
        """
        Submit a proposal to a job
        
        API Endpoint: POST /api/hr/v4/engagements/offers
        """
        if not self.is_authenticated():
            return {"error": "Not authenticated"}
        
        try:
            url = f"{self.BASE_URL}/hr/v4/engagements/offers"
            
            payload = {
                "job_id": job_id,
                "message": cover_letter,
                "rate": proposed_rate,
                "milestones": milestones or []
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ Proposal submitted to job {job_id}")
            
            return {
                "success": True,
                "proposal_id": result.get("offer_id"),
                "status": "submitted",
                "platform": "upwork"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Upwork proposal submission error: {e}")
            return {"error": str(e)}
    
    def get_my_earnings(self) -> Dict[str, Any]:
        """Get earnings summary from Upwork"""
        if not self.is_authenticated():
            return {"error": "Not authenticated"}
        
        try:
            url = f"{self.BASE_URL}/reports/v1/financial_accounts/earnings"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return {
                "platform": "upwork",
                "total_earnings": data.get("total_earnings", 0),
                "available_balance": data.get("available_balance", 0),
                "pending_balance": data.get("pending_balance", 0),
                "currency": "USD"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Upwork earnings fetch error: {e}")
            return {"error": str(e)}


class FiverrAPIClient:
    """
    Fiverr API Client
    Docs: https://developers.fiverr.com/
    
    Note: Fiverr has limited public API access.
    Sellers API allows managing gigs and orders.
    """
    
    BASE_URL = "https://www.fiverr.com/api/v1"
    
    def __init__(self):
        self.api_key = os.getenv("FIVERR_API_KEY")
        self.api_secret = os.getenv("FIVERR_API_SECRET")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "AI-Earning-Platform/1.0"
            })
    
    def is_authenticated(self) -> bool:
        return bool(self.api_key)
    
    def get_my_gigs(self) -> List[Dict[str, Any]]:
        """Get my Fiverr gigs (as a seller)"""
        if not self.is_authenticated():
            return []
        
        try:
            url = f"{self.BASE_URL}/sellers/gigs"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            gigs = []
            for gig in data.get("gigs", []):
                gigs.append({
                    "id": gig.get("id"),
                    "title": gig.get("title"),
                    "category": gig.get("category"),
                    "price": gig.get("price"),
                    "rating": gig.get("rating"),
                    "orders_in_queue": gig.get("orders_in_queue"),
                    "status": gig.get("status"),
                    "url": f"https://www.fiverr.com/gig/{gig.get('id')}"
                })
            
            return gigs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Fiverr API error: {e}")
            return []
    
    def get_orders(self, status: str = "active") -> List[Dict[str, Any]]:
        """Get orders (active, completed, etc.)"""
        if not self.is_authenticated():
            return []
        
        try:
            url = f"{self.BASE_URL}/sellers/orders"
            params = {"status": status}
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            orders = []
            for order in data.get("orders", []):
                orders.append({
                    "id": order.get("id"),
                    "gig_title": order.get("gig_title"),
                    "buyer_name": order.get("buyer_name"),
                    "amount": order.get("amount"),
                    "status": order.get("status"),
                    "due_date": order.get("due_date"),
                    "delivered_at": order.get("delivered_at")
                })
            
            return orders
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Fiverr orders fetch error: {e}")
            return []
    
    def search_buyer_requests(self, category: str = "programming-tech") -> List[Dict[str, Any]]:
        """
        Search buyer requests (seller responds to buyer needs)
        Note: Requires active seller account with good ratings
        """
        if not self.is_authenticated():
            return []
        
        try:
            url = f"{self.BASE_URL}/sellers/buyer_requests"
            params = {"category": category}
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            requests_list = []
            for req in data.get("requests", []):
                requests_list.append({
                    "id": req.get("id"),
                    "title": req.get("title"),
                    "description": req.get("description"),
                    "budget": req.get("budget"),
                    "duration": req.get("duration"),
                    "skills": req.get("skills", []),
                    "posted_at": req.get("posted_at"),
                    "responses_count": req.get("responses_count")
                })
            
            return requests_list
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Fiverr buyer requests error: {e}")
            return []


class ToptalAPIClient:
    """
    Toptal API Client
    
    Toptal is an exclusive network - requires application and vetting.
    Once accepted, you get access to high-quality clients.
    API access is more restricted than Upwork/Fiverr.
    """
    
    BASE_URL = "https://www.toptal.com/api/v1"
    
    def __init__(self):
        self.api_key = os.getenv("TOPTAL_API_KEY")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"ApiKey {self.api_key}",
                "User-Agent": "AI-Earning-Platform/1.0"
            })
    
    def is_authenticated(self) -> bool:
        return bool(self.api_key)
    
    def get_available_jobs(self) -> List[Dict[str, Any]]:
        """Get available jobs from Toptal (requires accepted talent status)"""
        if not self.is_authenticated():
            return []
        
        try:
            url = f"{self.BASE_URL}/talent/jobs"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            jobs = []
            for job in data.get("jobs", []):
                jobs.append({
                    "id": job.get("id"),
                    "title": job.get("title"),
                    "description": job.get("description", "")[:300],
                    "client_type": job.get("client_type"),  # startup, enterprise, etc.
                    "duration": job.get("duration"),
                    "commitment": job.get("commitment"),  # full-time, part-time
                    "rate_min": job.get("rate_min"),
                    "rate_max": job.get("rate_max"),
                    "currency": job.get("currency", "USD"),
                    "skills": job.get("skills", []),
                    "posted_at": job.get("posted_at"),
                    "is_remote": job.get("is_remote", True),
                    "timezone": job.get("timezone")
                })
            
            logger.info(f"✅ Found {len(jobs)} Toptal opportunities")
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Toptal API error: {e}")
            return []
    
    def get_my_assignments(self) -> List[Dict[str, Any]]:
        """Get current assignments from Toptal"""
        if not self.is_authenticated():
            return []
        
        try:
            url = f"{self.BASE_URL}/talent/assignments"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            assignments = []
            for assignment in data.get("assignments", []):
                assignments.append({
                    "id": assignment.get("id"),
                    "client_name": assignment.get("client_name"),
                    "role": assignment.get("role"),
                    "start_date": assignment.get("start_date"),
                    "end_date": assignment.get("end_date"),
                    "rate": assignment.get("rate"),
                    "currency": assignment.get("currency"),
                    "status": assignment.get("status"),
                    "weekly_hours": assignment.get("weekly_hours")
                })
            
            return assignments
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Toptal assignments fetch error: {e}")
            return []
    
    def submit_application(self, job_id: str, message: str) -> Dict[str, Any]:
        """Submit application to a Toptal job"""
        if not self.is_authenticated():
            return {"error": "Not authenticated"}
        
        try:
            url = f"{self.BASE_URL}/talent/jobs/{job_id}/apply"
            
            payload = {
                "message": message,
                "availability": "immediate"
            }
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            return {
                "success": True,
                "job_id": job_id,
                "status": "applied",
                "platform": "toptal"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Toptal application error: {e}")
            return {"error": str(e)}


class FreelanceAggregator:
    """
    Aggregates freelance opportunities from multiple platforms
    Finds the best coding jobs across Upwork, Fiverr, and Toptal
    """
    
    def __init__(self):
        self.upwork = UpworkAPIClient()
        self.fiverr = FiverrAPIClient()
        self.toptal = ToptalAPIClient()
        
        # Track applications and earnings
        self.proposals_submitted: List[FreelanceProposal] = []
        self.total_earned = 0.0
    
    def get_all_platforms_status(self) -> Dict[str, Any]:
        """Get authentication status for all platforms"""
        return {
            "upwork": {
                "authenticated": self.upwork.is_authenticated(),
                "setup_required": not self.upwork.is_authenticated(),
                "setup_url": "https://developers.upwork.com/" if not self.upwork.is_authenticated() else None
            },
            "fiverr": {
                "authenticated": self.fiverr.is_authenticated(),
                "setup_required": not self.fiverr.is_authenticated(),
                "setup_url": "https://developers.fiverr.com/" if not self.fiverr.is_authenticated() else None
            },
            "toptal": {
                "authenticated": self.toptal.is_authenticated(),
                "setup_required": not self.toptal.is_authenticated(),
                "note": "Toptal requires application/vetting process"
            }
        }
    
    def search_all_jobs(self, query: str = "python", skills: List[str] = None,
                       min_budget: float = 100) -> Dict[str, List[FreelanceJob]]:
        """Search for jobs across all authenticated platforms"""
        results = {
            "upwork": [],
            "fiverr": [],
            "toptal": [],
            "errors": []
        }
        
        # Search Upwork
        if self.upwork.is_authenticated():
            try:
                upwork_jobs = self.upwork.search_jobs(
                    query=query,
                    skills=skills,
                    budget_min=min_budget
                )
                results["upwork"] = upwork_jobs
            except Exception as e:
                results["errors"].append(f"Upwork: {e}")
        
        # Search Fiverr (buyer requests)
        if self.fiverr.is_authenticated():
            try:
                fiverr_requests = self.fiverr.search_buyer_requests(category="programming-tech")
                # Convert to FreelanceJob format
                for req in fiverr_requests:
                    results["fiverr"].append(FreelanceJob(
                        job_id=req["id"],
                        platform="fiverr",
                        title=req["title"],
                        description=req["description"],
                        budget_type="fixed",
                        budget_min=req.get("budget", {}).get("min", 0),
                        budget_max=req.get("budget", {}).get("max", 0),
                        hourly_rate=None,
                        skills_required=req.get("skills", []),
                        client_info={"type": "fiverr_buyer"},
                        posted_at=datetime.fromisoformat(req.get("posted_at", datetime.now().isoformat())),
                        proposals_count=req.get("responses_count", 0),
                        status="open",
                        url=f"https://www.fiverr.com/buyer_request/{req['id']}",
                        is_verified=True
                    ))
            except Exception as e:
                results["errors"].append(f"Fiverr: {e}")
        
        # Search Toptal
        if self.toptal.is_authenticated():
            try:
                toptal_jobs = self.toptal.get_available_jobs()
                # Convert to FreelanceJob format
                for job in toptal_jobs:
                    results["toptal"].append(FreelanceJob(
                        job_id=job["id"],
                        platform="toptal",
                        title=job["title"],
                        description=job["description"],
                        budget_type="hourly",
                        budget_min=job.get("rate_min", 0),
                        budget_max=job.get("rate_max", 0),
                        hourly_rate=(job.get("rate_min", 0) + job.get("rate_max", 0)) / 2,
                        skills_required=job.get("skills", []),
                        client_info={"type": job.get("client_type", "unknown")},
                        posted_at=datetime.fromisoformat(job.get("posted_at", datetime.now().isoformat())),
                        proposals_count=0,  # Toptal doesn't show this
                        status="open",
                        url=f"https://www.toptal.com/platform/jobs/{job['id']}",
                        is_verified=True
                    ))
            except Exception as e:
                results["errors"].append(f"Toptal: {e}")
        
        return results
    
    def get_best_opportunities(self, min_budget: float = 500, 
                               required_skills: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get the best freelance opportunities across all platforms
        Sorted by budget and client quality
        """
        all_jobs = self.search_all_jobs(min_budget=min_budget)
        
        opportunities = []
        
        for platform, jobs in all_jobs.items():
            if platform == "errors":
                continue
                
            for job in jobs:
                # Calculate opportunity score
                score = 0
                
                # Budget score (higher is better)
                avg_budget = (job.budget_min + job.budget_max) / 2
                score += min(avg_budget / 100, 10)  # Cap at 10 points
                
                # Verified client bonus
                if job.is_verified:
                    score += 2
                
                # Competition factor (fewer proposals = better)
                if job.proposals_count < 10:
                    score += 3
                elif job.proposals_count < 20:
                    score += 1
                
                # Skill match bonus
                if required_skills:
                    matching = set(job.skills_required) & set(required_skills)
                    score += len(matching) * 2
                
                opportunities.append({
                    "job": job,
                    "score": score,
                    "platform": platform,
                    "estimated_value": avg_budget,
                    "competition_level": "low" if job.proposals_count < 10 else "medium" if job.proposals_count < 25 else "high"
                })
        
        # Sort by score (descending)
        opportunities.sort(key=lambda x: x["score"], reverse=True)
        
        return opportunities[:10]  # Top 10 opportunities
    
    def submit_proposal_to_best_matches(self, auto_submit: bool = False) -> List[Dict[str, Any]]:
        """
        Find and optionally submit proposals to best matching jobs
        """
        opportunities = self.get_best_opportunities()
        results = []
        
        for opp in opportunities[:3]:  # Top 3 matches
            job = opp["job"]
            
            if not auto_submit:
                # Just return opportunities for review
                results.append({
                    "action": "review",
                    "platform": job.platform,
                    "job_id": job.job_id,
                    "title": job.title,
                    "budget": f"${job.budget_min}-${job.budget_max}",
                    "score": opp["score"],
                    "url": job.url,
                    "message": "Review and approve to submit proposal"
                })
            else:
                # Auto-submit proposal
                cover_letter = self._generate_cover_letter(job)
                
                if job.platform == "upwork" and self.upwork.is_authenticated():
                    result = self.upwork.submit_proposal(
                        job_id=job.job_id,
                        cover_letter=cover_letter,
                        proposed_rate=job.budget_min
                    )
                    results.append(result)
                    
                elif job.platform == "toptal" and self.toptal.is_authenticated():
                    result = self.toptal.submit_application(
                        job_id=job.job_id,
                        message=cover_letter
                    )
                    results.append(result)
        
        return results
    
    def _generate_cover_letter(self, job: FreelanceJob) -> str:
        """Generate a cover letter based on job requirements"""
        skills_str = ", ".join(job.skills_required[:5])
        
        return f"""Hello,

I'm excited about your project: {job.title}

I have extensive experience with {skills_str} and have successfully delivered similar projects for {job.client_info.get('total_spent', 'various')} clients.

Key strengths I bring:
• Deep expertise in {job.skills_required[0] if job.skills_required else 'software development'}
• Proven track record of on-time delivery
• Clear communication throughout the project
• High-quality, maintainable code

I'm available to start immediately and can commit to the timeline you've outlined. I'd love to discuss your project in more detail.

Best regards,
AI Coding Agent"""
    
    def get_earnings_summary(self) -> Dict[str, Any]:
        """Get earnings summary from all platforms"""
        summary = {
            "total_earned": 0.0,
            "by_platform": {},
            "pending": 0.0,
            "available": 0.0
        }
        
        # Upwork earnings
        if self.upwork.is_authenticated():
            upwork_earnings = self.upwork.get_my_earnings()
            if "error" not in upwork_earnings:
                summary["by_platform"]["upwork"] = upwork_earnings
                summary["total_earned"] += upwork_earnings.get("total_earnings", 0)
                summary["available"] += upwork_earnings.get("available_balance", 0)
                summary["pending"] += upwork_earnings.get("pending_balance", 0)
        
        # Fiverr earnings would require separate balance API
        # Toptal earnings would require assignments API
        
        return summary


# Global instance
_freelance_aggregator: Optional[FreelanceAggregator] = None

def get_freelance_aggregator() -> FreelanceAggregator:
    """Get or create freelance aggregator"""
    global _freelance_aggregator
    if _freelance_aggregator is None:
        _freelance_aggregator = FreelanceAggregator()
    return _freelance_aggregator


if __name__ == "__main__":
    # Test the real freelance API integration
    print("=" * 70)
    print("REAL FREELANCE API INTEGRATION TEST")
    print("=" * 70)
    
    aggregator = FreelanceAggregator()
    
    # Check platform status
    print("\n1. Platform Authentication Status")
    status = aggregator.get_all_platforms_status()
    for platform, info in status.items():
        auth = "✅" if info["authenticated"] else "❌"
        print(f"   {auth} {platform.upper()}: {'Authenticated' if info['authenticated'] else 'Not configured'}")
        if info.get("setup_required"):
            print(f"      Setup URL: {info.get('setup_url', 'See documentation')}")
    
    print("\n2. Setup Instructions")
    print("""
To use real freelance APIs, you need API credentials:

UPWORK:
1. Create app at https://developers.upwork.com/
2. Complete OAuth flow to get access_token
3. Set environment variables:
   export UPWORK_CLIENT_ID='your_client_id'
   export UPWORK_CLIENT_SECRET='your_secret'
   export UPWORK_ACCESS_TOKEN='your_token'

FIVERR:
1. Request API access at https://developers.fiverr.com/
2. Set environment variable:
   export FIVERR_API_KEY='your_api_key'

TOPTAL:
1. Apply as talent at https://www.toptal.com/
2. Once accepted, request API access
3. Set environment variable:
   export TOPTAL_API_KEY='your_api_key'

Note: These are real platforms that require:
- Real identity verification
- Professional profiles
- Application/approval processes
- Compliance with platform TOS
    """)
    
    print("=" * 70)
