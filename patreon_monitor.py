# Patreon Tier Availability Monitor
# By Jerren Trifan - https://github.com/Trifall

# this one is specific for drumsanddrams patreon tier availability, but you can modify the implementation for other pages

import logging
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("patreon_monitor.log"), logging.StreamHandler()],
)

# pushover notification settings (for phone notifications)
# sign up at https://pushover.net/ to get these credentials
PUSHOVER_USER_KEY = "YOUR_USER_KEY_HERE"
PUSHOVER_API_TOKEN = "YOUR_API_TOKEN_HERE"

# configuration
URL = "https://www.patreon.com/drumsanddrams/membership"
CHECK_INTERVAL = 15  # seconds
TIER_NAME = "WHISKEY DRUMMERS"

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}


# send a notification to your phone using Pushover or change it to something else
def send_notification(message):
    try:
        if (
            PUSHOVER_USER_KEY == "YOUR_USER_KEY_HERE"
            or PUSHOVER_API_TOKEN == "YOUR_API_TOKEN_HERE"
        ):
            logging.warning(
                "Pushover credentials not configured. Skipping notification."
            )
            return False

        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": PUSHOVER_API_TOKEN,
                "user": PUSHOVER_USER_KEY,
                "message": message,
                "title": "Patreon Tier Available!",
                "priority": 1,
            },
        )
        if response.status_code == 200:
            logging.info("Notification sent successfully")
            return True
        else:
            logging.error(f"Failed to send notification: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error sending notification: {str(e)}")
        return False


# check if the specified Patreon tier is available
def check_patreon_availability():
    try:
        # make the request to the URL
        logging.info(f"Making request to {URL}")
        response = requests.get(URL, headers=HEADERS, timeout=30)

        # check if the request was successful
        if response.status_code != 200:
            logging.error(
                f"Failed to retrieve the page: Status code {response.status_code}"
            )
            return False

        logging.info("Page retrieved successfully")

        # parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        tier_elements = soup.find_all()

        found_tier = False
        is_sold_out = True

        # look through all potential tier elements
        for element in tier_elements:
            if TIER_NAME in element.text:
                logging.info(f"Found tier: {TIER_NAME}")
                found_tier = True

                # navigate up to find the tier card container
                # the tier card is typically a few levels up from the tier name
                tier_card = element
                for _ in range(10):  # look up to 10 levels up
                    if tier_card.parent:
                        tier_card = tier_card.parent

                        # look for "Sold Out" text or disabled button
                        if "Sold Out" in tier_card.text:
                            logging.info(
                                "Tier appears to be sold out (found 'Sold Out' text)"
                            )
                            is_sold_out = True
                            break

                        # look for join/checkout button
                        checkout_link = tier_card.find(
                            "a", {"role": "link", "aria-disabled": "true"}
                        )
                        if checkout_link:
                            logging.info(
                                "Tier appears to be sold out (button is disabled)"
                            )
                            is_sold_out = True
                            break

                        # look for enabled button
                        enabled_link = tier_card.find(
                            "a", {"role": "link", "aria-disabled": "false"}
                        )
                        if enabled_link:
                            logging.info(
                                "Tier appears to be available! (button is enabled)"
                            )
                            is_sold_out = False
                            break

                break  # we found our tier, no need to continue the loop

        if not found_tier:
            logging.warning(f"Could not find tier with name '{TIER_NAME}'")
            return False

        if not is_sold_out:
            logging.info(f"🎉 {TIER_NAME} tier is NOW AVAILABLE!")
            send_notification(
                f"The {TIER_NAME} tier on Patreon is now available! Check it out at {URL}"
            )
            return True
        else:
            logging.info(f"{TIER_NAME} tier is still sold out.")
            return False

    except Exception as e:
        logging.error(f"Error checking availability: {str(e)}")
        return False


def main():
    logging.info("Starting Patreon tier availability monitor")
    logging.info(f"Monitoring URL: {URL}")
    logging.info(f"Looking for tier: {TIER_NAME}")
    logging.info(f"Check interval: {CHECK_INTERVAL} seconds")

    consecutive_failures = 0
    max_failures = 5

    while True:
        try:
            is_available = check_patreon_availability()
            if is_available:
                logging.info(
                    "Tier is available! Continuing to monitor for confirmation..."
                )
                # Check again after a short delay to confirm it's not a false positive
                time.sleep(5)
                confirmation = check_patreon_availability()
                if confirmation:
                    logging.info(
                        "Tier availability confirmed! Monitoring will continue."
                    )

            consecutive_failures = 0  # Reset failure counter on success

        except Exception as e:
            consecutive_failures += 1
            logging.error(f"Error in main loop: {str(e)}")

            if consecutive_failures >= max_failures:
                logging.critical(
                    f"Too many consecutive failures ({consecutive_failures}). Pausing for 5 minutes."
                )
                time.sleep(300)  # pause for 5 minutes
                consecutive_failures = 0  # reset counter after pause

        # log timestamp for next check
        next_check = datetime.now().timestamp() + CHECK_INTERVAL
        next_check_time = datetime.fromtimestamp(next_check).strftime("%H:%M:%S")
        logging.info(f"Next check at {next_check_time}")

        # wait for the configured interval
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
