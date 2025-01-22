import time
from datetime import datetime, timedelta
import httpx
from bs4 import BeautifulSoup
import pytz  # For timezone handling

# Pushover credentials
api_token = "amqmtqh5hjne37tk68keg9iwytjwhd"
user_key = "unb249suwmpir19ng1zguhxqxyyfgd"

# Define the URL
url = "https://www.thrill-data.com/waits/park/dlr/disneyland/"

# List of rides with their notification thresholds in hours
rides_to_check = {
    "Space Mountain": 1.5,
    "Indiana Jones Adventure": 1.5,
    "Big Thunder Mountain Railroad": 1,
    "Matterhorn Bobsleds": 1.5,
    "Autopia": 1,
    "Buzz Lightyear Astro Blasters": 1,
    "Haunted Mansion": 2,
    "Mickey & Minnie's Runaway Railway": 2,
    "Millennium Falcon: Smugglers Run": 1,
    "Pirates of the Caribbean": 1,
    "Roger Rabbit's Car Toon Spin": 2,
    "Star Tours - The Adventures Continue": 1,
    "Tiana's Bayou Adventure": 1.5
}

# Initialize the previous state of Lightning Lane times to prevent duplicate notifications
previous_times = {ride: None for ride in rides_to_check}
notified_in_range = {ride: False for ride in rides_to_check}  # Track notifications for range changes

# Set the timezone to Pacific Time
pacific_tz = pytz.timezone("America/Los_Angeles")

def get_ride_times():
    """Fetch the Lightning Lane times for the rides."""
    updated_times = {}

    try:
        # Send a GET request to retrieve the page's content
        response = httpx.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all anchor tags with the title attribute containing the ride name
        ride_name_elements = soup.find_all("a", title=True)

        # Iterate through all found ride names and check for the specified rides
        for ride in ride_name_elements:
            ride_name = ride.get_text(strip=True)

            if ride_name in rides_to_check:
                parent_tr = ride.find_parent("tr")
                td_elements = parent_tr.find_all("td")

                if len(td_elements) >= 4:  # Ensure there are enough columns
                    lightning_lane_anchor = parent_tr.find("a", href="/lightning-lane/dlr")

                    if lightning_lane_anchor:
                        lightning_lane_time = lightning_lane_anchor.get_text(strip=True)
                    else:
                        lightning_lane_time = "Sold Out"
                else:
                    lightning_lane_time = "Closed"

                updated_times[ride_name] = lightning_lane_time

    except httpx.RequestError as e:
        print(f"An error occurred while fetching data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return updated_times

def parse_time_to_minutes(lightning_time):
    """Convert a Lightning Lane time (e.g., '6:35 PM') to minutes from now in Pacific Time."""
    try:
        # Parse the provided time string
        ride_time = datetime.strptime(lightning_time, "%I:%M %p")

        # Set both times to Pacific Time zone (make both aware)
        now = datetime.now(pacific_tz)
        ride_time = pacific_tz.localize(ride_time.replace(year=now.year, month=now.month, day=now.day))

        # If the ride time is earlier in the day but later than the current time, adjust for next day
        if ride_time < now:
            ride_time += timedelta(days=1)

        delta_minutes = (ride_time - now).total_seconds() / 60
        return delta_minutes
    except ValueError:
        return None  # Invalid or unparseable time

def send_notification(message):
    """Send a combined notification using Pushover."""
    try:
        pushover_response = httpx.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": api_token,
                "user": user_key,
                "title": "Lightning Lane Status for Selected Rides",
                "message": message
            }
        )

        if pushover_response.status_code == 200:
            print(f"Push Notification Sent: {message}")
        else:
            print(f"Failed to send notification: {pushover_response.status_code} - {pushover_response.text}")

    except Exception as e:
        print(f"Error while sending notification: {e}")

def main_loop():
    """Main loop to check and notify about Lightning Lane times."""
    global previous_times, notified_in_range

    while True:
        print("Checking Lightning Lane times...")
        updated_times = get_ride_times()

        # Prepare the notification message only for changes into the range
        messages = []
        for ride, lightning_time in updated_times.items():
            # Parse the time to minutes from now
            if lightning_time in ["Sold Out", "Closed"]:
                minutes_from_now = None
            else:
                minutes_from_now = parse_time_to_minutes(lightning_time)

            # Check if the time has changed
            if previous_times[ride] != lightning_time:
                # Determine if the new time is within the specified range
                threshold_minutes = rides_to_check[ride] * 60

                # Add a green checkmark if the time is within the next hour
                emoji = " ✅" if minutes_from_now is not None and minutes_from_now <= 60 else ""

                if minutes_from_now is not None and minutes_from_now <= threshold_minutes:
                    if not notified_in_range[ride]:  # Notify only if not already in range
                        messages.append(f"{ride}: {lightning_time}{emoji}")
                        notified_in_range[ride] = True
                else:
                    notified_in_range[ride] = False  # Reset if no longer in range

            # Update the previous time for the ride
            previous_times[ride] = lightning_time

        # Send the notification if there are messages
        if messages:
            combined_message = "\n".join(messages)
            send_notification(combined_message)

        # Wait for 30 seconds
        time.sleep(10)

if __name__ == "__main__":
    main_loop()
