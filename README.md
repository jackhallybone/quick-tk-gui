# quick-tk-gui

A helper class to quickly create and thread [tkinter](https://docs.python.org/3/library/tkinter.html) GUIs, with an optional feature for handling basic user input.

A `ThreadedGUI` instance runs the tkinter GUI in the main thread, with the "app logic" running in a background thread. This allows the GUI to remain responsive while the app code manages its own flow.

Tkinter can be used as normal, and the UI provides a method to pass updates from the app code to the main thread (`run_on_ui_thread()`). Optionally, there is also a pre-built "prompt mechanism" to handle the display, waiting and getting of user input into the app thread.

## Getting started

```
pip install -e .
```

The following snippet shows how a `ThreadedGUI` UI can be used to create a responsive GUI. It uses both direct tkinter and the optional "prompt mechanism" to modify the UI and capture user input.

```python
import tkinter as tk

import quick_tk_gui as qtkgui


def build_ui(gui):
    """Create an initial UI layout (this runs on the main thread during init)."""

    # Use tkinter directly to add a header
    gui.label = tk.Label(gui.root, text="User Response: waiting...", font=("Arial", 14))
    gui.label.pack(pady=(50, 0))

    # Make a frame to hold the prompt
    gui.prompt_frame = tk.Frame(gui.root)
    gui.prompt_frame.pack(expand=True, fill="both")

    # Add a button array prompt to the GUI using the n_button preset UI
    gui.prompt = gui.add_prompt(
        setup_func=qtkgui.presets.n_button,
        parent_frame=gui.prompt_frame,
        label="Choose an option:",
        buttons=[
            {"label": "A", "value": "A", "keybindings": ["A", "a"]},
            {"label": "B", "value": "B", "keybindings": ["B", "b"]},
        ],
    )


def app_logic(gui):
    """Run the app logic in a background thread to keep the UI responsive."""

    # Get user input from the buttons
    value, timestamp = gui.prompt.wait_for_response()
    print(f"User input: '{value}' at {timestamp}")

    # Remove the prompt from the screen (empty the frame)
    gui.remove_prompt(gui.prompt)

    # Update the header with the user response
    gui.run_on_ui_thread(
        lambda: gui.label.config(text=f"User Response: '{value}' at t={timestamp}")
    )


qtkgui.ThreadedGUI(name="Example GUI", build_ui=build_ui, app_logic=app_logic)
```

## Timing

Many factors impact the timing of visual updates and user input capture.

If using the "prompt mechanism", a timestamp is taken as close to the visual render as possible and saved to the `presentation_timestamp` property of the prompt instance. Similarly, the prompt `wait_for_response()` method returns a timestamp taken as close to the user input as possible.

### Clock

Timestamps are taken from the `ThreadedGUI` clock. The `now` property returns the current time.

By default, the clock function uses `time.time()`, but this can be changed using `set_clock()`. For example, this is necessary when comparing UI timestamps to events from other sources such as a [sounddevice](https://github.com/spatialaudio/python-sounddevice/) or [DipStream](https://github.com/jackhallybone/dipstream) stream.

For example, to use the [sounddevice Stream time](https://python-sounddevice.readthedocs.io/en/0.3.15/api/streams.html#sounddevice.Stream.time) as the clock:

```python
gui.set_clock(clock=lambda: stream.time)
```

## API

### `ThreadedGUI`

Instantiate using `ThreadedGUI(name, build_ui, app_logic)`, where `build_ui` is a function which runs on the main thread during init and lays out the initial UI, and `app_logic` is a function which runs on a background thread and handles the ongoing app and interactivity. The `build_ui` function is optional if it acceptable to draw the initial UI after the GUI window opens.

**Methods:**
- `run_on_ui_thread(function, *args, **kwargs)` schedules a function to run on the main (UI) thread. Additional augments are passed to the scheduled function and any returns are returned. Blocks until the scheduled function completes. Deep-copies arguments where possible for thread safety.
- `close()` closes the UI window.
- `set_clock(clock_func)` sets the clock function.
- `add_prompt(setup_func, parent_frame, *args, **kwargs)` adds a new prompt to the UI by calling the setup function with any provided arguments.
    - The setup function could be a `preset` or a custom function (see the example in "Prompt Mechanism" below).
- `remove(prompt)` removes a prompt from the UI (destroys the UI elements and unbinds events).
- `clear_prompts()` removes all prompts from the UI (destroys the UI elements and unbinds events).

**Properties:**
- `root` is the `tk.Tk()` instance.
- `now` is the current time from the clock function.

### Prompts

Prompts should **not** be instantiated directly, but by using the `add_prompt()` method above.

**Methods:**
- `enable()` enables the interactive widgets (eg buttons) in the prompt.
- `disable()` disables the interactive widgets (eg buttons) in the prompt.
- `wait_for_response()` blocks until a user input is captured, and returns the value and timestamp.
- `reset()` resets the state of the prompt so that another user input can be captured without removing and re-creating it.

*The following methods should only be used in the prompt setup function:*
- `set_return_type(type)` sets the type of data that the prompt will return.
- `submit(value)` a callback for binding to widgets or keys which sets the timestamp and value of the user input.
- `track_interactive_widgets(widget)` adds a widget to the set that can be enabled and disabled.
- `track_root_keybindings(key)` adds a key name to the set that can be unbound from the root when the prompt is removed.

**Properties (readonly):**
- `presentation_timestamp` is a timestamp taken as close to the visual render as possible.#

*The following properties should only be used in the prompt setup function:*
- `root` is the Tk() root for binding keypresses to.

## "Prompt Mechanism"

`ThreadedGUI` can be used as a base for directly using tkinter for UI layout and interactivity. For convenience, the "prompt mechanism" provides a basic way of setting up user input.

Additionally, the `presets` module provides some basic prompts, such as:
 a text label, button input or text input.

The examples and API description above provides an overview of using the preset prompts.

### `Presets` module

The presets module provides some basic prompt setup functions. These are all horizontally and vertical centred inside their `parent_frame`.
- `label(label: str, ...)` adds a text label to the UI with no user input interactivity.
- `n_button(label, buttons, ...)` adds a text label with a row of n buttons below it. Returns the value the button pressed.
    - The `buttons` argument is a list of dicts where each dict defines a button. The format of a button dict is like: `{"label": "Yes", "value": True "keybindings": ["Y", "y"]}` .
- `text_entry(label, ...)` adds a text label with a text box below it and a submit button. Returns the string in the text box on submit.
- `dropdown(label, options, ...)` adds a text label with a dropdown box below it and a submit button. The `options` argument should be a list of strings. Returns the string of the selected option on submit.
- `file_select(label, ...)` adds a text label with a button to open a file selection dialogue. Returns the absolute filepath of the selected file.

The required arguments for the setup function are listed above, but there are optional formatting arguments for each preset (for example to customise font and spacing). See the `presets.py` file for the full signature.

### Creating custom prompts

It's possible to create user input from scratch without using the prompt mechanism. However, custom prompts can be connected to the underlying mechanism which could simplify the process.

When creating a custom prompt **the setup function must**:
- Accept an instance of the prompt as an argument (this is init'd and passed by the GUI `add_prompt(...)` function).
- Set the return type of the prompt using `set_return_type(type)`.
- Bind user input events (buttons, keypresses, etc) to the `submit(value)` callback, where the value argument is of the correct return type.
- Keep track of all interactive widgets (for enabling and disabling the prompt) using `track_interactive_widget(widget)`.
- Keep track of all root keybinding (for unbinding when the prompt is removed) using `track_root_keybinding(key)`.
    - Keys should be bound to the root using the `root` property.

#### Example

The following example uses both a preset and a custom prompt.

```python
import time
import tkinter as tk

import quick_tk_gui as qtkgui


def preset_prompt(prompt, parent_frame: tk.Widget):
    """Create a 3 button input choice prompt using a preset."""

    qtkgui.presets.n_button(
        prompt,
        parent_frame=parent_frame,
        label="Select a number:",
        buttons=[
            {"label": "One", "value": 1, "keybindings": ["1"]},
            {"label": "Two", "value": 2, "keybindings": ["2"]},
            {"label": "Three", "value": 3, "keybindings": ["3"]},
        ],
    )


def custom_prompt(prompt, parent_frame: tk.Widget):
    """Create a text input field prompt from scratch."""

    prompt.set_return_type(str)  # set the return type of the custom prompt

    lbl = tk.Label(parent_frame, text="Enter some text:")
    lbl.pack()

    entry = tk.Entry(parent_frame)
    entry.pack()

    prompt.track_interactive_widget(
        entry
    )  # track the interactive widgets in the custom prompt

    b = tk.Button(
        parent_frame, text="Submit", command=lambda: prompt.submit(entry.get())
    )
    b.pack()

    prompt.track_interactive_widget(
        b
    )  # track the interactive widgets in the custom prompt

    keybinding = "<Return>"
    prompt.root.bind(keybinding, lambda _: prompt.submit(entry.get()))

    prompt.track_root_keybinding(
        keybinding
    )  # track the keybindings in the custom prompt


def app_logic(gui):
    """Run the app logic in a background thread to keep the UI responsive."""

    # Create a prompt using a preset and wait for user input
    my_preset_prompt = gui.add_prompt(setup_func=preset_prompt, parent_frame=gui.root)
    value, ts = my_preset_prompt.wait_for_response()
    print("Original preset prompt:", value, ts)

    time.sleep(2)

    # Clear the existing prompt and use it again, then destroy (remove) it
    my_preset_prompt.reset()
    my_preset_prompt.enable()
    value, ts = my_preset_prompt.wait_for_response()
    print("Reset preset prompt:", value, ts)
    gui.remove_prompt(my_preset_prompt)

    time.sleep(2)

    # Create a new prompt, custom defined, wait for then input the destroy it
    my_custom_prompt = gui.add_prompt(setup_func=custom_prompt, parent_frame=gui.root)
    value, ts = my_custom_prompt.wait_for_response()
    print("Original custom prompt:", value, ts)
    gui.remove_prompt(my_custom_prompt)

    time.sleep(2)

    print("Closing...")
    gui.close()


qtkgui.ThreadedGUI(name="Prompt Example", app_logic=app_logic)
```
