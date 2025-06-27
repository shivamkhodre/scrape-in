import datetime
import logging
import time
import random
import json
import os
import subprocess
import platform
import re
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from utils.behaviour import HumanBehaviorSimulator
from utils.fingerprint import BrowserFingerprintManager
from utils.throttler import RequestThrottler
from utils.user_agent import UserAgentRotator

CHROME_BIN = os.getenv('CHROME_BIN')
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
CHROME_BROWSER= os.getenv('CHROME_BROWSER')
HEADLESS= os.getenv('HEADLESS')
IS_DOCKER= os.getenv('IS_DOCKER')


class LinkedInScraper:
    """Advanced LinkedIn scraper with comprehensive anti-detection measures"""
    
    def __init__(self, headless=False, proxy=None):
        self.headless = headless
        self.proxy = proxy
        self.driver = None
        self.wait = None
        self.throttler = RequestThrottler(min_delay=2, max_delay=8, burst_protection=True)
        self.fingerprint_manager = BrowserFingerprintManager()
        self.user_agent_rotator = UserAgentRotator()
        self.behavior_simulator = None
        self.session_data = {
            'profiles_scraped': 0,
            'searches_performed': 0,
            'session_start': time.time(),
            'errors': 0,
            'last_activity': time.time()
        }
        
        # Setup logging
        self._setup_logging()
        
        # Session management
        self.session_cookies = None
        self.session_headers = {}
        
        # Data storage
        self.scraped_data = []
        self.failed_profiles = []
        
        # Rate limiting and health monitoring
        self.health_monitor = {
            'consecutive_errors': 0,
            'last_successful_scrape': time.time(),
            'blocked_indicators': 0,
            'captcha_encounters': 0
        }
        
    def _setup_logging(self):
        """Setup comprehensive logging system"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(f'logs/linkedin_scraper_{datetime.date.today()}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_chrome_version(self):
        try:
            system = platform.system()

            if system == "Darwin":  # macOS
                output = subprocess.check_output([
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "--version"
                ])
            elif system == "Linux":
                output = subprocess.check_output(["google-chrome", "--version"])
            elif system == "Windows":
                output = subprocess.check_output([
                    r"reg", "query",
                    r"HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon",
                    "/v", "version"
                ])
            else:
                raise Exception("Unsupported OS")

            version = output.decode("utf-8")
            match = re.search(r"(\d+)\.", version)
            if match:
                return int(match.group(1))
            else:
                raise Exception("Could not parse Chrome version")

        except Exception as e:
            print("Error detecting Chrome version:", e)
            return None


    def _create_advanced_driver(self):
        """Create advanced Chrome driver with comprehensive stealth configuration"""
        try:
            # Use undetected-chromedriver for better stealth
            options = uc.ChromeOptions()
            
            # Essential stealth arguments
            stealth_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions-file-access-check',
                '--disable-extensions-http-throttling',
                '--disable-extensions-except',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--no-first-run',
                '--no-service-autorun',
                '--password-store=basic',
                '--use-mock-keychain',
                '--no-default-browser-check',
                '--disable-default-apps',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu',
                '--disable-web-security',
                '--allow-running-insecure-content',
                '--disable-features=VizDisplayCompositor',
                '--disable-logging',
                '--disable-permissions-api',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-hang-monitor',
                '--disable-background-networking',
                '--disable-background-media-suspend',
                '--disable-client-side-phishing-detection',
                '--disable-sync',
                '--metrics-recording-only',
                '--safebrowsing-disable-auto-update',
                '--disable-component-update'
            ]
            
            for arg in stealth_args:
                options.add_argument(arg)
            # options.binary_location = "/usr/bin/chromium"
            options.binary_location = CHROME_BIN or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            # Conditional headless mode
            if HEADLESS:
                options.add_argument('--headless=new')  # Use new headless mode
            
            # Proxy configuration
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
            
            # User agent rotation
            user_agent = self.user_agent_rotator.get_mixed_agent()
            options.add_argument(f'--user-agent={user_agent}')
            
            # Additional privacy and performance settings
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "geolocation": 2,
                    "media_stream": 2,
                },
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2,  # Block images for faster loading
                "profile.password_manager_enabled": False,
                "credentials_enable_service": False,
                "webrtc.ip_handling_policy": "disable_non_proxied_udp",
                "webrtc.multiple_routes_enabled": False,
                "webrtc.nonproxied_udp_enabled": False
            }
            # options.add_experimental_option("prefs", prefs)
            # options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            # options.add_experimental_option('useAutomationExtension', False)
            
            # Create driver with advanced configuration
            self.driver = uc.Chrome(
                options=options,
                version_main=None if IS_DOCKER else self.get_chrome_version(),  # Auto-detect Chrome version
                driver_executable_path=CHROMEDRIVER_PATH or None,
                browser_executable_path=CHROME_BROWSER or None
                # driver_executable_path=None
            )
            
            # Apply browser fingerprinting
            self.fingerprint_manager.apply_fingerprint(self.driver)
            
            # Initialize behavior simulator
            self.behavior_simulator = HumanBehaviorSimulator(self.driver)
            
            # Set implicit wait and page load timeout
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            # Create WebDriverWait instance
            self.wait = WebDriverWait(self.driver, 20)
            
            # Execute additional stealth JavaScript
            self._execute_stealth_scripts()
            
            self.logger.info(f"Advanced Chrome driver created successfully with UA: {user_agent[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create driver: {e}")
            return False
    
    def _execute_stealth_scripts(self):
        """Execute additional JavaScript for stealth browsing"""
        try:
            stealth_script = """
            // Remove automation indicators
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            
            // Override permissions API
            // Object.defineProperty(navigator, 'permissions', {
            //     get: () => ({
            //         query: () => Promise.resolve({ state: 'granted' })
            //     })
            // });
            
            // Mock media devices
            Object.defineProperty(navigator, 'mediaDevices', {
                get: () => ({
                    enumerateDevices: () => Promise.resolve([
                        { deviceId: 'default', kind: 'audioinput', label: 'Default - Microphone' },
                        { deviceId: 'default', kind: 'audiooutput', label: 'Default - Speaker' },
                        { deviceId: 'default', kind: 'videoinput', label: 'Default - Camera' }
                    ])
                })
            });
            
            // Override connection property
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    effectiveType: '4g',
                    rtt: 100,
                    downlink: 2.0
                })
            });
            
            // Mock battery API
            Object.defineProperty(navigator, 'getBattery', {
                get: () => () => Promise.resolve({
                    charging: true,
                    chargingTime: 0,
                    dischargingTime: Infinity,
                    level: 1
                })
            });
            
            // Enhanced iframe detection evasion
            Object.defineProperty(window, 'outerHeight', {
                get: () => window.innerHeight
            });
            Object.defineProperty(window, 'outerWidth', {
                get: () => window.innerWidth
            });
            
            // Mock notification permission
            Object.defineProperty(Notification, 'permission', {
                get: () => 'default'
            });
            """
            
            self.driver.execute_script(stealth_script)
            self.logger.debug("Advanced stealth scripts executed successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to execute stealth scripts: {e}")
    
    def login(self, email, password):
        """Enhanced login with human-like behavior and anti-detection measures"""
        try:
            self.logger.info("Starting LinkedIn login process...")
            
            # Navigate to LinkedIn login page
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for page load and simulate reading time
            time.sleep(random.uniform(2, 5))
            self.behavior_simulator.simulate_page_interaction("casual")
            
            # Apply request throttling for login
            self.throttler.wait_for_next_request("login")
            
            # Find email field with multiple selectors
            email_selectors = [
                "input[name='session_key']",
                "input[id='username']",
                "input[type='email']",
                "#session_key"
            ]
            
            email_element = None
            for selector in email_selectors:
                try:
                    email_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            # print(email_element)
            if not email_element:
                raise Exception("Could not find email input field")
            
            # Simulate human-like interaction with email field
            self.behavior_simulator.simulate_mouse_movement(email_element, "precise")
            time.sleep(random.uniform(0.5, 1.5))
            # print("...")
            # Type email with human-like behavior
            self.behavior_simulator.simulate_typing(email_element, email, "normal")
            # print("..")
            # Small delay before moving to password field
            time.sleep(random.uniform(1, 3))
            
            # Find password field
            password_selectors = [
                "input[name='session_password']",
                "input[id='password']",
                "input[type='password']",
                "#session_password"
            ]
            
            password_element = None
            for selector in password_selectors:
                try:
                    password_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not password_element:
                raise Exception("Could not find password input field")
            
            # Simulate mouse movement to password field
            self.behavior_simulator.simulate_mouse_movement(password_element, "smooth")
            time.sleep(random.uniform(0.5, 1.5))
            
            # Type password with human-like behavior
            self.behavior_simulator.simulate_typing(password_element, password, "careful")
            
            # Simulate brief hesitation before clicking login
            time.sleep(random.uniform(2, 4))
            self.behavior_simulator.simulate_page_interaction("focused")
            
            # Find and click login button
            login_selectors = [
                "button[type='submit']",
                "button[data-id='sign-in-form__submit-btn']",
                ".btn__primary--large",
                "input[type='submit']"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                raise Exception("Could not find login button")
            
            # Simulate human-like click
            self.behavior_simulator.simulate_mouse_movement(login_button, "precise")
            time.sleep(random.uniform(0.5, 1.0))
            login_button.click()
            
            # Wait for login to complete
            self.logger.info("Waiting for login to complete...")
            time.sleep(random.uniform(3, 7))
            
            # Check for successful login or potential issues
            current_url = self.driver.current_url
            
            if "challenge" in current_url or "checkpoint" in current_url:
                self.logger.warning("Login challenge/checkpoint detected")
                self.health_monitor['captcha_encounters'] += 1
                return self._handle_login_challenge()
            
            elif "feed" in current_url or "linkedin.com/in/" in current_url or self.driver.current_url == "https://www.linkedin.com/feed/":
                self.logger.info("Login successful!")
                self.session_data['last_activity'] = time.time()
                
                # Save session cookies for later use
                self.session_cookies = self.driver.get_cookies()
                
                # Simulate post-login browsing behavior
                self.behavior_simulator.simulate_human_scrolling("browsing")
                
                return True
            
            else:
                # Check for error messages
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".form__label--error, .alert, .error")
                if error_elements:
                    error_text = error_elements[0].text
                    self.logger.error(f"Login failed with error: {error_text}")
                    self.health_monitor['consecutive_errors'] += 1
                else:
                    self.logger.error("Login failed - unknown error")
                
                return False
        
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            self.health_monitor['consecutive_errors'] += 1
            return False
    
    def _handle_login_challenge(self):
        """Handle login challenges/captchas"""
        try:
            self.logger.info("Handling login challenge...")
            
            # Wait longer for manual intervention if not headless
            if not self.headless:
                self.logger.info("Please complete the challenge manually. Waiting...")
                time.sleep(60)  # Wait 1 minute for manual completion
                
                # Check if challenge was completed
                if "feed" in self.driver.current_url or "linkedin.com/in/" in self.driver.current_url:
                    self.logger.info("Challenge completed successfully!")
                    return True
            
            self.logger.warning("Challenge not completed or running in headless mode")
            return False
            
        except Exception as e:
            self.logger.error(f"Challenge handling failed: {e}")
            return False
    
    def search_profiles(self, keywords, location=None, industry=None, max_results=50):
        """Enhanced profile search with advanced filtering and human-like behavior"""
        profiles = []
        # print(max_results)
        try:
            self.logger.info(f"Starting profile search for: {keywords}")
            
            # Build search URL with parameters
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords.replace(' ', '%20')}"
         # https://www.linkedin.com/search/results/people/?geoUrn=%5B%22United%20States%22%5D&keywords=IT%20Recruiter&origin=FACETED_SEARCH&sid=!JI
         # https://www.linkedin.com/search/results/people/?geoUrn=%5B%22103644278%22%5D&keywords=IT%20recruiter&origin=FACETED_SEARCH&sid=wZl   
            if True:
                search_url += f"&origin=FACETED_SEARCH&geoUrn=%5B""{103644278}""%5D"
            
            if industry:
                search_url += f"&industry=%5B%22{industry}%22%5D"
            
            # Apply request throttling
            self.throttler.wait_for_next_request("search")
            
            # Navigate to search page
            self.driver.get(search_url)
            self.logger.info(f"Navigated to search URL: {search_url}")
            
            # Wait for search results to load
            time.sleep(random.uniform(3, 6))
            
            # Simulate human reading behavior
            self.behavior_simulator.simulate_human_scrolling("search_results")
            # self.behavior_simulator.simulate_page_interaction("searching")
            
            # Check for search results
            try:
                # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".search-result__wrapper")))
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results-container")))

            except TimeoutException:
                self.logger.warning("No search results found or page didn't load properly")
                return profiles
            
            page_count = 0
            max_pages = min(10, (max_results // 10) + 1)
            # print(max_pages, max_results)
            while len(profiles) < max_results and page_count < max_pages:
                page_count += 1
                self.logger.info(f"Processing search results page {page_count}")
                
                # Get current page results
                page_profiles = self._extract_search_results(max_results)
                profiles.extend(page_profiles)
                
                # Update session data
                self.session_data['searches_performed'] += 1
                
                if len(profiles) >= max_results:
                    break
                
                # Navigate to next page with human-like behavior
                if not self._go_to_next_page():
                    break
                
                # Random delay between pages
                self.throttler.apply_smart_delay()
                
                # Simulate reading new page
                self.behavior_simulator.simulate_human_scrolling("search_results")
            
            self.logger.info(f"Found {len(profiles)} profiles from search")
            return profiles[:max_results]
        
        except Exception as e:
            self.logger.error(f"Profile search failed: {e}")
            self.health_monitor['consecutive_errors'] += 1
            return profiles
    
    def _extract_search_results(self, max_results):
        """Extract profile data from search results page"""
        profiles = []
        
        try:
            # Multiple selectors for different LinkedIn layouts
            result_selectors = [
                # ".search-result__wrapper",
                # ".search-results__result-item",
                # ".reusable-search__result-container",
                # ".search-entity-result-universal-template",
                "div[data-view-name='search-entity-result-universal-template']"
            ]
           
            search_results = []
            for selector in result_selectors:
                search_results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if search_results:
                    break
            
            if not search_results:
                self.logger.warning("No search result elements found")
                return profiles
            
            self.logger.info(f"Found {len(search_results)} search result elements")

            if len(search_results) > max_results:
                search_results = search_results[:max_results]

            self.logger.info(f"Found {len(search_results)} search result elements")

            # print("....")
            for i, result in enumerate(search_results):
                try:
                    # print(result)
                    profile_data = self._extract_profile_from_search_result(result)
                    if profile_data:
                        profiles.append(profile_data)
                        
                        # Occasional mouse movement for realism
                        if i % 3 == 0:
                            self.behavior_simulator.simulate_mouse_movement(result, "casual")
                            time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    self.logger.debug(f"Failed to extract profile from result {i}: {e}")
                    continue
            # print("profiles", profiles)
            return profiles
            
        except Exception as e:
            self.logger.error(f"Failed to extract search results: {e}")
            return profiles
    
    def _extract_profile_from_search_result(self, result_element):
        """Extract individual profile data from search result element"""
        try:
            profile_data = {}
            # print("-----------")
            # Extract name
            # name_selectors = [
            #     # ".search-result__title-text a",
            #     # ".actor-name-with-distance strong",
            #     # ".search-result__result-link",
            #     # ".app-aware-link .search-result__title-text"
            #     "a[data-test-app-aware-link] span[aria-hidden='true']"
            # ]
            
            # name_element = None
            # for selector in name_selectors:
            #     try:
            #         name_element = result_element.find_element(By.CSS_SELECTOR, selector)
            #         break
            #     except NoSuchElementException:
            #         continue
            
            # if name_element:
            #     profile_data['name'] = name_element.text.strip()
            #     profile_data['profile_url'] = name_element.get_attribute('href')
            # else:
            #     return None
            # print("result", result_element)
            # print("....", result_element.find_element(By.CSS_SELECTOR, "a[data-test-app-aware-link]"))
            try:
                anchor_element = result_element.find_element(By.CSS_SELECTOR, "a[data-test-app-aware-link]:not([aria-hidden])")
                # print(anchor_element.get_attribute('href'))
                # print("======",anchor_element.get_attribute("outerHTML"))
                WebDriverWait(anchor_element, 5).until(
                    lambda el: el.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
                )
                name_element = anchor_element.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
                # print("name", name_element)
                # profile_data['name'] = name_element.text.strip()
                # profile_data['profile_url'] = anchor_element.get_attribute('href')
                
                # name_element = anchor_element.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
                
                profile_data['name'] = name_element.text.strip()
                profile_data['profile_url'] = anchor_element.get_attribute('href')
                # print("''''''''", profile_data)
            except NoSuchElementException:
                print("some error")
                return None

            
            # Extract headline/title
            headline_selectors = [
                ".t-14.t-black.t-normal",
            ]
            
            for selector in headline_selectors:
                try:
                    headline_elem = result_element.find_element(By.CSS_SELECTOR, selector)
                    profile_data['headline'] = headline_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Extract location
            location_selectors = [
                "div.t-14.t-normal:not(.t-black)",
            ]
            
            for selector in location_selectors:
                try:
                    location_elem = result_element.find_element(By.CSS_SELECTOR, selector)
                    location_text = location_elem.text.strip()
                    if location_text and len(location_text) < 100:  # Reasonable location length
                        profile_data['location'] = location_text
                    break
                except NoSuchElementException:
                    continue
            
            # Extract mutual connections if available
            # try:
            #     mutual_elem = result_element.find_element(By.CSS_SELECTOR, ".search-result__social-proof")
            #     profile_data['mutual_connections'] = mutual_elem.text.strip()
            # except NoSuchElementException:
            #     profile_data['mutual_connections'] = None
            
            # Extract company if visible
            try:
                company_elem = result_element.find_element(By.CSS_SELECTOR, ".entity-result__summary--2-lines")
                profile_data['current_company'] = company_elem.text.strip()
            except NoSuchElementException:
                profile_data['current_company'] = None
            
            # Add extraction timestamp
            profile_data['scraped_at'] = datetime.datetime.now().isoformat()
            
            return profile_data
            
        except Exception as e:
            self.logger.debug(f"Failed to extract profile data: {e}")
            return None
    
    def _go_to_next_page(self):
        """Navigate to next page of search results with human-like behavior"""
        try:
            # Multiple selectors for next page button
            next_selectors = [
                "button[aria-label='Next']",
                ".artdeco-pagination__button--next",
                "button.artdeco-pagination__button[aria-label='Next']",
                ".pv2 button[aria-label='Next']"
            ]
            
            next_button = None
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_button.is_enabled():
                        break
                    else:
                        next_button = None
                except NoSuchElementException:
                    continue
            
            if not next_button:
                self.logger.info("No next page button found or disabled")
                return False
            
            # Scroll to button and simulate human interaction
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(random.uniform(1, 2))
            
            self.behavior_simulator.simulate_mouse_movement(next_button, "precise")
            time.sleep(random.uniform(0.5, 1.5))
            
            next_button.click()
            
            # Wait for new page to load
            time.sleep(random.uniform(3, 6))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to go to next page: {e}")
            return False
    
    def scrape_profile_details(self, profile_url):
        """Enhanced profile scraping with comprehensive data extraction"""
        try:
            self.logger.info(f"Scraping profile: {profile_url}")
            
            # Apply request throttling for profile visits
            self.throttler.wait_for_next_request("profile_visit")
            
            # Navigate to profile
            start_time = time.time()
            self.driver.get(profile_url)
            page_load_time = time.time() - start_time
            
            # Wait for profile to load completely
            time.sleep(random.uniform(3, 6))
            
            # Simulate human reading behavior
            self.behavior_simulator.simulate_human_scrolling("profile_reading")
            self.behavior_simulator.simulate_page_interaction("focused")
            
            # Initialize profile data structure
            profile_data = {
                'url': profile_url,
                'scraped_at': datetime.datetime.now().isoformat(),
                'page_load_time': page_load_time,
                'personal_info': {},
                'experience': [],
                'education': [],
                'skills': [],
                'recommendations': [],
                'connections': None,
                'about': None,
                'contact_info': {},
                'languages': [],
                'certifications': [],
                'publications': [],
                'projects': [],
                'honors_awards': []
            }
            
            # Extract basic profile information
            self._extract_basic_profile_info(profile_data)
            
            # Extract about section
            self._extract_about_section(profile_data)
            
            # Extract experience section
            self._extract_experience_section(profile_data)
            
            # Extract education section
            self._extract_education_section(profile_data)
            
            # Extract skills section
            self._extract_skills_section(profile_data)
            
            # Extract contact information if available
            self._extract_contact_info(profile_data)
            
            # Extract additional sections
            self._extract_additional_sections(profile_data)
            
            # Update session statistics
            self.session_data['profiles_scraped'] += 1
            self.session_data['last_activity'] = time.time()
            self.health_monitor['last_successful_scrape'] = time.time()
            self.health_monitor['consecutive_errors'] = 0
            
            self.logger.info(f"Successfully scraped profile: {profile_data['personal_info'].get('name', 'Unknown')}")
            return profile_data
            
        except Exception as e:
            self.logger.error(f"Failed to scrape profile {profile_url}: {e}")
            self.health_monitor['consecutive_errors'] += 1
            self.failed_profiles.append(profile_url)
            return None
    
    def _extract_basic_profile_info(self, profile_data):
        """Extract basic profile information (name, headline, location, etc.)"""
        try:
            # Extract name
            name_selectors = [
                "h1.text-heading-xlarge",
                ".pv-text-details__left-panel h1",
                ".ph5 h1",
                ".pv-top-card .pv-top-card__name",
                "h1[data-anonymize='person-name']"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    profile_data['personal_info']['name'] = name_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Extract headline
            headline_selectors = [
                ".text-body-medium.break-words",
                ".pv-text-details__left-panel .text-body-medium",
                ".pv-top-card .pv-top-card__headline",
                "[data-anonymize='headline']"
            ]
            
            for selector in headline_selectors:
                try:
                    headline_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    profile_data['personal_info']['headline'] = headline_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Extract location
            location_selectors = [
                ".text-body-small.inline.t-black--light.break-words",
                ".pv-text-details__left-panel .text-body-small",
                ".pv-top-card .pv-top-card__location",
                "[data-anonymize='location']"
            ]
            
            for selector in location_selectors:
                try:
                    location_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    location_text = location_elem.text.strip()
                    if "connections" not in location_text.lower():
                        profile_data['personal_info']['location'] = location_text
                        break
                except NoSuchElementException:
                    continue
            
            # Extract connection count
            connections_selectors = [
                ".pv-top-card .pv-top-card__connections",
                "a[href*='overlay/connections'] span",
                ".pv-text-details__left-panel button span"
            ]
            
            for selector in connections_selectors:
                try:
                    connections_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    connections_text = connections_elem.text.strip()
                    if "connection" in connections_text.lower():
                        profile_data['connections'] = connections_text
                        break
                except NoSuchElementException:
                    continue
            
            # Extract profile picture URL
            try:
                img_elem = self.driver.find_element(By.CSS_SELECTOR, ".pv-top-card__photo img, .profile-photo-edit__preview img")
                profile_data['personal_info']['profile_picture'] = img_elem.get_attribute('src')
            except NoSuchElementException:
                profile_data['personal_info']['profile_picture'] = None
            
        except Exception as e:
            self.logger.debug(f"Error extracting basic profile info: {e}")
    
    def _extract_about_section(self, profile_data):
        """Extract the about/summary section"""
        try:
            # Scroll to about section
            self.behavior_simulator.simulate_human_scrolling("section_reading")
            
            about_selectors = [
                "#about ~ .pv-shared-text-with-see-more .inline-show-more-text",
                ".pv-about-section .pv-about__summary-text",
                "[data-section='summary'] .pv-about__summary-text",
                ".summary-section .pv-about__summary-text"
            ]
            
            for selector in about_selectors:
                try:
                    about_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    profile_data['about'] = about_elem.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # Try to click "Show more" if available
            try:
                show_more_btn = self.driver.find_element(By.CSS_SELECTOR, ".inline-show-more-text__button")
                if show_more_btn.is_displayed():
                    self.behavior_simulator.simulate_mouse_movement(show_more_btn, "precise")
                    show_more_btn.click()
                    time.sleep(random.uniform(1, 2))
                    # Re-extract the expanded text
                    about_elem = self.driver.find_element(By.CSS_SELECTOR, ".inline-show-more-text__text")
                    profile_data['about'] = about_elem.text.strip()
            except NoSuchElementException:
                pass
            
        except Exception as e:
            self.logger.debug(f"Error extracting about section: {e}")
    
    def _extract_experience_section(self, profile_data):
        """Extract work experience information"""
        try:
            # Scroll to experience section
            self.behavior_simulator.simulate_human_scrolling("section_reading")
            time.sleep(random.uniform(1, 3))
            
            experience_selectors = [
                "#experience ~ .pvs-list__container .pvs-list__item",
                ".pv-profile-section[data-section='experience'] .pv-entity__summary-info",
                ".experience-section .pv-entity__summary-info"
            ]
            
            experience_items = []
            for selector in experience_selectors:
                try:
                    experience_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if experience_items:
                        break
                except NoSuchElementException:
                    continue
            
            if not experience_items:
                self.logger.debug("No experience items found")
                return
            
            for item in experience_items[:10]:  # Limit to first 10 experiences
                try:
                    experience_data = {}
                    
                    # Extract job title
                    title_selectors = [
                        ".mr1.hoverable-link-text.t-bold span[aria-hidden='true']",
                        ".pv-entity__summary-info h3",
                        ".pvs-entity__summary-title"
                    ]
                    
                    for selector in title_selectors:
                        try:
                            title_elem = item.find_element(By.CSS_SELECTOR, selector)
                            experience_data['title'] = title_elem.text.strip()
                            break
                        except NoSuchElementException:
                            continue
                    
                    # Extract company name
                    company_selectors = [
                        ".t-14.t-normal span[aria-hidden='true']",
                        ".pv-entity__secondary-title",
                        ".pvs-entity__summary-subtitle"
                    ]
                    
                    for selector in company_selectors:
                        try:
                            company_elem = item.find_element(By.CSS_SELECTOR, selector)
                            experience_data['company'] = company_elem.text.strip()
                            break
                        except NoSuchElementException:
                            continue
                    
                    # Extract duration
                    duration_selectors = [
                        ".t-14.t-normal.t-black--light span[aria-hidden='true']",
                        ".pv-entity__bullet-item-v2",
                        ".pvs-entity__caption-wrapper"
                    ]
                    
                    for selector in duration_selectors:
                        try:
                            duration_elem = item.find_element(By.CSS_SELECTOR, selector)
                            duration_text = duration_elem.text.strip()
                            if any(keyword in duration_text.lower() for keyword in ['year', 'month', 'present', 'yr', 'mo']):
                                experience_data['duration'] = duration_text
                                break
                        except NoSuchElementException:
                            continue
                    
                    # Extract location
                    try:
                        location_elem = item.find_element(By.CSS_SELECTOR, ".pv-entity__location span")
                        experience_data['location'] = location_elem.text.strip()
                    except NoSuchElementException:
                        experience_data['location'] = None
                    
                    # Extract description if available
                    try:
                        desc_elem = item.find_element(By.CSS_SELECTOR, ".pv-entity__description")
                        experience_data['description'] = desc_elem.text.strip()
                    except NoSuchElementException:
                        experience_data['description'] = None
                    
                    if experience_data.get('title') or experience_data.get('company'):
                        profile_data['experience'].append(experience_data)
                
                except Exception as e:
                    self.logger.debug(f"Error extracting individual experience: {e}")
                    continue
            
        except Exception as e:
            self.logger.debug(f"Error extracting experience section: {e}")
    
    def _extract_education_section(self, profile_data):
        """Extract education information"""
        try:
            # Scroll to education section
            self.behavior_simulator.simulate_human_scrolling("section_reading")
            
            education_selectors = [
                "#education ~ .pvs-list__container .pvs-list__item",
                ".pv-profile-section[data-section='education'] .pv-entity__summary-info",
                ".education-section .pv-entity__summary-info"
            ]
            
            education_items = []
            for selector in education_selectors:
                try:
                    education_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if education_items:
                        break
                except NoSuchElementException:
                    continue
            
            for item in education_items[:5]:  # Limit to first 5 education entries
                try:
                    education_data = {}
                    
                    # Extract school name
                    school_selectors = [
                        ".mr1.hoverable-link-text.t-bold span[aria-hidden='true']",
                        ".pv-entity__school-name",
                        ".pvs-entity__summary-title"
                    ]
                    
                    for selector in school_selectors:
                        try:
                            school_elem = item.find_element(By.CSS_SELECTOR, selector)
                            education_data['school'] = school_elem.text.strip()
                            break
                        except NoSuchElementException:
                            continue
                    
                    # Extract degree
                    degree_selectors = [
                        ".t-14.t-normal span[aria-hidden='true']",
                        ".pv-entity__degree-name",
                        ".pvs-entity__summary-subtitle"
                    ]
                    
                    for selector in degree_selectors:
                        try:
                            degree_elem = item.find_element(By.CSS_SELECTOR, selector)
                            education_data['degree'] = degree_elem.text.strip()
                            break
                        except NoSuchElementException:
                            continue
                    
                    # Extract duration
                    try:
                        duration_elem = item.find_element(By.CSS_SELECTOR, ".pv-entity__dates span")
                        education_data['duration'] = duration_elem.text.strip()
                    except NoSuchElementException:
                        education_data['duration'] = None
                    
                    if education_data.get('school'):
                        profile_data['education'].append(education_data)
                
                except Exception as e:
                    self.logger.debug(f"Error extracting individual education: {e}")
                    continue
            
        except Exception as e:
            self.logger.debug(f"Error extracting education section: {e}")
    
    def _extract_skills_section(self, profile_data):
        """Extract skills information"""
        try:
            # Scroll to skills section
            self.behavior_simulator.simulate_human_scrolling("section_reading")
            
            skills_selectors = [
                "#skills ~ .pvs-list__container .pvs-list__item",
                ".pv-profile-section[data-section='skills'] .pv-skill-category-entity",
                ".skills-section .pv-skill-category-entity"
            ]
            
            skills_items = []
            for selector in skills_selectors:
                try:
                    skills_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if skills_items:
                        break
                except NoSuchElementException:
                    continue
            
            for item in skills_items[:20]:  # Limit to first 20 skills
                try:
                    skill_name_selectors = [
                        ".mr1.hoverable-link-text.t-bold span[aria-hidden='true']",
                        ".pv-skill-category-entity__name",
                        ".pvs-entity__summary-title"
                    ]
                    
                    for selector in skill_name_selectors:
                        try:
                            skill_elem = item.find_element(By.CSS_SELECTOR, selector)
                            skill_name = skill_elem.text.strip()
                            if skill_name and skill_name not in profile_data['skills']:
                                profile_data['skills'].append(skill_name)
                            break
                        except NoSuchElementException:
                            continue
                
                except Exception as e:
                    self.logger.debug(f"Error extracting individual skill: {e}")
                    continue
            
        except Exception as e:
            self.logger.debug(f"Error extracting skills section: {e}")
    
    def _extract_contact_info(self, profile_data):
        """Extract contact information if available"""
        try:
            # Try to find and click contact info button
            contact_selectors = [
                "a[data-control-name='contact_see_more']",
                ".pv-s-profile-actions button[data-control-name='contact_see_more']",
                "button[aria-label*='Contact']"
            ]
            
            contact_button = None
            for selector in contact_selectors:
                try:
                    contact_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if contact_button.is_displayed():
                        break
                    else:
                        contact_button = None
                except NoSuchElementException:
                    continue
            
            if contact_button:
                self.behavior_simulator.simulate_mouse_movement(contact_button, "precise")
                contact_button.click()
                time.sleep(random.uniform(2, 4))
                
                # Extract contact information from modal
                contact_info_selectors = [
                    ".pv-contact-info__contact-type",
                    ".ci-email a",
                    ".ci-phone",
                    ".ci-websites a"
                ]
                
                for selector in contact_info_selectors:
                    try:
                        contact_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in contact_elements:
                            text = elem.text.strip()
                            if "@" in text:
                                profile_data['contact_info']['email'] = text
                            elif text.startswith(('http', 'www')):
                                if 'websites' not in profile_data['contact_info']:
                                    profile_data['contact_info']['websites'] = []
                                profile_data['contact_info']['websites'].append(text)
                            elif any(char.isdigit() for char in text) and len(text) > 5:
                                profile_data['contact_info']['phone'] = text
                    except NoSuchElementException:
                        continue
                
                # Close contact info modal
                try:
                    close_button = self.driver.find_element(By.CSS_SELECTOR, ".artdeco-modal__dismiss")
                    close_button.click()
                    time.sleep(random.uniform(1, 2))
                except NoSuchElementException:
                    # Press Escape to close modal
                    ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            
        except Exception as e:
            self.logger.debug(f"Error extracting contact info: {e}")
    
    def _extract_additional_sections(self, profile_data):
        """Extract additional profile sections (certifications, languages, etc.)"""
        try:
            # Extract certifications
            cert_selectors = [
                "#licenses_and_certifications ~ .pvs-list__container .pvs-list__item",
                ".pv-profile-section[data-section='certifications'] .pv-entity__summary-info"
            ]
            
            for selector in cert_selectors:
                try:
                    cert_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for item in cert_items[:5]:
                        try:
                            cert_name = item.find_element(By.CSS_SELECTOR, ".mr1.hoverable-link-text.t-bold span").text.strip()
                            cert_issuer = item.find_element(By.CSS_SELECTOR, ".t-14.t-normal span").text.strip()
                            profile_data['certifications'].append({
                                'name': cert_name,
                                'issuer': cert_issuer
                            })
                        except NoSuchElementException:
                            continue
                    break
                except NoSuchElementException:
                    continue
            
            # Extract languages
            lang_selectors = [
                "#languages ~ .pvs-list__container .pvs-list__item",
                ".pv-profile-section[data-section='languages'] .pv-entity__summary-info"
            ]
            
            for selector in lang_selectors:
                try:
                    lang_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for item in lang_items[:5]:
                        try:
                            lang_name = item.find_element(By.CSS_SELECTOR, ".mr1.hoverable-link-text.t-bold span").text.strip()
                            profile_data['languages'].append(lang_name)
                        except NoSuchElementException:
                            continue
                    break
                except NoSuchElementException:
                    continue
            
        except Exception as e:
            self.logger.debug(f"Error extracting additional sections: {e}")
    
    def save_data(self, filename=None, format='json'):
        """Save scraped data to file"""
        try:
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)

            if not filename:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"linkedin_profiles_{timestamp}"
            
            if format.lower() == 'json':
                filename += '.json'
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == 'csv':
                filename += '.csv'
                filepath = os.path.join(output_dir, filename)
                if self.scraped_data:
            #         # Flatten the data for CSV
            #         structured_data = []
            #         for profile in self.scraped_data:
            #             if isinstance(profile, list):
            #                 for subprofile in profile:
            #                     if isinstance(subprofile, dict):
            #                         structured_data.append(subprofile)
            #             elif isinstance(profile, dict):
            #                 structured_data.append(profile)

                    flattened_data = []
                    for profile in self.scraped_data:
                        flat_profile = {
                            'name': profile['name'],
                            'headline': profile['headline'],
                            'location': profile['location'],
                            # 'connections': profile.get('connections', ''),
                            # 'about': profile.get('about', ''),
                            'url': profile['profile_url'],
                            'scraped_at': profile['scraped_at'],
                            # 'experience_count': len(profile.get('experience', [])),
                            # 'education_count': len(profile.get('education', [])),
                            # 'skills_count': len(profile.get('skills', [])),
                            'current_company': profile['current_company'],
                            # 'current_title': profile.get('experience', [{}])[0].get('title', '') if profile.get('experience') else ''
                        }
                        flattened_data.append(flat_profile)
                    
                    df = pd.DataFrame(flattened_data)
                    df.to_csv(filepath, index=False, encoding='utf-8')
            
            self.logger.info(f"Data saved to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            return None
    
    def get_session_stats(self):
        """Get current session statistics"""
        current_time = time.time()
        session_duration = current_time - self.session_data['session_start']
        
        stats = {
            'session_duration_minutes': round(session_duration / 60, 2),
            'profiles_scraped': self.session_data['profiles_scraped'],
            'searches_performed': self.session_data['searches_performed'],
            'failed_profiles': len(self.failed_profiles),
            'success_rate': (self.session_data['profiles_scraped'] / max(1, self.session_data['profiles_scraped'] + len(self.failed_profiles))) * 100,
            'average_time_per_profile': round(session_duration / max(1, self.session_data['profiles_scraped']), 2),
            'errors': self.session_data['errors'],
            'consecutive_errors': self.health_monitor['consecutive_errors'],
            'captcha_encounters': self.health_monitor['captcha_encounters']
        }
        
        return stats
    
    def close(self):
        """Clean up and close the scraper"""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser closed successfully")
            
            # Print final session statistics
            stats = self.get_session_stats()
            self.logger.info(f"Final session stats: {stats}")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

