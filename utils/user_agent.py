import random
from fake_useragent import UserAgent

class UserAgentRotator:
    """Enhanced User-Agent rotation with predefined and dynamic agents"""
    
    def __init__(self):
        self.ua = UserAgent()
        
        # High-quality, real User-Agent strings
        self.predefined_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
        
        self.current_index = 0
    
    def get_random_agent(self):
        """Get a random User-Agent from fake_useragent library"""
        try:
            return self.ua.random
        except:
            return self.get_predefined_agent()
    
    def get_chrome_agent(self):
        """Get a Chrome User-Agent"""
        try:
            return self.ua.chrome
        except:
            return self.predefined_agents[0]
    
    def get_predefined_agent(self):
        """Get a predefined User-Agent (rotating)"""
        agent = self.predefined_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.predefined_agents)
        return agent
    
    def get_mixed_agent(self):
        """Get a mixed approach - sometimes random, sometimes predefined"""
        if random.choice([True, False]):
            return self.get_random_agent()
        else:
            return self.get_predefined_agent()
