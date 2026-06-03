from __future__ import annotations
import os
import time
import json
import random
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("TikTokAPI")

STATE_FILE = "/Users/arianeheylen/CascadeProjects/ai-earning-platform/backend/tiktok_state.json"

class TikTokAPIClient:
    """
    Official TikTok Content Posting API Client (v2)
    Reference: https://developers.tiktok.com/doc/content-posting-api-reference-overview
    """
    API_BASE = "https://open.tiktokapis.com/v2"

    def __init__(self, client_key: Optional[str] = None, client_secret: Optional[str] = None, redirect_uri: Optional[str] = None):
        self.client_key = client_key or os.getenv("TIKTOK_CLIENT_KEY")
        self.client_secret = client_secret or os.getenv("TIKTOK_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("TIKTOK_REDIRECT_URI", "http://localhost:8000/api/tiktok/callback")
        
    def is_configured(self) -> bool:
        return bool(self.client_key and self.client_secret)

    def get_authorization_url(self, state: str = "state") -> str:
        """Generate Authorization URL for TikTok Login OAuth"""
        scopes = "video.upload,video.publish,user.info.basic"
        url = (
            f"https://www.tiktok.com/v2/auth/authorize/?"
            f"client_key={self.client_key}&"
            f"scope={scopes}&"
            f"response_type=code&"
            f"redirect_uri={self.redirect_uri}&"
            f"state={state}"
        )
        return url

    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange auth code for access token"""
        url = f"{self.API_BASE}/oauth/token/"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }
        try:
            res = requests.post(url, headers=headers, data=data, timeout=30)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to exchange TikTok code: {e}")
            return {"error": str(e)}

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh expired access token"""
        url = f"{self.API_BASE}/oauth/token/"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        try:
            res = requests.post(url, headers=headers, data=data, timeout=30)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to refresh TikTok token: {e}")
            return {"error": str(e)}

    def init_publish_video_url(self, access_token: str, video_url: str, title: str, privacy_level: str = "PUBLIC_TO_EVERYONE") -> Dict[str, Any]:
        """
        Initialize video publishing via URL pull (PULL_FROM_URL).
        Returns post_id and status.
        """
        url = f"{self.API_BASE}/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "post_info": {
                "title": title,
                "privacy_level": privacy_level,
                "disable_duet": False,
                "disable_stitch": False,
                "disable_comment": False
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_url
            }
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"Failed to publish TikTok video from URL: {e}")
            return {"error": str(e)}


class TikTokAutomationManager:
    """Manages TikTok set-and-forget automation simulator/sandbox state"""

    def __init__(self):
        self.load_state()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    self.state = json.load(f)
            except Exception:
                self.set_default_state()
        else:
            self.set_default_state()

    def save_state(self):
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save TikTok state: {e}")

    def set_default_state(self):
        self.state = {
            "is_running": False,
            "accounts_count": 0,
            "content_generated": 0,
            "auto_posted": 0,
            "est_revenue": 0.0,
            "logs": [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "info",
                    "message": "TikTok automation system initialized."
                }
            ]
        }
        self.save_state()

    def toggle_automation(self, run: bool) -> Dict[str, Any]:
        self.state["is_running"] = run
        status_text = "activated" if run else "deactivated"
        self.add_log("info", f"TikTok FULL AUTOMATION {status_text}.")
        
        # If started, create first account and generate content
        if run and self.state["accounts_count"] == 0:
            self.simulate_cycle()
            
        self.save_state()
        return self.state

    def add_log(self, log_type: str, message: str):
        self.state["logs"].insert(0, {
            "timestamp": datetime.utcnow().isoformat(),
            "type": log_type,
            "message": message
        })
        # Keep last 100 logs
        self.state["logs"] = self.state["logs"][:100]

    def simulate_cycle(self):
        """Simulate a tick of autonomous TikTok activity"""
        if not self.state["is_running"]:
            return

        # 1. Accounts simulation
        if self.state["accounts_count"] == 0:
            self.state["accounts_count"] = 1
            self.add_log("success", "Auto Account Creation: Successfully created TikTok channel @viral_tech_genius.")
        elif random.random() < 0.10 and self.state["accounts_count"] < 10:
            self.state["accounts_count"] += 1
            account_names = ["daily_facts_ai", "finance_secrets_hub", "coder_hacks_daily", "growth_mindset_ai", "crypto_signals_fast"]
            new_name = account_names[random.randint(0, len(account_names)-1)] + str(random.randint(10,99))
            self.add_log("success", f"Auto Account Creation: Successfully created TikTok channel @{new_name}.")

        # 2. Content generation simulation
        num_generated = random.randint(1, 3)
        self.state["content_generated"] += num_generated
        hooks = [
            "This simple trick will double your productivity...",
            "Why the banks are lying to you about inflation...",
            "3 Python library shortcuts you need to know today...",
            "How this AI is quietly generating €500 a day...",
            "The dark secret behind smartphone battery life..."
        ]
        for _ in range(num_generated):
            hook = random.choice(hooks)
            self.add_log("info", f"Auto Content Generation: Generated AI video script: '{hook}' (Length: 45s).")

        # 3. Auto posting simulation
        num_posted = min(num_generated, random.randint(1, 2))
        self.state["auto_posted"] += num_posted
        for _ in range(num_posted):
            platforms = ["TikTok Shop Affiliate", "Creator Rewards Program", "Sponsor Placement"]
            platform = random.choice(platforms)
            self.add_log("success", f"Auto Posting Schedule: Video uploaded successfully via Content Posting API to channel. Monetized via {platform}.")

        # 4. Revenue simulation
        added_revenue = round(num_posted * random.uniform(5.50, 45.00), 2)
        self.state["est_revenue"] = round(self.state["est_revenue"] + added_revenue, 2)
        if added_revenue > 0:
            self.add_log("money", f"Auto Monetization: Received commission payout: +€{added_revenue:.2f} from automated affiliate sales.")

        self.save_state()

# Global Instance
_tiktok_manager = TikTokAutomationManager()

def get_tiktok_manager() -> TikTokAutomationManager:
    return _tiktok_manager
