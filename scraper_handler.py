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


def get_user_input():
    """
    Prompts the user for scraping configuration.
    """
    # Define default values
    DEFAULT_EMAIL = "saggy852kr@gmail.com"
    DEFAULT_PASSWORD = "boto3505"

    print("\n--- LinkedIn Scraper Configuration ---")

    # Get Email
    email_input = input(f"Enter LinkedIn email (or press Enter to use default: {DEFAULT_EMAIL}): ")
    email = email_input if email_input else DEFAULT_EMAIL

    # Get Password only if email is not default
    if email == DEFAULT_EMAIL:
        password = DEFAULT_PASSWORD
    else:
        password = input("Enter LinkedIn password: ")

    # Get Mandatory Inputs
    keywords_input = input("Enter the job position you want to search for (e.g., 'IT Recruiter'): ")
    keywords = keywords_input if keywords_input else 'IT Recruiter'

    location_input = input("Enter search location geoURN(e.g., '103644278'): ")
    location = location_input if location_input else '103644278'

    # Get Optional Input
    max_profiles_input = input("Enter max number of profiles to scrape (default: 10): ")
    max_profiles_input = max_profiles_input if max_profiles_input else 10
    try:
        max_profiles = int(max_profiles_input) if max_profiles_input else 10
    except ValueError:
        print("Invalid input. Using default value of 50 for max profiles.")
        max_profiles = 50

    return {
        "email": email,
        "password": password,
        "keywords": keywords,
        "location": location,
        "max_profiles": max_profiles
    }


if __name__ == "__main__":
    load_dotenv()
    print("🚀 Starting LinkedIn scraper manually...")

    user_config = get_user_input()
    try:
        result = scrape_linkedin_handler(user_config, None)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
