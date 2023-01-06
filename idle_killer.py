"""This code enumerates all minimized windows, gets their process names and
elapsed times, and closes the ones that have been minimized for the idle time
limit, while ignoring certain processes specified in the 'exclude_processes'
list.

A GUI is also created to allow the user to input the list of processes to
exclude and the idle time limit before starting the main loop. """
import time
import win32gui
import win32process
import psutil
import tkinter as tk
import os

# Processes that we don't want to close
exclude_processes = ["dwm.exe", "explorer.exe", "Discord.exe", "steam.exe",
                     "idle_killer.exe", "Spotify.exe", "steamwebhelper.exe",
                     "pythonw.exe", "py.exe"]

# Initialize the idle time limit (it will be set by the user in the GUI)
idle_time_limit = 0
# The time interval (in seconds) at which the loop runs
check_interval = 10
minimized_program_names = []
minimized_time = {}
# Initialize a dictionary to store the PIDs for each process
PID = {}


def get_input():
    """Get the input from the GUI and close the window."""
    global exclude_processes, idle_time_limit
    exclude_processes += excluded_processes_entry.get().split(',')
    idle_time_limit = int(elapsed_time_entry.get())
    root.destroy()


# Create a GUI to get the list of excluded processes and the idle time limit
root = tk.Tk()
root.title("Idle Killer")
root.geometry("250x130")

excluded_processes_label = tk.Label(root,
                                    text="Excluded Processes (comma-separated):"
                                    )
excluded_processes_label.pack()
excluded_processes_entry = tk.Entry(root)
excluded_processes_entry.pack()

elapsed_time_label = tk.Label(root, text="Idle Time Limit (seconds):")
elapsed_time_label.pack()
elapsed_time_entry = tk.Entry(root)
# Set a default value of 600 seconds (10 minutes) for the idle time limit
elapsed_time_entry.insert(0, "600")
elapsed_time_entry.pack()

run_button = tk.Button(root, text="Run", command=get_input)
run_button.pack()

root.mainloop()


def get_minimized_window_names():
    """Get a list of minimized window names.
    Returns:
        minimized_names (list): A list of strings representing the names of
            the minimized windows.
        pids (dict): A dictionary mapping the process names to their PIDs.
    """
    # Get a list of all minimized windows
    minimized_windows = []
    win32gui.EnumWindows(lambda hwnd, _: minimized_windows.append(hwnd), 0)
    minimized_windows = [hwnd for hwnd in minimized_windows if
                         win32gui.IsIconic(hwnd)]

    # Get a list of minimized window names and their corresponding PIDs
    minimized_names = []
    pids = {}
    for hwnd in minimized_windows:
        # Get the process ID and process object for the window
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        process_name = process.name()
        # Skip certain processes that we don't want to close
        if process_name in exclude_processes:
            continue
        # Initialize the elapsed time for this window if it is not already in
        # the minimized_time dictionary
        if process_name not in minimized_time:
            minimized_time[process_name] = -check_interval
        # Add the process name and PID to the lists
        pids[process_name] = pid
        minimized_names.append(process_name)
    return minimized_names, pids


def increase_elapsed_time():
    """Increase the elapsed time for each minimized window."""
    for process_name in minimized_time:
        # Increment the elapsed time for this window
        minimized_time[process_name] += check_interval
        print(f"Elapsed time for {process_name}: "
              f"{minimized_time[process_name]} seconds\n")


def close_idle_windows():
    """Close minimized windows that have been idle for a specified amount of
    time. """
    for process_name in minimized_time:
        # Kill the process if the elapsed time is bigger than the specified time
        if minimized_time[process_name] >= idle_time_limit:
            process = psutil.Process(PID[process_name])
            process.kill()
            print(f"Closing the {process_name}\n")


def remove_non_minimized_windows():
    """Remove keys from the minimized_time dictionary that are no longer
    minimized. """
    for process_name in list(minimized_time.keys()):
        if process_name not in minimized_program_names:
            del minimized_time[process_name]


# Main loop
while True:
    os.system('cls')
    minimized_program_names, PID = get_minimized_window_names()
    remove_non_minimized_windows()
    increase_elapsed_time()
    close_idle_windows()
    time.sleep(check_interval)
