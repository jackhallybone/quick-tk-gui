# quick-tk-gui

A helper class to quickly create and thread basic [tkinter](https://docs.python.org/3/library/tkinter.html) GUIs.

## Getting started

```
pip install -e .
```

For example, use a preset layout to add a button choice to the screen and capture the user response.

```python
from quick_tk_gui import GUI, presets

def initial_layout(gui):

    # Add Yes/No button input to the GUI screen
    presets.add_n_button_input(
        gui=gui,
        container=gui.root,
        prompt="Ready?",
        buttons = [
            {"name": "Yes", "value": True, "keybindings": ["Y", "y"]},
            {"name": "No", "value": False, "keybindings": ["N", "n"]},
        ]
    )

def app_logic(gui):

    # Get user input from the buttons
    value, timestamp = gui.get_user_input()
    print(f"User input: {value} at {timestamp}")

    # Close the GUI window
    gui.close()

GUI(name="Example GUI", initial_layout=initial_layout, app_logic=app_logic)
```

The `presets` module contains some functions for adding elements to the user interface. Alternatively, Tkinter can be used as normal to create custom interfaces.

To keep the GUI responsive, tkinter (and the `initial_layout` function) runs in the *main thread*, and the `app_logic` runs in a *background thread*. Edits to the GUI from the `app_logic` function/thread must be wrapped in the `gui.on_main_thread` function.

## Timing

The `clock` argument of `gui.get_user_input` can be used to get the response timestamp based on a particular clock. By default the timestamp is `time.time()`.

For example, to use the [sounddevice Stream](https://python-sounddevice.readthedocs.io/en/0.3.15/api/streams.html#sounddevice.Stream) clock:

```python
value, timestamp = gui.get_user_input(clock=lambda: stream.time)
```