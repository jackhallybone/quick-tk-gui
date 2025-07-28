from quick_tk_gui import GUI, presets


def layout(gui):
    presets.n_button_row(
        gui,
        gui.root,
        prompt="Press a button:",
        button_bindings={"1": 1, "2": 2, "3": 3},
        keybindings={"1": "1", "2": "2", "3": "3"},
    )


def show_data(data):
    """Show data using matplotlib, which must be run on the main thread."""
    import matplotlib.pyplot as plt

    plt.plot(data)
    plt.show()


def main(gui):

    responses = []
    while len(responses) < 5:

        # Get user input
        value, timestamp = gui.get_user_input()  # blocking
        print(f"User input: {value} at {timestamp}")
        responses.append(value)

    # Display the responses in a plot
    data = [int(response) for response in responses]
    gui.run_on_main_thread(show_data, data)

    # Close the window once complete
    gui.close()


gui = GUI(name="Example", initial_layout=layout, main=main)
