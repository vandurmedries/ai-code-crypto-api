# Real API Integrations - AI Earning Platform

This document describes the three real API integrations implemented to enable actual earning and blockchain functionality.

---

## 1. Real Blockchain Wallet Integration

**File:** `backend/app/services/real_blockchain_wallet.py`

### Overview
Real-time blockchain balance tracking using:
- **BlockCypher API** for Bitcoin (BTC)
- **Etherscan API** for Ethereum (ETH)

### Features
- Real balance lookups from blockchain
- Transaction history fetching
- Wallet tracking for existing addresses
- Multi-currency support (BTC, ETH)

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/real-agency/wallet/add` | POST | Add real wallet to track |
| `/api/real-agency/wallet/{id}/refresh` | GET | Refresh balance from blockchain |
| `/api/real-agency/wallet/{id}/transactions` | GET | Get real transactions |
| `/api/real-agency/wallets/summary` | GET | All wallets summary |

### Setup

1. **Get BlockCypher API Token** (free tier: 200 requests/day)
   - Visit: https://www.blockcypher.com/
   - Sign up and get API token

2. **Get Etherscan API Key** (free tier: 5 calls/sec, 100k/day)
   - Visit: https://etherscan.io/apis
   - Create account and get API key

3. **Set Environment Variables:**
   ```bash
   export BLOCKCYPHER_API_TOKEN='your_token_here'
   export ETHERSCAN_API_KEY='your_key_here'
   ```

### Usage Example

```bash
# Add a real Bitcoin wallet
curl -X POST http://localhost:8000/api/real-agency/wallet/add \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "BTC",
    "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
  }'

# Refresh balance (queries blockchain)
curl http://localhost:8000/api/real-agency/wallet/user_1_BTC_1A1zP1eP/refresh \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 2. Real Freelance API Integration

**File:** `backend/app/services/real_freelance_apis.py`

### Overview
Real job search and proposal submission on:
- **Upwork** (via OAuth 2.0 API)
- **Fiverr** (via Seller API)
- **Toptal** (via Talent API)

### Features
- Search real job postings
- View client ratings and verification status
- Submit real proposals
- Track earnings across platforms
- Opportunity scoring algorithm

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/real-agency/platforms/status` | GET | Check platform auth status |
| `/api/real-agency/platforms/setup-guide` | POST | Get platform setup guide |
| `/api/real-agency/jobs/search` | GET | Search real jobs |
| `/api/real-agency/jobs/best-opportunities` | GET | Get scored opportunities |
| `/api/real-agency/proposals/submit` | POST | Submit proposal |
| `/api/real-agency/earnings/summary` | GET | Real earnings summary |

### Setup - Upwork

1. **Create Upwork Account**
   - Visit: https://www.upwork.com/
   - Complete freelancer profile

2. **Create Developer App**
   - Visit: https://developers.upwork.com/
   - Create new app
   - Get Client ID and Secret

3. **Complete OAuth Flow**
   - Get authorization URL: `/api/real-agency/platforms/setup-guide`
   - User authorizes app
   - Exchange code for access token

4. **Set Environment Variables:**
   ```bash
   export UPWORK_CLIENT_ID='your_client_id'
   export UPWORK_CLIENT_SECRET='your_secret'
   export UPWORK_ACCESS_TOKEN='your_token'
   export UPWORK_REFRESH_TOKEN='your_refresh_token'
   ```

### Setup - Fiverr

1. **Create Seller Account**
   - Visit: https://www.fiverr.com/
   - Switch to Seller mode
   - Create gigs

2. **Request API Access**
   - Contact: https://developers.fiverr.com/
   - Wait for approval (can take weeks)

3. **Set Environment Variable:**
   ```bash
   export FIVERR_API_KEY='your_api_key'
   ```

### Setup - Toptal

1. **Apply as Talent**
   - Visit: https://www.toptal.com/developers
   - Complete rigorous vetting process
   - Pass technical interview and test project

2. **Request API Access**
   - Contact support after acceptance

3. **Set Environment Variable:**
   ```bash
   export TOPTAL_API_KEY='your_api_key'
   ```

### Usage Example

```bash
# Check platform status
curl http://localhost:8000/api/real-agency/platforms/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Search for Python jobs
curl "http://localhost:8000/api/real-agency/jobs/search?query=python&min_budget=500" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get best opportunities
curl "http://localhost:8000/api/real-agency/jobs/best-opportunities?min_budget=1000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Submit proposal
curl -X POST http://localhost:8000/api/real-agency/proposals/submit \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "upwork_job_id_here",
    "platform": "upwork",
    "cover_letter": "I am experienced in Python and FastAPI...",
    "proposed_rate": 75
  }'
```

---

## 3. Google A2A Protocol Implementation

**File:** `backend/app/services/google_a2a_protocol.py`

### Overview
Full implementation of Google's Agent-to-Agent (A2A) protocol specification for AI agent communication.

### Features
- Agent discovery and registration
- Task submission and execution
- Skill matching and routing
- Real-time communication between agents
- Agent Card for capability advertisement

### A2A Protocol Methods

| Method | Description |
|--------|-------------|
| `agent/card` | Get agent capabilities |
| `skills/query` | Query available skills |
| `tasks/send` | Submit task to agent |
| `tasks/get` | Get task status |
| `tasks/cancel` | Cancel running task |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/real-agency/a2a` | POST | A2A protocol handler |
| `/api/real-agency/a2a/agent-card` | GET | Get agent capabilities |
| `/api/real-agency/a2a/discover` | GET | Discover other agents |
| `/api/real-agency/a2a/send-task` | POST | Send task to agent |

### Skills Available

1. **code_review** - Professional code analysis
2. **bug_fix** - Bug fixing and debugging
3. **feature_dev** - Full-stack feature development
4. **api_integration** - Third-party API integration

### Usage Example

```bash
# Get agent card (discovery)
curl http://localhost:8000/api/real-agency/a2a/agent-card

# Send A2A task
curl -X POST http://localhost:8000/api/real-agency/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tasks/send",
    "params": {
      "id": "task_123",
      "sessionId": "session_456",
      "message": {
        "role": "user",
        "parts": [
          {"type": "text", "text": "Review my Python function for API error handling"}
        ]
      }
    }
  }'

# Discover other agents
curl http://localhost:8000/api/real-agency/a2a/discover \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Send task to external agent
curl -X POST http://localhost:8000/api/real-agency/a2a/send-task \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_url": "https://other-agent.com/a2a",
    "message": "Please help me optimize this database query",
    "skill_hint": "code_review"
  }'
```

---

## 4. Combined Auto-Earn Cycle

**Endpoint:** `POST /api/real-agency/auto-earn-cycle`

This endpoint runs one complete autonomous earning cycle:
1. Searches real jobs across all platforms
2. Finds best opportunities using scoring algorithm
3. Checks real wallet balances
4. Returns actionable recommendations

```bash
curl -X POST http://localhost:8000/api/real-agency/auto-earn-cycle \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Complete Environment Setup

Create a `.env` file in `backend/` directory:

```bash
# Blockchain APIs
BLOCKCYPHER_API_TOKEN=your_blockcypher_token
ETHERSCAN_API_KEY=your_etherscan_key

# Upwork OAuth
UPWORK_CLIENT_ID=your_upwork_client_id
UPWORK_CLIENT_SECRET=your_upwork_secret
UPWORK_ACCESS_TOKEN=your_upwork_token
UPWORK_REFRESH_TOKEN=your_upwork_refresh

# Fiverr API
FIVERR_API_KEY=your_fiverr_key

# Toptal API
TOPTAL_API_KEY=your_toptal_key

# A2A Directory (optional)
A2A_DIRECTORY_URL=http://localhost:8000/a2a-directory

# App
API_BASE_URL=http://localhost:8000
```

---

## API Comparison: Simulated vs Real

| Feature | Simulated | Real |
|---------|-----------|------|
| Job Search | Fake opportunities | Real Upwork/Fiverr/Toptal |
| Proposals | Pretend submission | Actual proposal sent |
| Earnings | Fake numbers | Real API balance queries |
| Wallets | Fake addresses | Real BTC/ETH addresses |
| Transactions | Simulated | Real blockchain data |
| A2A | Local mock | Real protocol implementation |

---

## Notes on Real Usage

### Freelance Platforms
- **Upwork**: 10% fee, requires complete profile, first job typically 1-4 weeks
- **Fiverr**: 20% fee, easier to start, buyer requests available
- **Toptal**: No fee (built into rate), exclusive (top 3% only), highest rates ($60-250/hr)

### Blockchain
- BlockCypher free tier: 200 requests/day
- Etherscan free tier: 5 calls/sec, 100,000 calls/day
- For production, consider paid tiers or running your own nodes

### A2A Protocol
- This implements the full Google A2A specification
- Can communicate with any other A2A-compliant agent
- Skills are matched based on message content analysis

---

## Testing

Each module can be tested independently:

```bash
cd backend/app/services

# Test blockchain wallet
python real_blockchain_wallet.py

# Test freelance APIs
python real_freelance_apis.py

# Test A2A protocol
python google_a2a_protocol.py
```

---

## Next Steps

1. **Get API Keys** for at least one freelance platform
2. **Set up blockchain tracking** for your real crypto wallets
3. **Test the A2A protocol** with other A2A agents
4. **Run the auto-earn cycle** to get real recommendations
5. **Submit real proposals** to earn actual money

Remember: These are real APIs that interact with real platforms. Proposals you submit are real and may result in actual client contact and work obligations.

---

## 5. Selenium Automation (10 Use Cases)

**File:** `backend/app/services/selenium_automation.py`

### Overview
Complete Selenium WebDriver implementation with Chrome automation covering 10 core web automation patterns:

1. **Auto-Login** - Automate website authentication
2. **File Downloads** - Auto-download and organize files
3. **Infinite Scroll** - Scroll pages with lazy loading
4. **Form Filling** - Bulk form submission automation
5. **Price Scraping** - Scrape e-commerce without APIs
6. **Screenshots** - Automated screenshot capture
7. **Website Monitoring** - Check site health and uptime
8. **Google Search** - Search automation and results scraping
9. **Auto-Reply** - Send messages on web platforms
10. **Analytics Capture** - Dashboard metrics extraction

### API Endpoints

| Endpoint | Method | Use Case | Description |
|----------|--------|----------|-------------|
| `/api/real-agency/selenium/screenshot` | POST | #6 | Take website screenshot |
| `/api/real-agency/selenium/website-check` | POST | #7 | Check if site is up |
| `/api/real-agency/selenium/google-search` | POST | #8 | Search Google |
| `/api/real-agency/selenium/scrape-prices` | POST | #5 | Scrape product prices |
| `/api/real-agency/utils/auto-login` | POST | #1 | Auto-login to websites |

### Usage Examples

```bash
# Take screenshot
curl -X POST http://localhost:8000/api/real-agency/selenium/screenshot \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "full_page": true
  }'

# Check website status
curl -X POST http://localhost:8000/api/real-agency/selenium/website-check \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "expected_content": "Welcome"
  }'

# Google search
curl -X POST http://localhost:8000/api/real-agency/selenium/google-search \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python developer jobs",
    "result_count": 10
  }'

# Scrape prices
curl -X POST http://localhost:8000/api/real-agency/selenium/scrape-prices \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/products",
    "price_selector": ".price",
    "name_selector": ".product-name"
  }'

# Auto-login (visible browser for captcha)
curl -X POST http://localhost:8000/api/real-agency/utils/auto-login \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/login",
    "username": "your_username",
    "password": "your_password",
    "username_selector": "#email",
    "password_selector": "#password",
    "submit_selector": "button[type=submit]"
  }'
```

---

## 6. Job Scraping (Platforms Without APIs)

**File:** `backend/app/services/job_scraper.py`

### Overview
Scrape jobs from platforms that don't offer APIs using Selenium:

- **LinkedIn Jobs** - Professional network job listings
- **Indeed** - World's largest job site
- **We Work Remotely** - Remote work opportunities
- **Remote.co** - Remote job board

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/real-agency/jobs/scrape` | GET | Scrape jobs from platforms |
| `/api/real-agency/jobs/scrape/best-opportunities` | GET | AI-scored opportunities |

### Usage Examples

```bash
# Scrape jobs from all sources
curl "http://localhost:8000/api/real-agency/jobs/scrape?query=python+developer&sources=all&max_per_source=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Scrape specific sources
curl "http://localhost:8000/api/real-agency/jobs/scrape?query=react&sources=weworkremotely,remoteco" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get best opportunities with scoring
curl "http://localhost:8000/api/real-agency/jobs/scrape/best-opportunities?query=full+stack" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Scoring Algorithm

Opportunities are scored based on:
- **Remote work** (+5 points) - Remote positions preferred
- **Salary transparency** (+3 points) - Public salary ranges
- **Company reputation** (+3 points) - FAANG and known companies
- **Seniority level** (+2 points) - Senior/Lead roles

---

## 7. Auto-Apply to Jobs

**File:** `backend/app/services/auto_apply.py`

### Overview
Automatically fill and submit job applications using Selenium:

- **LinkedIn Easy Apply** - One-click applications
- **Indeed Apply** - Direct applications
- **Generic Forms** - Any career page form

### ⚠️ WARNING
**This submits REAL job applications to REAL companies. Use with extreme caution and review applications before bulk submission.**

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/real-agency/apply/auto-fill` | POST | Apply to single job |
| `/api/real-agency/apply/bulk` | POST | Apply to multiple jobs |
| `/api/real-agency/apply/stats` | GET | Application statistics |

### Usage Examples

```bash
# Single job application
curl -X POST http://localhost:8000/api/real-agency/apply/auto-fill \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_url": "https://linkedin.com/jobs/view/12345",
    "platform": "linkedin",
    "profile": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "linkedin_url": "https://linkedin.com/in/johndoe",
      "resume_path": "/path/to/resume.pdf",
      "skills": ["Python", "FastAPI", "React"],
      "summary": "Full-stack developer with 5 years experience"
    }
  }'

# Bulk application (USE WITH CAUTION)
curl -X POST http://localhost:8000/api/real-agency/apply/bulk \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_urls": [
      "https://linkedin.com/jobs/view/12345",
      "https://linkedin.com/jobs/view/67890",
      "https://indeed.com/viewjob?jk=abcde"
    ],
    "profile": { ... },
    "delay_seconds": 60
  }'

# Check stats
curl http://localhost:8000/api/real-agency/apply/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Complete Integration Summary

| Integration | Type | Real Data | Risk Level |
|-------------|------|-----------|------------|
| Blockchain Wallets | API (BlockCypher/Etherscan) | ✅ Real balances | Low |
| Upwork | OAuth API | ✅ Real jobs/proposals | Medium |
| Fiverr | API | ✅ Real gigs | Medium |
| Toptal | API | ✅ Real opportunities | Medium |
| A2A Protocol | Protocol | ✅ Real agents | Low |
| LinkedIn Scraping | Selenium | ✅ Real jobs | Low |
| Indeed Scraping | Selenium | ✅ Real jobs | Low |
| Job Applications | Selenium | ✅ REAL APPLICATIONS | **HIGH** |

---

## Prerequisites

1. **Chrome Browser** installed
2. **Python dependencies**:
   ```bash
   pip install selenium webdriver-manager
   ```
3. **ChromeDriver** (auto-managed by webdriver-manager)

---

## Testing Selenium

```bash
cd backend/app/services

# Test selenium automation
python selenium_automation.py

# Test job scraper
python job_scraper.py

# Test auto-apply (requires valid job URLs)
python auto_apply.py
```

---

## Security Notes

1. **Never commit credentials** to git
2. **Use environment variables** for API keys
3. **Review auto-applications** before bulk submission
4. **Add delays** between actions to avoid rate limiting
5. **Use headless mode** for production automation
6. **Rotate User-Agent** strings to avoid detection
7. **Respect robots.txt** and platform ToS

---

## Troubleshooting

### ChromeDriver Issues
```bash
# Update ChromeDriver
pip install --upgrade webdriver-manager

# Or specify Chrome path
export CHROME_BIN=/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome
```

### Selenium Timeout Errors
- Increase `wait_timeout` in SeleniumAutomation
- Check if site has anti-bot protection
- Try using `headless=False` to see what's happening

### LinkedIn Blocking
- LinkedIn has strong anti-scraping measures
- Consider using their official API instead
- Add delays between requests (30+ seconds)
- Use rotating proxies for production

---

## Complete API Endpoint Summary

| Endpoint | Purpose |
|----------|---------|
| `GET /api/real-agency/platforms/status` | Check platform auth |
| `GET /api/real-agency/jobs/search` | Search API-based platforms |
| `GET /api/real-agency/jobs/best-opportunities` | Scored opportunities |
| `GET /api/real-agency/jobs/scrape` | Scrape jobs (Selenium) |
| `POST /api/real-agency/proposals/submit` | Submit proposals |
| `POST /api/real-agency/apply/auto-fill` | Auto-apply to job |
| `POST /api/real-agency/apply/bulk` | Bulk applications |
| `POST /api/real-agency/wallet/add` | Add crypto wallet |
| `GET /api/real-agency/wallet/{id}/refresh` | Refresh balance |
| `POST /api/real-agency/a2a` | A2A protocol |
| `POST /api/real-agency/selenium/screenshot` | Screenshot |
| `POST /api/real-agency/selenium/website-check` | Site monitoring |
| `POST /api/real-agency/auto-earn-cycle` | Full earning cycle |
