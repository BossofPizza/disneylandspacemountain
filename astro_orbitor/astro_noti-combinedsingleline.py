import time
import httpx
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz  # Import pytz for time zone handling

# Pushover credentials
api_token = "amqmtqh5hjne37tk68keg9iwytjwhd"
user_key = "unb249suwmpir19ng1zguhxqxyyfgd"
PUSHOVER_USER_KEY = 'unb249suwmpir19ng1zguhxqxyyfgd'
PUSHOVER_API_TOKEN = 'amqmtqh5hjne37tk68keg9iwytjwhd'

# Define the URL for the Astro Orbitor wait times page
url = "https://www.thrill-data.com/waits/park/dlr/disneyland/"

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
    'January': 'Astro Orbitor, January 2024, Disneyland.csv',
    'February': 'Astro Orbitor, February 2024, Disneyland.csv',
    'March': 'Astro Orbitor, March 2024, Disneyland.csv',
    'April': 'Astro Orbitor, April 2024, Disneyland.csv',
    'June': 'Astro Orbitor, June 2024, Disneyland.csv',
    'July': 'Astro Orbitor, July 2024, Disneyland.csv',
    'August': 'Astro Orbitor, August 2024, Disneyland.csv',
    'September': 'Astro Orbitor, September 2024, Disneyland.csv',
    'October': 'Astro Orbitor, October 2024, Disneyland.csv',
    'November': 'Astro Orbitor, November 2024, Disneyland.csv',
    'December': 'Astro Orbitor, December 2024, Disneyland.csv',
}

# Load all data into a single DataFrame
all_data = []
for month, file_path in months_data.items():
    month_data = pd.read_csv(file_path)
    month_data['Date/Time'] = pd.to_datetime(month_data['Date/Time'])
    month_data['Date'] = month_data['Date/Time'].dt.date  # Extract the date part
    month_data['Day'] = month_data['Date/Time'].dt.day_name()  # Add day of the week
    month_data['Hour'] = month_data['Date/Time'].dt.hour  # Add hour of the day
    all_data.append(month_data)

all_data_df = pd.concat(all_data, ignore_index=True)

# Ensure 'Wait Time' is numeric
all_data_df['Wait Time'] = pd.to_numeric(all_data_df['Wait Time'], errors='coerce')

# Convert 'Day' and 'Month' to categorical type
all_data_df['Day'] = all_data_df['Day'].astype('category')
all_data_df['Month'] = all_data_df['Date/Time'].dt.month.astype('category')

# Prepare data for manual linear regression model
all_data_df['Day_Code'] = all_data_df['Day'].cat.codes
all_data_df['Month_Code'] = all_data_df['Month'].cat.codes

X = all_data_df[['Day_Code', 'Month_Code', 'Hour']].values
y = all_data_df['Wait Time'].values

# Add a column of ones for the intercept term in the linear regression formula
X_ = np.c_[np.ones(X.shape[0]), X]

# Compute the coefficients (beta values) using the normal equation
X_transpose = X_.T
beta = np.linalg.inv(X_transpose.dot(X_)).dot(X_transpose).dot(y)

# Function to predict wait time for a given day, month, and hour
def predict_wait_time(day: str, month: str, hour: int):
    # Convert the day and month to the corresponding numeric codes
    day_code = pd.Categorical([day], categories=all_data_df['Day'].cat.categories).codes[0]
    month_code = pd.Categorical([month], categories=all_data_df['Month'].cat.categories).codes[0]

    # Prepare the input for prediction (add intercept term)
    X_input = np.array([1, day_code, month_code, hour]).reshape(1, -1)

    # Predict the wait time using the linear regression formula
    predicted_wait_time = X_input.dot(beta)
    return predicted_wait_time[0]

# Get the current day, month, and hour in Pacific Time (PT)
pacific_time = pytz.timezone('US/Pacific')
now = datetime.now(pacific_time)  # Get current time in Pacific Time zone

current_day = now.strftime('%A')  # Full weekday name (e.g., "Monday")
current_month = now.strftime('%B')  # Full month name (e.g., "January")
current_hour = now.hour  # Current hour (0-23)

# Predict the wait time for the current day, month, and hour
predicted_time = predict_wait_time(current_day, current_month, current_hour)

# Get the actual wait time from the website
actual_time = None
try:
    # Send a GET request to retrieve the page's content
    response = httpx.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all anchor tags with the title attribute containing the ride name
    ride_name_elements = soup.find_all("a", title=True)

    for ride in ride_name_elements:
        ride_name = ride.get_text(strip=True)

        if ride_name == "Astro Orbitor":
            parent_tr = ride.find_parent("tr")
            td_elements = parent_tr.find_all("td")

            if len(td_elements) >= 4:
                wait_time_td = td_elements[3]
                actual_time = wait_time_td.find("div")["title"] if wait_time_td.find("div") else None
            break
except Exception as e:
    print(f"Error retrieving actual wait time: {e}")

if actual_time is not None:
    actual_time = int(actual_time.replace(" Minute Wait", "").strip())
else:
    actual_time = 0  # Or some other appropriate value if actual time isn't found

# Calculate the difference between the predicted and actual times
difference = predicted_time - actual_time

# Prepare the message content
message = f"Predicted wait time for {current_day} in {current_month} at {current_hour}:00 PT is {predicted_time:.2f} minutes.\n"
message += f"Actual wait time is {actual_time} minutes.\n"

# Compare the predicted time to the actual time
if difference > 10:
    message += "Good time to go! ✅"
elif -10 <= difference <= 10:
    message += "Average time to go! 👌"
else:
    message += "Bad time to go! ❌"

# Send the notification
title = f"Astro Orbitor: {current_day}"
send_pushover_notification(title, message)
