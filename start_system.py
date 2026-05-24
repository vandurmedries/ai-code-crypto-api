#!/usr/bin/env python3
"""
AI Earning Platform - Autonomous System Starter
Starts everything automatically without manual intervention
"""

import subprocess
import time
import sys
import os
import requests
import signal

BASE = "http://localhost:8000"

def kill_existing():
    """Kill any existing processes"""
    print("🧹 Cleaning up old processes...")
    subprocess.run(["killall", "-9", "python3"], capture_output=True)
    subprocess.run(["killall", "-9", "node"], capture_output=True)
    time.sleep(2)

def start_backend():
    """Start the backend"""
    print("🚀 Starting backend...")
    backend_dir = "/Users/arianeheylen/CascadeProjects/ai-earning-platform/backend"
    
    # Reset database
    os.chdir(backend_dir)
    for f in os.listdir("."):
        if f.endswith(".db"):
            os.remove(f)
    
    # Start backend
    activate = os.path.join(backend_dir, "venv/bin/activate")
    cmd = f"source {activate} && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &"
    subprocess.run(cmd, shell=True, executable="/bin/bash")
    
    # Wait for startup
    print("⏳ Waiting for backend...")
    for i in range(10):
        try:
            r = requests.get(f"{BASE}/health", timeout=2)
            if r.status_code == 200:
                print("✅ Backend running!")
                return True
        except:
            pass
        time.sleep(1)
    return False

def setup_auto_user():
    """Create and setup auto user"""
    print("👤 Setting up auto user...")
    
    # Register
    try:
        requests.post(f"{BASE}/api/auth/register", json={
            "email": "auto@earning.ai",
            "password": "auto123",
            "full_name": "Auto User"
        }, timeout=5)
    except:
        pass
    
    # Login
    r = requests.post(f"{BASE}/api/auth/login", data={
        "username": "auto@earning.ai",
        "password": "auto123"
    }, timeout=5)
    
    if r.status_code == 200:
        token = r.json()["access_token"]
        
        # Setup A2A agent
        requests.post(f"{BASE}/api/a2a/agents/register", 
            params={"agent_type": "earner", "capabilities": "market_analysis,earning_generation"},
            headers={"Authorization": f"Bearer {token}"}, timeout=5)
        
        # Create wallet
        requests.post(f"{BASE}/api/wallets/create",
            params={"currency": "BTC", "network": "mainnet"},
            headers={"Authorization": f"Bearer {token}"}, timeout=5)
        
        # Share initial context via MCP
        requests.post(f"{BASE}/api/mcp/context/create",
            params={"context_type": "market_data", "priority": "8"},
            json={"message": "System started", "timestamp": time.time()},
            headers={"Authorization": f"Bearer {token}"}, timeout=5)
        
        print("✅ User, agent, wallet and MCP context ready!")
        return token
    return None

def start_frontend():
    """Start frontend"""
    print("🎨 Starting frontend...")
    frontend_dir = "/Users/arianeheylen/CascadeProjects/ai-earning-platform/frontend"
    os.chdir(frontend_dir)
    
    # Build if needed
    if not os.path.exists("build"):
        print("📦 Building frontend...")
        subprocess.run("npm run build", shell=True, capture_output=True)
    
    # Serve
    cmd = f"cd {frontend_dir}/build && python3 -m http.server 8080 > /dev/null 2>&1 &"
    subprocess.run(cmd, shell=True)
    
    time.sleep(3)
    print("✅ Frontend on http://localhost:8080")

def auto_earn_loop(token):
    """Continuous auto-earning loop"""
    print("💰 Starting autonomous earning...")
    print("   (Press Ctrl+C to stop)")
    print("")
    
    total_earned = 0
    cycle = 0
    
    try:
        while True:
            cycle += 1
            
            # Trigger auto-earn
            r = requests.post(f"{BASE}/api/ml/trigger-auto-earn",
                headers={"Authorization": f"Bearer {token}"}, timeout=10)
            
            result = r.json()
            if result.get("success"):
                amt = result["earning"]["amount"]
                total_earned += amt
                print(f"💵 Cycle {cycle}: Earned ${amt:.2f} | Total: ${total_earned:.2f}")
            else:
                print(f"⏳ Cycle {cycle}: No high-confidence opportunity")
            
            # Every 5 cycles, broadcast via A2A
            if cycle % 5 == 0:
                requests.post(f"{BASE}/api/a2a/agents/user_auto_earning.ai_earner_0/broadcast",
                    json={"opportunity_id": f"auto_{cycle}", "potential_earning": 10.0},
                    headers={"Authorization": f"Bearer {token}"}, timeout=5)
                print("📡 A2A broadcast sent")
            
            # Every 3 cycles, share via MCP
            if cycle % 3 == 0:
                requests.post(f"{BASE}/api/mcp/context/earning",
                    json={"opportunity": {"type": "auto", "cycle": cycle}, "confidence": 0.5},
                    headers={"Authorization": f"Bearer {token}"}, timeout=5)
                print("🔄 MCP context shared")
            
            time.sleep(10)  # Wait 10 seconds between cycles
            
    except KeyboardInterrupt:
        print(f"\n\n🏁 Stopped. Total earned: ${total_earned:.2f}")

def main():
    print("=" * 60)
    print("AI EARNING PLATFORM - AUTONOMOUS STARTER")
    print("=" * 60)
    print()
    
    kill_existing()
    
    if not start_backend():
        print("❌ Failed to start backend")
        sys.exit(1)
    
    token = setup_auto_user()
    if not token:
        print("❌ Failed to setup user")
        sys.exit(1)
    
    start_frontend()
    
    print()
    print("=" * 60)
    print("SYSTEM READY - STARTING AUTONOMOUS EARNING")
    print("=" * 60)
    print()
    print("URLs:")
    print("  📊 Dashboard: http://localhost:8080")
    print("  🔧 API Docs:  http://localhost:8000/docs")
    print("  💰 Backend:   http://localhost:8000")
    print()
    
    auto_earn_loop(token)

if __name__ == "__main__":
    main()
