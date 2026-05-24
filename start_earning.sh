#!/bin/bash
echo "=== AI Earning Platform - Starting Earnings ==="

# Register demo user
echo "Creating demo user..."
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@local.ai","password":"demo123","full_name":"Demo User"}' 2>/dev/null

# Login and get token
echo ""
echo "Logging in..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@local.ai&password=demo123" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")

echo "Token received: ${TOKEN:0:20}..."

# Trigger auto-earn multiple times
echo ""
echo "Triggering earnings..."
for i in 1 2 3; do
  echo "Attempt $i:"
  RESULT=$(curl -s -X POST http://localhost:8000/api/ml/trigger-auto-earn \
    -H "Authorization: Bearer $TOKEN" 2>/dev/null)
  echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"  Success: {d.get('success')}, Amount: {d.get('earning',{}).get('amount','N/A')}, New Balance: {d.get('new_balance','N/A')}\")" 2>/dev/null || echo "  $RESULT"
  sleep 1
done

# Check final status
echo ""
echo "=== Final Status ==="
curl -s http://localhost:8000/api/users/dashboard \
  -H "Authorization: Bearer $TOKEN" 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f\"Balance:       ${d.get('balance',0):.2f}\")
    print(f\"Total Earned:  ${d.get('total_earned',0):.2f}\")
    print(f\"Total Spent:   ${d.get('total_spent',0):.2f}\")
    print(f\"Opportunities: {len(d.get('active_opportunities',[]))}\")
except:
    print('Error parsing response')
"

echo ""
echo "=== Done ==="
echo "Open http://localhost:3000 and click 'Auto Login' to see your earnings!"
