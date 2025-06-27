import json
from scraper.scraper import LinkedInScraper  # Make sure this import path matches
from dotenv import load_dotenv
import os

def scrape_linkedin_handler(event, context):
    """
    AWS Lambda handler function to scrape LinkedIn profiles.
    Expects `event` to contain search config parameters.
    """

    # Default configuration (can be overridden by event payload)
    EMAIL = event.get("email", "saggy852kr@gmail.com")
    PASSWORD = event.get("password", "boto3505")
    SEARCH_KEYWORDS = event.get("keywords", "IT Recruiter")
    SEARCH_LOCATION = event.get("location", "United States")
    MAX_PROFILES = event.get("max_profiles", 2)
    print(EMAIL, PASSWORD)
    # Initialize scraper
    scraper = LinkedInScraper(headless=True, proxy=None)

    try:
        if not scraper._create_advanced_driver():
            return {"statusCode": 500, "body": json.dumps("Failed to create browser driver")}

        if not scraper.login(EMAIL, PASSWORD):
            return {"statusCode": 401, "body": json.dumps("Login failed")}

        search_results = scraper.search_profiles(
            keywords=SEARCH_KEYWORDS,
            location=SEARCH_LOCATION,
            max_results=MAX_PROFILES
        )
        scraper.scraped_data.append(search_results)

        # OPTIONAL: detailed scraping
        # scraped_profiles = []
        # for profile in search_results:
        #     detailed_profile = scraper.scrape_profile_details(profile['profile_url'])
        #     if detailed_profile:
        #         detailed_profile.update(profile)
        #         scraped_profiles.append(detailed_profile)
        #         scraper.scraped_data.append(detailed_profile)
        #     time.sleep(random.uniform(3, 8))

        # Save to JSON and CSV
        json_file = scraper.save_data(format='json')
        csv_file = scraper.save_data(format='csv')

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Scraped {len(search_results)} profiles",
                "json_file": json_file,
                "csv_file": csv_file,
                "stats": scraper.get_session_stats()
            })
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(str(e))}

    finally:
        scraper.close()

if __name__ == "__main__":
    load_dotenv()
    print("Starting LinkedIn scraper manually...")

    email = os.getenv('EMAIL') or "saggy852kr@gmail.com"
    password = os.getenv('PASSWORD') or "boto3505"
    keywords = os.getenv('KEYWORDS') or os.getenv('SEARCH_PARAMETER') or "IT Recruiter"
    location = os.getenv('LOCATION') or os.getenv('LOCATION_PARAMETER') or "103644278"
    max_profiles = int(os.getenv('MAX_PROFILES', '10'))  # Default to 2 if not set
    
    event = {
        "email": email,
        "password": password,
        "keywords": keywords,
        "location": location,
        "max_profiles": max_profiles
    }
    
    try:
        result = scrape_linkedin_handler(event, None)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
