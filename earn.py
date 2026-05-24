#!/usr/bin/env python3
import requests

BASE = 'http://localhost:8000'

def main():
    # Register first
    print("Registering...")
    r = requests.post(f'{BASE}/api/auth/register', 
        json={'email':'demo@local.ai','password':'demo123','full_name':'Demo User'})
    print(f"Register: {r.status_code}")
    
    # Login
    print("Logging in...")
    r = requests.post(f'{BASE}/api/auth/login', 
        data={'username':'demo@local.ai','password':'demo123'})
    print(f"Login: {r.status_code}")
    if r.status_code != 200:
        print(f"Error: {r.text}")
        return
    
    token = r.json()['access_token']
    print(f"Token: {token[:20]}...")
    headers = {'Authorization': f'Bearer {token}'}
    
    print("Triggering auto-earnings...")
    total = 0
    for i in range(5):
        r = requests.post(f'{BASE}/api/ml/trigger-auto-earn', headers=headers)
        d = r.json()
        if d.get('success'):
            amt = d['earning']['amount']
            total += amt
            print(f"  #{i+1}: +${amt:.2f}")
        else:
            print(f"  #{i+1}: {d.get('message', 'No opportunity')}")
    
    # Check status
    r = requests.get(f'{BASE}/api/users/dashboard', headers=headers)
    d = r.json()
    print(f"\n=== RESULTS ===")
    print(f"Balance:      ${d['balance']:.2f}")
    print(f"Total Earned: ${d['total_earned']:.2f}")
    print(f"Opportunities: {len(d['active_opportunities'])}")
    print(f"\nOpen http://localhost:3000 and click 'Auto Login'")

if __name__ == '__main__':
    main()
