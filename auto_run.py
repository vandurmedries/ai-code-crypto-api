#!/usr/bin/env python3
"""
AI Earning Platform - Autonomous Runner
This script starts the system and lets it run itself
"""

import requests
import time
import sys

BASE = 'http://localhost:8000'

def ensure_user():
    """Ensure demo user exists and return token"""
    email = 'auto@earning.ai'
    password = 'auto123'
    
    # Try to register (may fail if exists)
    try:
        requests.post(f'{BASE}/api/auth/register', 
            json={'email': email, 'password': password, 'full_name': 'Auto User'})
    except:
        pass
    
    # Login
    r = requests.post(f'{BASE}/api/auth/login', 
        data={'username': email, 'password': password})
    
    if r.status_code == 200:
        return r.json()['access_token']
    return None

def main():
    print("=" * 60)
    print("AI EARNING PLATFORM - AUTONOMOUS MODE")
    print("=" * 60)
    print()
    
    # Setup user
    print("Setting up auto-user...")
    token = ensure_user()
    if not token:
        print("ERROR: Could not login")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Check initial status
    r = requests.get(f'{BASE}/api/users/dashboard', headers=headers)
    data = r.json()
    print(f"Starting balance: ${data['balance']:.2f}")
    print(f"Total earned: ${data['total_earned']:.2f}")
    print()
    
    print("System is now running itself!")
    print("- Auto-earning every 30 seconds via scheduler")
    print("- Market analysis every 15 minutes")
    print("- No manual intervention needed")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Monitor mode
    try:
        while True:
            time.sleep(60)
            r = requests.get(f'{BASE}/api/users/dashboard', headers=headers)
            data = r.json()
            print(f"[{time.strftime('%H:%M:%S')}] Balance: ${data['balance']:.2f} | Earned: ${data['total_earned']:.2f}")
    except KeyboardInterrupt:
        print()
        print("\nStopped.")
        r = requests.get(f'{BASE}/api/users/dashboard', headers=headers)
        data = r.json()
        print(f"\nFINAL: Balance: ${data['balance']:.2f} | Total Earned: ${data['total_earned']:.2f}")

if __name__ == '__main__':
    main()
