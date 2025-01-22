import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import pytz  # Import pytz for time zone handling

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

    def calculate_average_wait_time(self, timezone='US/Pacific'):
        pacific = pytz.timezone(timezone)
        current_time = datetime.now(pacific)

        current_hour = current_time.hour
        current_weekday = current_time.weekday()
        one_year_ago = current_time - timedelta(days=365)
        two_weeks_before = one_year_ago - timedelta(days=14)
        two_weeks_after = one_year_ago + timedelta(days=14)

        weighted_wait_times = []
        total_weights = 0

        for month_name, csv_path in self.data_paths.items():
            try:
                # Read CSV file
                df = pd.read_csv(csv_path, parse_dates=['Date/Time'])
                print(f"Data for {month_name}:")
                print(df.head())  # Check the first few rows of data

                # Ensure Date/Time is correctly parsed and converted to timezone
                df['Date/Time'] = pd.to_datetime(df['Date/Time']).dt.tz_localize('UTC').dt.tz_convert(timezone)
                print(f"Converted Date/Time for {month_name}:")
                print(df['Date/Time'].head())  # Check the converted Date/Time

                # Add necessary columns for filtering
                df['Hour'] = df['Date/Time'].dt.hour
                df['Weekday'] = df['Date/Time'].dt.weekday
                df['Date'] = df['Date/Time'].dt.date

                # Print current hour and current weekday for debugging
                print(f"Current hour: {current_hour}, Current weekday: {current_weekday}")

                # Filter data based on current hour
                filtered_data = df[df['Hour'] == current_hour]
                print(f"Filtered data for hour {current_hour} in {month_name}:")
                print(filtered_data.head())  # Check if there's any data for the current hour

                if filtered_data.empty:
                    print(f"No data found for the current hour ({current_hour}) in {month_name}.")
                    continue  # Skip to the next month if no data is found

                for _, row in filtered_data.iterrows():
                    weight = 1

                    # Apply weight based on proximity to the same date last year
                    if row['Date'] == one_year_ago.date():
                        weight = 4
                    elif two_weeks_before.date() <= row['Date'] <= two_weeks_after.date():
                        weight = 2

                    # Double the weight for the same weekday
                    if row['Weekday'] == current_weekday:
                        weight *= 2

                    # Add weighted wait time
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


# Data paths for all months
data_paths = {
    'January': 'Buzz Lightyear Astro Blasters, January 2024, Disneyland.csv',
    'February': 'Buzz Lightyear Astro Blasters, February 2024, Disneyland.csv',
    'March': 'Buzz Lightyear Astro Blasters, March 2024, Disneyland.csv',
    'April': 'Buzz Lightyear Astro Blasters, April 2024, Disneyland.csv',
    'June': 'Buzz Lightyear Astro Blasters, June 2024, Disneyland.csv',
    'July': 'Buzz Lightyear Astro Blasters, July 2024, Disneyland.csv',
    'August': 'Buzz Lightyear Astro Blasters, August 2024, Disneyland.csv',
    'September': 'Buzz Lightyear Astro Blasters, September 2024, Disneyland.csv',
    'October': 'Buzz Lightyear Astro Blasters, October 2024, Disneyland.csv',
    'November': 'Buzz Lightyear Astro Blasters, November 2024, Disneyland.csv',
    'December': 'Buzz Lightyear Astro Blasters, December 2024, Disneyland.csv',
}

# Initialize predictor
predictor = WaitTimePredictor(data_paths)

# Calculate the average wait time for the current time
average_wait_time = predictor.calculate_average_wait_time()

# Send the notification if wait time is available
if average_wait_time is not None:
    title = "Buzz Lightyear Astro Blasters Wait Time Prediction"
    message = f"Predicted wait time: {average_wait_time:.2f} minutes."
    send_pushover_notification(title, message)
else:
    print("Insufficient data to calculate average wait time.")
