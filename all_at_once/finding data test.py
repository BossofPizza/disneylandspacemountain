import os

base_path = r'C:\Users\luked\PycharmProjects\disneylandapp\space_mountain'

months_data_space_mountain = {
    'January': os.path.join(base_path, 'Space Mountain, January 2024, Disneyland.csv'),
    'February': os.path.join(base_path, 'Space Mountain, February 2024, Disneyland.csv'),
    'March': os.path.join(base_path, 'Space Mountain, March 2024, Disneyland.csv'),
    'April': os.path.join(base_path, 'Space Mountain, April 2024, Disneyland.csv'),
    'June': os.path.join(base_path, 'Space Mountain, June 2024, Disneyland.csv'),
    'July': os.path.join(base_path, 'Space Mountain, July 2024, Disneyland.csv'),
    'August': os.path.join(base_path, 'Space Mountain, August 2024, Disneyland.csv'),
    'September': os.path.join(base_path, 'Space Mountain, September 2024, Disneyland.csv'),
    'October': os.path.join(base_path, 'Space Mountain, October 2024, Disneyland.csv'),
    'November': os.path.join(base_path, 'Space Mountain, November 2024, Disneyland.csv'),
    'December': os.path.join(base_path, 'Space Mountain, December 2024, Disneyland.csv'),
}

print("Current working directory:", os.getcwd())