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

# Define rides
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
    ),

    Ride(
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
    ),
    Ride(
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
    ),
    Ride(
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
    ),
    Ride(
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
    ),
    Ride(
        name="Chip 'n' Dale's GADGETcoaster",
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
    ),
    Ride(
        name="Dumbo the Flying Elephant",
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
    ),
    Ride(
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
    ),
    Ride(
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
    ),
    Ride(
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
    ),
    Ride(
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
    ),
    Ride(
        name="Pirates of the Caribbean",
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
    ),
    Ride(
        name="Roger Rabbit's Car Toon Spin",
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
    ),
    Ride(
        name="Star Tours – The Adventures Continue",
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
    ),
    Ride(
        name="Peter Pan's Flight",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\peter_pans_flight\Peter Pans Flight, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),
    Ride(
        name="Alice in Wonderland",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\alice_in_wonderland\Alice In Wonderland, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),
    Ride(
        name="Jungle Cruise",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\jungle_cruise\Jungle Cruise, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),

    Ride(
        name="King Arthur Carrousel",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\king_arthur_carrousel\King Arthur Carrousel, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),

    Ride(
        name="Mad Tea Party",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\mad_tea_party\Mad Tea Party, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),

    Ride(
        name="Mickey & Minnie's Runaway Railway",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\mickey_minnies_runaway_railway\Mickey Minnies Runaway Railway, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),

    Ride(
        name="Millennium Falcon: Smugglers Run",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\millennium_falcon_smugglers_run\Millennium Falcon Smugglers Run, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),

    Ride(
        name="Mr. Toad's Wild Ride",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\mr_toads_wild_ride\Mr Toads Wild Ride, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),

    Ride(
        name="Pinocchio's Daring Journey",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\pinocchios_daring_journey\Pinocchios Daring Journey, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),

    Ride(
        name="Star Wars: Rise of the Resistance",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\star_wars_rise_of_the_resistance\Star Wars Rise Of The Resistance, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),

    Ride(
        name="Storybook Land Canal Boats",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\storybookland_canal_boats\Storybookland Canal Boats, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),

    Ride(
        name="The Many Adventures of Winnie the Pooh",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\the_many_adventures_of_winnie_the_pooh\The Many Adventures Of Winnie The Pooh, December 2024, Disneyland.csv',
        },
        pushover_user_key="unb249suwmpir19ng1zguhxqxyyfgd",
        pushover_api_token="amqmtqh5hjne37tk68keg9iwytjwhd"
    ),

    Ride(
        name="Tiana's Bayou Adventure",
        url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
        data_paths={  # Paths for your data here
            'January': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, January 2024, Disneyland.csv',
            'February': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, February 2024, Disneyland.csv',
            'March': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, March 2024, Disneyland.csv',
            'April': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, April 2024, Disneyland.csv',
            'May': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, May 2024, Disneyland.csv',
            'June': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, June 2024, Disneyland.csv',
            'July': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, July 2024, Disneyland.csv',
            'August': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, August 2024, Disneyland.csv',
            'September': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, September 2024, Disneyland.csv',
            'October': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, October 2024, Disneyland.csv',
            'November': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, November 2024, Disneyland.csv',
            'December': r'C:\Users\luked\PycharmProjects\disneylandapp\tianas_bayou_adventure\Tianas Bayou Adventure, December 2024, Disneyland.csv',
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
