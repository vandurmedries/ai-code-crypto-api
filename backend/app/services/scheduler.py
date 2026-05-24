from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.database import SessionLocal
from app.services.ml_engine import MLEngineService
from app.services.affiliate_engine import get_affiliate_engine
from app.services.system_monitor import get_system_monitor, ErrorSeverity
from app import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
_monitor = get_system_monitor()


def affiliate_earn_job():
    """Autonomous affiliate earning job"""
    db = SessionLocal()
    try:
        engine = get_affiliate_engine()
        
        # Get all campaigns and simulate daily earnings
        campaigns = engine.get_all_campaigns()
        total_daily = 0.0
        
        for campaign_data in campaigns:
            if campaign_data:
                daily = engine.simulate_daily_earnings(campaign_data['campaign_id'])
                total_daily += daily
        
        if total_daily > 0:
            logger.info(f"Affiliate auto-earned: ${total_daily:.2f} from {len(campaigns)} campaigns")
        
    except Exception as e:
        logger.error(f"Error in affiliate_earn_job: {e}")
        _monitor.report_error("affiliate_scheduler", e, ErrorSeverity.MEDIUM)
    finally:
        db.close()


def auto_earn_job():
    """Background job to automatically generate earnings for all users"""
    db = SessionLocal()
    try:
        ml_service = MLEngineService(db)
        
        # Get all active users
        users = db.query(models.User).filter(models.User.is_active == True).all()
        
        total_earnings = 0
        total_amount = 0.0
        
        for user in users:
            try:
                earning = ml_service.auto_earn(user.id)
                if earning:
                    total_earnings += 1
                    total_amount += earning.amount
                    logger.info(f"Auto-earned {earning.amount} for user {user.id}")
            except Exception as e:
                logger.error(f"Error auto-earning for user {user.id}: {e}")
        
        logger.info(f"Auto-earn job completed: {total_earnings} earnings, ${total_amount:.2f} total")
        
    except Exception as e:
        logger.error(f"Error in auto_earn_job: {e}")
    finally:
        db.close()


def market_analysis_job():
    """Background job to periodically analyze market data"""
    db = SessionLocal()
    try:
        ml_service = MLEngineService(db)
        
        # Analyze market trends
        trends = ml_service.analyze_market_trends()
        
        # Store analysis results
        logger.info(f"Market analysis completed: {len(trends)} trends identified")
        
        for trend in trends[:3]:
            logger.info(f"  - {trend['type']}: {trend['strength']:.2f} strength, {trend['direction']}")
            
    except Exception as e:
        logger.error(f"Error in market_analysis_job: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler"""
    # Auto-earn job - runs every 30 seconds for active earning
    scheduler.add_job(
        auto_earn_job,
        trigger=IntervalTrigger(seconds=30),
        id="auto_earn",
        name="Auto Earn Job",
        replace_existing=True
    )
    
    # Affiliate earning job - runs every 5 minutes
    scheduler.add_job(
        affiliate_earn_job,
        trigger=IntervalTrigger(minutes=5),
        id="affiliate_earn",
        name="Affiliate Earn Job",
        replace_existing=True
    )
    
    # Market analysis job - runs every 15 minutes
    scheduler.add_job(
        market_analysis_job,
        trigger=IntervalTrigger(minutes=15),
        id="market_analysis",
        name="Market Analysis Job",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started with auto-earn, affiliate, and market analysis jobs")
    
    # Register with system monitor
    _monitor.register_component(
        "scheduler",
        lambda: scheduler.running,
        lambda: restart_scheduler() if not scheduler.running else None
    )


def restart_scheduler():
    """Restart the scheduler if it fails"""
    try:
        if scheduler.running:
            scheduler.shutdown()
        start_scheduler()
        logger.info("Scheduler restarted successfully")
    except Exception as e:
        logger.error(f"Failed to restart scheduler: {e}")


def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")
