"""
Selenium Automation Service
Implements 10 core automation patterns for web interaction
Integrated with AI Earning Platform for autonomous job hunting and monitoring
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, 
    ElementNotInteractableException, WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger('SeleniumAutomation')


@dataclass
class AutomationResult:
    """Result of an automation task"""
    success: bool
    message: str
    data: Dict[str, Any]
    timestamp: str
    screenshot_path: Optional[str] = None


@dataclass
class JobListing:
    """Scraped job listing"""
    title: str
    description: str
    url: str
    platform: str
    budget: Optional[str] = None
    posted_time: Optional[str] = None
    skills: List[str] = None
    client_info: Dict[str, Any] = None


class SeleniumAutomation:
    """
    Core Selenium automation implementing 10 use cases:
    1. Auto-login to any website
    2. Download files without clicking
    3. Auto-scroll infinite pages
    4. Auto-fill forms in bulk
    5. Scrape prices without API
    6. Take automated screenshots
    7. Check website status
    8. Automate Google search
    9. Auto-reply to messages
    10. Capture analytics data
    """
    
    def __init__(self, headless: bool = True, download_dir: str = None):
        self.headless = headless
        self.download_dir = download_dir or os.path.expanduser("~/Downloads/selenium_automation")
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        
        # Ensure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)
        
        logger.info(f"🤖 Selenium Automation initialized (headless={headless})")
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        # Download preferences
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            
            self.wait = WebDriverWait(driver, 20)
            self.driver = driver
            
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def _safe_find(self, by: By, value: str, timeout: int = 10) -> Optional[Any]:
        """Safely find an element with timeout"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            return None
    
    def _safe_click(self, element) -> bool:
        """Safely click an element"""
        try:
            element.click()
            return True
        except ElementNotInteractableException:
            # Try scrolling to element first
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            try:
                element.click()
                return True
            except:
                return False
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Browser closed")
    
    # ============================================
    # 1. AUTO-LOGIN TO ANY WEBSITE
    # ============================================
    
    def auto_login(self, url: str, username: str, password: str,
                   username_selector: str = "#username",
                   password_selector: str = "#password",
                   submit_selector: str = "#submit",
                   selector_type: str = "css") -> AutomationResult:
        """
        Automatically login to any website
        
        Args:
            url: Login page URL
            username: Username/email
            password: Password
            username_selector: Selector for username field
            password_selector: Selector for password field
            submit_selector: Selector for submit button
            selector_type: 'css', 'id', 'xpath', or 'name'
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            # Map selector types to By
            by_map = {
                "css": By.CSS_SELECTOR,
                "id": By.ID,
                "xpath": By.XPATH,
                "name": By.NAME
            }
            by = by_map.get(selector_type, By.CSS_SELECTOR)
            
            # Navigate to login page
            self.driver.get(url)
            time.sleep(2)
            
            # Find and fill username
            username_field = self._safe_find(by, username_selector)
            if not username_field:
                return AutomationResult(
                    success=False,
                    message=f"Username field not found: {username_selector}",
                    data={},
                    timestamp=datetime.utcnow().isoformat()
                )
            
            username_field.clear()
            username_field.send_keys(username)
            
            # Find and fill password
            password_field = self._safe_find(by, password_selector)
            if not password_field:
                return AutomationResult(
                    success=False,
                    message=f"Password field not found: {password_selector}",
                    data={},
                    timestamp=datetime.utcnow().isoformat()
                )
            
            password_field.clear()
            password_field.send_keys(password)
            
            # Click submit
            submit_btn = self._safe_find(by, submit_selector)
            if submit_btn:
                self._safe_click(submit_btn)
                time.sleep(3)
            
            # Check if login succeeded
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Success indicators
            error_indicators = ['invalid', 'error', 'incorrect', 'failed', 'wrong']
            has_error = any(indicator in page_source for indicator in error_indicators)
            
            success = not has_error and "login" not in current_url.lower()
            
            # Take screenshot
            screenshot_path = self._take_screenshot(f"login_{int(time.time())}")
            
            return AutomationResult(
                success=success,
                message="Login successful" if success else "Login may have failed",
                data={
                    "url_after": current_url,
                    "has_error_indicator": has_error
                },
                timestamp=datetime.utcnow().isoformat(),
                screenshot_path=screenshot_path
            )
            
        except Exception as e:
            logger.error(f"Auto-login error: {e}")
            return AutomationResult(
                success=False,
                message=f"Error: {str(e)}",
                data={},
                timestamp=datetime.utcnow().isoformat()
            )
    
    # ============================================
    # 2. DOWNLOAD FILES WITHOUT CLICKING
    # ============================================
    
    def auto_download(self, url: str, download_link_text: str = None,
                      download_selector: str = None,
                      wait_time: int = 10) -> AutomationResult:
        """
        Automatically download files
        
        Args:
            url: Page with download link
            download_link_text: Text of download link (e.g., "Download Report")
            download_selector: CSS selector for download button
            wait_time: Seconds to wait for download
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            # Get files before download
            files_before = set(os.listdir(self.download_dir))
            
            # Navigate to page
            self.driver.get(url)
            time.sleep(2)
            
            # Find and click download
            if download_link_text:
                link = self._safe_find(By.LINK_TEXT, download_link_text)
            elif download_selector:
                link = self._safe_find(By.CSS_SELECTOR, download_selector)
            else:
                # Try common download selectors
                selectors = [
                    "a[download]",
                    "[class*='download']",
                    "[id*='download']",
                    "button:contains('Download')"
                ]
                link = None
                for sel in selectors:
                    link = self._safe_find(By.CSS_SELECTOR, sel, timeout=3)
                    if link:
                        break
            
            if not link:
                return AutomationResult(
                    success=False,
                    message="Download link not found",
                    data={},
                    timestamp=datetime.utcnow().isoformat()
                )
            
            self._safe_click(link)
            
            # Wait for download
            time.sleep(wait_time)
            
            # Check for new files
            files_after = set(os.listdir(self.download_dir))
            new_files = files_after - files_before
            
            success = len(new_files) > 0
            
            # Organize download - move to dated folder
            if new_files:
                dated_folder = os.path.join(
                    self.download_dir,
                    datetime.now().strftime("%Y-%m-%d")
                )
                os.makedirs(dated_folder, exist_ok=True)
                
                moved_files = []
                for filename in new_files:
                    src = os.path.join(self.download_dir, filename)
                    dst = os.path.join(dated_folder, filename)
                    os.rename(src, dst)
                    moved_files.append(dst)
                
                return AutomationResult(
                    success=True,
                    message=f"Downloaded {len(new_files)} file(s)",
                    data={
                        "files": list(new_files),
                        "organized_to": dated_folder,
                        "paths": moved_files
                    },
                    timestamp=datetime.utcnow().isoformat()
                )
            
            return AutomationResult(
                success=False,
                message="No new files detected",
                data={},
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Download error: {e}")
            return AutomationResult(
                success=False,
                message=f"Error: {str(e)}",
                data={},
                timestamp=datetime.utcnow().isoformat()
            )
    
    # ============================================
    # 3. AUTO-SCROLL INFINITE PAGES
    # ============================================
    
    def auto_scroll(self, url: str, scroll_count: int = 10,
                    scroll_pixels: int = 2000, wait_between: float = 1.0) -> AutomationResult:
        """
        Auto-scroll infinite scroll pages (LinkedIn, Twitter, etc.)
        
        Args:
            url: Page to scroll
            scroll_count: Number of scroll actions
            scroll_pixels: Pixels to scroll each time
            wait_between: Seconds between scrolls
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            self.driver.get(url)
            time.sleep(2)
            
            # Get initial page height
            initial_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            
            scrolls_performed = 0
            content_loaded = []
            
            for i in range(scroll_count):
                # Scroll down
                self.driver.execute_script(
                    f"window.scrollBy(0, {scroll_pixels});"
                )
                scrolls_performed += 1
                
                # Wait for new content to load
                time.sleep(wait_between)
                
                # Check if new content loaded
                new_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
                
                if new_height > initial_height:
                    content_loaded.append({
                        "scroll": i + 1,
                        "height_before": initial_height,
                        "height_after": new_height
                    })
                    initial_height = new_height
            
            # Take final screenshot
            screenshot = self._take_screenshot(f"scrolled_{int(time.time())}")
            
            return AutomationResult(
                success=True,
                message=f"Scrolled {scrolls_performed} times",
                data={
                    "scrolls_performed": scrolls_performed,
                    "content_loads": len(content_loaded),
                    "final_page_height": initial_height,
                    "content_load_details": content_loaded
                },
                timestamp=datetime.utcnow().isoformat(),
                screenshot_path=screenshot
            )
            
        except Exception as e:
            logger.error(f"Scroll error: {e}")
            return AutomationResult(
                success=False,
                message=f"Error: {str(e)}",
                data={},
                timestamp=datetime.utcnow().isoformat()
            )
    
    # ============================================
    # 4. AUTO-FILL FORMS IN BULK
    # ============================================
    
    def auto_fill_forms(self, url: str, form_data: List[Dict[str, str]],
                         field_mapping: Dict[str, str],
                         submit_selector: str = "button[type='submit']",
                         wait_between: float = 2.0) -> AutomationResult:
        """
        Auto-fill forms in bulk
        
        Args:
            url: Form page URL
            form_data: List of dicts with form values
            field_mapping: Maps data keys to CSS selectors
                         e.g., {"first_name": "#first", "last_name": "#last"}
            submit_selector: Selector for submit button
            wait_between: Seconds between form submissions
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            results = []
            
            for i, data in enumerate(form_data):
                try:
                    # Navigate to form
                    self.driver.get(url)
                    time.sleep(1)
                    
                    # Fill each field
                    for field_key, selector in field_mapping.items():
                        if field_key in data:
                            field = self._safe_find(By.CSS_SELECTOR, selector)
                            if field:
                                field.clear()
                                field.send_keys(data[field_key])
                    
                    # Submit form
                    submit_btn = self._safe_find(By.CSS_SELECTOR, submit_selector)
                    if submit_btn:
                        self._safe_click(submit_btn)
                    
                    time.sleep(wait_between)
                    
                    results.append({
                        "index": i,
                        "data": data,
                        "success": True,
                        "current_url": self.driver.current_url
                    })
                    
                except Exception as e:
                    results.append({
                        "index": i,
                        "data": data,
                        "success": False,
                        "error": str(e)
                    })
            
            successful = sum(1 for r in results if r["success"])
            
            return AutomationResult(
                success=successful == len(form_data),
                message=f"Filled {successful}/{len(form_data)} forms",
                data={
                    "total": len(form_data),
                    "successful": successful,
                    "failed": len(form_data) - successful,
                    "results": results
                },
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Form fill error: {e}")
            return AutomationResult(
                success=False,
                message=f"Error: {str(e)}",
                data={},
                timestamp=datetime.utcnow().isoformat()
            )
    
    # ============================================
    # 5. SCRAPE PRICES WITHOUT API
    # ============================================
    
    def scrape_prices(self, url: str, price_selector: str,
                      name_selector: str = None,
                      wait_for_load: bool = True) -> AutomationResult:
        """
        Scrape prices and product names from e-commerce sites
        
        Args:
            url: Product listing page
            price_selector: CSS selector for price elements
            name_selector: CSS selector for product names
            wait_for_load: Wait for dynamic content
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            self.driver.get(url)
            
            if wait_for_load:
                time.sleep(3)
            
            # Scrape prices
            price_elements = self.driver.find_elements(By.CSS_SELECTOR, price_selector)
            prices = []
            
            for elem in price_elements:
                price_text = elem.text.strip()
                if price_text:
                    # Try to parse price
                    prices.append(price_text)
            
            # Scrape names if selector provided
            names = []
            if name_selector:
                name_elements = self.driver.find_elements(By.CSS_SELECTOR, name_selector)
                names = [elem.text.strip() for elem in name_elements if elem.text.strip()]
            
            # Combine data
            products = []
            for i, price in enumerate(prices):
                product = {
                    "price": price,
                    "name": names[i] if i < len(names) else f"Product {i+1}"
                }
                products.append(product)
            
            return AutomationResult(
                success=True,
                message=f"Scraped {len(products)} products",
                data={
                    "url": url,
                    "products_found": len(products),
                    "products": products[:20]  # Limit to 20
                },
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Price scraping error: {e}")
            return AutomationResult(
                success=False,
                message=f"Error: {str(e)}",
                data={},
                timestamp=datetime.utcnow().isoformat()
            )
    
    # ============================================
    # 6. TAKE AUTOMATED SCREENSHOTS
    # ============================================
    
    def _take_screenshot(self, name: str = None) -> str:
        """Take and save a screenshot"""
        if not self.driver:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name or 'screenshot'}_{timestamp}.png"
        
        screenshot_dir = os.path.join(self.download_dir, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        filepath = os.path.join(screenshot_dir, filename)
        self.driver.save_screenshot(filepath)
        
        return filepath
    
    def take_screenshot(self, url: str = None, full_page: bool = False,
                        element_selector: str = None) -> AutomationResult:
        """
        Take automated screenshots
        
        Args:
            url: Page to screenshot (None for current page)
            full_page: Capture full scrollable page
            element_selector: Screenshot specific element only
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            if url:
                self.driver.get(url)
                time.sleep(2)
            
            screenshot_path = None
            
            if element_selector:
                # Screenshot specific element
                element = self._safe_find(By.CSS_SELECTOR, element_selector)
                if element:
                    screenshot_path = element.screenshot_as_png
                    # Save to file
                    filename = f"element_{int(time.time())}.png"
                    filepath = os.path.join(self.download_dir, "screenshots", filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    with open(filepath, "wb") as f:
                        f.write(screenshot_path)
                    screenshot_path = filepath
            elif full_page:
                # Full page screenshot
                original_size = self.driver.get_window_size()
                
                # Get full height
                full_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
                self.driver.set_window_size(1920, full_height)
                time.sleep(1)
                
                screenshot_path = self._take_screenshot(f"fullpage_{int(time.time())}")
                
                # Restore size
                self.driver.set_window_size(original_size["width"], original_size["height"])
            else:
                # Standard viewport screenshot
                screenshot_path = self._take_screenshot(f"viewport_{int(time.time())}")
            
            return AutomationResult(
                success=True,
                message="Screenshot captured",
                data={
                    "screenshot_path": screenshot_path,
                    "url": self.driver.current_url if self.driver else url,
                    "type": "element" if element_selector else ("fullpage" if full_page else "viewport")
                },
                timestamp=datetime.utcnow().isoformat(),
                screenshot_path=screenshot_path
            )
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return AutomationResult(
                success=False,
                message=f"Error: {str(e)}",
                data={},
                timestamp=datetime.utcnow().isoformat()
            )
    
    # ============================================
    # 7. CHECK WEBSITE STATUS LIKE A BOT
    # ============================================
    
    def check_website_status(self, url: str, 
                           expected_content: str = None,
                           check_selectors: List[str] = None) -> AutomationResult:
        """
        Check if website is up and functioning correctly
        
        Args:
            url: Website to check
            expected_content: Text that should be present
            check_selectors: CSS selectors that should exist
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            start_time = time.time()
            self.driver.get(url)
            load_time = time.time() - start_time
            
            # Check for errors in page
            page_source = self.driver.page_source.lower()
            
            error_indicators = [
                "error", "404", "not found", "503", "maintenance",
                "service unavailable", "something went wrong"
            ]
            
            found_errors = [
                indicator for indicator in error_indicators
                if indicator in page_source
            ]
            
            # Check expected content
            content_found = True
            if expected_content:
                content_found = expected_content.lower() in page_source
            
            # Check selectors
            selector_results = {}
            if check_selectors:
                for selector in check_selectors:
                    elem = self._safe_find(By.CSS_SELECTOR, selector, timeout=3)
                    selector_results[selector] = elem is not None
            
            # Determine status
            is_up = len(found_errors) == 0 and content_found
            
            status_data = {
                "url": url,
                "is_up": is_up,
                "load_time_seconds": round(load_time, 2),
                "status_code": 200,  # Selenium doesn't expose this directly
                "errors_detected": found_errors,
                "expected_content_found": content_found,
                "selector_checks": selector_results,
                "page_title": self.driver.title,
                "current_url": self.driver.current_url
            }
            
            # Take screenshot of status
            screenshot = self._take_screenshot(f"status_{int(time.time())}")
            
            return AutomationResult(
                success=is_up,
                message="Website is up" if is_up else "Website may be down",
                data=status_data,
                timestamp=datetime.utcnow().isoformat(),
                screenshot_path=screenshot
            )
            
        except WebDriverException as e:
            logger.error(f"Website check error: {e}")
            return AutomationResult(
                success=False,
                message=f"Failed to load: {str(e)}",
                data={"url": url, "error": str(e)},
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return AutomationResult(
                success=False,
                message=f"Error: {str(e)}",
                data={},
                timestamp=datetime.utcnow().isoformat()
            )
    
    # ============================================
    # 8. AUTOMATE GOOGLE SEARCH
    # ============================================
    
    def google_search(self, query: str, result_count: int = 10) -> AutomationResult:
        """
        Automate Google search and scrape results
        
        Args:
            query: Search query
            result_count: Number of results to scrape
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            # Navigate to Google
            self.driver.get("https://www.google.com")
            time.sleep(1)
            
            # Accept cookies if present (EU)
            try:
                accept_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Accept all')]")
                accept_btn.click()
                time.sleep(1)
            except:
                pass
            
            # Find search box and submit
            search_box = self._safe_find(By.NAME, "q")
            if not search_box:
                return AutomationResult(
                    success=False,
                    message="Search box not found",
                    data={},
                    timestamp=datetime.utcnow().isoformat()
                )
            
            search_box.clear()
            search_box.send_keys(query)
            search_box.submit()
            
            time.sleep(2)
            
            # Scrape results
            results = []
            
            # Different selectors for Google results
            result_selectors = [
                "div.g",  # Standard result
                "div[data-ved]",  # Another format
                ".yuRUbf"  # Link container
            ]
            
            for selector in result_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for elem in elements[:result_count]:
                    try:
                        # Extract title
                        title_elem = elem.find_element(By.CSS_SELECTOR, "h3")
                        title = title_elem.text if title_elem else "No title"
                        
                        # Extract URL
                        link_elem = elem.find_element(By.CSS_SELECTOR, "a")
                        url = link_elem.get_attribute("href") if link_elem else ""
                        
                        # Extract snippet
                        snippet_elem = elem.find_element(By.CSS_SELECTOR, ".VwiC3b, .s3v94d, span")
                        snippet = snippet_elem.text if snippet_elem else ""
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet[:200] if snippet else ""
                        })
                    except:
                        continue
                
                if results:
                    break
            
            return AutomationResult(
                success=True,
                message=f"Found {len(results)} results",
                data={
                    "query": query,
                    "results_count": len(results),
                    "results": results
                },
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return AutomationResult(
                success=False,
                message=f"Error: {str(e)}",
                data={},
                timestamp=datetime.utcnow().isoformat()
            )
    
    # ============================================
    # 9. AUTO-REPLY TO MESSAGES
    # ============================================
    
    def auto_reply_message(self, url: str, message_input_selector: str,
                         reply_text: str, send_button_selector: str = None,
                         wait_for_messages: bool = True) -> AutomationResult:
        """
        Auto-reply to messages on web platforms
        
        Works with: Slack Web, WhatsApp Web, Messenger, etc.
        
        Args:
            url: Messaging platform URL
            message_input_selector: CSS selector for input field
            reply_text: Text to send
            send_button_selector: Selector for send button (optional, can use Enter)
            wait_for_messages: Wait for message list to load
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            self.driver.get(url)
            time.sleep(3)  # Give time for messages to load
            
            # Find message input
            input_field = self._safe_find(By.CSS_SELECTOR, message_input_selector)
            if not input_field:
                return AutomationResult(
                    success=False,
                    message=f"Message input not found: {message_input_selector}",
                    data={},
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Type message
            input_field.clear()
            input_field.send_keys(reply_text)
            time.sleep(0.5)
            
            # Send message
            if send_button_selector:
                send_btn = self._safe_find(By.CSS_SELECTOR, send_button_selector)
                if send_btn:
                    self._safe_click(send_btn)
                else:
                    # Fallback to Enter key
                    input_field.send_keys(Keys.RETURN)
            else:
                # Use Enter key
                input_field.send_keys(Keys.RETURN)
            
            time.sleep(1)
            
            return AutomationResult(
                success=True,
                message="Message sent",
                data={
                    "platform_url": url,
                    "message_sent": reply_text,
                    "method": "button_click" if send_button_selector else "enter_key"
                },
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Auto-reply error: {e}")
            return AutomationResult(
                success=False,
                message=f"Error: {str(e)}",
                data={},
                timestamp=datetime.utcnow().isoformat()
            )
    
    # ============================================
    # 10. CAPTURE ANALYTICS DATA
    # ============================================
    
    def capture_analytics(self, url: str, metric_selectors: Dict[str, str],
                         wait_for_data: bool = True) -> AutomationResult:
        """
        Capture analytics/metrics from dashboards
        
        Args:
            url: Analytics dashboard URL
            metric_selectors: Dict mapping metric names to CSS selectors
            wait_for_data: Wait for dynamic data to load
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            self.driver.get(url)
            
            if wait_for_data:
                time.sleep(5)  # Wait for charts/data to load
            
            # Extract metrics
            metrics = {}
            for metric_name, selector in metric_selectors.items():
                try:
                    element = self._safe_find(By.CSS_SELECTOR, selector, timeout=5)
                    if element:
                        value = element.text.strip()
                        metrics[metric_name] = value
                    else:
                        metrics[metric_name] = "Not found"
                except Exception as e:
                    metrics[metric_name] = f"Error: {str(e)}"
            
            # Take screenshot of dashboard
            screenshot = self._take_screenshot(f"analytics_{int(time.time())}")
            
            return AutomationResult(
                success=True,
                message=f"Captured {len(metrics)} metrics",
                data={
                    "url": url,
                    "metrics": metrics,
                    "screenshot": screenshot
                },
                timestamp=datetime.utcnow().isoformat(),
                screenshot_path=screenshot
            )
            
        except Exception as e:
            logger.error(f"Analytics capture error: {e}")
            return AutomationResult(
                success=False,
                message=f"Error: {str(e)}",
                data={},
                timestamp=datetime.utcnow().isoformat()
            )


# Global instance
_selenium_instance: Optional[SeleniumAutomation] = None

def get_selenium_automation(headless: bool = True) -> SeleniumAutomation:
    """Get or create Selenium automation instance"""
    global _selenium_instance
    if _selenium_instance is None:
        _selenium_instance = SeleniumAutomation(headless=headless)
    return _selenium_instance


if __name__ == "__main__":
    # Test all 10 automation patterns
    print("=" * 70)
    print("SELENIUM AUTOMATION - 10 USE CASES TEST")
    print("=" * 70)
    
    auto = SeleniumAutomation(headless=True)
    
    # 6. Screenshot test (safe, no auth needed)
    print("\n6. Testing Screenshot")
    result = auto.take_screenshot(url="https://www.google.com")
    print(f"   Success: {result.success}")
    print(f"   Path: {result.data.get('screenshot_path')}")
    
    # 7. Website status check
    print("\n7. Testing Website Status Check")
    result = auto.check_website_status(
        url="https://www.google.com",
        expected_content="Google"
    )
    print(f"   Is up: {result.data.get('is_up')}")
    print(f"   Load time: {result.data.get('load_time_seconds')}s")
    
    # 8. Google search
    print("\n8. Testing Google Search")
    result = auto.google_search(query="Python Selenium tutorial", result_count=5)
    print(f"   Found: {result.data.get('results_count')} results")
    if result.data.get('results'):
        print(f"   First result: {result.data['results'][0]['title'][:50]}...")
    
    # 5. Price scraping (example - will fail without valid e-commerce URL)
    print("\n5. Testing Price Scraping (demo)")
    # This would need a real e-commerce URL to work
    print("   (Requires valid e-commerce URL with price elements)")
    
    auto.close()
    
    print("\n" + "=" * 70)
    print("Test complete. Close browser and exit.")
    print("=" * 70)
