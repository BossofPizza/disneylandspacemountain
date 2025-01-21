import time
import httpx
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import os

# Pushover credentials
api_token = "amqmtqh5hjne37tk68keg9iwytjwhd"
user_key = "unb249suwmpir19ng1zguhxqxyyfgd"
PUSHOVER_USER_KEY = 'unb249suwmpir19ng1zguhxqxyyfgd'
PUSHOVER_API_TOKEN = 'amqmtqh5hjne37tk68keg9iwytjwhd'

# Define the URLs for both rides' wait times pages
url_space_mountain = "https://www.thrill-data.com/waits/park/dlr/disneyland/"
url_big_thunder = "https://www.thrill-data.com/waits/park/dlr/disneyland/"  # Adjust the URL for Big Thunder if different

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


# Define base paths for both directories
base_path_space_mountain = r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain'
base_path_big_thunder_mountain = r'C:\Users\luked\PycharmProjects\disneylandapp\big_thunder_mountain_railroad'

# Create dictionaries for months for both rides
months_data_space_mountain = {
    'January': os.path.join(base_path_space_mountain, 'Space Mountain, January 2024, Disneyland.csv'),
    'February': os.path.join(base_path_space_mountain, 'Space Mountain, February 2024, Disneyland.csv'),
    'March': os.path.join(base_path_space_mountain, 'Space Mountain, March 2024, Disneyland.csv'),
    'April': os.path.join(base_path_space_mountain, 'Space Mountain, April 2024, Disneyland.csv'),
    'June': os.path.join(base_path_space_mountain, 'Space Mountain, June 2024, Disneyland.csv'),
    'July': os.path.join(base_path_space_mountain, 'Space Mountain, July 2024, Disneyland.csv'),
    'August': os.path.join(base_path_space_mountain, 'Space Mountain, August 2024, Disneyland.csv'),
    'September': os.path.join(base_path_space_mountain, 'Space Mountain, September 2024, Disneyland.csv'),
    'October': os.path.join(base_path_space_mountain, 'Space Mountain, October 2024, Disneyland.csv'),
    'November': os.path.join(base_path_space_mountain, 'Space Mountain, November 2024, Disneyland.csv'),
    'December': os.path.join(base_path_space_mountain, 'Space Mountain, December 2024, Disneyland.csv'),
}

months_data_big_thunder_mountain_railroad = {
    'January': os.path.join(base_path_big_thunder_mountain, 'Big Thunder Mountain Railroad, January 2024, Disneyland.csv'),
    'February': os.path.join(base_path_big_thunder_mountain, 'Big Thunder Mountain Railroad, February 2024, Disneyland.csv'),
    'March': os.path.join(base_path_big_thunder_mountain, 'Big Thunder Mountain Railroad, March 2024, Disneyland.csv'),
    'April': os.path.join(base_path_big_thunder_mountain, 'Big Thunder Mountain Railroad, April 2024, Disneyland.csv'),
    'June': os.path.join(base_path_big_thunder_mountain, 'Big Thunder Mountain Railroad, June 2024, Disneyland.csv'),
    'July': os.path.join(base_path_big_thunder_mountain, 'Big Thunder Mountain Railroad, July 2024, Disneyland.csv'),
    'August': os.path.join(base_path_big_thunder_mountain, 'Big Thunder Mountain Railroad, August 2024, Disneyland.csv'),
    'September': os.path.join(base_path_big_thunder_mountain, 'Big Thunder Mountain Railroad, September 2024, Disneyland.csv'),
    'October': os.path.join(base_path_big_thunder_mountain, 'Big Thunder Mountain Railroad, October 2024, Disneyland.csv'),
    'November': os.path.join(base_path_big_thunder_mountain, 'Big Thunder Mountain Railroad, November 2024, Disneyland.csv'),
    'December': os.path.join(base_path_big_thunder_mountain, 'Big Thunder Mountain Railroad, December 2024, Disneyland.csv'),
}


# Load all data for both rides into separate DataFrames
def load_data(months_data):
    all_data = []
    for month, file_path in months_data.items():
        month_data = pd.read_csv(file_path)
        month_data['Date/Time'] = pd.to_datetime(month_data['Date/Time'])
        month_data['Date'] = month_data['Date/Time'].dt.date  # Extract the date part
        month_data['Day'] = month_data['Date/Time'].dt.day_name()  # Add day of the week
        month_data['Hour'] = month_data['Date/Time'].dt.hour  # Add hour of the day
        all_data.append(month_data)

    all_data_df = pd.concat(all_data, ignore_index=True)
    all_data_df['Wait Time'] = pd.to_numeric(all_data_df['Wait Time'], errors='coerce')
    all_data_df['Day'] = all_data_df['Day'].astype('category')
    all_data_df['Month'] = all_data_df['Date/Time'].dt.month.astype('category')
    return all_data_df

# Load data for both rides
all_data_space_mountain = load_data(months_data_space_mountain)
all_data_big_thunder = load_data(months_data_big_thunder_mountain_railroad)

# Prepare data for manual linear regression model for both rides
def prepare_regression_data(all_data_df):
    all_data_df['Day_Code'] = all_data_df['Day'].cat.codes
    all_data_df['Month_Code'] = all_data_df['Month'].cat.codes
    X = all_data_df[['Day_Code', 'Month_Code', 'Hour']].values
    y = all_data_df['Wait Time'].values
    X_ = np.c_[np.ones(X.shape[0]), X]
    X_transpose = X_.T
    beta = np.linalg.inv(X_transpose.dot(X_)).dot(X_transpose).dot(y)
    return beta

# Prepare regression models for both rides
beta_space_mountain = prepare_regression_data(all_data_space_mountain)
beta_big_thunder = prepare_regression_data(all_data_big_thunder)

# Function to predict wait time for a given ride, day, month, and hour
def predict_wait_time(beta, day, month, hour):
    day_code = pd.Categorical([day], categories=all_data_space_mountain['Day'].cat.categories).codes[0]
    month_code = pd.Categorical([month], categories=all_data_space_mountain['Month'].cat.categories).codes[0]
    X_input = np.array([1, day_code, month_code, hour]).reshape(1, -1)
    predicted_wait_time = X_input.dot(beta)
    return predicted_wait_time[0]

# Set the initial notification state for both rides
notified_good_time_space_mountain = False
notified_bad_time_space_mountain = False
notified_good_time_big_thunder = False
notified_bad_time_big_thunder = False

# Infinite loop to run every 30 seconds
while True:
    now = datetime.now()
    current_day = now.strftime('%A')  # Full weekday name (e.g., "Monday")
    current_month = now.strftime('%B')  # Full month name (e.g., "January")
    current_hour = now.hour  # Current hour (0-23)

    # Predict the wait time for both rides
    predicted_time_space_mountain = predict_wait_time(beta_space_mountain, current_day, current_month, current_hour)
    predicted_time_big_thunder = predict_wait_time(beta_big_thunder, current_day, current_month, current_hour)

    # Get the actual wait times from the website for both rides
    actual_time_space_mountain = None
    actual_time_big_thunder = None

    try:
        response = httpx.get(url_space_mountain)
        soup = BeautifulSoup(response.text, "html.parser")
        ride_name_elements = soup.find_all("a", title=True)

        for ride in ride_name_elements:
            ride_name = ride.get_text(strip=True)
            if ride_name == "Space Mountain":
                parent_tr = ride.find_parent("tr")
                td_elements = parent_tr.find_all("td")
                if len(td_elements) >= 4:
                    wait_time_td = td_elements[3]
                    actual_time_space_mountain = wait_time_td.find("div")["title"] if wait_time_td.find("div") else None
                break
    except Exception as e:
        print(f"Error retrieving actual Space Mountain wait time: {e}")

    try:
        response = httpx.get(url_big_thunder)
        soup = BeautifulSoup(response.text, "html.parser")
        ride_name_elements = soup.find_all("a", title=True)

        for ride in ride_name_elements:
            ride_name = ride.get_text(strip=True)
            if ride_name == "Big Thunder Mountain Railroad":
                parent_tr = ride.find_parent("tr")
                td_elements = parent_tr.find_all("td")
                if len(td_elements) >= 4:
                    wait_time_td = td_elements[3]
                    actual_time_big_thunder = wait_time_td.find("div")["title"] if wait_time_td.find("div") else None
                break
    except Exception as e:
        print(f"Error retrieving actual Big Thunder wait time: {e}")

    # Process actual times for both rides
    if actual_time_space_mountain is not None:
        actual_time_space_mountain = int(actual_time_space_mountain.replace(" Minute Wait", "").strip())
    else:
        actual_time_space_mountain = 0

    if actual_time_big_thunder is not None:
        actual_time_big_thunder = int(actual_time_big_thunder.replace(" Minute Wait", "").strip())
    else:
        actual_time_big_thunder = 0

    # Calculate the difference for both rides
    difference_space_mountain = predicted_time_space_mountain - actual_time_space_mountain
    difference_big_thunder = predicted_time_big_thunder - actual_time_big_thunder

    # Handle notifications for both rides
    if difference_space_mountain > 10 and not notified_good_time_space_mountain:
        message = f"Predicted wait time for Space Mountain: {predicted_time_space_mountain:.2f} minutes.\nActual wait time: {actual_time_space_mountain} minutes.\nGood time to go! ✅"
        title = f"Space Mountain: {current_day}"
        send_pushover_notification(title, message)
        notified_good_time_space_mountain = True
        notified_bad_time_space_mountain = False

    if difference_big_thunder > 10 and not notified_good_time_big_thunder:
        message = f"Predicted wait time for Big Thunder Mountain Railroad: {predicted_time_big_thunder:.2f} minutes.\nActual wait time: {actual_time_big_thunder} minutes.\nGood time to go! ✅"
        title = f"Big Thunder Mountain: {current_day}"
        send_pushover_notification(title, message)
        notified_good_time_big_thunder = True
        notified_bad_time_big_thunder = False

    # Handle bad time notifications for both rides
    if difference_space_mountain <= 10 and not notified_bad_time_space_mountain:
        message = f"Predicted wait time for Space Mountain: {predicted_time_space_mountain:.2f} minutes.\nActual wait time: {actual_time_space_mountain} minutes.\nNo longer a good time to go. ❌"
        title = f"Space Mountain: {current_day}"
        send_pushover_notification(title, message)
        notified_good_time_space_mountain = False
        notified_bad_time_space_mountain = True

    if difference_big_thunder <= 10 and not notified_bad_time_big_thunder:
        message = f"Predicted wait time for Big Thunder Mountain Railroad: {predicted_time_big_thunder:.2f} minutes.\nActual wait time: {actual_time_big_thunder} minutes.\nNo longer a good time to go. ❌"
        title = f"Big Thunder Mountain: {current_day}"
        send_pushover_notification(title, message)
        notified_good_time_big_thunder = False
        notified_bad_time_big_thunder = True

    # Wait for the next iteration
    time.sleep(30)