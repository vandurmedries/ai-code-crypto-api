"""
Crypto Recovery Service
Helps recover lost/forgotten crypto wallets
Takes percentage of recovered funds as fee
"""

import os
import json
import hashlib
import itertools
import string
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import random


class RecoveryType(Enum):
    FORGOTTEN_PASSWORD = "forgotten_password"
    PARTIAL_SEED = "partial_seed"
    CORRUPT_WALLET = "corrupt_wallet"
    OLD_HARDWARE = "old_hardware"
    UNKNOWN = "unknown"


class RecoveryStatus(Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    ATTEMPTING_RECOVERY = "attempting_recovery"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"


@dataclass
class RecoveryJob:
    job_id: str
    client_email: str
    recovery_type: RecoveryType
    wallet_type: str  # BTC, ETH, etc.
    wallet_address: Optional[str]
    partial_info: Dict[str, Any]  # What client remembers
    status: RecoveryStatus
    created_at: str
    attempted_methods: List[str] = field(default_factory=list)
    recovered_amount: float = 0.0
    fee_percentage: float = 20.0  # 20% of recovered funds
    fee_amount: float = 0.0
    client_payout: float = 0.0


class CryptoRecoveryService:
    """
    Service to recover lost crypto wallets
    Legitimate business: Helps people recover lost funds
    Revenue: Percentage of successful recoveries
    """
    
    def __init__(self, success_rate: float = 0.15):  # 15% success rate realistic
        self.success_rate = success_rate
        self.recovery_jobs: Dict[str, RecoveryJob] = {}
        self.successful_recoveries: List[RecoveryJob] = []
        self.total_recovered = 0.0
        self.total_fees_earned = 0.0
        self.logger = logging.getLogger('CryptoRecovery')
        
        # Recovery methods available
        self.methods = [
            "brute_force_dictionary",
            "pattern_analysis", 
            "partial_seed_reconstruction",
            "wallet_file_repair",
            "entropy_analysis"
        ]
    
    def submit_recovery_request(
        self,
        client_email: str,
        wallet_type: str,
        recovery_type: RecoveryType,
        wallet_address: Optional[str],
        partial_info: Dict[str, Any]
    ) -> RecoveryJob:
        """
        Submit new recovery request
        Client provides whatever they remember
        """
        job_id = f"rec_{hashlib.md5(f'{client_email}_{datetime.utcnow().timestamp()}'.encode()).hexdigest()[:10]}"
        
        job = RecoveryJob(
            job_id=job_id,
            client_email=client_email,
            recovery_type=recovery_type,
            wallet_type=wallet_type,
            wallet_address=wallet_address,
            partial_info=partial_info,
            status=RecoveryStatus.PENDING,
            created_at=datetime.utcnow().isoformat()
        )
        
        self.recovery_jobs[job_id] = job
        
        self.logger.info(f"🔍 New recovery request: {job_id} ({wallet_type})")
        
        return job
    
    def analyze_recovery_feasibility(self, job_id: str) -> Dict[str, Any]:
        """
        Analyze if recovery is possible
        Check partial info provided by client
        """
        if job_id not in self.recovery_jobs:
            return {"error": "Job not found"}
        
        job = self.recovery_jobs[job_id]
        job.status = RecoveryStatus.ANALYZING
        
        # Analyze based on recovery type
        feasibility_score = 0.0
        estimated_attempts = 0
        time_estimate = ""
        
        if job.recovery_type == RecoveryType.FORGOTTEN_PASSWORD:
            # Check if partial password hints available
            hints = job.partial_info.get("password_hints", [])
            length_range = job.partial_info.get("length_range", [8, 16])
            known_chars = job.partial_info.get("known_characters", "")
            
            if hints or known_chars:
                feasibility_score = 0.25  # 25% chance with hints
                estimated_attempts = 100000  # Dictionary + variations
                time_estimate = "24-72 hours"
            else:
                feasibility_score = 0.01  # 1% brute force only
                estimated_attempts = 1000000000  # Nearly impossible
                time_estimate = "Years (not feasible)"
        
        elif job.recovery_type == RecoveryType.PARTIAL_SEED:
            # Check how many seed words are known
            known_words = job.partial_info.get("known_words", [])
            word_count = job.partial_info.get("total_words", 12)
            
            missing_words = word_count - len(known_words)
            
            if missing_words <= 2:
                feasibility_score = 0.60  # 60% chance
                estimated_attempts = 2048 ** missing_words  # BIP39 wordlist
                time_estimate = "1-24 hours"
            elif missing_words <= 4:
                feasibility_score = 0.20  # 20% chance
                estimated_attempts = 2048 ** missing_words
                time_estimate = "1-7 days"
            else:
                feasibility_score = 0.01  # 1% chance
                time_estimate = "Not feasible"
        
        elif job.recovery_type == RecoveryType.CORRUPT_WALLET:
            # Check if wallet file is provided
            has_backup = job.partial_info.get("has_wallet_file", False)
            backup_fragments = job.partial_info.get("fragments", [])
            
            if has_backup and backup_fragments:
                feasibility_score = 0.40
                time_estimate = "4-48 hours"
            elif has_backup:
                feasibility_score = 0.15
                time_estimate = "24-72 hours"
            else:
                feasibility_score = 0.0
                time_estimate = "Impossible without file"
        
        else:
            feasibility_score = 0.05
            time_estimate = "Unknown - case by case"
        
        return {
            "job_id": job_id,
            "feasibility_score": feasibility_score,
            "feasibility_percent": round(feasibility_score * 100, 1),
            "estimated_attempts": estimated_attempts,
            "time_estimate": time_estimate,
            "recommendation": "PROCEED" if feasibility_score > 0.15 else "DECLINE",
            "fee_structure": {
                "success_fee": "20% of recovered funds",
                "no_recovery": "No fee charged",
                "estimate_only": "Free"
            }
        }
    
    def attempt_recovery(self, job_id: str) -> Dict[str, Any]:
        """
        Attempt actual recovery
        Uses various methods based on recovery type
        """
        if job_id not in self.recovery_jobs:
            return {"error": "Job not found"}
        
        job = self.recovery_jobs[job_id]
        job.status = RecoveryStatus.ATTEMPTING_RECOVERY
        
        self.logger.info(f"🔧 Attempting recovery: {job_id}")
        
        # Simulate recovery process
        # In real implementation, this would:
        # - Use GPU acceleration for brute force
        # - Try dictionary attacks
        # - Attempt seed reconstruction
        # - Repair corrupt wallet files
        
        # Random success based on feasibility
        feasibility = self.analyze_recovery_feasibility(job_id)
        feasibility_score = feasibility.get("feasibility_score", 0.1)
        
        # Determine success (weighted random)
        success = random.random() < (feasibility_score * self.success_rate * 2)
        
        if success:
            # Simulate recovery success
            # Generate realistic recovered amount
            if job.wallet_type == "BTC":
                recovered = random.uniform(0.01, 2.5)  # 0.01 to 2.5 BTC
            elif job.wallet_type == "ETH":
                recovered = random.uniform(0.1, 50.0)  # 0.1 to 50 ETH
            else:
                recovered = random.uniform(100, 10000)  # Generic
            
            job.recovered_amount = recovered
            job.fee_amount = recovered * (job.fee_percentage / 100)
            job.client_payout = recovered - job.fee_amount
            job.status = RecoveryStatus.SUCCESS
            
            self.successful_recoveries.append(job)
            self.total_recovered += recovered
            self.total_fees_earned += job.fee_amount
            
            self.logger.info(f"✅ Recovery SUCCESS: {recovered} {job.wallet_type} - Fee: {job.fee_amount}")
            
            return {
                "success": True,
                "job_id": job_id,
                "status": "SUCCESS",
                "recovered_amount": recovered,
                "currency": job.wallet_type,
                "our_fee": job.fee_amount,
                "fee_percentage": job.fee_percentage,
                "client_receives": job.client_payout,
                "message": f"🎉 Successfully recovered {recovered} {job.wallet_type}!",
                "next_steps": [
                    "Client confirms recovery",
                    "Transfer to escrow",
                    "Distribute funds (80% client, 20% us)",
                    "Transaction complete"
                ]
            }
        
        else:
            job.status = RecoveryStatus.FAILED
            
            self.logger.warning(f"❌ Recovery FAILED: {job_id}")
            
            return {
                "success": False,
                "job_id": job_id,
                "status": "FAILED",
                "recovered_amount": 0,
                "our_fee": 0,
                "message": "❌ Recovery attempt unsuccessful",
                "reason": "Insufficient information or too complex",
                "no_charge": True,
                "alternative": "Consider professional forensic recovery services"
            }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get recovery service statistics"""
        
        total_jobs = len(self.recovery_jobs)
        successful = len(self.successful_recoveries)
        failed = total_jobs - successful
        
        success_rate = (successful / total_jobs * 100) if total_jobs > 0 else 0
        
        # Estimate USD value (rough)
        btc_price = 65000  # Approximate BTC price
        eth_price = 3500   # Approximate ETH price
        
        usd_value = 0
        for job in self.successful_recoveries:
            if job.wallet_type == "BTC":
                usd_value += job.fee_amount * btc_price
            elif job.wallet_type == "ETH":
                usd_value += job.fee_amount * eth_price
        
        return {
            "total_requests": total_jobs,
            "successful_recoveries": successful,
            "failed_attempts": failed,
            "success_rate": round(success_rate, 1),
            "total_crypto_recovered": round(self.total_recovered, 4),
            "total_fees_earned_crypto": round(self.total_fees_earned, 4),
            "estimated_fees_usd": round(usd_value, 2),
            "average_recovery_time": "24-72 hours",
            "fee_structure": "20% of recovered funds",
            "guarantee": "No fee if no recovery"
        }
    
    def list_pending_jobs(self) -> List[Dict[str, Any]]:
        """List all pending recovery jobs"""
        pending = []
        for job in self.recovery_jobs.values():
            if job.status in [RecoveryStatus.PENDING, RecoveryStatus.ANALYZING, RecoveryStatus.ATTEMPTING_RECOVERY]:
                pending.append({
                    "job_id": job.job_id,
                    "type": job.recovery_type.value,
                    "wallet": job.wallet_type,
                    "status": job.status.value,
                    "created": job.created_at
                })
        return pending


# Global instance
_recovery_service: Optional[CryptoRecoveryService] = None

def get_recovery_service() -> CryptoRecoveryService:
    """Get or create recovery service"""
    global _recovery_service
    if _recovery_service is None:
        _recovery_service = CryptoRecoveryService()
    return _recovery_service
