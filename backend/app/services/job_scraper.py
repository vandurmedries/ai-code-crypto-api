"""
Job Scraper for Platforms Without APIs
Uses Selenium to scrape job listings from:
- LinkedIn Jobs
- Indeed
- We Work Remotely
- Remote.co
- AngelList / Wellfound
- And more
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urljoin, quote_plus

from .selenium_automation import SeleniumAutomation, AutomationResult

logger = logging.getLogger('JobScraper')


@dataclass
class ScrapedJob:
    """A job scraped from a website"""
    title: str
    company: str
    location: str
    description: str
    url: str
    platform: str
    salary: Optional[str] = None
    posted_date: Optional[str] = None
    job_type: Optional[str] = None  # full-time, contract, etc.
    remote: bool = False
    skills: List[str] = None
    scraped_at: str = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.utcnow().isoformat()
        if self.skills is None:
            self.skills = []


class LinkedInJobScraper:
    """Scraper for LinkedIn Jobs"""
    
    BASE_URL = "https://www.linkedin.com/jobs"
    
    def __init__(self, selenium: SeleniumAutomation):
        self.selenium = selenium
    
    def search_jobs(self, keywords: str, location: str = "",
                    experience_level: str = None,  # entry, associate, mid-senior, etc.
                    job_type: str = None,  # full-time, contract, part-time
                    remote: bool = True,
                    max_results: int = 25) -> List[ScrapedJob]:
        """
        Search LinkedIn Jobs
        
        Note: LinkedIn requires login for full functionality.
        This scraper works best when authenticated.
        """
        jobs = []
        
        try:
            # Build search URL
            query = quote_plus(keywords)
            loc = quote_plus(location)
            
            url = f"{self.BASE_URL}/search?keywords={query}&location={loc}"
            
            if remote:
                url += "&f_WT=2"  # Remote filter
            
            if experience_level:
                level_map = {
                    "entry": "1",
                    "associate": "2",
                    "mid-senior": "3",
                    "director": "4",
                    "executive": "5"
                }
                if experience_level in level_map:
                    url += f"&f_E={level_map[experience_level]}"
            
            # Navigate to search
            result = self.selenium.check_website_status(url)
            if not result.success:
                logger.error(f"Failed to load LinkedIn jobs: {result.message}")
                return []
            
            driver = self.selenium.driver
            
            # Scroll to load more jobs
            self.selenium.auto_scroll(
                url=url,
                scroll_count=min(max_results // 5, 10),
                scroll_pixels=800,
                wait_between=1.5
            )
            
            # Scrape job cards
            # LinkedIn job card selectors
            job_cards = driver.find_elements(
                "css selector",
                ".job-search-card, .jobs-search-results__list-item, [data-job-id]"
            )
            
            for card in job_cards[:max_results]:
                try:
                    # Extract job data
                    title_elem = card.find_element(
                        "css selector",
                        ".job-search-card__title, .job-card-list__title, h3"
                    )
                    title = title_elem.text if title_elem else "Unknown Title"
                    
                    company_elem = card.find_element(
                        "css selector",
                        ".job-search-card__company-name, .job-card-container__company-name"
                    )
                    company = company_elem.text if company_elem else "Unknown Company"
                    
                    location_elem = card.find_element(
                        "css selector",
                        ".job-search-card__location, .job-card-container__metadata-item"
                    )
                    location_text = location_elem.text if location_elem else ""
                    
                    # Check if remote
                    is_remote = "remote" in location_text.lower() or remote
                    
                    # Get job URL
                    link_elem = card.find_element("css selector", "a")
                    job_url = link_elem.get_attribute("href") if link_elem else ""
                    
                    # Get posted date
                    date_elem = card.find_element(
                        "css selector",
                        ".job-search-card__listdate, time"
                    )
                    posted = date_elem.text if date_elem else None
                    
                    job = ScrapedJob(
                        title=title,
                        company=company,
                        location=location_text,
                        description="",  # Would need to click to get full description
                        url=job_url,
                        platform="linkedin",
                        posted_date=posted,
                        remote=is_remote
                    )
                    jobs.append(job)
                    
                except Exception as e:
                    logger.debug(f"Error parsing LinkedIn job card: {e}")
                    continue
            
            logger.info(f"✅ Scraped {len(jobs)} jobs from LinkedIn")
            return jobs
            
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}")
            return jobs


class IndeedJobScraper:
    """Scraper for Indeed"""
    
    BASE_URL = "https://www.indeed.com/jobs"
    
    def __init__(self, selenium: SeleniumAutomation):
        self.selenium = selenium
    
    def search_jobs(self, query: str, location: str = "",
                    remote: bool = True,
                    max_results: int = 25) -> List[ScrapedJob]:
        """Search Indeed Jobs"""
        jobs = []
        
        try:
            # Build URL
            q = quote_plus(query)
            l = quote_plus(location)
            url = f"{self.BASE_URL}?q={q}&l={l}"
            
            if remote:
                url += "&remotejob=032b3046-06a3-4876-8dfd-c08f8177096d"
            
            # Load page
            self.selenium.driver.get(url)
            import time
            time.sleep(3)
            
            driver = self.selenium.driver
            
            # Find job cards
            job_cards = driver.find_elements(
                "css selector",
                ".slider_container .slider_item, [data-testid='jobTitle']"
            )
            
            for card in job_cards[:max_results]:
                try:
                    # Title
                    title_elem = card.find_element(
                        "css selector",
                        "h2 a span, .jobTitle span"
                    )
                    title = title_elem.text if title_elem else "Unknown"
                    
                    # Company
                    company_elem = card.find_element(
                        "css selector",
                        ".companyName, [data-testid='company-name']"
                    )
                    company = company_elem.text if company_elem else "Unknown"
                    
                    # Location
                    location_elem = card.find_element(
                        "css selector",
                        ".companyLocation, [data-testid='job-location']"
                    )
                    loc = location_elem.text if location_elem else ""
                    
                    # Salary
                    salary_elem = card.find_element(
                        "css selector",
                        ".salary-snippet-container, [data-testid='job-salary']"
                    )
                    salary = salary_elem.text if salary_elem else None
                    
                    # Job URL
                    link_elem = card.find_element("css selector", "h2 a")
                    job_url = link_elem.get_attribute("href") if link_elem else ""
                    
                    # Snippet
                    snippet_elem = card.find_element(
                        "css selector",
                        ".job-snippet, .summary"
                    )
                    snippet = snippet_elem.text if snippet_elem else ""
                    
                    job = ScrapedJob(
                        title=title,
                        company=company,
                        location=loc,
                        description=snippet,
                        url=job_url,
                        platform="indeed",
                        salary=salary,
                        remote="remote" in loc.lower() or remote
                    )
                    jobs.append(job)
                    
                except Exception as e:
                    logger.debug(f"Error parsing Indeed job card: {e}")
                    continue
            
            logger.info(f"✅ Scraped {len(jobs)} jobs from Indeed")
            return jobs
            
        except Exception as e:
            logger.error(f"Indeed scraping error: {e}")
            return jobs


class WeWorkRemotelyScraper:
    """Scraper for We Work Remotely"""
    
    BASE_URL = "https://weworkremotely.com"
    
    def __init__(self, selenium: SeleniumAutomation):
        self.selenium = selenium
    
    def search_jobs(self, category: str = "programming",
                    max_results: int = 25) -> List[ScrapedJob]:
        """Search We Work Remotely (all jobs are remote)"""
        jobs = []
        
        try:
            url = f"{self.BASE_URL}/categories/{category}"
            
            self.selenium.driver.get(url)
            import time
            time.sleep(2)
            
            driver = self.selenium.driver
            
            # Find job listings
            job_elements = driver.find_elements(
                "css selector",
                ".jobs li, article"
            )
            
            for elem in job_elements[:max_results]:
                try:
                    # Company (first span/element)
                    company_elem = elem.find_element("css selector", ".company, .title")
                    company = company_elem.text if company_elem else "Unknown"
                    
                    # Title
                    title_elem = elem.find_element("css selector", ".title, h4, a span")
                    title = title_elem.text if title_elem else "Unknown"
                    
                    # Link
                    link_elem = elem.find_element("css selector", "a")
                    job_url = link_elem.get_attribute("href") if link_elem else ""
                    if job_url and not job_url.startswith("http"):
                        job_url = urljoin(self.BASE_URL, job_url)
                    
                    # Tags/Job Type
                    tags_elems = elem.find_elements("css selector", ".tag, .region")
                    tags = [t.text for t in tags_elems if t.text]
                    
                    job = ScrapedJob(
                        title=title,
                        company=company,
                        location="Remote",
                        description="",
                        url=job_url,
                        platform="weworkremotely",
                        remote=True,
                        job_type=tags[0] if tags else None,
                        skills=tags
                    )
                    jobs.append(job)
                    
                except Exception as e:
                    logger.debug(f"Error parsing WWR job: {e}")
                    continue
            
            logger.info(f"✅ Scraped {len(jobs)} jobs from We Work Remotely")
            return jobs
            
        except Exception as e:
            logger.error(f"WWR scraping error: {e}")
            return jobs


class RemoteCoScraper:
    """Scraper for Remote.co"""
    
    BASE_URL = "https://remote.co"
    
    def __init__(self, selenium: SeleniumAutomation):
        self.selenium = selenium
    
    def search_jobs(self, category: str = "developer",
                    max_results: int = 25) -> List[ScrapedJob]:
        """Search Remote.co jobs"""
        jobs = []
        
        try:
            url = f"{self.BASE_URL}/remote-jobs/{category}/"
            
            self.selenium.driver.get(url)
            import time
            time.sleep(2)
            
            driver = self.selenium.driver
            
            # Find job cards
            job_cards = driver.find_elements("css selector", ".job_card")
            
            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find_element("css selector", ".job_title")
                    title = title_elem.text if title_elem else "Unknown"
                    
                    company_elem = card.find_element("css selector", ".company_name")
                    company = company_elem.text if company_elem else "Unknown"
                    
                    link_elem = card.find_element("css selector", "a")
                    job_url = link_elem.get_attribute("href") if link_elem else ""
                    
                    job = ScrapedJob(
                        title=title,
                        company=company,
                        location="Remote",
                        description="",
                        url=job_url,
                        platform="remoteco",
                        remote=True
                    )
                    jobs.append(job)
                    
                except Exception as e:
                    logger.debug(f"Error parsing Remote.co job: {e}")
                    continue
            
            logger.info(f"✅ Scraped {len(jobs)} jobs from Remote.co")
            return jobs
            
        except Exception as e:
            logger.error(f"Remote.co scraping error: {e}")
            return jobs


class FreelanceJobAggregator:
    """
    Aggregates jobs from multiple sources:
    - API-based platforms (Upwork, Fiverr, Toptal)
    - Scraped platforms (LinkedIn, Indeed, WWR, etc.)
    """
    
    def __init__(self):
        self.selenium = SeleniumAutomation(headless=True)
        self.scrapers = {
            "linkedin": LinkedInJobScraper(self.selenium),
            "indeed": IndeedJobScraper(self.selenium),
            "weworkremotely": WeWorkRemotelyScraper(self.selenium),
            "remoteco": RemoteCoScraper(self.selenium)
        }
    
    def search_all_sources(self, query: str, location: str = "",
                          remote_only: bool = True,
                          max_per_source: int = 10) -> Dict[str, List[ScrapedJob]]:
        """Search all available job sources"""
        results = {}
        
        for source_name, scraper in self.scrapers.items():
            try:
                if source_name in ["linkedin", "indeed"]:
                    jobs = scraper.search_jobs(
                        keywords=query,
                        location=location,
                        remote=remote_only,
                        max_results=max_per_source
                    )
                else:
                    # Category-based scrapers
                    category = "programming" if "programming" in query.lower() else "developer"
                    jobs = scraper.search_jobs(
                        category=category,
                        max_results=max_per_source
                    )
                
                results[source_name] = jobs
                
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
                results[source_name] = []
        
        return results
    
    def get_best_opportunities(self, query: str = "python developer",
                               min_salary: str = None,
                               remote_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get best opportunities across all sources with scoring
        """
        all_jobs = self.search_all_sources(
            query=query,
            remote_only=remote_only,
            max_per_source=15
        )
        
        opportunities = []
        
        for source, jobs in all_jobs.items():
            for job in jobs:
                # Calculate opportunity score
                score = 0
                reasons = []
                
                # Remote work bonus
                if job.remote:
                    score += 5
                    reasons.append("Remote work")
                
                # Salary indicator
                if job.salary:
                    score += 3
                    reasons.append("Salary disclosed")
                    
                    # Parse salary if possible
                    try:
                        salary_nums = re.findall(r'\$?[\d,]+', job.salary)
                        if salary_nums:
                            max_salary = max(
                                int(n.replace(",", "").replace("$", ""))
                                for n in salary_nums if n.replace(",", "").replace("$", "").isdigit()
                            )
                            if max_salary > 100000:
                                score += 5
                                reasons.append("High salary range")
                    except:
                        pass
                
                # Company reputation (would need external data in production)
                if job.company and any(word in job.company.lower() for word in ["google", "amazon", "microsoft", "meta", "apple"]):
                    score += 3
                    reasons.append("Well-known company")
                
                # Title relevance
                title_lower = job.title.lower()
                if "senior" in title_lower or "lead" in title_lower or "principal" in title_lower:
                    score += 2
                    reasons.append("Senior position")
                
                opportunities.append({
                    "job": asdict(job),
                    "source": source,
                    "score": score,
                    "match_reasons": reasons,
                    "estimated_quality": "high" if score >= 10 else "medium" if score >= 5 else "low"
                })
        
        # Sort by score
        opportunities.sort(key=lambda x: x["score"], reverse=True)
        
        return opportunities
    
    def close(self):
        """Clean up resources"""
        self.selenium.close()


# Global instance
_job_aggregator: Optional[FreelanceJobAggregator] = None

def get_job_scraper() -> FreelanceJobAggregator:
    """Get or create job scraper instance"""
    global _job_aggregator
    if _job_aggregator is None:
        _job_aggregator = FreelanceJobAggregator()
    return _job_aggregator


if __name__ == "__main__":
    print("=" * 70)
    print("JOB SCRAPER TEST")
    print("=" * 70)
    
    scraper = FreelanceJobAggregator()
    
    # Test We Work Remotely (doesn't require auth)
    print("\n1. Testing We Work Remotely Scraper")
    wwr = WeWorkRemotelyScraper(scraper.selenium)
    jobs = wwr.search_jobs(category="programming", max_results=5)
    
    print(f"   Found {len(jobs)} jobs")
    for job in jobs[:3]:
        print(f"   - {job.title} at {job.company}")
    
    # Show best opportunities scoring
    print("\n2. Testing Opportunity Scoring")
    opportunities = scraper.get_best_opportunities(
        query="python developer",
        remote_only=True
    )
    
    print(f"   Total opportunities found: {len(opportunities)}")
    if opportunities:
        best = opportunities[0]
        print(f"   Best match: {best['job']['title']}")
        print(f"   Score: {best['score']}")
        print(f"   Reasons: {', '.join(best['match_reasons'])}")
    
    scraper.close()
    
    print("\n" + "=" * 70)
    print("Job scraper test complete")
    print("=" * 70)
