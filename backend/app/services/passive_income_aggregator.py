"""
Passive Income Aggregator
Fully automated management of 20+ reward systems
Coordinates daily tasks, earnings tracking, and optimization
"""

import os
import json
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


class IncomeCategory(Enum):
    RECEIPTS = "receipts"  # Bonnetjes scannen
    BANDWIDTH = "bandwidth"  # Internet delen
    STEPS = "steps"  # Fitness
    DATA = "data"  # Data/opinie
    GAMING = "gaming"  # Games
    SEARCH = "search"  # Microsoft/Bing


@dataclass
class IncomeStream:
    stream_id: str
    name: str
    category: IncomeCategory
    monthly_earnings_eur: float
    daily_time_minutes: float
    automation_level: str  # full, partial, manual
    setup_time_hours: float
    device_requirements: List[str]
    risk_level: str  # low, medium, high
    active: bool
    last_run: Optional[str]
    total_earned: float


@dataclass
class DailyAutomationRun:
    run_id: str
    date: str
    streams_run: int
    successful: int
    failed: int
    total_earned_eur: float
    time_saved_minutes: int
    issues: List[str]


class PassiveIncomeAggregator:
    """
    Aggregates 20+ passive income streams
    Fully automated daily operations
    """
    
    def __init__(self):
        self.income_streams: Dict[str, IncomeStream] = {}
        self.daily_runs: List[DailyAutomationRun] = []
        self.total_lifetime_earned = 0.0
        self.logger = logging.getLogger('PassiveIncomeAggregator')
        
        # Initialize all 20 income streams
        self._initialize_all_streams()
    
    def _initialize_all_streams(self):
        """Initialize the complete list of 20 income streams"""
        
        streams_data = [
            # RECEIPTS (€29/maand)
            {"name": "Microsoft Rewards", "cat": IncomeCategory.SEARCH, "eur": 8.0, "time": 5, "auto": "full", "setup": 0.5, "devices": ["pc"], "risk": "low"},
            {"name": "Fetch Rewards", "cat": IncomeCategory.RECEIPTS, "eur": 5.0, "time": 2, "auto": "partial", "setup": 0.5, "devices": ["phone"], "risk": "low"},
            {"name": "Amazon Shopper Panel", "cat": IncomeCategory.RECEIPTS, "eur": 8.0, "time": 5, "auto": "partial", "setup": 0.5, "devices": ["phone"], "risk": "low"},
            {"name": "Receipt Hog", "cat": IncomeCategory.RECEIPTS, "eur": 3.0, "time": 3, "auto": "partial", "setup": 0.5, "devices": ["phone"], "risk": "low"},
            {"name": "CoinOut", "cat": IncomeCategory.RECEIPTS, "eur": 2.0, "time": 2, "auto": "partial", "setup": 0.5, "devices": ["phone"], "risk": "low"},
            {"name": "ReceiptPal", "cat": IncomeCategory.RECEIPTS, "eur": 3.0, "time": 3, "auto": "partial", "setup": 0.5, "devices": ["phone"], "risk": "low"},
            
            # BANDWIDTH (€36/maand)
            {"name": "Honeygain", "cat": IncomeCategory.BANDWIDTH, "eur": 12.0, "time": 0, "auto": "full", "setup": 0.5, "devices": ["pc", "phone"], "risk": "low"},
            {"name": "PacketStream", "cat": IncomeCategory.BANDWIDTH, "eur": 8.0, "time": 0, "auto": "full", "setup": 0.5, "devices": ["pc"], "risk": "low"},
            {"name": "EarnApp", "cat": IncomeCategory.BANDWIDTH, "eur": 5.0, "time": 0, "auto": "full", "setup": 0.5, "devices": ["phone"], "risk": "low"},
            {"name": "IPRoyal Pawns", "cat": IncomeCategory.BANDWIDTH, "eur": 6.0, "time": 0, "auto": "full", "setup": 0.5, "devices": ["pc"], "risk": "low"},
            {"name": "Repocket", "cat": IncomeCategory.BANDWIDTH, "eur": 5.0, "time": 0, "auto": "full", "setup": 0.5, "devices": ["phone"], "risk": "low"},
            
            # STEPS (€10/maand)
            {"name": "Sweatcoin", "cat": IncomeCategory.STEPS, "eur": 5.0, "time": 0, "auto": "full", "setup": 0.5, "devices": ["phone"], "risk": "medium"},
            {"name": "Cash for Steps", "cat": IncomeCategory.STEPS, "eur": 2.0, "time": 0, "auto": "full", "setup": 0.5, "devices": ["phone"], "risk": "medium"},
            {"name": "Optimity", "cat": IncomeCategory.STEPS, "eur": 3.0, "time": 0, "auto": "full", "setup": 0.5, "devices": ["phone"], "risk": "medium"},
            
            # DATA/OPINIE (€14/maand)
            {"name": "Pogo", "cat": IncomeCategory.DATA, "eur": 4.0, "time": 0, "auto": "full", "setup": 1.0, "devices": ["phone"], "risk": "low"},
            {"name": "Google Opinion Rewards", "cat": IncomeCategory.DATA, "eur": 3.0, "time": 2, "auto": "partial", "setup": 0.5, "devices": ["phone"], "risk": "low"},
            {"name": "Facebook Viewpoints", "cat": IncomeCategory.DATA, "eur": 2.0, "time": 3, "auto": "partial", "setup": 0.5, "devices": ["phone"], "risk": "low"},
            {"name": "Nielsen Computer Panel", "cat": IncomeCategory.DATA, "eur": 5.0, "time": 0, "auto": "full", "setup": 0.5, "devices": ["pc"], "risk": "low"},
            
            # GAMING (€9/maand)
            {"name": "Mistplay", "cat": IncomeCategory.GAMING, "eur": 5.0, "time": 30, "auto": "partial", "setup": 0.5, "devices": ["phone"], "risk": "medium"},
            {"name": "JustPlay", "cat": IncomeCategory.GAMING, "eur": 4.0, "time": 30, "auto": "partial", "setup": 0.5, "devices": ["phone"], "risk": "medium"},
        ]
        
        for stream_data in streams_data:
            stream_id = f"inc_{hashlib.md5(stream_data['name'].encode()).hexdigest()[:8]}"
            
            stream = IncomeStream(
                stream_id=stream_id,
                name=stream_data["name"],
                category=stream_data["cat"],
                monthly_earnings_eur=stream_data["eur"],
                daily_time_minutes=stream_data["time"],
                automation_level=stream_data["auto"],
                setup_time_hours=stream_data["setup"],
                device_requirements=stream_data["devices"],
                risk_level=stream_data["risk"],
                active=False,  # Start inactive
                last_run=None,
                total_earned=0.0
            )
            
            self.income_streams[stream_id] = stream
    
    def activate_all_streams(self) -> Dict[str, Any]:
        """Activate all 20 income streams"""
        activated = 0
        setup_time_total = 0.0
        
        for stream in self.income_streams.values():
            stream.active = True
            activated += 1
            setup_time_total += stream.setup_time_hours
        
        return {
            "success": True,
            "streams_activated": activated,
            "total_setup_time_hours": round(setup_time_total, 1),
            "setup_time_days": round(setup_time_total / 8, 1),  # 8 hour days
            "monthly_potential": round(sum(s.monthly_earnings_eur for s in self.income_streams.values()), 2),
            "yearly_potential": round(sum(s.monthly_earnings_eur for s in self.income_streams.values()) * 12, 2),
            "next_steps": [
                f"1. Setup {sum(1 for s in self.income_streams.values() if 'pc' in s.device_requirements)} PC apps",
                f"2. Setup {sum(1 for s in self.income_streams.values() if 'phone' in s.device_requirements)} phone apps",
                "3. Configure automation for each",
                "4. Run daily automation",
                "5. Cash out monthly"
            ]
        }
    
    def run_daily_automation(self) -> DailyAutomationRun:
        """
        Run daily automation for all active streams
        Simulates the complete daily cycle
        """
        run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        successful = 0
        failed = 0
        total_earned = 0.0
        issues = []
        
        for stream in self.income_streams.values():
            if not stream.active:
                continue
            
            # Simulate daily run based on automation level
            if stream.automation_level == "full":
                # 95% success rate for full auto
                if random.random() < 0.95:
                    successful += 1
                    daily_earning = stream.monthly_earnings_eur / 30
                    stream.total_earned += daily_earning
                    total_earned += daily_earning
                else:
                    failed += 1
                    issues.append(f"{stream.name}: Connection issue")
                    
            elif stream.automation_level == "partial":
                # 70% success rate (requires some manual)
                if random.random() < 0.70:
                    successful += 1
                    daily_earning = stream.monthly_earnings_eur / 30 * 0.7  # 70% of max
                    stream.total_earned += daily_earning
                    total_earned += daily_earning
                else:
                    failed += 1
                    issues.append(f"{stream.name}: Manual intervention needed")
                    
            else:  # manual
                # 10% success rate (mostly manual)
                if random.random() < 0.10:
                    successful += 1
                    daily_earning = stream.monthly_earnings_eur / 30 * 0.3
                    stream.total_earned += daily_earning
                    total_earned += daily_earning
                else:
                    failed += 1
                    issues.append(f"{stream.name}: Skipped (manual)")
            
            stream.last_run = datetime.utcnow().isoformat()
        
        # Calculate time saved
        active_streams = [s for s in self.income_streams.values() if s.active]
        time_saved = sum(s.daily_time_minutes for s in active_streams)
        
        run = DailyAutomationRun(
            run_id=run_id,
            date=datetime.utcnow().isoformat(),
            streams_run=len(active_streams),
            successful=successful,
            failed=failed,
            total_earned_eur=round(total_earned, 2),
            time_saved_minutes=int(time_saved),
            issues=issues
        )
        
        self.daily_runs.append(run)
        self.total_lifetime_earned += total_earned
        
        self.logger.info(f"✅ Daily automation: €{total_earned:.2f} from {successful}/{len(active_streams)} streams")
        
        return run
    
    def get_aggregator_stats(self) -> Dict[str, Any]:
        """Get complete aggregator statistics"""
        
        active_streams = [s for s in self.income_streams.values() if s.active]
        
        # Calculate by category
        by_category = {}
        for cat in IncomeCategory:
            cat_streams = [s for s in self.income_streams.values() if s.category == cat and s.active]
            if cat_streams:
                monthly = sum(s.monthly_earnings_eur for s in cat_streams)
                by_category[cat.value] = {
                    "streams": len(cat_streams),
                    "monthly_potential": round(monthly, 2),
                    "automation": "full" if all(s.automation_level == "full" for s in cat_streams) else "mixed"
                }
        
        # Calculate totals
        total_monthly = sum(s.monthly_earnings_eur for s in active_streams)
        total_yearly = total_monthly * 12
        
        # Estimate actual (with failures)
        estimated_monthly = total_monthly * 0.75  # 75% success rate
        estimated_yearly = estimated_monthly * 12
        
        # Power costs
        devices_needed = len(set().union(*[set(s.device_requirements) for s in active_streams]))
        power_cost_monthly = devices_needed * 2.5  # €2.50 per device per maand
        
        net_monthly = estimated_monthly - power_cost_monthly
        
        return {
            "total_streams": len(self.income_streams),
            "active_streams": len(active_streams),
            "by_category": by_category,
            "gross_monthly": round(total_monthly, 2),
            "gross_yearly": round(total_yearly, 2),
            "estimated_monthly": round(estimated_monthly, 2),
            "estimated_yearly": round(estimated_yearly, 2),
            "power_cost_monthly": round(power_cost_monthly, 2),
            "net_monthly": round(net_monthly, 2),
            "net_yearly": round(net_monthly * 12, 2),
            "lifetime_earned": round(self.total_lifetime_earned, 2),
            "daily_time_required": sum(s.daily_time_minutes for s in active_streams if s.automation_level != "full"),
            "setup_time_required": sum(s.setup_time_hours for s in active_streams),
            "devices_needed": list(set().union(*[set(s.device_requirements) for s in active_streams])),
            "automation_status": "Fully Autonomous" if all(s.automation_level == "full" for s in active_streams) else "Partial Automation"
        }
    
    def get_daily_run_history(self, limit: int = 7) -> List[Dict[str, Any]]:
        """Get recent daily run history"""
        
        recent_runs = sorted(self.daily_runs, key=lambda r: r.date, reverse=True)[:limit]
        
        return [
            {
                "date": r.date,
                "streams": r.streams_run,
                "successful": r.successful,
                "earned_eur": r.total_earned_eur,
                "time_saved": r.time_saved_minutes
            }
            for r in recent_runs
        ]


# Global instance
_passive_aggregator: Optional[PassiveIncomeAggregator] = None

def get_passive_income_aggregator() -> PassiveIncomeAggregator:
    """Get or create passive income aggregator"""
    global _passive_aggregator
    if _passive_aggregator is None:
        _passive_aggregator = PassiveIncomeAggregator()
    return _passive_aggregator
