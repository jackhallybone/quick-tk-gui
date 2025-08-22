import time
import tkinter as tk

import matplotlib.pyplot as plt

from quick_tk_gui import ThreadedGUI, presets


def build_ui(gui):
    """Create an initial UI layout (this runs on the main thread during init)."""

    gui.set_clock(time.perf_counter)

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

    gui.loading_prompt = gui.add_prompt(
        setup_func=presets.label, parent_frame=gui.content_frame, label="Loading..."
    )


def app_logic(gui):
    """Run the app logic in a background thread to keep the UI responsive."""

    time.sleep(2)

    gui.remove_prompt(gui.loading_prompt)

    # Get the participant ID
    prompt = gui.add_prompt(
        setup_func=presets.text_entry,
        parent_frame=gui.content_frame,
        label="Participant ID:",
    )
    participant_id, _ = prompt.wait_for_response()
    gui.remove_prompt(prompt)

    # Get the number of trials to complete
    prompt = gui.add_prompt(
        setup_func=presets.n_button,
        parent_frame=gui.content_frame,
        label="Choose number of trials:",
        buttons=[
            {"label": "1", "value": 1, "keybindings": ["1"]},
            {"label": "2", "value": 2, "keybindings": ["2"]},
            {"label": "3", "value": 3, "keybindings": ["3"]},
            {"label": "4", "value": 4, "keybindings": ["4"]},
            {"label": "5", "value": 5, "keybindings": ["5"]},
        ],
    )
    num_trials, _ = prompt.wait_for_response()
    gui.remove_prompt(prompt)

    # Present each trial and capture the response
    response_times = []
    while len(response_times) < num_trials:
        response_time = present_trial(gui)
        response_times.append(response_time)

    # Display the responses in a plot, which has to run on the main thread
    gui.run_on_ui_thread(show_data, response_times, participant_id)

    # Close the window once complete
    gui.close()


def present_trial(gui):
    """Present an example trial where two buttons are shown and reaction time is measured."""

    def add_AB_user_input(prompt, parent_frame):
        """Add a two button A/B user input choice."""
        presets.n_button(
            prompt,
            parent_frame=parent_frame,
            label="Choose number of trials:",
            buttons=[
                {"label": "A", "value": "A", "keybindings": ["A", "a"]},
                {"label": "B", "value": "B", "keybindings": ["B", "b"]},
            ],
        )

    # Fake a trial being presented (show some text, wait, then remove it)
    prompt = gui.add_prompt(
        setup_func=presets.label, parent_frame=gui.content_frame, label="x"
    )
    time.sleep(2)
    gui.remove_prompt(prompt)

    # Add the user input for the trial response
    prompt = gui.add_prompt(
        setup_func=add_AB_user_input, parent_frame=gui.content_frame
    )

    # Wait for and capture the user response
    value, timestamp = prompt.wait_for_response()
    response_time = timestamp - prompt.presentation_timestamp
    print(f"User input: '{value}' at {timestamp} in {response_time}")

    # Remove the trial response user input
    gui.remove_prompt(prompt)

    return response_time


def show_data(data, participant_name):
    """Show data using matplotlib. Matplotlib must be run on the main thread."""
    plt.plot(data)
    plt.title(f"Responses by '{participant_name}'")
    plt.show()


ThreadedGUI(name="Example", build_ui=build_ui, app_logic=app_logic)
