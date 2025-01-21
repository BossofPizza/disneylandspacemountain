import time
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz  # Library for timezone management

# Pushover credentials
api_token = "amqmtqh5hjne37tk68keg9iwytjwhd"
user_key = "unb249suwmpir19ng1zguhxqxyyfgd"

# Define the URL
url = "https://www.thrill-data.com/waits/park/dlr/disneyland/"

# List of rides you want to check and their time thresholds in hours
rides_to_check = {
    "Space Mountain": 3.0,  # Notify if less than 3 hours out
    "Indiana Jones Adventure": 2.0,  # Notify if less than 2 hours out
    "Big Thunder Mountain Railroad": 1.5  # Notify if less than 1.5 hours out
}

# Initialize the previous state of Lightning Lane times to prevent duplicate notifications
previous_times = {ride: None for ride in rides_to_check}

# Set up Pacific Time timezone
pacific_time = pytz.timezone("America/Los_Angeles")

def parse_time(time_str):
    """Parse the time string and return a datetime object in Pacific Time."""
    try:
        now = datetime.now(pacific_time)
        ride_time = datetime.strptime(time_str, "%I:%M %p")  # Parse time in the format 6:35 PM
        # Adjust date if the ride time is earlier than the current time (assume it's for the next day)
        if ride_time.time() < now.time():
            ride_time += timedelta(days=1)
        # Localize to Pacific Time
        return pacific_time.localize(ride_time)
    except ValueError:
        return None

def get_ride_times():
    """Fetch the Lightning Lane times for the rides."""
    updated_times = {}

    try:
        # Send a GET request to retrieve the page's content
        response = httpx.get(url, timeout=10)  # Adding a timeout for robustness
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
    global previous_times

    while True:
        print("Checking Lightning Lane times...")
        updated_times = get_ride_times()

        # Prepare the notification message only for changes
        messages = []
        now = datetime.now(pacific_time)
        for ride, time_str in updated_times.items():
            if time_str in ["Sold Out", "Closed"]:  # Always notify for "Sold Out" or "Closed"
                if previous_times[ride] != time_str:
                    messages.append(f"{ride}'s Lightning Lane is {time_str}.")
            else:
                ride_time = parse_time(time_str)
                if ride_time:
                    threshold = timedelta(hours=rides_to_check[ride])
                    if ride_time - now <= threshold:
                        if previous_times[ride] != time_str:
                            messages.append(f"{ride}'s Lightning Lane Time: {time_str} (within {rides_to_check[ride]} hours).")
                else:
                    print(f"Could not parse time for {ride}: {time_str}")

        # Send the notification if there are changes
        if messages:
            combined_message = "\n".join(messages)
            send_notification(combined_message)

        # Update the previous times
        previous_times.update(updated_times)

        # Wait for 30 seconds
        time.sleep(30)

if __name__ == "__main__":
    main_loop()
