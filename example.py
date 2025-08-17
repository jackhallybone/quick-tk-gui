import time
import tkinter as tk

import matplotlib.pyplot as plt

from quick_tk_gui import GUI, presets


def setup_ui(gui):
    """Define the opening layout of the GUI.

    This function runs on the main thread and uses a mixture of presets and custom tkinter.
    """

    # Header frame
    header = tk.Frame(gui.root, height=50)
    header.pack(side="top", fill="x")

    header_label = tk.Label(header, text="Example GUI", font=("Arial", 16))
    header_label.pack(pady=10)

    # Bottom border (using a thin frame)
    header_border = tk.Frame(gui.root, height=1, bg="grey")
    header_border.pack(side="top", fill="x")

    # Content frame
    content = tk.Frame(gui.root)
    content.pack(side="top", fill="both", expand=True)

    # Save a reference to the content frame
    gui.content_frame = content

    presets.add_text_input(
        gui,
        container=gui.content_frame,
        prompt="Enter your name:",
    )


def prompt_for_number_of_trials(gui):
    """Prompt the user to choose the number of trials to complete."""

    # Add a preset n_button user input to select the number of trials
    gui.on_main_thread(
        presets.add_n_button_input,
        gui=gui,
        container=gui.content_frame,
        prompt="How many trials?",
        buttons=[
            {"name": "1", "value": 1, "keybindings": ["1"]},
            {"name": "2", "value": 2, "keybindings": ["2"]},
            {"name": "3", "value": 3, "keybindings": ["3"]},
            {"name": "4", "value": 4, "keybindings": ["4"]},
        ],
    )

    # Wait for the user to respond with the number of trials
    num_trials, _ = gui.get_user_input()

    # Remove the number of trials user input
    gui.on_main_thread(gui.clear_current_input_ui)

    return num_trials


def present_trial(gui):
    """Present an example trial where two buttons are shown and reaction time is measured."""

    def add_AB_user_input(gui):
        """Add a two button A/B user input choice."""
        presets.add_n_button_input(
            gui=gui,
            container=gui.content_frame,
            prompt="Choose an option",
            buttons=[
                {"name": "A", "value": "A", "keybindings": ["A", "a"]},
                {"name": "B", "value": "B", "keybindings": ["B", "b"]},
            ],
        )

    # Fake a trial being presented (show some text, wait, then remove it)
    gui.on_main_thread(presets.add_text, container=gui.content_frame, text="x")
    time.sleep(2)
    gui.on_main_thread(gui.clear_frame, gui.content_frame)

    # Add the user input for the trial response
    gui.on_main_thread(add_AB_user_input, gui)

    # Wait for and capture the user response
    start_time = time.time()
    value, timestamp = gui.get_user_input()
    response_time = timestamp - start_time
    print(f"User input: '{value}' at {timestamp} in {response_time}")

    # Remove the trial response user input
    gui.on_main_thread(gui.clear_current_input_ui)

    return response_time


def show_data(data, participant_name):
    """Show data using matplotlib. Matplotlib must be run on the main thread."""
    plt.plot(data)
    plt.title(f"Responses by '{participant_name}'")
    plt.show()


def run_app(gui):
    """Define the app logic.

    This function runs in a background thread and so any GUI updates must be passed to the main thread.
    """

    # Wait until the user has pressed "START" and clear it from the screen
    participant_name, _ = gui.get_user_input()
    gui.on_main_thread(gui.clear_current_input_ui)

    # Prompt the user to choose the number of trials to complete
    num_trials = prompt_for_number_of_trials(gui)

    # Present each trial and capture the response
    response_times = []
    while len(response_times) < num_trials:
        response_time = present_trial(gui)
        response_times.append(response_time)

    # Display the responses in a plot, which has to run on the main thread
    gui.on_main_thread(show_data, response_times, participant_name)

    # Close the window once complete
    gui.close()


gui = GUI(name="Example GUI", setup_ui=setup_ui, run_app=run_app)
