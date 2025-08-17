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

## Customer Interfaces

The `presets` module provides some simple user input UI elements, but ktinter can be used as normal to interact with the UI.

To use the user input handling built into `quick_tk_gui`, a custom user input UI must set the following on creation:
- `gui.current_input_container: tk.Widget`: the parent container frame to allow the input UI to be removed.
- `gui.current_input_widgets: set[tk.Widget]`: the interactive elements of the input UI to allow them to be enabled and disabled.
- `gui.current_input_keybindings: set[str]`: a list of keys bound to the `gui.root` (`tk.root`) to allow them to be unbound later.

In the input event handler callback, the input value and timestamp of the input must be set:
- `gui.current_input_value: tk.Variable`: the value of the user input
- `gui.current_input_timestamp: float`: the time of the user input, most likely `= gui.now`.

## Timing

User input events are timestamped. The `presets` module sets the response timestamp early in the event handler callback. The "gui clock" can be accessed with `gui.now`.

By default, the "gui clock" uses `time.time()`, but this can be overwritten using `gui.set_clock()`. For example, to use the [sounddevice Stream](https://python-sounddevice.readthedocs.io/en/0.3.15/api/streams.html#sounddevice.Stream) clock:

```python
gui.set_clock(clock=lambda: stream.time)
```