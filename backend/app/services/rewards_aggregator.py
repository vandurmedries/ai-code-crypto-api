"""
Reward Points Aggregator
Automates point collection from multiple rewards programs
Microsoft Rewards, Swagbucks, Fetch, Google Opinion Rewards, etc.
"""

import os
import json
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


class RewardPlatform(Enum):
    MICROSOFT_REWARDS = "microsoft_rewards"
    SWAGBUCKS = "swagbucks"
    FETCH_REWARDS = "fetch"
    GOOGLE_OPINION = "google_opinion"
    MISTPLAY = "mistplay"
    SURVEY_JUNKIE = "survey_junkie"


@dataclass
class RewardAccount:
    account_id: str
    platform: RewardPlatform
    email: str
    daily_points_target: int
    current_points: int
    lifetime_earned: int
    status: str  # active, suspended, pending
    last_activity: str
    estimated_value_eur: float


@dataclass
class DailyTask:
    task_id: str
    platform: RewardPlatform
    task_type: str  # search, quiz, survey, game, video
    points_reward: int
    time_required_minutes: int
    completed: bool
    automation_difficulty: str  # easy, medium, hard


class RewardsAggregator:
    """
    Aggregates multiple reward point systems
    Automates daily point collection across platforms
    """
    
    def __init__(self):
        self.accounts: Dict[str, RewardAccount] = {}
        self.daily_tasks: List[DailyTask] = []
        self.total_earned_eur = 0.0
        self.logger = logging.getLogger('RewardsAggregator')
        
        # Platform configurations
        self.platform_configs = {
            RewardPlatform.MICROSOFT_REWARDS: {
                "daily_max": 400,
                "points_per_eur": 1300,  # 1300 points = €1
                "tasks": ["bing_searches", "daily_quiz", "edge_bonus", "mobile_searches"],
                "automation": "medium",  # Requires browser automation
                "risk_level": "medium"  # Can get banned
            },
            RewardPlatform.SWAGBUCKS: {
                "daily_max": 100,
                "points_per_eur": 175,  # 175 SB = €1
                "tasks": ["watch_videos", "search", "surveys", "shopping"],
                "automation": "hard",  # Very strict detection
                "risk_level": "high"
            },
            RewardPlatform.FETCH_REWARDS: {
                "daily_max": 50,
                "points_per_eur": 1250,  # 1250 points = €1
                "tasks": ["scan_receipts", "special_offers", "referrals"],
                "automation": "easy",  # Just upload receipts
                "risk_level": "low"
            },
            RewardPlatform.GOOGLE_OPINION: {
                "daily_max": 30,
                "points_per_eur": 33,  # 33 cents per survey avg
                "tasks": ["location_surveys", "shopping_surveys"],
                "automation": "hard",  # Very hard to automate
                "risk_level": "low"
            },
            RewardPlatform.MISTPLAY: {
                "daily_max": 200,
                "points_per_eur": 1500,  # Gaming rewards
                "tasks": ["play_games", "reach_levels", "daily_checkin"],
                "automation": "medium",
                "risk_level": "medium"
            }
        }
    
    def create_reward_account(
        self,
        platform: RewardPlatform,
        email: str,
        account_count: int = 1
    ) -> List[RewardAccount]:
        """
        Create reward accounts for a platform
        """
        accounts = []
        config = self.platform_configs[platform]
        
        for i in range(account_count):
            account_id = f"{platform.value}_{hashlib.md5(f'{email}_{i}_{datetime.utcnow().timestamp()}'.encode()).hexdigest()[:8]}"
            
            account = RewardAccount(
                account_id=account_id,
                platform=platform,
                email=f"{email}+{i}@gmail.com" if i > 0 else email,
                daily_points_target=config["daily_max"],
                current_points=0,
                lifetime_earned=0,
                status="active",
                last_activity=datetime.utcnow().isoformat(),
                estimated_value_eur=0.0
            )
            
            self.accounts[account_id] = account
            accounts.append(account)
            
            self.logger.info(f"✅ Created {platform.value} account: {account_id}")
        
        return accounts
    
    def generate_daily_tasks(self, account_id: str) -> List[DailyTask]:
        """
        Generate daily automation tasks for an account
        """
        if account_id not in self.accounts:
            return []
        
        account = self.accounts[account_id]
        config = self.platform_configs[account.platform]
        
        tasks = []
        
        for task_type in config["tasks"]:
            task_id = f"task_{account_id}_{task_type}_{datetime.utcnow().strftime('%Y%m%d')}"
            
            # Calculate points based on task
            if task_type == "bing_searches":
                points = 150
                time = 5
                difficulty = "easy"
            elif task_type == "daily_quiz":
                points = 40
                time = 2
                difficulty = "easy"
            elif task_type == "mobile_searches":
                points = 100
                time = 3
                difficulty = "easy"
            elif task_type == "watch_videos":
                points = 20
                time = 10
                difficulty = "medium"
            elif task_type == "scan_receipts":
                points = 25
                time = 2
                difficulty = "easy"
            else:
                points = 10
                time = 5
                difficulty = "medium"
            
            task = DailyTask(
                task_id=task_id,
                platform=account.platform,
                task_type=task_type,
                points_reward=points,
                time_required_minutes=time,
                completed=False,
                automation_difficulty=difficulty
            )
            
            tasks.append(task)
            self.daily_tasks.append(task)
        
        return tasks
    
    def simulate_daily_automation(self, account_id: str) -> Dict[str, Any]:
        """
        Simulate daily automation run for an account
        """
        if account_id not in self.accounts:
            return {"error": "Account not found"}
        
        account = self.accounts[account_id]
        
        if account.status != "active":
            return {"error": f"Account {account.status}"}
        
        # Generate tasks
        tasks = self.generate_daily_tasks(account_id)
        
        # Simulate completion (with success rate based on difficulty)
        total_points = 0
        completed_tasks = []
        failed_tasks = []
        
        for task in tasks:
            # Success rates
            if task.automation_difficulty == "easy":
                success_rate = 0.95
            elif task.automation_difficulty == "medium":
                success_rate = 0.80
            else:
                success_rate = 0.60
            
            # Random success
            if random.random() < success_rate:
                task.completed = True
                total_points += task.points_reward
                completed_tasks.append(task.task_type)
            else:
                failed_tasks.append(task.task_type)
        
        # Update account
        account.current_points += total_points
        account.lifetime_earned += total_points
        account.last_activity = datetime.utcnow().isoformat()
        
        # Calculate EUR value
        config = self.platform_configs[account.platform]
        eur_earned = total_points / config["points_per_eur"]
        account.estimated_value_eur += eur_earned
        self.total_earned_eur += eur_earned
        
        # Risk of ban (random 5% chance for Microsoft, 10% for Swagbucks)
        if account.platform == RewardPlatform.MICROSOFT_REWARDS and random.random() < 0.05:
            account.status = "suspended"
            return {
                "account_id": account_id,
                "status": "SUSPENDED",
                "reason": "Automated activity detected by Microsoft",
                "warning": "⚠️ Account banned - need new account/phone number"
            }
        
        return {
            "success": True,
            "account_id": account_id,
            "platform": account.platform.value,
            "points_earned_today": total_points,
            "eur_value_today": round(eur_earned, 2),
            "total_account_points": account.current_points,
            "total_account_value_eur": round(account.estimated_value_eur, 2),
            "tasks_completed": len(completed_tasks),
            "tasks_failed": len(failed_tasks),
            "completed_task_types": completed_tasks,
            "failed_task_types": failed_tasks,
            "status": account.status,
            "time_spent": sum(t.time_required_minutes for t in tasks if t.completed)
        }
    
    def run_all_accounts_daily(self) -> Dict[str, Any]:
        """
        Run daily automation for all active accounts
        """
        results = {
            "total_accounts": len(self.accounts),
            "active_accounts": 0,
            "suspended_accounts": 0,
            "total_points_today": 0,
            "total_eur_today": 0.0,
            "account_results": []
        }
        
        for account_id, account in self.accounts.items():
            if account.status == "active":
                result = self.simulate_daily_automation(account_id)
                results["account_results"].append(result)
                results["active_accounts"] += 1
                
                if result.get("success"):
                    results["total_points_today"] += result["points_earned_today"]
                    results["total_eur_today"] += result["eur_value_today"]
                
                if result.get("status") == "SUSPENDED":
                    results["suspended_accounts"] += 1
        
        return results
    
    def get_aggregator_stats(self) -> Dict[str, Any]:
        """Get complete aggregator statistics"""
        
        by_platform = {}
        for platform in RewardPlatform:
            platform_accounts = [a for a in self.accounts.values() if a.platform == platform]
            if platform_accounts:
                total_points = sum(a.current_points for a in platform_accounts)
                total_eur = sum(a.estimated_value_eur for a in platform_accounts)
                
                by_platform[platform.value] = {
                    "account_count": len(platform_accounts),
                    "total_points": total_points,
                    "total_value_eur": round(total_eur, 2),
                    "avg_per_account": round(total_eur / len(platform_accounts), 2) if platform_accounts else 0
                }
        
        # Calculate monthly projection
        daily_avg = self.total_earned_eur / max(len(self.accounts), 1)
        monthly_projection = daily_avg * 30
        yearly_projection = daily_avg * 365
        
        return {
            "total_accounts": len(self.accounts),
            "active_accounts": len([a for a in self.accounts.values() if a.status == "active"]),
            "suspended_accounts": len([a for a in self.accounts.values() if a.status == "suspended"]),
            "total_lifetime_earned_eur": round(self.total_earned_eur, 2),
            "monthly_projection": round(monthly_projection, 2),
            "yearly_projection": round(yearly_projection, 2),
            "by_platform": by_platform,
            "risk_factors": [
                "Account bans possible (5-10% per month)",
                "Requires VPN rotation for multiple accounts",
                "Platform terms of service violations",
                "Low individual earnings, needs scale"
            ],
            "automation_status": "Simulated - Real implementation requires browser automation (Selenium/Playwright)"
        }


# Global instance
_rewards_aggregator: Optional[RewardsAggregator] = None

def get_rewards_aggregator() -> RewardsAggregator:
    """Get or create rewards aggregator"""
    global _rewards_aggregator
    if _rewards_aggregator is None:
        _rewards_aggregator = RewardsAggregator()
    return _rewards_aggregator
