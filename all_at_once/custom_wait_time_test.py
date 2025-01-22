import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import pandas as pd
import time
import threading
import httpx

class Ride:
    def __init__(self, name, url, data_paths, pushover_user_key, pushover_api_token):
        self.name = name
        self.url = url
        self.data_paths = data_paths
        self.pushover_user_key = pushover_user_key
        self.pushover_api_token = pushover_api_token
        self.previous_category = None
        self.previous_actual_wait_time = None  # Track the last actual wait time
        self.time_shift = -3  # Change this line for time adjustment: positive for future, negative for past

    def calculate_average_wait_time(self, timezone='US/Pacific'):
        local_time = datetime.now() + timedelta(hours=self.time_shift)  # Apply time shift here
        current_hour = local_time.hour
        current_weekday = local_time.weekday()
        one_year_ago = local_time - timedelta(days=365)
        two_weeks_before = one_year_ago - timedelta(days=14)
        two_weeks_after = one_year_ago + timedelta(days=14)

        weighted_wait_times = []
        total_weights = 0

        for month_name, csv_path in self.data_paths.items():
            try:
                df = pd.read_csv(csv_path, parse_dates=['Date/Time'])
                df['Date/Time'] = pd.to_datetime(df['Date/Time'])
                df['Date/Time'] = df['Date/Time'].dt.tz_localize('UTC')

                df['Hour'] = df['Date/Time'].dt.hour
                df['Weekday'] = df['Date/Time'].dt.weekday
                df['Date'] = df['Date/Time'].dt.date

                filtered_data = df[df['Hour'] == current_hour]

                for _, row in filtered_data.iterrows():
                    weight = 1

                    if row['Date'] == one_year_ago.date():
                        weight = 4
                    elif two_weeks_before.date() <= row['Date'] <= two_weeks_after.date():
                        weight = 2

                    if row['Weekday'] == current_weekday:
                        weight *= 2

                    weighted_wait_times.append(row['Wait Time'] * weight)
                    total_weights += weight

            except FileNotFoundError:
                print(f"File not found: {csv_path}")
            except Exception as e:
                print(f"Error processing file {csv_path}: {e}")

        if weighted_wait_times:
            total_weighted_wait_time = sum(weighted_wait_times)
            average_wait_time = total_weighted_wait_time / total_weights
            return average_wait_time
        else:
            return None

    def fetch_actual_wait_time(self):
        try:
            print(f"Fetching actual wait time for {self.name}...")
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, "html.parser")
            ride_name_elements = soup.find_all("a", title=True)

            for ride in ride_name_elements:
                ride_name = ride.get_text(strip=True)
                if ride_name == self.name:
                    parent_tr = ride.find_parent("tr")
                    td_elements = parent_tr.find_all("td")
                    if len(td_elements) >= 4:
                        wait_time_td = td_elements[3]
                        return int(wait_time_td.find("div")["title"].replace(" Minute Wait", "").strip())
            return 0
        except Exception as e:
            print(f"Error retrieving actual wait time for {self.name}: {e}")
            return 0

    def get_wait_time_category(self, predicted_wait_time, actual_wait_time):
        # Calculate the difference between predicted and actual wait times
        difference = predicted_wait_time - actual_wait_time

        if difference > 10:
            return "good"  # If the difference is greater than 10, it's good
        elif -10 <= difference <= 10:
            return "average"  # If the difference is between -10 and +10, it's average
        else:
            return "bad"  # If the difference is less than -10, it's bad

    def send_notification(self, message):
        try:
            response = httpx.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": self.pushover_api_token,
                    "user": self.pushover_user_key,
                    "title": f"{self.name} Wait Time Update",
                    "message": message
                }
            )

            if response.status_code == 200:
                print(f"Push Notification Sent: {message}")
            else:
                print(f"Failed to send notification: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending notification: {e}")

    def check_wait_time(self):
        predicted_wait_time = self.calculate_average_wait_time()
        actual_wait_time = self.fetch_actual_wait_time()

        if predicted_wait_time is None or actual_wait_time == 0:
            print(f"Could not retrieve wait time for {self.name}.")
            return

        current_category = self.get_wait_time_category(predicted_wait_time, actual_wait_time)

        if current_category != self.previous_category:
            if current_category == "good":
                message = f"Good time to go! ✅ (Predicted: {predicted_wait_time:.2f} mins, Actual: {actual_wait_time} mins)"
            elif current_category == "average":
                message = f"Average wait time. 😐 (Predicted: {predicted_wait_time:.2f} mins, Actual: {actual_wait_time} mins)"
            else:
                message = f"Bad time to go. ❌ (Predicted: {predicted_wait_time:.2f} mins, Actual: {actual_wait_time} mins)"

            self.send_notification(message)
            self.previous_category = current_category

        # Check if the wait time has decreased
        if self.previous_actual_wait_time is not None and actual_wait_time < self.previous_actual_wait_time:
            decrease_message = f"Wait time has decreased! 🎉 (Previous: {self.previous_actual_wait_time} mins, Now: {actual_wait_time} mins)"
            self.send_notification(decrease_message)

        # Update the previous actual wait time
        self.previous_actual_wait_time = actual_wait_time

def process_rides(rides):
    while True:
        for ride in rides:
            print(f"Processing ride: {ride.name}")
            ride.check_wait_time()
            print(f"Finished processing ride: {ride.name}")
            time.sleep(5)  # Optional: Add delay between rides to avoid overloading resources

# Example usage
rides = [
    Ride(
    name="Space Mountain",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain\Space Mountain, December 2024, Disneyland.csv',
    },
    pushover_user_key='unb249suwmpir19ng1zguhxqxyyfgd',
    pushover_api_token='amqmtqh5hjne37tk68keg9iwytjwhd'
)



]

process_rides(rides)
