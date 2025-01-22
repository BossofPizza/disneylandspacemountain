def generate_thread_code():
    import threading

    threads = []

    while True:
        ride_name = input("Enter the ride name (or type 'stop' to finish): ")
        if ride_name.strip().lower() == 'stop':
            break

        # Format the ride name to be lowercase and replace spaces with underscores
        formatted_ride_name = ride_name.replace(" ", "_").lower()

        # Generate the thread creation code
        thread_code = []
        thread_code.append(f"{formatted_ride_name}_thread = threading.Thread(target={formatted_ride_name}.start_checking)")
        thread_code.append(f"{formatted_ride_name}_thread.daemon = True")
        thread_code.append(f"{formatted_ride_name}_thread.start()")

        threads.append("\n".join(thread_code))

    print("\n\n".join(threads))

# Example usage:
generate_thread_code()
