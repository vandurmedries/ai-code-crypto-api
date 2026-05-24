"""
Auto-Apply Service
Automatically fills and submits job applications using Selenium
Works with LinkedIn Easy Apply, Indeed, and generic application forms
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    NoSuchElementException, ElementNotInteractableException,
    TimeoutException
)

from .selenium_automation import SeleniumAutomation, AutomationResult

logger = logging.getLogger('AutoApply')


@dataclass
class ApplicationResult:
    """Result of a job application"""
    success: bool
    platform: str
    job_url: str
    message: str
    submitted_at: str
    screenshot_path: Optional[str] = None
    form_fields_filled: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class UserProfile:
    """User profile for auto-filling applications"""
    
    def __init__(self, profile_data: Dict[str, Any]):
        self.first_name = profile_data.get("first_name", "")
        self.last_name = profile_data.get("last_name", "")
        self.email = profile_data.get("email", "")
        self.phone = profile_data.get("phone", "")
        self.linkedin_url = profile_data.get("linkedin_url", "")
        self.portfolio_url = profile_data.get("portfolio_url", "")
        self.github_url = profile_data.get("github_url", "")
        self.location = profile_data.get("location", "")
        self.years_experience = profile_data.get("years_experience", "")
        self.skills = profile_data.get("skills", [])
        self.summary = profile_data.get("summary", "")
        self.resume_path = profile_data.get("resume_path", "")
        
        # Cover letter templates
        self.cover_letter_template = profile_data.get("cover_letter_template", "")


class LinkedInEasyApply:
    """LinkedIn Easy Apply automation"""
    
    def __init__(self, selenium: SeleniumAutomation):
        self.selenium = selenium
    
    def apply_to_job(self, job_url: str, profile: UserProfile,
                     custom_cover_letter: str = None) -> ApplicationResult:
        """
        Apply to a LinkedIn job using Easy Apply
        
        Args:
            job_url: LinkedIn job posting URL
            profile: User profile data
            custom_cover_letter: Optional custom cover letter text
        """
        errors = []
        fields_filled = 0
        
        try:
            driver = self.selenium.driver
            if not driver:
                self.selenium._setup_driver()
                driver = self.selenium.driver
            
            # Navigate to job
            driver.get(job_url)
            time.sleep(3)
            
            # Check if Easy Apply button exists
            easy_apply_btn = self.selenium._safe_find(
                By.CSS_SELECTOR,
                ".jobs-apply-button, [data-control-name='jobdetails_topcard_inapply']",
                timeout=5
            )
            
            if not easy_apply_btn:
                return ApplicationResult(
                    success=False,
                    platform="linkedin",
                    job_url=job_url,
                    message="Easy Apply button not found - may require external application",
                    submitted_at=datetime.utcnow().isoformat()
                )
            
            # Click Easy Apply
            self.selenium._safe_click(easy_apply_btn)
            time.sleep(2)
            
            # Handle multi-step application form
            max_steps = 10
            for step in range(max_steps):
                try:
                    # Fill contact info (step 1 usually)
                    fields_filled += self._fill_contact_info(profile)
                    
                    # Fill resume upload if present
                    self._handle_resume_upload(profile)
                    
                    # Fill additional questions
                    fields_filled += self._fill_questions(profile)
                    
                    # Check for next/submit button
                    next_btn = self.selenium._safe_find(
                        By.CSS_SELECTOR,
                        "button[aria-label='Continue to next step'], " +
                        "button[aria-label='Review your application'], " +
                        "button[aria-label='Submit application']",
                        timeout=3
                    )
                    
                    if next_btn:
                        btn_text = next_btn.text.lower()
                        self.selenium._safe_click(next_btn)
                        time.sleep(2)
                        
                        # Check if submit was successful
                        if "submit" in btn_text:
                            # Take success screenshot
                            screenshot = self.selenium._take_screenshot(
                                f"linkedin_apply_success_{int(time.time())}"
                            )
                            
                            return ApplicationResult(
                                success=True,
                                platform="linkedin",
                                job_url=job_url,
                                message="Application submitted successfully via LinkedIn Easy Apply",
                                submitted_at=datetime.utcnow().isoformat(),
                                screenshot_path=screenshot,
                                form_fields_filled=fields_filled
                            )
                    else:
                        break
                        
                except Exception as e:
                    errors.append(f"Step {step} error: {str(e)}")
                    continue
            
            # If we get here, we didn't complete the application
            return ApplicationResult(
                success=False,
                platform="linkedin",
                job_url=job_url,
                message="Application incomplete - manual review required",
                submitted_at=datetime.utcnow().isoformat(),
                form_fields_filled=fields_filled,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"LinkedIn Easy Apply error: {e}")
            return ApplicationResult(
                success=False,
                platform="linkedin",
                job_url=job_url,
                message=f"Error: {str(e)}",
                submitted_at=datetime.utcnow().isoformat(),
                errors=errors + [str(e)]
            )
    
    def _fill_contact_info(self, profile: UserProfile) -> int:
        """Fill contact information fields"""
        fields_filled = 0
        
        # First name
        try:
            fname = self.selenium.driver.find_element(By.NAME, "firstName")
            if not fname.get_attribute("value"):
                fname.clear()
                fname.send_keys(profile.first_name)
                fields_filled += 1
        except:
            pass
        
        # Last name
        try:
            lname = self.selenium.driver.find_element(By.NAME, "lastName")
            if not lname.get_attribute("value"):
                lname.clear()
                lname.send_keys(profile.last_name)
                fields_filled += 1
        except:
            pass
        
        # Email
        try:
            email = self.selenium.driver.find_element(By.NAME, "email")
            if not email.get_attribute("value"):
                email.clear()
                email.send_keys(profile.email)
                fields_filled += 1
        except:
            pass
        
        # Phone
        try:
            phone = self.selenium.driver.find_element(By.NAME, "phone")
            if not phone.get_attribute("value") and profile.phone:
                phone.clear()
                phone.send_keys(profile.phone)
                fields_filled += 1
        except:
            pass
        
        return fields_filled
    
    def _handle_resume_upload(self, profile: UserProfile):
        """Handle resume file upload"""
        if not profile.resume_path or not os.path.exists(profile.resume_path):
            return
        
        try:
            # Look for file input
            file_input = self.selenium.driver.find_element(
                By.CSS_SELECTOR,
                "input[type='file'], input[name='resume']"
            )
            file_input.send_keys(profile.resume_path)
            time.sleep(1)
        except:
            pass
    
    def _fill_questions(self, profile: UserProfile) -> int:
        """Fill additional screening questions"""
        fields_filled = 0
        
        # Common question patterns
        question_patterns = [
            ("experience", profile.years_experience),
            ("location", profile.location),
            ("email", profile.email),
            ("phone", profile.phone)
        ]
        
        for pattern, value in question_patterns:
            try:
                # Find inputs that might match this pattern
                inputs = self.selenium.driver.find_elements(
                    By.CSS_SELECTOR,
                    f"input[name*='{pattern}' i], textarea[name*='{pattern}' i]"
                )
                
                for inp in inputs:
                    if not inp.get_attribute("value") and value:
                        inp.clear()
                        inp.send_keys(value)
                        fields_filled += 1
            except:
                continue
        
        # Handle yes/no questions - default to yes
        try:
            radio_yes = self.selenium.driver.find_elements(
                By.CSS_SELECTOR,
                "input[type='radio'][value='yes'], input[type='radio'][value='true']"
            )
            for radio in radio_yes:
                if not radio.is_selected():
                    radio.click()
                    fields_filled += 1
        except:
            pass
        
        return fields_filled


class IndeedApply:
    """Indeed Apply automation"""
    
    def __init__(self, selenium: SeleniumAutomation):
        self.selenium = selenium
    
    def apply_to_job(self, job_url: str, profile: UserProfile) -> ApplicationResult:
        """Apply to a job on Indeed"""
        errors = []
        
        try:
            driver = self.selenium.driver
            if not driver:
                self.selenium._setup_driver()
                driver = self.selenium.driver
            
            driver.get(job_url)
            time.sleep(3)
            
            # Find and click apply button
            apply_btn = self.selenium._safe_find(
                By.CSS_SELECTOR,
                "#indeedApplyButton, .indeed-apply-button, [data-testid='apply-button']",
                timeout=5
            )
            
            if not apply_btn:
                return ApplicationResult(
                    success=False,
                    platform="indeed",
                    job_url=job_url,
                    message="Apply button not found",
                    submitted_at=datetime.utcnow().isoformat()
                )
            
            self.selenium._safe_click(apply_btn)
            time.sleep(3)
            
            # Indeed apply opens in iframe or new window
            # Try to switch to application iframe
            try:
                iframe = driver.find_element(By.CSS_SELECTOR, "iframe[name*='indeedapply']")
                driver.switch_to.frame(iframe)
                time.sleep(2)
            except:
                pass
            
            # Fill application form
            fields_filled = self._fill_indeed_form(profile)
            
            # Look for submit button
            submit_btn = self.selenium._safe_find(
                By.CSS_SELECTOR,
                "button[type='submit'], .ia-ApplyButton, [data-testid='send-button']",
                timeout=5
            )
            
            if submit_btn:
                self.selenium._safe_click(submit_btn)
                time.sleep(3)
                
                screenshot = self.selenium._take_screenshot(
                    f"indeed_apply_{int(time.time())}"
                )
                
                return ApplicationResult(
                    success=True,
                    platform="indeed",
                    job_url=job_url,
                    message="Application submitted on Indeed",
                    submitted_at=datetime.utcnow().isoformat(),
                    screenshot_path=screenshot,
                    form_fields_filled=fields_filled
                )
            
            return ApplicationResult(
                success=False,
                platform="indeed",
                job_url=job_url,
                message="Submit button not found",
                submitted_at=datetime.utcnow().isoformat(),
                form_fields_filled=fields_filled
            )
            
        except Exception as e:
            logger.error(f"Indeed apply error: {e}")
            return ApplicationResult(
                success=False,
                platform="indeed",
                job_url=job_url,
                message=f"Error: {str(e)}",
                submitted_at=datetime.utcnow().isoformat(),
                errors=errors + [str(e)]
            )
    
    def _fill_indeed_form(self, profile: UserProfile) -> int:
        """Fill Indeed application form"""
        fields_filled = 0
        
        # Common field mappings
        field_map = {
            "name": f"{profile.first_name} {profile.last_name}",
            "email": profile.email,
            "phone": profile.phone,
            "resume": profile.resume_path
        }
        
        for field_name, value in field_map.items():
            try:
                # Try different selectors
                selectors = [
                    f"input[name='{field_name}']",
                    f"input[id*='{field_name}' i]",
                    f"input[placeholder*='{field_name}' i]"
                ]
                
                for selector in selectors:
                    try:
                        field = self.selenium.driver.find_element(By.CSS_SELECTOR, selector)
                        if field.tag_name == "input" and field.get_attribute("type") == "file":
                            if value and os.path.exists(value):
                                field.send_keys(value)
                                fields_filled += 1
                        else:
                            if not field.get_attribute("value") and value:
                                field.clear()
                                field.send_keys(value)
                                fields_filled += 1
                        break
                    except:
                        continue
            except:
                continue
        
        return fields_filled


class GenericApplicationFiller:
    """Fills generic job application forms on company career pages"""
    
    def __init__(self, selenium: SeleniumAutomation):
        self.selenium = selenium
    
    def apply(self, job_url: str, profile: UserProfile,
              form_config: Dict[str, str] = None) -> ApplicationResult:
        """
        Apply to a job on a generic career page
        
        Args:
            job_url: Job posting URL
            profile: User profile
            form_config: Custom field mappings {field_name: css_selector}
        """
        errors = []
        fields_filled = 0
        
        try:
            driver = self.selenium.driver
            if not driver:
                self.selenium._setup_driver()
                driver = self.selenium.driver
            
            driver.get(job_url)
            time.sleep(3)
            
            # Common field patterns and their likely selectors
            default_mappings = {
                "first_name": ["input[name*='first' i]", "#firstName", "#fname", "[placeholder*='first' i]"],
                "last_name": ["input[name*='last' i]", "#lastName", "#lname", "[placeholder*='last' i]"],
                "email": ["input[type='email']", "input[name*='email' i]", "#email"],
                "phone": ["input[type='tel']", "input[name*='phone' i]", "#phone"],
                "resume": ["input[type='file']", "input[name*='resume' i]", "input[name*='cv' i]"],
                "cover_letter": ["textarea[name*='cover' i]", "textarea[name*='letter' i]", "#coverLetter"],
                "linkedin": ["input[name*='linkedin' i]", "#linkedin"],
                "website": ["input[name*='website' i]", "input[name*='portfolio' i]", "#website"],
                "location": ["input[name*='location' i]", "input[name*='city' i]"]
            }
            
            # Merge with custom config
            if form_config:
                for key, selector in form_config.items():
                    default_mappings[key] = [selector]
            
            # Fill each field
            for field_name, selectors in default_mappings.items():
                value = getattr(profile, field_name, None)
                if not value:
                    continue
                
                for selector in selectors:
                    try:
                        field = self.selenium._safe_find(By.CSS_SELECTOR, selector, timeout=2)
                        if field:
                            # Handle file upload
                            if field.get_attribute("type") == "file":
                                if os.path.exists(value):
                                    field.send_keys(value)
                                    fields_filled += 1
                            else:
                                # Regular text input
                                if not field.get_attribute("value"):
                                    field.clear()
                                    field.send_keys(value)
                                    fields_filled += 1
                            break
                    except:
                        continue
            
            # Look for submit button
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Apply')",
                "button:contains('Submit')",
                ".apply-button",
                "#submit"
            ]
            
            submit_btn = None
            for selector in submit_selectors:
                submit_btn = self.selenium._safe_find(By.CSS_SELECTOR, selector, timeout=2)
                if submit_btn:
                    break
            
            if submit_btn:
                # Take screenshot before submitting
                screenshot = self.selenium._take_screenshot(
                    f"before_submit_{int(time.time())}"
                )
                
                # Submit
                self.selenium._safe_click(submit_btn)
                time.sleep(3)
                
                return ApplicationResult(
                    success=True,
                    platform="generic",
                    job_url=job_url,
                    message="Application submitted",
                    submitted_at=datetime.utcnow().isoformat(),
                    screenshot_path=screenshot,
                    form_fields_filled=fields_filled
                )
            
            return ApplicationResult(
                success=False,
                platform="generic",
                job_url=job_url,
                message="Could not find submit button",
                submitted_at=datetime.utcnow().isoformat(),
                form_fields_filled=fields_filled
            )
            
        except Exception as e:
            logger.error(f"Generic application error: {e}")
            return ApplicationResult(
                success=False,
                platform="generic",
                job_url=job_url,
                message=f"Error: {str(e)}",
                submitted_at=datetime.utcnow().isoformat(),
                form_fields_filled=fields_filled,
                errors=errors + [str(e)]
            )


class AutoApplyManager:
    """
    Manages auto-apply functionality across multiple platforms
    """
    
    def __init__(self):
        self.selenium = SeleniumAutomation(headless=True)
        self.linkedin = LinkedInEasyApply(self.selenium)
        self.indeed = IndeedApply(self.selenium)
        self.generic = GenericApplicationFiller(self.selenium)
        
        self.application_history: List[ApplicationResult] = []
    
    def apply_to_job(self, job_url: str, profile: UserProfile,
                     platform: str = None) -> ApplicationResult:
        """
        Apply to a job, auto-detecting platform if not specified
        
        Args:
            job_url: Job posting URL
            profile: User profile
            platform: 'linkedin', 'indeed', or None for auto-detect
        """
        # Auto-detect platform from URL
        if not platform:
            url_lower = job_url.lower()
            if "linkedin.com" in url_lower:
                platform = "linkedin"
            elif "indeed.com" in url_lower:
                platform = "indeed"
            else:
                platform = "generic"
        
        # Route to appropriate handler
        if platform == "linkedin":
            result = self.linkedin.apply_to_job(job_url, profile)
        elif platform == "indeed":
            result = self.indeed.apply_to_job(job_url, profile)
        else:
            result = self.generic.apply(job_url, profile)
        
        # Track application
        self.application_history.append(result)
        
        return result
    
    def bulk_apply(self, job_urls: List[str], profile: UserProfile,
                   delay_between: int = 30) -> List[ApplicationResult]:
        """
        Apply to multiple jobs with delay between applications
        
        Args:
            job_urls: List of job URLs
            profile: User profile
            delay_between: Seconds to wait between applications
        """
        results = []
        
        for i, url in enumerate(job_urls):
            logger.info(f"Applying to job {i+1}/{len(job_urls)}: {url}")
            
            result = self.apply_to_job(url, profile)
            results.append(result)
            
            # Delay between applications (to not trigger rate limits)
            if i < len(job_urls) - 1:
                time.sleep(delay_between)
        
        return results
    
    def get_application_stats(self) -> Dict[str, Any]:
        """Get statistics on applications submitted"""
        total = len(self.application_history)
        successful = sum(1 for r in self.application_history if r.success)
        by_platform = {}
        
        for app in self.application_history:
            platform = app.platform
            if platform not in by_platform:
                by_platform[platform] = {"total": 0, "success": 0}
            by_platform[platform]["total"] += 1
            if app.success:
                by_platform[platform]["success"] += 1
        
        return {
            "total_applications": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": round(successful / total * 100, 1) if total > 0 else 0,
            "by_platform": by_platform,
            "recent_applications": [
                {
                    "platform": app.platform,
                    "success": app.success,
                    "submitted_at": app.submitted_at,
                    "message": app.message
                }
                for app in self.application_history[-5:]
            ]
        }
    
    def close(self):
        """Clean up resources"""
        self.selenium.close()


# Global instance
_auto_apply_manager: Optional[AutoApplyManager] = None

def get_auto_apply_manager() -> AutoApplyManager:
    """Get or create auto-apply manager"""
    global _auto_apply_manager
    if _auto_apply_manager is None:
        _auto_apply_manager = AutoApplyManager()
    return _auto_apply_manager


if __name__ == "__main__":
    print("=" * 70)
    print("AUTO-APPLY SERVICE TEST")
    print("=" * 70)
    
    # Note: This requires valid job URLs and profile to test fully
    print("""
To test auto-apply functionality:

1. Create a UserProfile:
   profile = UserProfile({
       "first_name": "John",
       "last_name": "Doe",
       "email": "john@example.com",
       "phone": "+1234567890",
       "linkedin_url": "https://linkedin.com/in/johndoe",
       "resume_path": "/path/to/resume.pdf",
       "skills": ["Python", "FastAPI", "React"],
       "summary": "Full-stack developer with 5 years experience"
   })

2. Apply to a job:
   manager = get_auto_apply_manager()
   result = manager.apply_to_job(
       job_url="https://linkedin.com/jobs/view/...",
       profile=profile,
       platform="linkedin"
   )

3. Bulk apply:
   results = manager.bulk_apply(
       job_urls=["url1", "url2", "url3"],
       profile=profile,
       delay_between=60
   )

Note: This requires:
- Chrome browser installed
- Selenium WebDriver
- Valid job URLs
- User must be logged into platforms (LinkedIn, Indeed)
- LinkedIn Easy Apply jobs only (not external applications)
    """)
    
    print("=" * 70)
