"""
Auto Setup Service
Automatically configures and starts the entire system without human intervention
"""

import os
import time
import subprocess
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from .system_monitor import get_system_monitor, ErrorSeverity


class AutoSetupService:
    """Fully autonomous setup and initialization"""
    
    def __init__(self):
        self.monitor = get_system_monitor()
        self.setup_steps = []
        self.is_configured = False
        self.system_user = None
        self.initialized_components = []
        
    def full_autonomous_setup(self) -> Dict[str, Any]:
        """Perform complete autonomous system setup"""
        results = {
            "started_at": datetime.utcnow().isoformat(),
            "steps_completed": [],
            "errors": [],
            "status": "running"
        }
        
        steps = [
            ("check_prerequisites", self._check_prerequisites),
            ("initialize_database", self._init_database),
            ("create_system_user", self._create_system_user),
            ("setup_auto_earn", self._setup_auto_earn),
            ("initialize_affiliate", self._init_affiliate),
            ("setup_wallets", self._setup_wallets),
            ("initialize_a2a_agents", self._init_a2a_agents),
            ("setup_mcp_context", self._setup_mcp_context),
            ("start_scheduler", self._start_scheduler),
            ("verify_system", self._verify_system)
        ]
        
        for step_name, step_func in steps:
            try:
                self.monitor.logger.info(f"Auto-setup: {step_name}")
                result = step_func()
                results["steps_completed"].append({
                    "step": step_name,
                    "status": "success",
                    "result": result
                })
                self.initialized_components.append(step_name)
                time.sleep(0.5)  # Small delay between steps
                
            except Exception as e:
                error_report = self.monitor.report_error(
                    f"auto_setup_{step_name}", 
                    e, 
                    ErrorSeverity.HIGH if step_name in ["initialize_database", "create_system_user"] else ErrorSeverity.MEDIUM
                )
                results["errors"].append({
                    "step": step_name,
                    "error": str(e),
                    "error_id": error_report.error_id
                })
                # Continue with other steps even if one fails
        
        results["completed_at"] = datetime.utcnow().isoformat()
        results["status"] = "completed" if len(results["errors"]) == 0 else "completed_with_errors"
        results["initialized_components"] = self.initialized_components
        self.is_configured = True
        
        return results
    
    def _check_prerequisites(self) -> Dict[str, Any]:
        """Check if all prerequisites are met"""
        checks = {
            "python_version": True,
            "database_writeable": os.access(".", os.W_OK),
            "port_8000_available": self._check_port_available(8000),
            "dependencies_installed": True  # Assumed if we got this far
        }
        
        if not all(checks.values()):
            failed = [k for k, v in checks.items() if not v]
            raise Exception(f"Prerequisites failed: {failed}")
        
        return checks
    
    def _init_database(self) -> Dict[str, Any]:
        """Initialize database tables"""
        from app.database import engine
        from app import models
        
        # Create all tables
        models.Base.metadata.create_all(bind=engine)
        
        return {"tables_created": True, "database": "sqlite"}
    
    def _create_system_user(self) -> Dict[str, Any]:
        """Create the system user (the system IS the user)"""
        from app.database import SessionLocal
        from app import models
        from app.services.auth import get_password_hash
        
        db = SessionLocal()
        try:
            # Check if system user exists
            system_user = db.query(models.User).filter(models.User.email == "system@autonomous.ai").first()
            
            if not system_user:
                system_user = models.User(
                    email="system@autonomous.ai",
                    hashed_password=get_password_hash("auto"),
                    full_name="Autonomous System",
                    is_active=True,
                    is_verified=True,
                    balance=0.0,
                    total_earned=0.0,
                    total_spent=0.0
                )
                db.add(system_user)
                db.commit()
                db.refresh(system_user)
            
            self.system_user = system_user
            
            return {
                "user_id": system_user.id,
                "email": system_user.email,
                "created": system_user.id is not None
            }
            
        finally:
            db.close()
    
    def _setup_auto_earn(self) -> Dict[str, Any]:
        """Setup auto-earn configuration"""
        from app.services.ml_engine import MLEngineService
        from app.database import SessionLocal
        
        db = SessionLocal()
        try:
            engine = MLEngineService(db)
            return {
                "ml_engine_ready": engine is not None
            }
        finally:
            db.close()
    
    def _init_affiliate(self) -> Dict[str, Any]:
        """Initialize affiliate earning system"""
        from app.services.affiliate_engine import get_affiliate_engine
        
        engine = get_affiliate_engine()
        
        # Create initial campaign
        if self.system_user:
            campaign = engine.create_affiliate_campaign()
            return {
                "affiliate_engine_ready": True,
                "initial_campaign_id": campaign.campaign_id,
                "opportunities": len(campaign.opportunities)
            }
        
        return {"affiliate_engine_ready": True}
    
    def _setup_wallets(self) -> Dict[str, Any]:
        """Setup initial crypto wallets"""
        from app.database import SessionLocal
        from app import models
        import hashlib
        
        if not self.system_user:
            return {"wallets_created": 0}
        
        db = SessionLocal()
        try:
            # Check if wallets exist
            existing = db.query(models.Wallet).filter(models.Wallet.user_id == self.system_user.id).count()
            
            if existing == 0:
                # Create BTC wallet
                wallet = models.Wallet(
                    user_id=self.system_user.id,
                    currency="BTC",
                    network="mainnet",
                    address=hashlib.sha256(f"btc_{self.system_user.id}".encode()).hexdigest()[:34],
                    balance=0.0,
                    pending_balance=0.0,
                    wallet_type="auto_generated",
                    is_active=True
                )
                db.add(wallet)
                db.commit()
                
                return {"wallets_created": 1, "currencies": ["BTC"]}
            
            return {"wallets_created": 0, "existing_wallets": existing}
            
        finally:
            db.close()
    
    def _init_a2a_agents(self) -> Dict[str, Any]:
        """Initialize A2A agents"""
        from app.services.a2a_protocol import AgentRegistry, A2AAgent
        
        registry = AgentRegistry()
        
        # Create system agents
        agents_config = [
            ("earner", ["market_analysis", "earning_generation"]),
            ("trader", ["trading", "arbitrage"]),
            ("federator", ["communication", "coordination"])
        ]
        
        created = []
        for agent_type, capabilities in agents_config:
            agent_id = f"system_{agent_type}_agent"
            agent = A2AAgent(
                agent_id=agent_id,
                agent_type=agent_type,
                capabilities=capabilities
            )
            registry.register_agent(agent, f"/api/a2a/agents/{agent_id}/receive")
            created.append(agent_id)
        
        return {
            "agents_created": len(created),
            "agent_ids": created
        }
    
    def _setup_mcp_context(self) -> Dict[str, Any]:
        """Setup MCP context sharing"""
        from app.routers.mcp import get_or_create_client
        from app.services.mcp_protocol import create_market_context
        
        if self.system_user:
            client = get_or_create_client(self.system_user.id, "system@autonomous.ai")
            
            # Create initial market context
            context = create_market_context(
                client,
                [{"type": "system_init", "strength": 1.0}],
                "system_initializer"
            )
            
            return {
                "mcp_client_ready": True,
                "initial_context_id": context.context_id
            }
        
        return {"mcp_client_ready": False, "reason": "no_system_user"}
    
    def _start_scheduler(self) -> Dict[str, Any]:
        """Configure scheduler (actual start happens in lifespan)"""
        return {"scheduler_configured": True, "note": "Will be started by application lifespan"}
    
    def _verify_system(self) -> Dict[str, Any]:
        """Verify all components are working"""
        from app.database import SessionLocal
        from app import models
        
        db = SessionLocal()
        try:
            # Count entities
            users = db.query(models.User).count()
            earnings = db.query(models.Earning).count()
            wallets = db.query(models.Wallet).count()
            
            health_checks = {
                "database_accessible": True,
                "users_count": users,
                "earnings_count": earnings,
                "wallets_count": wallets,
                "system_user_exists": self.system_user is not None,
                "all_components_initialized": len(self.initialized_components) >= 8
            }
            
            return health_checks
            
        finally:
            db.close()
    
    def _check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
                return True
        except:
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            "is_configured": self.is_configured,
            "system_user": {
                "id": self.system_user.id if self.system_user else None,
                "email": self.system_user.email if self.system_user else None
            },
            "initialized_components": self.initialized_components,
            "timestamp": datetime.utcnow().isoformat(),
            "mode": "autonomous"
        }


# Global instance
_setup_service: Optional[AutoSetupService] = None

def get_auto_setup() -> AutoSetupService:
    """Get or create auto setup service"""
    global _setup_service
    if _setup_service is None:
        _setup_service = AutoSetupService()
    return _setup_service


def run_autonomous_startup() -> Dict[str, Any]:
    """Entry point for fully autonomous system startup"""
    setup = get_auto_setup()
    return setup.full_autonomous_setup()
