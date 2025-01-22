import time
import httpx
from bs4 import BeautifulSoup

# Pushover credentials
api_token = "amqmtqh5hjne37tk68keg9iwytjwhd"
user_key = "unb249suwmpir19ng1zguhxqxyyfgd"

# Define the URL
url = "https://www.thrill-data.com/waits/park/dlr/disneyland/"

def send_notification():
    try:
        # Send a GET request to retrieve the page's content
        response = httpx.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all anchor tags with the title attribute containing the ride name
        ride_name_elements = soup.find_all("a", title=True)

        # Iterate through all found ride names to find Mad Tea Party
        for ride in ride_name_elements:
            ride_name = ride.get_text(strip=True)

            if ride_name == "Mad Tea Party":
                parent_tr = ride.find_parent("tr")
                td_elements = parent_tr.find_all("td")

                if len(td_elements) >= 4:  # Ensure there are enough columns
                    # Now, we need to find the Lightning Lane time
                    lightning_lane_anchor = parent_tr.find("a", href="/lightning-lane/dlr")

                    if lightning_lane_anchor:
                        lightning_lane_time = lightning_lane_anchor.get_text(strip=True)
                    else:
                        lightning_lane_time = "Not Available"
                else:
                    lightning_lane_time = "closed"

                if lightning_lane_time == "closed":
                    message = "Mad Tea Party's Lightning Lane is currently closed."
                else:
                    message = f"Current Lightning Lane Time: {lightning_lane_time}"

                # Send the notification using Pushover
                pushover_response = httpx.post(
                    "https://api.pushover.net/1/messages.json",
                    data={
                        "token": api_token,
                        "user": user_key,
                        "title": "Mad Tea Party Lightning Lane Wait Time",
                        "message": message
                    }
                )

                # Log the notification status
                if pushover_response.status_code == 200:
                    print(f"Push Notification Sent: {message}")
                else:
                    print(f"Failed to send notification: {pushover_response.status_code} - {pushover_response.text}")

                break  # Exit the loop once we find Mad Tea Party

    except httpx.RequestError as e:
        print(f"An error occurred while sending the request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


while True:
    send_notification()
    time.sleep(300)  # Wait for 5 minutes (300 seconds)
