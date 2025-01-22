import time
import httpx
import os
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import pytz  # Add the pytz import

class Ride:
    def __init__(self, name, url, data_paths, pushover_user_key, pushover_api_token):
        self.name = name
        self.url = url
        self.data_paths = data_paths
        self.pushover_user_key = pushover_user_key
        self.pushover_api_token = pushover_api_token
        self.notified_good_time = False
        self.notified_bad_time = False
        self.beta = None
        self.load_data()

    def load_data(self):
        all_data = []
        day_categories = []  # List to store unique days
        month_categories = []  # List to store unique months

        for month, file_path in self.data_paths.items():
            month_data = pd.read_csv(file_path)
            month_data['Date/Time'] = pd.to_datetime(month_data['Date/Time'])
            month_data['Date'] = month_data['Date/Time'].dt.date
            month_data['Day'] = month_data['Date/Time'].dt.day_name()
            month_data['Hour'] = month_data['Date/Time'].dt.hour
            all_data.append(month_data)

            # Collect unique days and months
            day_categories.extend(month_data['Day'].unique())
            month_categories.extend(month_data['Date/Time'].dt.month_name().unique())

        # Remove duplicates by converting to a set and back to a list
        self.day_categories = list(set(day_categories))
        self.month_categories = list(set(month_categories))

        # Sorting the categories to maintain a consistent order
        self.day_categories.sort()
        self.month_categories.sort()

        all_data_df = pd.concat(all_data, ignore_index=True)
        all_data_df['Wait Time'] = pd.to_numeric(all_data_df['Wait Time'], errors='coerce')
        all_data_df['Day'] = all_data_df['Day'].astype('category')
        all_data_df['Month'] = all_data_df['Date/Time'].dt.month.astype('category')
        self.prepare_regression_data(all_data_df)

    def prepare_regression_data(self, all_data_df):
        all_data_df['Day_Code'] = all_data_df['Day'].cat.codes
        all_data_df['Month_Code'] = all_data_df['Month'].cat.codes
        X = all_data_df[['Day_Code', 'Month_Code', 'Hour']].values
        y = all_data_df['Wait Time'].values
        X_ = np.c_[np.ones(X.shape[0]), X]
        X_transpose = X_.T
        self.beta = np.linalg.inv(X_transpose.dot(X_)).dot(X_transpose).dot(y)

    def predict_wait_time(self, day, month, hour):
        day_code = pd.Categorical([day], categories=self.day_categories).codes[0]
        month_code = pd.Categorical([month], categories=self.month_categories).codes[0]
        X_input = np.array([1, day_code, month_code, hour]).reshape(1, -1)
        predicted_wait_time = X_input.dot(self.beta)
        return predicted_wait_time[0]

    def send_pushover_notification(self, title, message):
        url = "https://api.pushover.net/1/messages.json"
        data = {
            "token": self.pushover_api_token,
            "user": self.pushover_user_key,
            "title": title,
            "message": message,
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"Notification sent successfully for {self.name}!")
        else:
            print(f"Failed to send notification for {self.name}: {response.status_code} - {response.text}")

    def fetch_actual_wait_time(self):
        try:
            print(f"Fetching actual wait time for {self.name}...")
            response = requests.get(self.url)  # Use requests.get instead
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

    def check_and_notify(self, predicted_time, actual_time, day):
        difference = predicted_time - actual_time
        if difference > 10 and not self.notified_good_time:
            message = f"Predicted wait time for {self.name}: {predicted_time:.2f} minutes.\nActual wait time: {actual_time} minutes.\nGood time to go! ✅"
            title = f"{self.name}: {day}"
            self.send_pushover_notification(title, message)
            self.notified_good_time = True
            self.notified_bad_time = False
        elif difference <= 10 and not self.notified_bad_time:
            message = f"Predicted wait time for {self.name}: {predicted_time:.2f} minutes.\nActual wait time: {actual_time} minutes.\nNo longer a good time to go. ❌"
            title = f"{self.name}: {day}"
            self.send_pushover_notification(title, message)
            self.notified_good_time = False
            self.notified_bad_time = True


def get_pacific_time():
    # Define Pacific Time timezone
    pacific_tz = pytz.timezone('US/Pacific')
    # Get current time in Pacific Time zone
    pacific_time = datetime.now(pacific_tz)
    return pacific_time


def main():
    pacific_time = get_pacific_time()
    print(f"Current time in Pacific Time (PT): {pacific_time.strftime('%Y-%m-%d %H:%M:%S')}")

    rides = [
        Ride(
            name="Space Mountain",
            url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
            data_paths={  # Path to CSV files for Space Mountain
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
            data_paths={  # Path to CSV files for Big Thunder
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
            name="Indiana Jones Adventure",
            url="https://www.thrill-data.com/waits/park/dlr/disneyland/",
            data_paths={  # Path to CSV files for Space Mountain
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
            pushover_user_key='unb249suwmpir19ng1zguhxqxyyfgd',
            pushover_api_token='amqmtqh5hjne37tk68keg9iwytjwhd'
        ),
    ]

    while True:
        now = datetime.now()
        current_day = now.strftime('%A')
        current_month = now.strftime('%B')
        current_hour = now.hour

        for ride in rides:
            predicted_time = ride.predict_wait_time(current_day, current_month, current_hour)
            actual_time = ride.fetch_actual_wait_time()
            ride.check_and_notify(predicted_time, actual_time, current_day)

        time.sleep(30)


if __name__ == "__main__":
    main()
