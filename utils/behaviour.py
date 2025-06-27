
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import logging


class HumanBehaviorSimulator:
    """Advanced simulation of human-like behavior during web browsing"""
    
    def __init__(self, driver):
        self.driver = driver
        self.actions = ActionChains(driver)
        self.reading_patterns = ['focused', 'scanning', 'detailed', 'distracted']
        self.mouse_movement_styles = ['smooth', 'jittery', 'precise', 'casual']
    
    def simulate_mouse_movement(self, element=None, style="random"):
        """Simulate realistic mouse movements with different styles"""
        try:
            if style == "random":
                style = random.choice(self.mouse_movement_styles)
            
            if element:
                # Get element location and size
                location = element.location
                size = element.size
                
                if style == "smooth":
                    # Smooth, direct movement to element
                    self.actions.move_to_element_with_offset(
                        element, 
                        random.randint(-size['width']//4, size['width']//4), 
                        random.randint(-size['height']//4, size['height']//4)
                    ).perform()
                elif style == "jittery":
                    # Multiple small movements to simulate nervousness or precision
                    for _ in range(random.randint(2, 4)):
                        self.actions.move_to_element_with_offset(
                            element,
                            random.randint(-10, 10),
                            random.randint(-10, 10)
                        ).perform()
                        time.sleep(random.uniform(0.05, 0.2))
                elif style == "precise":
                    # Very precise movement to center of element
                    self.actions.move_to_element(element).perform()
                else:  # casual
                    # Casual movement with overshooting and correction
                    overshoot_x = random.randint(-20, 20)
                    overshoot_y = random.randint(-20, 20)
                    self.actions.move_to_element_with_offset(
                        element, overshoot_x, overshoot_y
                    ).perform()
                    time.sleep(random.uniform(0.1, 0.3))
                    # Correction movement
                    self.actions.move_to_element(element).perform()
            else:
                # Random mouse movement on page
                body = self.driver.find_element(By.TAG_NAME, "body")
                viewport_width = self.driver.execute_script("return window.innerWidth")
                viewport_height = self.driver.execute_script("return window.innerHeight")
                
                if style == "scanning":
                    # Simulate scanning behavior - multiple quick movements
                    for _ in range(random.randint(3, 6)):
                        x = random.randint(50, viewport_width - 50)
                        y = random.randint(50, viewport_height - 50)
                        self.actions.move_to_element_with_offset(body, x, y).perform()
                        time.sleep(random.uniform(0.2, 0.5))
                else:
                    # Single random movement
                    x = random.randint(100, viewport_width - 100)
                    y = random.randint(100, viewport_height - 100)
                    self.actions.move_to_element_with_offset(body, x, y).perform()
            
            time.sleep(random.uniform(0.1, 0.5))
            
        except Exception as e:
            logging.debug(f"Mouse movement simulation failed: {e}")
    
    def simulate_human_scrolling(self, scroll_type="reading"):
        """Simulate human-like scrolling patterns with various behaviors"""
        try:
            if scroll_type == "reading":
                # Simulate reading behavior with pauses and back-scrolling
                reading_pattern = random.choice(self.reading_patterns)
                
                if reading_pattern == "focused":
                    # Focused reading - consistent small scrolls with longer pauses
                    for _ in range(random.randint(5, 10)):
                        scroll_amount = random.randint(80, 200)
                        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                        time.sleep(random.uniform(2, 5))  # Longer pauses for focused reading
                        
                elif reading_pattern == "scanning":
                    # Quick scanning - faster scrolls with shorter pauses
                    for _ in range(random.randint(8, 15)):
                        scroll_amount = random.randint(150, 400)
                        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                        time.sleep(random.uniform(0.5, 1.5))
                        
                elif reading_pattern == "detailed":
                    # Detailed reading - very slow with frequent back-scrolling
                    for _ in range(random.randint(6, 12)):
                        scroll_amount = random.randint(60, 150)
                        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                        time.sleep(random.uniform(3, 8))
                        
                        # Frequent back-scrolling for re-reading
                        if random.random() < 0.5:
                            back_scroll = random.randint(30, 100)
                            self.driver.execute_script(f"window.scrollBy(0, -{back_scroll});")
                            time.sleep(random.uniform(1, 3))
                            
                else:  # distracted
                    # Distracted reading - irregular patterns
                    for _ in range(random.randint(4, 8)):
                        scroll_amount = random.randint(100, 300)
                        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                        
                        # Random long pauses (getting distracted)
                        if random.random() < 0.3:
                            time.sleep(random.uniform(5, 15))
                        else:
                            time.sleep(random.uniform(1, 4))
                        
                        # Sometimes scroll in wrong direction (lost focus)
                        if random.random() < 0.2:
                            wrong_scroll = random.randint(50, 200)
                            self.driver.execute_script(f"window.scrollBy(0, -{wrong_scroll});")
                            time.sleep(random.uniform(0.5, 2))
            
            elif scroll_type == "browsing":
                # Faster scrolling for general browsing
                total_height = self.driver.execute_script("return document.body.scrollHeight")
                current_height = 0
                
                while current_height < total_height * random.uniform(0.6, 0.9):
                    scroll_amount = random.randint(200, 600)
                    
                    # Occasionally use scroll wheel simulation (more human-like)
                    if random.random() < 0.3:
                        # Simulate scroll wheel with multiple small scrolls
                        for _ in range(random.randint(2, 5)):
                            small_scroll = scroll_amount // random.randint(3, 6)
                            self.driver.execute_script(f"window.scrollBy(0, {small_scroll});")
                            time.sleep(random.uniform(0.05, 0.15))
                    else:
                        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    
                    current_height += scroll_amount
                    time.sleep(random.uniform(0.3, 1.2))
                    
                    # Sometimes pause to "look" at something
                    if random.random() < 0.2:
                        time.sleep(random.uniform(2, 6))
                    
                    # Update total height for dynamic content
                    total_height = self.driver.execute_script("return document.body.scrollHeight")
            
            elif scroll_type == "search_results":
                # Scroll through search results with examination pauses
                for i in range(random.randint(3, 8)):
                    scroll_amount = random.randint(250, 500)
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    
                    # Pause to examine search results
                    if i % 2 == 0:  # Every other scroll
                        time.sleep(random.uniform(2, 5))
                    else:
                        time.sleep(random.uniform(0.5, 1.5))
                    
                    # Sometimes go back to re-examine previous results
                    if random.random() < 0.3:
                        back_amount = random.randint(100, 300)
                        self.driver.execute_script(f"window.scrollBy(0, -{back_amount});")
                        time.sleep(random.uniform(1, 3))
        
        except Exception as e:
            logging.debug(f"Scrolling simulation failed: {e}")
    
    def simulate_typing(self, element, text, typing_speed="normal"):
        """Simulate human typing with realistic timing and mistakes"""
        try:
            element.clear()
            
            # Define typing speeds (characters per minute)
            speeds = {
                "slow": (30, 60),
                "normal": (60, 120),
                "fast": (120, 200),
                "hunt_and_peck": (20, 40)
            }
            
            min_cpm, max_cpm = speeds.get(typing_speed, speeds["normal"])
            
            # Simulate different typing patterns
            typing_pattern = random.choice(['consistent', 'burst', 'hesitant'])
            
            i = 0
            print(text)
            while i < len(text):
                char = text[i]
                
                # Calculate base delay
                base_delay = 60 / random.randint(min_cpm, max_cpm)
                
                # Apply typing pattern modifications
                if typing_pattern == 'burst':
                    # Fast bursts followed by pauses
                    if i % random.randint(5, 10) == 0:
                        base_delay *= random.uniform(3, 8)  # Long pause
                    else:
                        base_delay *= random.uniform(0.3, 0.7)  # Fast typing
                elif typing_pattern == 'hesitant':
                    # Frequent pauses, as if thinking
                    # Frequent pauses, as if thinking
                    if random.random() < 0.3:
                        base_delay *= random.uniform(2, 6)  # Thinking pause
                    else:
                        base_delay *= random.uniform(0.8, 1.2)
            
                # Apply character-specific delays
                if char == ' ':
                    base_delay *= random.uniform(0.5, 1.5)  # Space variations
                elif char in '.,!?':
                    base_delay *= random.uniform(1.5, 3.0)  # Punctuation pauses
                elif char.isupper():
                    base_delay *= random.uniform(1.2, 2.0)  # Shift key delay
                elif char.isdigit():
                    base_delay *= random.uniform(0.8, 1.3)  # Number typing
                
                # Simulate occasional typos and corrections
                if random.random() < 0.05 and i > 0:  # 5% chance of typo
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    element.send_keys(wrong_char)
                    time.sleep(random.uniform(0.2, 0.8))
                    element.send_keys(Keys.BACKSPACE)  # Delete typo
                    time.sleep(random.uniform(0.1, 0.5))
                
                # Type the actual character
                element.send_keys(char)
                time.sleep(base_delay)
                
                i += 1
            
                # Occasional longer pauses (distraction or thinking)
                if random.random() < 0.02:  # 2% chance
                    time.sleep(random.uniform(1, 4))
        
        except Exception as e:
            logging.debug(f"Typing simulation failed: {e}")
    
    def simulate_page_interaction(self, interaction_type="casual"):
        """Simulate various page interactions to appear more human"""
        try:
            if interaction_type == "casual":
                # Random casual interactions
                actions = [
                    self._simulate_highlight_text,
                    self._simulate_right_click,
                    self._simulate_tab_navigation,
                    self._simulate_zoom_action,
                    self._simulate_page_focus_loss
                ]
                
                # Perform 1-3 random actions
                for _ in range(random.randint(1, 3)):
                    action = random.choice(actions)
                    action()
                    time.sleep(random.uniform(0.5, 2.0))
            
            elif interaction_type == "focused":
                # More focused interactions for profile viewing
                self._simulate_highlight_text()
                time.sleep(random.uniform(1, 3))
                self._simulate_scroll_and_pause()
                
            elif interaction_type == "searching":
                # Search-related interactions
                self._simulate_tab_navigation()
                time.sleep(random.uniform(0.5, 1.5))
                self._simulate_page_focus_loss()
        
        except Exception as e:
            logging.debug(f"Page interaction simulation failed: {e}")
    
    def _simulate_highlight_text(self):
        """Simulate text highlighting behavior"""
        try:
            # Find text elements to highlight
            text_elements = self.driver.find_elements(By.CSS_SELECTOR, "p, div, span, h1, h2, h3")
            if text_elements:
                element = random.choice(text_elements)
                if element.text and len(element.text) > 10:
                    # Double-click to select word or triple-click for paragraph
                    action_type = random.choice(['double', 'triple', 'drag'])
                    
                    if action_type == 'double':
                        ActionChains(self.driver).double_click(element).perform()
                    elif action_type == 'triple':
                        ActionChains(self.driver).click(element).click(element).click(element).perform()
                    else:  # drag
                        ActionChains(self.driver).click_and_hold(element).move_by_offset(
                            random.randint(50, 200), 0
                        ).release().perform()
                    
                    time.sleep(random.uniform(0.5, 2.0))
                    # Deselect by clicking elsewhere
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    ActionChains(self.driver).click(body).perform()
        except:
            pass
    
    def _simulate_right_click(self):
        """Simulate right-click context menu"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div, p, img, a")
            if elements:
                element = random.choice(elements)
                ActionChains(self.driver).context_click(element).perform()
                time.sleep(random.uniform(0.5, 1.5))
                # Press Escape to close context menu
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except:
            pass
    
    def _simulate_tab_navigation(self):
        """Simulate tab key navigation"""
        try:
            for _ in range(random.randint(1, 4)):
                ActionChains(self.driver).send_keys(Keys.TAB).perform()
                time.sleep(random.uniform(0.2, 0.8))
        except:
            pass
    
    def _simulate_zoom_action(self):
        """Simulate zoom in/out actions"""
        try:
            zoom_action = random.choice(['+', '-'])
            if zoom_action == '+':
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('+').key_up(Keys.CONTROL).perform()
            else:
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('-').key_up(Keys.CONTROL).perform()
            
            time.sleep(random.uniform(0.5, 1.5))
            
            # Reset zoom
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('0').key_up(Keys.CONTROL).perform()
        except:
            pass
    
    def _simulate_page_focus_loss(self):
        """Simulate losing and regaining page focus"""
        try:
            # Simulate Alt+Tab (switching windows)
            ActionChains(self.driver).key_down(Keys.ALT).send_keys(Keys.TAB).key_up(Keys.ALT).perform()
            time.sleep(random.uniform(2, 8))  # Time "away" from page
            # Click to regain focus
            body = self.driver.find_element(By.TAG_NAME, "body")
            ActionChains(self.driver).click(body).perform()
        except:
            pass
    
    def _simulate_scroll_and_pause(self):
        """Simulate reading behavior with scroll and pause"""
        try:
            # Small scroll down
            self.driver.execute_script("window.scrollBy(0, 100);")
            time.sleep(random.uniform(2, 5))
            # Small scroll up (re-reading)
            self.driver.execute_script("window.scrollBy(0, -50);")
            time.sleep(random.uniform(1, 3))
        except:
            pass
