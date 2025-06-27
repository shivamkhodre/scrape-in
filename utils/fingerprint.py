import random
import logging

class BrowserFingerprintManager:
    """Advanced browser fingerprinting to avoid detection"""
    
    def __init__(self):
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864),
            (1280, 720), (1600, 900), (1920, 1200), (2560, 1440),
            (1280, 1024), (1680, 1050), (1024, 768)
        ]
        
        self.window_sizes = [
            (1200, 800), (1366, 768), (1440, 900), (1024, 768),
            (1280, 1024), (1600, 1200), (1300, 850), (1500, 950)
        ]
        
        self.languages = [
            "en-US,en;q=0.9",
            "en-GB,en;q=0.9",
            "en-US,en;q=0.8,es;q=0.6",
            "en-US,en;q=0.9,fr;q=0.8",
            "en-CA,en;q=0.9",
            "en-AU,en;q=0.9"
        ]
        
        self.timezones = [
            "America/New_York", "America/Los_Angeles", "Europe/London",
            "Europe/Paris", "Asia/Tokyo", "Australia/Sydney",
            "America/Chicago", "Europe/Berlin", "Asia/Singapore"
        ]
        
        self.platforms = [
            "Win32", "MacIntel", "Linux x86_64"
        ]
        
        # Realistic hardware configurations
        self.hardware_configs = [
            {"memory": 8, "cores": 4, "gpu": "Intel Iris Xe Graphics"},
            {"memory": 16, "cores": 8, "gpu": "NVIDIA GeForce RTX 3060"},
            {"memory": 32, "cores": 16, "gpu": "AMD Radeon RX 6700 XT"},
            {"memory": 8, "cores": 6, "gpu": "Intel UHD Graphics 620"},
            {"memory": 16, "cores": 12, "gpu": "NVIDIA GeForce GTX 1660"}
        ]
    
    def apply_fingerprint(self, driver):
        """Apply comprehensive browser fingerprinting techniques"""
        try:
            # Set random window size
            width, height = random.choice(self.window_sizes)
            driver.set_window_size(width, height)
            
            # Set language preferences
            language = random.choice(self.languages)
            
            # Apply advanced fingerprinting through CDP
            screen_width, screen_height = random.choice(self.screen_resolutions)
            
            # Override screen properties
            driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                'width': width,
                'height': height,
                'deviceScaleFactor': random.choice([1, 1.25, 1.5, 2]),
                'mobile': False
            })
            
            # Set timezone
            timezone = random.choice(self.timezones)
            driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
                'timezoneId': timezone
            })
            
            # Select hardware configuration
            hardware = random.choice(self.hardware_configs)
            platform = random.choice(self.platforms)
            
            # Override navigator properties with more comprehensive spoofing
            driver.execute_script(f"""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {{
                    get: () => undefined,
                }});
                
                // Spoof plugins
                Object.defineProperty(navigator, 'plugins', {{
                    get: () => [
                        {{name: 'Chrome PDF Plugin', description: 'Portable Document Format'}},
                        {{name: 'Chrome PDF Viewer', description: 'PDF Viewer'}},
                        {{name: 'Native Client', description: 'Native Client'}},
                        {{name: 'Widevine Content Decryption Module', description: 'Enables Widevine licenses'}},
                        {{name: 'Shockwave Flash', description: 'Shockwave Flash 32.0 r0'}}
                    ],
                }});
                
                // Spoof languages
                Object.defineProperty(navigator, 'languages', {{
                    get: () => ['{language.split(',')[0]}', 'en'],
                }});
                
                // Spoof platform
                Object.defineProperty(navigator, 'platform', {{
                    get: () => '{platform}',
                }});
                
                // Spoof hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {hardware['cores']},
                }});
                
                // Spoof device memory
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: () => {hardware['memory']},
                }});
                
                // Add chrome runtime
                window.chrome = {{
                    runtime: {{}},
                    loadTimes: function() {{}},
                    csi: function() {{}},
                    app: {{}}
                }};
                
                // Spoof permissions
                Object.defineProperty(navigator, 'permissions', {{
                    get: () => ({{
                        query: () => Promise.resolve({{ state: 'granted' }}),
                    }}),
                }});
                
                // Spoof WebGL fingerprint
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    if (parameter === 37445) {{
                        return '{hardware["gpu"]}';
                    }}
                    if (parameter === 37446) {{
                        return 'ANGLE (Intel, {hardware["gpu"]} Direct3D11 vs_5_0 ps_5_0, D3D11-27.20.100.8477)';
                    }}
                    return getParameter.call(this, parameter);
                }};
                
                // Spoof canvas fingerprint
                const getContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(contextType, contextAttributes) {{
                    if (contextType === '2d') {{
                        const context = getContext.call(this, contextType, contextAttributes);
                        const getImageData = context.getImageData;
                        context.getImageData = function(sx, sy, sw, sh) {{
                            const imageData = getImageData.call(this, sx, sy, sw, sh);
                            for (let i = 0; i < imageData.data.length; i += 4) {{
                                imageData.data[i] += Math.floor(Math.random() * 3) - 1;
                                imageData.data[i + 1] += Math.floor(Math.random() * 3) - 1;
                                imageData.data[i + 2] += Math.floor(Math.random() * 3) - 1;
                            }}
                            return imageData;
                        }};
                        return context;
                    }}
                    return getContext.call(this, contextType, contextAttributes);
                }};
                
                // Spoof screen properties
                Object.defineProperty(screen, 'width', {{
                    get: () => {screen_width},
                }});
                Object.defineProperty(screen, 'height', {{
                    get: () => {screen_height},
                }});
                Object.defineProperty(screen, 'availWidth', {{
                    get: () => {screen_width},
                }});
                Object.defineProperty(screen, 'availHeight', {{
                    get: () => {screen_height - 40},
                }});
            """)
            
            logging.info(f"Applied advanced fingerprint: {width}x{height}, {timezone}, {language}, {platform}, {hardware['cores']} cores, {hardware['memory']}GB RAM")
            
        except Exception as e:
            logging.warning(f"Failed to apply fingerprint: {e}")
