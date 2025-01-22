import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz  # Import pytz for time zone handling (but we won't use it for time conversion)

# Pushover credentials
PUSHOVER_USER_KEY = 'unb249suwmpir19ng1zguhxqxyyfgd'
PUSHOVER_API_TOKEN = 'amqmtqh5hjne37tk68keg9iwytjwhd'

# Function to send a Pushover notification
def send_pushover_notification(title, message):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message,
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Notification sent successfully!")
    else:
        print(f"Failed to send notification: {response.status_code} - {response.text}")

# Class for wait time analysis
class WaitTimePredictor:
    def __init__(self, data_paths):
        self.data_paths = data_paths

    def calculate_average_wait_time(self):
        # Get the system's current time (no timezone conversion)
        current_time = datetime.now()

        # Print the current time being used for analysis
        print(f"Using current system time for analysis: {current_time}")

        current_hour = current_time.hour
        current_weekday = current_time.weekday()
        one_year_ago = current_time - timedelta(days=365)
        two_weeks_before = one_year_ago - timedelta(days=14)
        two_weeks_after = one_year_ago + timedelta(days=14)

        weighted_wait_times = []
        total_weights = 0

        for month_name, csv_path in self.data_paths.items():
            try:
                df = pd.read_csv(csv_path, parse_dates=['Date/Time'])
                df['Date/Time'] = pd.to_datetime(df['Date/Time'])

                # No timezone conversion, using the datetime as is
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


# Data paths for all months for Millennium Falcon Smugglers Run
data_paths = {
    'January': 'Millennium Falcon Smugglers Run, January 2024, Disneyland.csv',
    'February': 'Millennium Falcon Smugglers Run, February 2024, Disneyland.csv',
    'March': 'Millennium Falcon Smugglers Run, March 2024, Disneyland.csv',
    'April': 'Millennium Falcon Smugglers Run, April 2024, Disneyland.csv',
    'June': 'Millennium Falcon Smugglers Run, June 2024, Disneyland.csv',
    'July': 'Millennium Falcon Smugglers Run, July 2024, Disneyland.csv',
    'August': 'Millennium Falcon Smugglers Run, August 2024, Disneyland.csv',
    'September': 'Millennium Falcon Smugglers Run, September 2024, Disneyland.csv',
    'October': 'Millennium Falcon Smugglers Run, October 2024, Disneyland.csv',
    'November': 'Millennium Falcon Smugglers Run, November 2024, Disneyland.csv',
    'December': 'Millennium Falcon Smugglers Run, December 2024, Disneyland.csv',
}

# Initialize predictor
predictor = WaitTimePredictor(data_paths)

# Calculate the average wait time for the current time
average_wait_time = predictor.calculate_average_wait_time()

# Send the notification if wait time is available
if average_wait_time is not None:
    title = "Millennium Falcon Smugglers Run Wait Time Prediction"
    message = f"Predicted wait time: {average_wait_time:.2f} minutes."
    send_pushover_notification(title, message)
else:
    print("Insufficient data to calculate average wait time.")
