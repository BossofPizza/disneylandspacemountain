import os

def replace_and_create_new_file(ride_name, original_script_file):
    # Read the content of the original script from the file
    try:
        with open(original_script_file, "r", encoding="utf-8") as file:
            original_script = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{original_script_file}' was not found.")
        return

    # Replace the placeholder 'Space Mountain' with the user-provided ride name
    modified_script = original_script.replace("Space Mountain", ride_name)

    # Get the base name of the original script file (without path and extension)
    base_filename = os.path.splitext(os.path.basename(original_script_file))[0]

    # Get the first word of the ride name
    first_word_ride_name = ride_name.split()[0]

    # Generate the filename for the new script (first word of ride name + original filename)
    filename = f"{first_word_ride_name.replace(' ', '_').lower()}_{base_filename}.py"

    # Write the modified script to a new file
    with open(filename, "w", encoding="utf-8") as new_file:
        new_file.write(modified_script)

    print(f"New script created: {filename}")


# Get the ride name from the user (only once)
ride_name_input = input("Enter the ride name: ")

# Get the current directory where the script is running
current_directory = os.getcwd()

# Loop through all .py files in the directory
for filename in os.listdir(current_directory):
    if filename.endswith(".py") and filename != os.path.basename(__file__):  # Exclude the current script file
        full_file_path = os.path.join(current_directory, filename)
        replace_and_create_new_file(ride_name_input, full_file_path)

print("All Python files have been processed.")
