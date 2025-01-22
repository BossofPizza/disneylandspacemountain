import os
import shutil

# Ride names mapping for proper formatting
ride_name_mapping = {
    'spacemountain': 'Space Mountain',
    'astroorbitor': 'Astro Orbitor',
    'buzzlightyearastroblasters': 'Buzz Lightyear Astro Blasters',
    'hauntedmansion': 'Haunted Mansion',
    'hyperspacemountain': 'Hyperspace Mountain',
    'bigthundermountain': 'Big Thunder Mountain',
    'itsasmallworld': 'it\'s a small world',
    'peterpansflight': 'Peter Pans Flight',
    'piratesofthecaribbean': 'Pirates of the Caribbean',
    'indianajones': 'Indiana Jones Adventure',
    'splashmountain': 'Splash Mountain',
    'starwars': 'Star Wars: Rise of the Resistance',
    'matterhorn': 'Matterhorn Bobsleds',
    'autopia': 'Autopia',
    'dumbotheflyingelephant': 'Dumbo the Flying Elephant',
    'findingnemosubmarinevoyage': 'Finding Nemo Submarine Voyage',
    'junglecruise': 'Jungle Cruise',
    'monorail': 'Disneyland Monorail',
    'marktwain': 'Mark Twain Riverboat',
    'mainstreetvehicles': 'Main Street Vehicles',
    'storybooklandcanalboats': 'Storybook Land Canal Boats',
    'snowwhite': 'Snow White\'s Enchanted Wish',
    'caseyjrcircustrain': 'Casey Jr. Circus Train',
    'chipndalesgadgetcoaster': 'Chip \'n\' Dale\'s gadgetcoaster',
    'aliceinwonderland': 'Alice in Wonderland',
    'winniepooh': 'The Many Adventures of Winnie the Pooh',
    'rogerabbit': 'Roger Rabbit\'s Car Toon Spin',
    'tarzanstreehouse': 'Tarzan\'s Treehouse',
    'davycrockett': 'Davy Crockett\'s Explorer Canoes',
    'goofysplayhouse': 'Goofy\'s Playhouse',
    'waltdisneyenchantedtikiroom': 'Walt Disney\'s Enchanted Tiki Room',
    'meetdisneyprincesses': 'Meet Disney Princesses at Royal Hall',
    'mickeyminniesrunawayrailway': 'Mickey Minnies Runaway Railway',
    'millenniumfalcon': 'Millennium Falcon: Smugglers Run',
    'rogerrabbitscartoonspin': 'Roger Rabbit\'s Car Toon Spin',
    'tarzanstreehouse': 'Tarzan\'s Treehouse',
    'disneylandrailroad': 'Disneyland Railroad',
    'disneyvillainsdanceparty': 'Disney Villains Dance Party',
    'disneylandbandcavalcade': 'Disneyland Band Cavalcade',
    'startourstheadventurescontinue': 'Star Tours',
    'madteaparty': 'Mad Tea Party',
    'kingarthurcarrousel': 'King Arthur Carrousel',
    'mrtoadswildride': 'Mr Toads Wild Ride',
    'millenniumfalconsmugglersrun': "Millennium Falcon Smugglers Run"
}

# Month names fully spelled out
month_names = {
    'jan': 'January',
    'feb': 'February',
    'mar': 'March',
    'apr': 'April',
    'may': 'May',
    'jun': 'June',
    'jul': 'July',
    'aug': 'August',
    'sep': 'September',
    'oct': 'October',
    'nov': 'November',
    'dec': 'December'
}

# Specify input and output directories
input_directory = r'C:\Users\luked\PycharmProjects\disneylandapp\csv_formatting'
output_directory = r'C:\Users\luked\PycharmProjects\disneylandapp\Output'

# Get all files in the directory
for filename in os.listdir(input_directory):
    if filename.endswith(".csv") and "download" in filename:
        # Extract ride name and month from filename
        parts = filename.split('_')
        ride_name_code = parts[1].lower()  # Ride name code (e.g., spacemountain, buzzlightyear)
        month_code = parts[2].lower()  # Month code (e.g., apr -> april)

        # Get the formatted ride name from the mapping
        formatted_ride_name = ride_name_mapping.get(ride_name_code, ride_name_code.replace("_", " ").title())

        # Get the full month name
        month_name = month_names.get(month_code, month_code.capitalize())

        # Construct the new file name
        new_filename = f"{formatted_ride_name}, {month_name} 2024, Disneyland.csv"

        # Full paths for input and output files
        input_file = os.path.join(input_directory, filename)
        output_file = os.path.join(output_directory, new_filename)

        # Move and rename the file
        shutil.move(input_file, output_file)
        print(f"Renamed '{filename}' to '{new_filename}'")
