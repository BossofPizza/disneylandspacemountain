import pandas as pd
import os
from datetime import datetime, timedelta


# Function to generate data for the entire month
def generate_month_data(ride_name, wait_time, month, year):
    # Generate a list of all dates in the specified month
    start_date = datetime(year, month, 1)
    # Get the last day of the month
    end_date = (start_date.replace(month=start_date.month % 12 + 1, day=1) - timedelta(days=1))

    # Generate a list of all 5-minute intervals in the day
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # Create an empty list to hold the data
    data = []

    for single_date in date_range:
        # For each day, generate time slots from 7:30 am to 12:00 pm
        for hour in range(7, 13):
            for minute in range(0, 60, 5):  # 5-minute intervals
                # Create the datetime for each 5-minute interval
                time = datetime(single_date.year, single_date.month, single_date.day, hour, minute)
                data.append([ride_name, time.strftime('%m/%d/%Y %H:%M'), wait_time])

    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=['Ride', 'Date/Time', 'Wait Time'])

    return df


# Function to generate data for each month of the year
def generate_year_data(ride_name, wait_time, year):
    all_month_data = []
    for month in range(1, 13):  # Loop through all months
        monthly_data = generate_month_data(ride_name, wait_time, month, year)

        # Save each month as a separate CSV file
        month_name = datetime(year, month, 1).strftime('%B')
        file_name = f"{ride_name}, {month_name} {year}, Disneyland.csv"

        # Create the output directory if it doesn't exist
        output_directory = "C:/Users/luked/PycharmProjects/disneylandapp/Output"  # Specify your desired directory here
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Full file path
        output_file_path = os.path.join(output_directory, file_name)

        # Save the data to a CSV file
        monthly_data.to_csv(output_file_path, index=False)

        print(f"CSV file generated: {output_file_path}")


# Input ride name and wait time
ride_name = input("Enter the ride name: ")
wait_time = float(input("Enter the wait time in minutes: "))

# Ask if the data should be for a specific month or the whole year
time_period = input("Would you like data for a specific month or the entire year? (Enter 'month' or 'year'): ").lower()

if time_period == 'month':
    month = int(input("Enter the month (1-12): "))
    year = int(input("Enter the year (e.g., 2024): "))
    result_df = generate_month_data(ride_name, wait_time, month, year)

    # Create the output directory if it doesn't exist
    output_directory = "C:/Users/luked/PycharmProjects/disneylandapp/Output"  # Specify your desired directory here
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Format the file name as "Haunted Mansion, January 2024, Disneyland.csv"
    month_name = datetime(year, month, 1).strftime('%B')
    file_name = f"{ride_name}, {month_name} {year}, Disneyland.csv"

    # Full file path
    output_file_path = os.path.join(output_directory, file_name)

    # Save the data to a CSV file
    result_df.to_csv(output_file_path, index=False)

    print(f"CSV file generated: {output_file_path}")

elif time_period == 'year':
    year = int(input("Enter the year (e.g., 2024): "))
    generate_year_data(ride_name, wait_time, year)
else:
    print("Invalid input. Please enter 'month' or 'year'.")
    exit()
