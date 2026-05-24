#!/bin/bash
# ONE-COMMAND AUTONOMOUS EARNING STARTER
# This script does EVERYTHING automatically

echo "🚀 Starting Full Autonomous Setup..."

# Step 1: Install dependencies
echo "📦 Installing dependencies..."
cd /Users/arianeheylen/CascadeProjects/ai-earning-platform/backend
source venv/bin/activate
pip install playwright -q
playwright install chromium

# Step 2: Start backend
echo "🔧 Starting backend server..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
sleep 5

# Step 3: Run autonomous setup
echo "🤖 Running autonomous platform setup..."
curl -X POST http://localhost:8000/api/setup/setup-all \
  -H "Authorization: Bearer $(curl -s -X POST http://localhost:8000/api/auth/login -d 'username=system@autonomous.ai&password=auto' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)" \
  > /tmp/setup_result.json 2>&1

# Step 4: Start browser automation
echo "🌐 Starting browser automation..."
cd /Users/arianeheylen/CascadeProjects/ai-earning-platform
python3 autonomous_browser_setup.py

echo "✅ Setup complete! Check browser windows."
