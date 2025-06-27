import random
import datetime
import time
import logging


class RequestThrottler:
    """Advanced request throttling system to mimic natural browsing behavior"""
    
    def __init__(self, min_delay=1, max_delay=10, burst_protection=True):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.burst_protection = burst_protection
        self.last_request_time = 0
        self.request_count = 0
        self.burst_threshold = 5  # Number of requests before applying burst protection
        self.burst_delay_multiplier = 2.0
        self.daily_request_count = 0
        self.daily_request_limit = 1000  # Daily request limit
        self.last_reset_date = datetime.date.today()
        self.session_start_time = time.time()
        self.hourly_limits = {
            'profile_visits': 50,
            'searches': 20,
            'page_views': 100
        }
        self.hourly_counters = {
            'profile_visits': 0,
            'searches': 0,
            'page_views': 0
        }
        self.last_hourly_reset = time.time()
    
    def reset_hourly_counters(self):
        """Reset hourly counters if an hour has passed"""
        if time.time() - self.last_hourly_reset >= 3600:  # 1 hour
            self.hourly_counters = {key: 0 for key in self.hourly_counters}
            self.last_hourly_reset = time.time()
            logging.info("Hourly counters reset")
    
    def check_hourly_limits(self, request_type):
        """Check if hourly limits are exceeded"""
        self.reset_hourly_counters()
        
        if request_type in self.hourly_counters:
            if self.hourly_counters[request_type] >= self.hourly_limits[request_type]:
                wait_time = 3600 - (time.time() - self.last_hourly_reset)
                logging.warning(f"Hourly limit for {request_type} exceeded. Waiting {wait_time:.0f} seconds")
                time.sleep(wait_time)
                self.reset_hourly_counters()
    
    def wait_for_next_request(self, request_type="normal"):
        """Wait appropriate time before next request based on throttling rules"""
        current_time = time.time()
        
        # Reset daily counter if new day
        if datetime.date.today() > self.last_reset_date:
            self.daily_request_count = 0
            self.last_reset_date = datetime.date.today()
            logging.info("Daily request counter reset")
        
        # Check hourly limits
        self.check_hourly_limits(request_type)
        
        # Check daily limit
        if self.daily_request_count >= self.daily_request_limit:
            logging.warning(f"Daily request limit ({self.daily_request_limit}) reached. Stopping.")
            raise Exception("Daily request limit exceeded")
        
        # Calculate base delay with enhanced randomness
        if request_type == "profile_visit":
            # Longer delays for profile visits (more suspicious activity)
            base_delay = random.uniform(self.min_delay * 3, self.max_delay * 2)
            # Add extra randomness for profile visits
            if random.random() < 0.3:  # 30% chance of extra long delay
                base_delay *= random.uniform(1.5, 3.0)
        elif request_type == "search":
            # Medium delays for search requests
            base_delay = random.uniform(self.min_delay * 2, self.max_delay * 1.5)
        elif request_type == "login":
            # Special handling for login requests
            base_delay = random.uniform(2, 5)
        else:
            # Normal delays for other requests
            base_delay = random.uniform(self.min_delay, self.max_delay)
        
        # Apply burst protection with progressive delays
        if self.burst_protection and self.request_count >= self.burst_threshold:
            burst_multiplier = min(self.burst_delay_multiplier + (self.request_count - self.burst_threshold) * 0.5, 5.0)
            burst_delay = base_delay * burst_multiplier
            logging.info(f"Burst protection activated. Extended delay: {burst_delay:.2f}s (multiplier: {burst_multiplier:.1f}x)")
            base_delay = burst_delay
            self.request_count = 0  # Reset burst counter
        
        # Apply time-of-day adjustments (slower during peak hours)
        current_hour = datetime.datetime.now().hour
        if 9 <= current_hour <= 17:  # Business hours
            base_delay *= random.uniform(1.2, 1.8)
            logging.debug("Business hours detected - applying slower delays")
        
        # Ensure minimum time has passed since last request
        time_since_last = current_time - self.last_request_time
        if time_since_last < base_delay:
            wait_time = base_delay - time_since_last
            logging.info(f"Throttling: waiting {wait_time:.2f}s before next {request_type} request")
            time.sleep(wait_time)
        
        # Update counters
        self.last_request_time = time.time()
        self.request_count += 1
        self.daily_request_count += 1
        
        # Update hourly counters
        if request_type in self.hourly_counters:
            self.hourly_counters[request_type] += 1
        
        logging.debug(f"Request #{self.daily_request_count} today, burst count: {self.request_count}")
    
    def apply_smart_delay(self, page_load_time=None, content_length=None):
        """Apply intelligent delay based on page characteristics"""
        # Base delay with more randomness
        delay = random.uniform(2, 8)
        
        # Adjust based on page load time (slower pages = longer delays)
        if page_load_time:
            if page_load_time > 5:
                delay *= random.uniform(1.5, 2.0)
            elif page_load_time > 3:
                delay *= random.uniform(1.2, 1.5)
            elif page_load_time < 1:
                delay *= random.uniform(0.7, 0.9)
        
        # Adjust based on content length (more content = longer read time)
        if content_length:
            if content_length > 50000:  # Very large pages
                delay *= random.uniform(1.8, 2.5)
            elif content_length > 20000:  # Large pages
                delay *= random.uniform(1.3, 1.7)
            elif content_length > 10000:  # Medium pages
                delay *= random.uniform(1.1, 1.4)
            elif content_length < 2000:  # Small pages
                delay *= random.uniform(0.8, 1.0)
        
        # Add random variance to make it more human-like
        variance = random.uniform(-0.5, 1.0)
        delay = max(1, delay + variance)
        
        # Occasionally have very long delays (like getting distracted)
        if random.random() < 0.05:  # 5% chance
            distraction_delay = random.uniform(10, 30)
            delay += distraction_delay
            logging.info(f"Simulating distraction - extra {distraction_delay:.1f}s delay")
        
        logging.info(f"Smart delay applied: {delay:.2f}s")
        time.sleep(delay)
    
    def get_reading_time(self, content_length):
        """Calculate realistic reading time based on content length"""
        # Average reading speed: 200-300 words per minute
        words_per_minute = random.randint(180, 320)
        estimated_words = content_length / 5  # Rough estimate: 5 chars per word
        reading_time = (estimated_words / words_per_minute) * 60
        
        # Add random variance (people don't read at constant speed)
        variance = random.uniform(0.3, 2.5)
        base_time = max(1, reading_time * variance)
        
        # Sometimes people skim or read very carefully
        reading_style = random.choice(['skim', 'normal', 'careful'])
        if reading_style == 'skim':
            base_time *= random.uniform(0.3, 0.6)
        elif reading_style == 'careful':
            base_time *= random.uniform(1.5, 2.5)
        
        return min(base_time, 15)  # Cap at 15 seconds

