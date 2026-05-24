#!/usr/bin/env python3
"""
24/7 AUTONOMOUS EARNING RUNNER
Keeps the system running forever, monitors, heals, and earns continuously
"""

import os
import sys
import time
import json
import logging
import subprocess
import requests
from datetime import datetime
from typing import Dict, Any, Optional
import signal
import threading

# Configuration
BASE_URL = "http://localhost:8000"
SYSTEM_EMAIL = "system@autonomous.ai"
SYSTEM_PASSWORD = "auto"
LOG_FILE = "/tmp/autonomous_earning.log"
STATUS_FILE = "/tmp/empire_status.json"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('AutonomousRunner')

class AutonomousEarningSystem:
    """24/7 Autonomous earning system manager"""
    
    def __init__(self):
        self.token = None
        self.running = True
        self.earnings_total = 0.0
        self.last_status = None
        self.error_count = 0
        
    def authenticate(self) -> bool:
        """Login to get token"""
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                data={"username": SYSTEM_EMAIL, "password": SYSTEM_PASSWORD},
                timeout=10
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                logger.info("✅ Authenticated successfully")
                return True
            else:
                logger.error(f"Auth failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Auth error: {e}")
            return False
    
    def check_health(self) -> bool:
        """Check if backend is running"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_backend(self):
        """Start the backend if not running"""
        logger.info("🔄 Starting backend...")
        try:
            subprocess.Popen(
                ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
                cwd="/Users/arianeheylen/CascadeProjects/ai-earning-platform/backend",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(5)  # Wait for startup
            logger.info("✅ Backend started")
        except Exception as e:
            logger.error(f"Failed to start backend: {e}")
    
    def trigger_earnings(self):
        """Trigger multiple earning mechanisms"""
        if not self.token:
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 1. ML Auto-earn
        try:
            response = requests.post(
                f"{BASE_URL}/api/ml/trigger-auto-earn",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("earning"):
                    amount = data["earning"]["amount"]
                    self.earnings_total += amount
                    logger.info(f"💰 ML Earning: ${amount:.2f}")
        except Exception as e:
            logger.warning(f"ML earn failed: {e}")
        
        # 2. Affiliate earnings
        try:
            response = requests.post(
                f"{BASE_URL}/api/empire/simulate-day",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                daily = data.get("daily_earnings", 0)
                self.earnings_total += daily
                logger.info(f"💰 Affiliate Daily: ${daily:.2f}")
        except Exception as e:
            logger.warning(f"Affiliate earn failed: {e}")
    
    def get_empire_status(self) -> Dict[str, Any]:
        """Get full empire status"""
        if not self.token:
            return {}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/empire/empire-status",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Status check failed: {e}")
        
        return {}
    
    def save_status(self):
        """Save current status to file"""
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "earnings_session": self.earnings_total,
            "empire": self.last_status,
            "running": self.running
        }
        
        try:
            with open(STATUS_FILE, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save status: {e}")
    
    def print_dashboard(self):
        """Print status dashboard"""
        print("\n" + "="*60)
        print("🤖 AUTONOMOUS EARNING SYSTEM - DASHBOARD")
        print("="*60)
        print(f"⏰ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💰 Session Earnings: ${self.earnings_total:.2f}")
        
        if self.last_status:
            earnings = self.last_status.get("earnings", {})
            sites = self.last_status.get("sites", {})
            print(f"💵 Total Empire Earnings: ${earnings.get('total', 0):.2f}")
            print(f"📈 Monthly Estimate: ${earnings.get('monthly_estimate', 0):.2f}")
            print(f"🌐 Active Sites: {sites.get('total', 0)}")
        
        print(f"✅ Status: RUNNING" if self.running else "❌ Status: STOPPED")
        print("="*60 + "\n")
    
    def run_forever(self):
        """Main loop - runs forever"""
        logger.info("🚀 Starting 24/7 Autonomous Earning System...")
        
        # Initial setup
        if not self.check_health():
            self.start_backend()
        
        # Authenticate
        retries = 0
        while not self.authenticate() and retries < 5:
            logger.warning("Retrying authentication...")
            time.sleep(2)
            retries += 1
        
        if not self.token:
            logger.error("❌ Failed to authenticate. Exiting.")
            return
        
        logger.info("✅ System ready. Entering earning loop...")
        
        last_earn = 0
        last_status = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Trigger earnings every 30 seconds
                if current_time - last_earn >= 30:
                    self.trigger_earnings()
                    last_earn = current_time
                
                # Update status every 2 minutes
                if current_time - last_status >= 120:
                    self.last_status = self.get_empire_status()
                    self.save_status()
                    self.print_dashboard()
                    last_status = current_time
                
                # Small sleep to prevent CPU hogging
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("👋 Shutdown requested by user")
                self.running = False
            except Exception as e:
                logger.error(f"Loop error: {e}")
                self.error_count += 1
                
                # If too many errors, restart backend
                if self.error_count > 10:
                    logger.error("Too many errors, restarting backend...")
                    self.start_backend()
                    self.error_count = 0
                    time.sleep(10)
        
        logger.info("🏁 System stopped")
        self.save_status()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the system
    system = AutonomousEarningSystem()
    system.run_forever()
