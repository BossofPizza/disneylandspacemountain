import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import pytz

# Define Pushover credentials (replace with your actual keys)
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


# Load all months' CSV files into a dictionary
months_data = {
    'January': 'Buzz Lightyear Astro Blasters, January 2024, Disneyland.csv',
    'February': 'Buzz Lightyear Astro Blasters, February 2024, Disneyland.csv',
    'March': 'Buzz Lightyear Astro Blasters, March 2024, Disneyland.csv',
    # Add other months as needed
}

# Load all data into a single DataFrame
all_data = []
for file_path in months_data.values():
    month_data = pd.read_csv(file_path)
    month_data['Date/Time'] = pd.to_datetime(month_data['Date/Time'])
    month_data['Day'] = month_data['Date/Time'].dt.day_name()  # Extract day of the week
    month_data['Hour'] = month_data['Date/Time'].dt.hour  # Extract hour of the day
    month_data['Minute'] = month_data['Date/Time'].dt.minute  # Extract minute of the hour
    month_data['Wait Time'] = pd.to_numeric(month_data['Wait Time'], errors='coerce')  # Ensure numeric wait times
    all_data.append(month_data)

all_data_df = pd.concat(all_data, ignore_index=True)

# Define the Pacific Time zone
pacific_tz = pytz.timezone('US/Pacific')


# Function to predict wait time with week and day weighting
def predict_wait_time_weighted(hour: int, current_day: str, now: datetime):
    # Convert 'Date/Time' to tz-naive for consistent comparison
    all_data_df['Date/Time'] = all_data_df['Date/Time'].dt.tz_localize(None)

    # Filter data for the specified hour
    hourly_data = all_data_df[all_data_df['Hour'] == hour]

    # Duplicate rows for the current day to give them double weight
    day_weighted_data = pd.concat([hourly_data, hourly_data[hourly_data['Day'] == current_day]])

    # Calculate the date range for two weeks before and after the same time last year
    last_year_date = now.replace(year=now.year - 1)
    start_date = last_year_date - timedelta(weeks=2)
    end_date = last_year_date + timedelta(weeks=2)

    # Ensure the comparison dates are tz-naive
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)

    # Filter for data within the two-week range
    week_weighted_data = day_weighted_data[
        (day_weighted_data['Date/Time'] >= start_date) &
        (day_weighted_data['Date/Time'] <= end_date)
        ]

    # Duplicate rows for the two-week range to give them double weight
    final_weighted_data = pd.concat([day_weighted_data, week_weighted_data])

    # Compute the weighted average wait time
    average_wait_time = final_weighted_data['Wait Time'].mean()

    return average_wait_time


# Get the current time in Pacific Time zone
now = datetime.now(pacific_tz)
current_hour = now.hour  # Current hour (0-23)
current_day = now.strftime('%A')  # Current day of the week (e.g., "Monday")

# Predict the wait time for the current hour with day and week weighting
predicted_time = predict_wait_time_weighted(current_hour, current_day, now)

# Send the notification
title = f"Buzz Lightyear Astro Blasters: {now.strftime('%A')}"
message = f"Buzz Lightyear Astro Blasters on {now.strftime('%A')} from {current_hour}:00 to {current_hour}:59 PT has an average wait time of {predicted_time:.2f} minutes."
send_pushover_notification(title, message)
