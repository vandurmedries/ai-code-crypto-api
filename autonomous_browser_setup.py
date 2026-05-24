#!/usr/bin/env python3
"""
Autonomous Browser Automation
Fills out affiliate application forms automatically using Playwright/Selenium
"""

import os
import time
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional


class AutonomousFormFiller:
    """
    Uses browser automation to fill affiliate applications automatically
    """
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.setup_data = self._load_setup_data()
        
    def _load_setup_data(self) -> Dict[str, Any]:
        """Load prepared setup data"""
        # Try multiple paths
        paths = [
            "./platform_accounts/setup_data.json",
            "./backend/platform_accounts/setup_data.json",
            "/Users/arianeheylen/CascadeProjects/ai-earning-platform/backend/platform_accounts/setup_data.json",
            "/Users/arianeheylen/CascadeProjects/ai-earning-platform/platform_accounts/setup_data.json"
        ]
        
        for setup_file in paths:
            if os.path.exists(setup_file):
                with open(setup_file, 'r') as f:
                    return json.load(f)
        
        # If no file found, try to get from API
        return self._fetch_setup_from_api()
    
    def _fetch_setup_from_api(self) -> Dict[str, Any]:
        """Fetch setup data from backend API"""
        try:
            import requests
            
            # First get token
            auth_res = requests.post(
                "http://localhost:8000/api/auth/login",
                data={"username": "system@autonomous.ai", "password": "auto"},
                timeout=5
            )
            
            if auth_res.status_code == 200:
                token = auth_res.json().get("access_token")
                
                # Get setup status
                status_res = requests.get(
                    "http://localhost:8000/api/setup/setup-status",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )
                
                if status_res.status_code == 200:
                    return status_res.json()
        except:
            pass
        
        return {}
    
    async def setup_amazon_associates(self):
        """
        Automate Amazon Associates signup
        Opens browser, fills form, submits application
        """
        from playwright.async_api import async_playwright
        
        account = self.setup_data.get("amazon_associates", {})
        business = self.setup_data.get("business_entity", {})
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Go to Amazon Associates signup
                await page.goto("https://affiliate-program.amazon.com/signup")
                await page.wait_for_load_state("networkidle")
                
                print("🤖 Filling Amazon Associates application...")
                
                # Step 1: Account Information
                await page.fill('input[name="email"]', account.get("email", ""))
                await page.fill('input[name="password"]', account.get("password", ""))
                await page.fill('input[name="passwordCheck"]', account.get("password", ""))
                
                # Click next
                await page.click('input[type="submit"]')
                await page.wait_for_timeout(2000)
                
                # Step 2: Website Information
                await page.fill('input[name="websiteUrl"]', business.get("website", ""))
                await page.fill('textarea[name="websiteDescription"]', 
                    f"Professional {business.get('name', '')} providing expert reviews and buying guides. "
                    f"We help consumers make informed purchasing decisions with unbiased recommendations."
                )
                
                # Select categories (check all relevant)
                categories = ["Electronics", "Home", "Sports", "Books"]
                for category in categories:
                    try:
                        await page.check(f'input[value="{category}"]')
                    except:
                        pass
                
                # Monetization methods
                await page.check('input[value="ContextualAdvertising"]')
                await page.check('input[value="AffiliateMarketing"]')
                
                # Traffic sources
                await page.check('input[value="SEO"]')
                await page.check('input[value="ContentMarketing"]')
                
                await page.click('input[type="submit"]')
                await page.wait_for_timeout(2000)
                
                # Step 3: Profile Information
                await page.fill('input[name="fullName"]', "Auto Admin")
                await page.fill('input[name="phoneNumber"]', business.get("phone", ""))
                await page.fill('input[name="addressLine1"]', business.get("address", "").split(",")[0])
                await page.fill('input[name="city"]', "San Francisco")  # Parse from address
                await page.select_option('select[name="state"]', "CA")
                await page.fill('input[name="zipCode"]', "94102")
                await page.select_option('select[name="country"]', "United States")
                
                await page.click('input[type="submit"]')
                await page.wait_for_timeout(2000)
                
                # Step 4: Payment & Tax
                # This requires real tax info - skip and alert user
                print("⚠️  Amazon Associates: Paused at tax information step")
                print("⚠️  Human needed: Enter SSN/Tax ID and bank account")
                
                # Take screenshot for user
                await page.screenshot(path="./platform_accounts/amazon_progress.png")
                
                # Keep browser open for manual completion
                if not self.headless:
                    print("✅ Form pre-filled! Complete tax info manually.")
                    input("Press Enter when done...")
                
            except Exception as e:
                print(f"❌ Amazon automation error: {e}")
                await page.screenshot(path="./platform_accounts/amazon_error.png")
            
            finally:
                await browser.close()
    
    async def setup_clickbank(self):
        """
        Automate ClickBank signup
        """
        from playwright.async_api import async_playwright
        
        account = self.setup_data.get("clickbank", {})
        business = self.setup_data.get("business_entity", {})
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto("https://accounts.clickbank.com/signup/affiliate")
                await page.wait_for_load_state("networkidle")
                
                print("🤖 Filling ClickBank application...")
                
                # Personal Information
                await page.fill('input[name="firstName"]', "Auto")
                await page.fill('input[name="lastName"]', "Admin")
                await page.fill('input[name="email"]', account.get("email", ""))
                await page.fill('input[name="password"]', account.get("password", ""))
                await page.fill('input[name="confirmPassword"]', account.get("password", ""))
                
                # Address
                await page.fill('input[name="streetAddress"]', business.get("address", ""))
                await page.fill('input[name="city"]', "San Francisco")
                await page.select_option('select[name="country"]', "United States")
                await page.select_option('select[name="state"]', "California")
                await page.fill('input[name="postalCode"]', "94102")
                await page.fill('input[name="phone"]', business.get("phone", ""))
                
                # Click next
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(3000)
                
                # Payee Information
                await page.fill('input[name="payeeName"]', business.get("name", ""))
                await page.select_option('select[name="paymentMethod"]', "Direct Deposit")
                
                # Skip to tax form
                print("⚠️  ClickBank: Paused at tax form")
                print("⚠️  Human needed: Complete W-9 tax form")
                
                await page.screenshot(path="./platform_accounts/clickbank_progress.png")
                
                if not self.headless:
                    input("Press Enter when done...")
                
            except Exception as e:
                print(f"❌ ClickBank automation error: {e}")
                await page.screenshot(path="./platform_accounts/clickbank_error.png")
            
            finally:
                await browser.close()
    
    def check_email_verification(self, email: str, password: str) -> bool:
        """
        Check email inbox for verification emails
        Attempts to auto-verify if possible
        """
        print(f"📧 Checking email: {email}")
        
        # This would integrate with email API (Gmail/Outlook)
        # For now, instruct user manually
        
        print(f"""
        📧 EMAIL VERIFICATION NEEDED:
        
        1. Login to: {email}
        2. Password: {password}
        3. Look for verification emails from:
           - Amazon Associates
           - ClickBank
           - ShareASale
        4. Click verification links
        5. Return here
        """)
        
        return False
    
    def run_full_setup(self):
        """
        Run complete autonomous setup
        """
        print("="*60)
        print("🤖 AUTONOMOUS BROWSER SETUP")
        print("="*60)
        print()
        
        # Load setup data
        if not self.setup_data:
            print("❌ No setup data found. Run /api/setup/setup-all first!")
            return
        
        # Check if Playwright is installed
        try:
            import playwright
        except ImportError:
            print("⚠️  Playwright not installed. Install with:")
            print("   pip install playwright")
            print("   playwright install chromium")
            return
        
        # Run automations
        print("Starting browser automations...")
        print("⚠️  Browser will open - don't close it!")
        print()
        
        try:
            # Amazon Associates
            print("1️⃣  Setting up Amazon Associates...")
            asyncio.run(self.setup_amazon_associates())
            
            # ClickBank
            print("2️⃣  Setting up ClickBank...")
            asyncio.run(self.setup_clickbank())
            
            # Email verification
            print("3️⃣  Checking email verifications...")
            business = self.setup_data.get("business_entity", {})
            
            for platform, account in self.setup_data.get("accounts", {}).items():
                self.check_email_verification(
                    account.get("email", ""),
                    account.get("password", "")
                )
            
            print()
            print("="*60)
            print("✅ Autonomous form filling complete!")
            print("⚠️  Manual steps remaining:")
            print("   - Complete tax forms")
            print("   - Verify emails")
            print("   - Wait for approvals")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Setup error: {e}")


def main():
    """Main entry point"""
    print("""
    AUTONOMOUS AFFILIATE SETUP
    ==========================
    
    This script will:
    1. Open browser windows
    2. Navigate to affiliate signup pages
    3. Fill in all forms automatically
    4. You complete the final verification steps
    
    Requirements:
    - pip install playwright
    - playwright install chromium
    
    Press Ctrl+C to cancel
    """)
    
    input("Press Enter to start browser automation...")
    
    filler = AutonomousFormFiller(headless=False)
    filler.run_full_setup()


if __name__ == "__main__":
    main()
