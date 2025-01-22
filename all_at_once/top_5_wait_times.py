import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import httpx

class Ride:
    def __init__(self, name, url, data_paths, pushover_user_key, pushover_api_token):
        self.name = name
        self.url = url
        self.data_paths = data_paths
        self.pushover_user_key = pushover_user_key
        self.pushover_api_token = pushover_api_token
        self.time_shift = -3  # Adjust time here if needed

    def calculate_average_wait_time(self, timezone='US/Pacific'):
        local_time = datetime.now() + timedelta(hours=self.time_shift)
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
                df['Date/Time'] = pd.to_datetime(df['Date/Time']).dt.tz_localize('UTC')
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

    def get_value(self, predicted_wait_time, actual_wait_time):
        if predicted_wait_time is None or actual_wait_time == 0:
            return float('inf')  # High value means it will not be selected
        return actual_wait_time - predicted_wait_time  # Smaller difference is better

    def send_notification(self, message):
        try:
            response = httpx.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": self.pushover_api_token,
                    "user": self.pushover_user_key,
                    "title": "Top Ride Wait Times",
                    "message": message
                }
            )

            if response.status_code == 200:
                print(f"Push Notification Sent: {message}")
            else:
                print(f"Failed to send notification: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending notification: {e}")

# Define all rides
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
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),

    Ride(
        name="Astro Orbitor",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\astro_orbitor\Astro Orbitor, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    )

]

# Check wait times for all rides
ride_values = []

for ride in rides:
    predicted_wait_time = ride.calculate_average_wait_time()
    actual_wait_time = ride.fetch_actual_wait_time()
    value = ride.get_value(predicted_wait_time, actual_wait_time)
    ride_values.append((ride.name, predicted_wait_time, actual_wait_time, value))

# Sort rides by best value
ride_values.sort(key=lambda x: x[3])

# Get top 5 rides
top_rides = ride_values[:5]

# Prepare notification message
message = "\n".join([
    f"{name}: Predicted {predicted:.2f} mins, Actual {actual} mins, Value {value:.2f}"
    for name, predicted, actual, value in top_rides
])

# Send notification
if top_rides:
    rides[0].send_notification(f"Top 5 Rides:\n{message}")