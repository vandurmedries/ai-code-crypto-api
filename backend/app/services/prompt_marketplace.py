"""
Prompt Goldmine Marketplace
Discovers, curates, and sells valuable AI prompts
"""

import os
import json
import hashlib
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging


class PromptCategory(Enum):
    MARKETING = "marketing"
    CODING = "coding"
    WRITING = "writing"
    DESIGN = "design"
    ANALYSIS = "analysis"
    BUSINESS = "business"
    CREATIVE = "creative"


@dataclass
class Prompt:
    prompt_id: str
    title: str
    description: str
    category: PromptCategory
    prompt_text: str
    price: float
    creator_id: str
    quality_score: float  # 0-10
    usage_count: int
    revenue_generated: float
    tags: List[str]
    created_at: str


@dataclass
class PromptDiscovery:
    discovery_id: str
    source: str
    original_prompt: str
    enhanced_version: str
    estimated_value: float
    category: PromptCategory
    discovered_at: str


class PromptMarketplace:
    """
    Marketplace for valuable AI prompts
    Revenue: 20% commission on sales + premium prompt packs
    """
    
    def __init__(self):
        self.prompts: Dict[str, Prompt] = {}
        self.discovered_prompts: Dict[str, PromptDiscovery] = {}
        self.total_sales = 0.0
        self.total_commission = 0.0
        self.logger = logging.getLogger('PromptMarketplace')
        
        # Price ranges by category
        self.price_ranges = {
            PromptCategory.MARKETING: (15.0, 150.0),
            PromptCategory.CODING: (25.0, 250.0),
            PromptCategory.WRITING: (10.0, 100.0),
            PromptCategory.DESIGN: (20.0, 200.0),
            PromptCategory.ANALYSIS: (30.0, 300.0),
            PromptCategory.BUSINESS: (50.0, 500.0),
            PromptCategory.CREATIVE: (15.0, 150.0)
        }
    
    def discover_valuable_prompts(self, source: str = "community") -> List[PromptDiscovery]:
        """
        Discover valuable prompts from various sources
        Analyzes effectiveness, demand, and pricing potential
        """
        discoveries = []
        
        # Simulate discovering high-value prompts
        # In production: Scrape Reddit, Twitter, GitHub, Discord for viral prompts
        
        high_value_prompts = [
            {
                "original": "Write a blog post about [topic]",
                "enhanced": """Act as a senior content strategist. 

CONTEXT:
- Target audience: [describe audience]
- Tone: [professional/casual/technical]
- Goal: [educate/convert/entertain]
- SEO keywords: [list keywords]

OUTPUT:
Create a comprehensive 2000-word blog post with:
1. Hook intro with statistic
2. 5 H2 sections with actionable advice
3. 3 bullet point summaries
4. Strong CTA conclusion

Make it engaging but authoritative.""",
                "category": PromptCategory.WRITING,
                "value": 75.0
            },
            {
                "original": "Debug my code",
                "enhanced": """You are a senior software engineer with 15 years experience.

CODE TO DEBUG:
```[paste code here]```

ANALYZE FOR:
1. Logic errors
2. Performance issues
3. Security vulnerabilities
4. Best practice violations

OUTPUT FORMAT:
- Issue #1: [description]
  - Location: [line number]
  - Severity: [high/medium/low]
  - Fix: [corrected code]
  - Explanation: [why this fixes it]

Provide optimized refactored version at the end.""",
                "category": PromptCategory.CODING,
                "value": 125.0
            },
            {
                "original": "Create a marketing plan",
                "enhanced": """Act as a CMO of a Fortune 500 company.

BUSINESS CONTEXT:
- Product: [describe product]
- Budget: $[amount]
- Timeline: [X months]
- Target market: [demographics]

CREATE:
1. Customer persona (3 detailed profiles)
2. Channel strategy with ROAS projections
3. 90-day content calendar
4. A/B testing roadmap
5. Viral loop mechanisms

Include specific tactics, not generic advice. Be data-driven.""",
                "category": PromptCategory.MARKETING,
                "value": 195.0
            },
            {
                "original": "Analyze my data",
                "enhanced": """You are a data scientist specializing in business intelligence.

DATA CONTEXT:
- Dataset: [describe data]
- Business question: [what to solve]
- Industry: [sector]

PERFORM:
1. Exploratory data analysis
2. Trend identification
3. Anomaly detection
4. Predictive modeling (if applicable)
5. Statistical significance testing

OUTPUT:
- Executive summary (3 bullet points)
- Detailed findings with charts described
- Actionable recommendations ranked by impact
- Risk factors to consider

Use professional business language.""",
                "category": PromptCategory.ANALYSIS,
                "value": 145.0
            }
        ]
        
        for prompt_data in high_value_prompts:
            original_text = prompt_data['original']
            disc_id = f"disc_{hashlib.md5(f'{source}_{original_text}'.encode()).hexdigest()[:8]}"
            
            discovery = PromptDiscovery(
                discovery_id=disc_id,
                source=source,
                original_prompt=prompt_data["original"],
                enhanced_version=prompt_data["enhanced"],
                estimated_value=prompt_data["value"],
                category=prompt_data["category"],
                discovered_at=datetime.utcnow().isoformat()
            )
            
            self.discovered_prompts[disc_id] = discovery
            discoveries.append(discovery)
            
            self.logger.info(f"💎 Discovered valuable prompt: {disc_id} (€{prompt_data['value']})")
        
        return discoveries
    
    def curate_prompt_for_sale(self, discovery_id: str) -> Optional[Prompt]:
        """
        Turn discovered prompt into marketplace listing
        """
        if discovery_id not in self.discovered_prompts:
            return None
        
        discovery = self.discovered_prompts[discovery_id]
        
        # Generate unique ID
        ts = datetime.utcnow().timestamp()
        prompt_id = f"prm_{hashlib.md5(f'{discovery_id}_{ts}'.encode()).hexdigest()[:10]}"
        
        # Calculate price based on value and category
        base_price = discovery.estimated_value
        min_price, max_price = self.price_ranges[discovery.category]
        
        # Price it competitively
        price = min(base_price * 0.8, max_price)  # 20% discount for value
        
        prompt = Prompt(
            prompt_id=prompt_id,
            title=f"{discovery.category.value.title()} Master Prompt",
            description=f"Professional {discovery.category.value} prompt with proven results. Saves 5-10 hours per use.",
            category=discovery.category,
            prompt_text=discovery.enhanced_version,
            price=round(price, 2),
            creator_id="platform_curated",
            quality_score=random.uniform(8.5, 9.8),
            usage_count=0,
            revenue_generated=0.0,
            tags=[discovery.category.value, "high-converting", "professional", "time-saving"],
            created_at=datetime.utcnow().isoformat()
        )
        
        self.prompts[prompt_id] = prompt
        
        self.logger.info(f"✅ Curated prompt for sale: {prompt_id} @ €{price}")
        
        return prompt
    
    def simulate_sale(self, prompt_id: str) -> Dict[str, Any]:
        """
        Simulate a prompt sale
        """
        if prompt_id not in self.prompts:
            return {"error": "Prompt not found"}
        
        prompt = self.prompts[prompt_id]
        
        # Simulate purchase
        prompt.usage_count += 1
        prompt.revenue_generated += prompt.price
        
        # Calculate commission (20% to platform, 80% to creator/pool)
        commission = prompt.price * 0.20
        creator_earning = prompt.price * 0.80
        
        self.total_sales += prompt.price
        self.total_commission += commission
        
        self.logger.info(f"💰 Prompt sold: {prompt_id} (€{prompt.price}), commission: €{commission}")
        
        return {
            "success": True,
            "prompt_id": prompt_id,
            "sale_price": prompt.price,
            "platform_commission": round(commission, 2),
            "creator_earning": round(creator_earning, 2),
            "total_usage": prompt.usage_count,
            "prompt_title": prompt.title
        }
    
    def batch_simulate_sales(self, count: int = 10) -> Dict[str, Any]:
        """
        Simulate multiple sales for revenue generation
        """
        total_revenue = 0.0
        total_commission = 0.0
        sales_made = []
        
        # Get available prompts
        available_prompts = list(self.prompts.values())
        
        if not available_prompts:
            return {"error": "No prompts available for sale"}
        
        for i in range(count):
            # Random prompt
            prompt = random.choice(available_prompts)
            
            result = self.simulate_sale(prompt.prompt_id)
            if result.get("success"):
                total_revenue += result["sale_price"]
                total_commission += result["platform_commission"]
                sales_made.append(result)
        
        return {
            "total_sales": count,
            "total_revenue": round(total_revenue, 2),
            "total_commission": round(total_commission, 2),
            "details": sales_made
        }
    
    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        
        # Calculate metrics
        avg_price = sum(p.price for p in self.prompts.values()) / len(self.prompts) if self.prompts else 0
        avg_quality = sum(p.quality_score for p in self.prompts.values()) / len(self.prompts) if self.prompts else 0
        total_usage = sum(p.usage_count for p in self.prompts.values())
        
        by_category = {}
        for cat in PromptCategory:
            cat_prompts = [p for p in self.prompts.values() if p.category == cat]
            if cat_prompts:
                by_category[cat.value] = {
                    "count": len(cat_prompts),
                    "avg_price": round(sum(p.price for p in cat_prompts) / len(cat_prompts), 2),
                    "total_revenue": round(sum(p.revenue_generated for p in cat_prompts), 2)
                }
        
        return {
            "total_prompts": len(self.prompts),
            "total_discovered": len(self.discovered_prompts),
            "total_sales_revenue": round(self.total_sales, 2),
            "total_commission_earned": round(self.total_commission, 2),
            "average_prompt_price": round(avg_price, 2),
            "average_quality_score": round(avg_quality, 2),
            "total_usage_count": total_usage,
            "by_category": by_category,
            "business_model": "20% commission on prompt sales",
            "autonomous_curation": True
        }
    
    def get_top_performing_prompts(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing prompts by revenue"""
        
        sorted_prompts = sorted(
            self.prompts.values(),
            key=lambda p: p.revenue_generated,
            reverse=True
        )[:limit]
        
        return [
            {
                "prompt_id": p.prompt_id,
                "title": p.title,
                "category": p.category.value,
                "price": p.price,
                "sales": p.usage_count,
                "revenue": round(p.revenue_generated, 2),
                "quality": round(p.quality_score, 2)
            }
            for p in sorted_prompts
        ]


# Global instance
_prompt_marketplace: Optional[PromptMarketplace] = None

def get_prompt_marketplace() -> PromptMarketplace:
    """Get or create prompt marketplace"""
    global _prompt_marketplace
    if _prompt_marketplace is None:
        _prompt_marketplace = PromptMarketplace()
    return _prompt_marketplace
