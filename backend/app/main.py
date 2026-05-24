from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from datetime import datetime

from app.database import engine, Base, get_db
from app.routers import auth, users, earnings, purchases, ml_engine, wallets, a2a, mcp, ruflo, affiliate, affiliate_empire, autonomous_setup, belgian_business, coding_agency, a2a_discovery, self_earning, wallet_earning, crypto_recovery, prompt_marketplace, repo_adopter, rewards_aggregator, passive_income, real_coding_agency, public_api
from app.services.scheduler import start_scheduler, stop_scheduler
from app.services.auto_setup import run_autonomous_startup, get_auto_setup
from app.services.system_monitor import get_system_monitor


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Autonomous startup (includes scheduler start)
    print("🤖 Starting Autonomous AI Earning System...")
    setup_result = run_autonomous_startup()
    print(f"✅ Auto-setup completed: {len(setup_result['steps_completed'])} steps")
    
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="AI Earning Platform",
    description="Autonomous AI-powered earning and purchase platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Public API — allow all origins for RapidAPI/external consumers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(earnings.router, prefix="/api/earnings", tags=["earnings"])
app.include_router(purchases.router, prefix="/api/purchases", tags=["purchases"])
app.include_router(ml_engine.router, prefix="/api/ml", tags=["ml-engine"])
app.include_router(wallets.router, prefix="/api/wallets", tags=["wallets"])
app.include_router(a2a.router, prefix="/api/a2a", tags=["a2a-protocol"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["mcp-protocol"])
app.include_router(ruflo.router, prefix="/api/ruflo", tags=["ruflo"])
app.include_router(affiliate.router, prefix="/api/affiliate", tags=["affiliate"])
app.include_router(affiliate_empire.router, prefix="/api/empire", tags=["affiliate-empire"])
app.include_router(autonomous_setup.router, prefix="/api/setup", tags=["autonomous-setup"])
app.include_router(belgian_business.router, prefix="/api/belgian", tags=["belgian-business"])
app.include_router(coding_agency.router, prefix="/api/coding", tags=["coding-agency"])
app.include_router(a2a_discovery.router, prefix="/api/a2a-discovery", tags=["a2a-discovery"])
app.include_router(self_earning.router, prefix="/api/self-earn", tags=["self-earning"])
app.include_router(wallet_earning.router, prefix="/api/wallet-earning", tags=["wallet-earning"])
app.include_router(crypto_recovery.router, prefix="/api/crypto-recovery", tags=["crypto-recovery"])
app.include_router(prompt_marketplace.router, prefix="/api/prompts", tags=["prompt-marketplace"])
app.include_router(repo_adopter.router, prefix="/api/repo-adopter", tags=["repo-adopter"])
app.include_router(rewards_aggregator.router, prefix="/api/rewards", tags=["rewards-aggregator"])
app.include_router(passive_income.router, prefix="/api/passive-income", tags=["passive-income"])
app.include_router(real_coding_agency.router, prefix="/api/real-agency", tags=["real-coding-agency"])
app.include_router(public_api.router, prefix="/api/v1", tags=["public-api"])


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-earning-platform"}


@app.get("/system/status")
def system_status():
    """Get complete autonomous system status for cascade monitoring"""
    monitor = get_system_monitor()
    auto_setup = get_auto_setup()
    
    return {
        "auto_setup": auto_setup.get_system_status(),
        "monitor": monitor.get_dashboard_data(),
        "autonomous_mode": True,
        "system_is_user": True
    }


@app.get("/system/report")
def system_report():
    """Get formatted system report for cascade analysis"""
    monitor = get_system_monitor()
    report = monitor.generate_system_report()
    
    # Also print to console for immediate visibility
    print("\n" + report)
    
    return {
        "report": report,
        "timestamp": datetime.utcnow().isoformat(),
        "for_cascade_analysis": True
    }


@app.post("/system/heal")
def trigger_healing():
    """Manually trigger system healing"""
    monitor = get_system_monitor()
    monitor.auto_heal_enabled = True
    
    # Check all components
    component_status = monitor.check_all_components()
    
    return {
        "healing_triggered": True,
        "component_status": component_status,
        "auto_heal_enabled": True
    }
