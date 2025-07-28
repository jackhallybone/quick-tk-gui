# quick-tk-gui

A helper class to quickly create and thread basic [tkinter](https://docs.python.org/3/library/tkinter.html) GUIs.

## Getting started

```
pip install -e .
```

Using a preset layout:

```python
from quick_tk_gui import GUI, presets

def layout(gui):

    presets.n_button(
        gui,
        gui.root,
        prompt="Ready?",
        button_bindings = {
            "Yes": True, # Yes button returns True
            "No": False # No button returns False
        }
        keybindings = {
            "y": "Yes", # y key fires Yes button
            "n": "No", # n key fires No button
        }
    )

def main(gui):

    # Get user input from the buttons
    value, timestamp = gui.get_user_input()
    print(f"User input: {value} at {timestamp}")

    # Close the GUI
    gui.close()

GUI(name="Example GUI", initial_layout=layout, main=main)
```

## Layout and Inputs

The GUI class accepts an `initial_layout` function to set up the tkinter elements on UI, and a `main` function which runs the ongoing functionality.

Currently, there should only be one user input option/type at a time.

### Custom Layouts

Custom UI can be initially set in the `initial_layout` function, and also changed later by interacting with the UI itself (like `gui.root`).

When creating a custom user input
- a [tkinter control variable](https://www.geeksforgeeks.org/python/python-setting-and-retrieving-values-of-tkinter-variable/) called `gui.user_input_var` must be defined, and,
- if the widgets can be enabled and disabled they should be listed in a list called `gui.all_input_widgets`, and,
- on user input, the `user_input_var` value and `user_input_event` event must both be set.

### Preset Layouts

The `presets` module provides some simple layout and user input options. These can be the only elements on the page (`parent=gui.root`) or they can be part of a larger layout.

## Timing

The `clock` argument of the `get_user_input` function can be used to get the response timestamp based on a particular clock. For example, to use the [sounddevice Stream](https://python-sounddevice.readthedocs.io/en/0.3.15/api/streams.html#sounddevice.Stream) clock:

```python
value, timestamp = gui.get_user_input(clock=lambda: stream.time)
```

## Main Thread

The `main` function runs in a background thread to allow tkinter to use the main thread for the GUI. Functions which must run on the main thread, such as displaying data with matplotlib, can be scheduled using the `run_on_main_thread()` function. This creates a deep copy of all args and kwargs for thread safety.

```python
def show_data(data):
    """Show data using matplotlib, which must be run on the main thread."""
    plt.plot(data)
    plt.show()

def main(gui):
    # ...
    gui.run_on_main_thread(show_data, my_data)
    # ...
```