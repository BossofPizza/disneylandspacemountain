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
        else:
            print(f"No change in category for {self.name}. No notification sent.")

    def start_checking(self):
        while True:
            self.check_wait_time()
            time.sleep(30)


# Ride instances
space_mountain = Ride(
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

big_thunder_mountain_railroad = Ride(
    name="Big Thunder Mountain Railroad",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad\Big Thunder Mountain Railroad, December 2024, Disneyland.csv',
    },
    pushover_user_key='unb249suwmpir19ng1zguhxqxyyfgd',
    pushover_api_token='amqmtqh5hjne37tk68keg9iwytjwhd'
)
astro_orbitor = Ride(
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
autopia = Ride(
    name="Autopia",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\autopia\Autopia, December 2024, Disneyland.csv',
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)
buzz_lightyear_astro_blasters = Ride(
    name="Buzz Lightyear Astro Blasters",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\buzz_lightyear_astro_blasters\Buzz Lightyear Astro Blasters, December 2024, Disneyland.csv',
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)
casey_jr_circus_train = Ride(
    name="Casey Jr. Circus Train",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\casey_jr_circus_train\Casey Jr. Circus Train, December 2024, Disneyland.csv',
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)
chip_n_dale_gadgetcoaster = Ride(
    name="Chip 'N' Dale Gadgetcoaster",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, January 2024, Disneyland.csv",
        'February': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, February 2024, Disneyland.csv",
        'March': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, March 2024, Disneyland.csv",
        'April': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, April 2024, Disneyland.csv",
        'May': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, May 2024, Disneyland.csv",
        'June': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, June 2024, Disneyland.csv",
        'July': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, July 2024, Disneyland.csv",
        'August': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, August 2024, Disneyland.csv",
        'September': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, September 2024, Disneyland.csv",
        'October': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, October 2024, Disneyland.csv",
        'November': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, November 2024, Disneyland.csv",
        'December': r"C:\Users\luked\PycharmProjects\disneylandapp\chip_'n'_dale's_GADGETcoaster\Chip 'N' Dale's Gadgetcoaster, December 2024, Disneyland.csv",
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)
dumbo_the_flying_elephant = Ride(
    name="Dumbo The Flying Elephant",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\dumbo_the_flying_elephant\Dumbo The Flying Elephant, December 2024, Disneyland.csv',
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)
finding_nemo_submarine_voyage = Ride(
    name="Finding Nemo Submarine Voyage",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\finding_nemo_submarine_voyage\Finding Nemo Submarine Voyage, December 2024, Disneyland.csv',
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)
haunted_mansion = Ride(
    name="Haunted Mansion",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\haunted_mansion\Haunted Mansion, December 2024, Disneyland.csv',
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)
indiana_jones_adventure = Ride(
    name="Indiana Jones Adventure",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\indiana_jones_adventure\Indiana Jones Adventure, December 2024, Disneyland.csv',
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)
matterhorn_bobsleds = Ride(
    name="Matterhorn Bobsleds",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\matterhorn\Matterhorn, December 2024, Disneyland.csv',
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)
pirates_of_the_caribbean = Ride(
    name="Pirates Of The Caribbean",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\pirates_of_the_caribbean\Pirates Of The Caribbean, December 2024, Disneyland.csv',
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)
roger_rabbit_car_toon_spin = Ride(
    name="Roger Rabbit'S Car Toon Spin",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, January 2024, Disneyland.csv",
        'February': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, February 2024, Disneyland.csv",
        'March': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, March 2024, Disneyland.csv",
        'April': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, April 2024, Disneyland.csv",
        'May': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, May 2024, Disneyland.csv",
        'June': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, June 2024, Disneyland.csv",
        'July': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, July 2024, Disneyland.csv",
        'August': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, August 2024, Disneyland.csv",
        'September': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, September 2024, Disneyland.csv",
        'October': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, October 2024, Disneyland.csv",
        'November': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, November 2024, Disneyland.csv",
        'December': r"C:\Users\luked\PycharmProjects\disneylandapp\roger_rabbit's_car_toon_spin\Roger Rabbit'S Car Toon Spin, December 2024, Disneyland.csv",
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)
star_tours = Ride(
    name="Star Tours",
    url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
    data_paths={  # Paths for your data here
        'January': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, January 2024, Disneyland.csv',
        'February': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, February 2024, Disneyland.csv',
        'March': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, March 2024, Disneyland.csv',
        'April': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, April 2024, Disneyland.csv',
        'May': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, May 2024, Disneyland.csv',
        'June': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, June 2024, Disneyland.csv',
        'July': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, July 2024, Disneyland.csv',
        'August': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, August 2024, Disneyland.csv',
        'September': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, September 2024, Disneyland.csv',
        'October': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, October 2024, Disneyland.csv',
        'November': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, November 2024, Disneyland.csv',
        'December': r'C:\Users\luked\PycharmProjects\disneylandapp\star_tours\Star Tours, December 2024, Disneyland.csv',
    },
    pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
    pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
)



# Start checking wait times in separate threads
### Through Haunted Mansion Only Bad One is Alice in Wonderland...
space_mountain_thread = threading.Thread(target=space_mountain.start_checking)
space_mountain_thread.daemon = True
space_mountain_thread.start()

big_thunder_mountain_railroad_thread = threading.Thread(target=big_thunder_mountain_railroad.start_checking)
big_thunder_mountain_railroad_thread.daemon = True
big_thunder_mountain_railroad_thread.start()

astro_orbitor_thread = threading.Thread(target=astro_orbitor.start_checking)
astro_orbitor_thread.daemon = True
astro_orbitor_thread.start()

autopia_thread = threading.Thread(target=autopia.start_checking)
autopia_thread.daemon = True
autopia_thread.start()

buzz_lightyear_astro_blasters_thread = threading.Thread(target=buzz_lightyear_astro_blasters.start_checking)
buzz_lightyear_astro_blasters_thread.daemon = True
buzz_lightyear_astro_blasters_thread.start()

casey_jr_circus_train_thread = threading.Thread(target=casey_jr_circus_train.start_checking)
casey_jr_circus_train_thread.daemon = True
casey_jr_circus_train_thread.start()

chip_n_dale_gadgetcoaster_thread = threading.Thread(target=chip_n_dale_gadgetcoaster.start_checking)
chip_n_dale_gadgetcoaster_thread.daemon = True
chip_n_dale_gadgetcoaster_thread.start()

dumbo_the_flying_elephant_thread = threading.Thread(target=dumbo_the_flying_elephant.start_checking)
dumbo_the_flying_elephant_thread.daemon = True
dumbo_the_flying_elephant_thread.start()

finding_nemo_submarine_voyage_thread = threading.Thread(target=finding_nemo_submarine_voyage.start_checking)
finding_nemo_submarine_voyage_thread.daemon = True
finding_nemo_submarine_voyage_thread.start()

haunted_mansion_thread = threading.Thread(target=haunted_mansion.start_checking)
haunted_mansion_thread.daemon = True
haunted_mansion_thread.start()

indiana_jones_adventure_thread = threading.Thread(target=indiana_jones_adventure.start_checking)
indiana_jones_adventure_thread.daemon = True
indiana_jones_adventure_thread.start()

matterhorn_bobsleds_thread = threading.Thread(target=matterhorn_bobsleds.start_checking)
matterhorn_bobsleds_thread.daemon = True
matterhorn_bobsleds_thread.start()

star_tours_thread = threading.Thread(target=star_tours.start_checking)
star_tours_thread.daemon = True
star_tours_thread.start()

roger_rabbit_car_toon_spin_thread = threading.Thread(target=roger_rabbit_car_toon_spin.start_checking)
roger_rabbit_car_toon_spin_thread.daemon = True
roger_rabbit_car_toon_spin_thread.start()

pirates_of_the_caribbean_thread = threading.Thread(target=pirates_of_the_caribbean.start_checking)
pirates_of_the_caribbean_thread.daemon = True
pirates_of_the_caribbean_thread.start()

# Keep the main program running
while True:
    time.sleep(10)

