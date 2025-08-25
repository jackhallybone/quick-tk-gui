# quick-tk-gui

A helper class to quickly create and thread basic [tkinter](https://docs.python.org/3/library/tkinter.html) GUIs, with an optional feature for handling basic user input.

A `ThreadedGUI` instance runs a tkinter GUI in the main thread, with the "app logic" running in a background thread. This allows the GUI to remain responsive while the app code manages its own flow.

Tkinter can be used as normal, and the UI provides a method to pass updates from the app code to the main thread (`run_on_ui_thread()`). Optionally, there is also a pre-built "prompt mechanism" to handle user input from the UI to the app thread.

## Getting started

```
pip install -e .
```

The following snippet shows how a `ThreadedGUI` UI can be used to create a responsive GUI. It uses both direct tkinter and the optional "prompt" mechanism to modify the UI and capture user input.

```python
import tkinter as tk

from quick_tk_gui import ThreadedGUI, presets


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
        setup_func=presets.n_button,
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


ThreadedGUI(name="Example GUI", build_ui=build_ui, app_logic=app_logic)
```

## Timing

Many factors impact the timing of visual updates and user input capture.

If using the "prompt mechanism", a timestamp is taken as close to the visual render as possible and saved to the `presentation_timestamp` properties. Similarly, the `wait_for_response()` method returns a timestamp taken as close to the user input as possible.

### Clock

Timestamps are taken from the `gui.now` clock, with uses `time.time()` by default. A different clock function can be set using `gui.set_clock()`. For example, to use the [sounddevice Stream](https://python-sounddevice.readthedocs.io/en/0.3.15/api/streams.html#sounddevice.Stream) clock:

```python
gui.set_clock(clock=lambda: stream.time)
```

## API

### `ThreadedGUI`

Instantiate using `ThreadedGUI(name, build_ui, app_logic)`, where `build_ui` is a function which runs on the main thread during init and lays out the initial UI, and `app_logic` is a function which runs on a background thread and handles the ongoing app and interactivity.

Methods:
- `run_on_ui_thread(function, *args, **kwargs)` schedules a function to run on the main (UI) thread, passing the args and kwargs. Deep-copies arguments when possible for thread safety. Blocks until the function returns, and returns its value(s).
- `close()` closes the UI window.
- `set_clock(clock_func)` sets the clock function used in `gui.now` and prompt timestamps.
- `add_prompt(setup_func, parent_frame, *args, **kwargs)` adds a new prompt to the UI by calling the setup function with the arguments.
- `remove(prompt)` removes a prompt from the UI (destroys the UI elements and unbinds events).
- `clear_prompts()` removes all prompts from the UI (destroys the UI elements and unbinds events).

Properties:
- `root` is the `tk.Tk()` instance.
- `now` is the current time from the clock function.

### Prompts

Prompts should **not** be instantiated directly, but by the GUI using `gui.add_prompt(...)`.

Methods:
- `set_return_type(type)` sets the type of data that the prompt will return. Should only be used in the setup function.
- `enable()` enables the interactive widgets (eg buttons) in the prompt.
- `disable()` disables the interactive widgets (eg buttons) in the prompt.
- `submit(value)` sets the time and return value of the prompt. Should only be called as a user input event from an event binding (eg, bound to a button click in the setup function).
- `wait_for_response()` blocks and waits until a user input is captured (a fires `submit()`), and returns the value and timestamp.
- `reset()` resets the state of the prompt so that another user input can be captured without removing and re-creating it.

## "Prompt" Mechanism

`ThreadedGUI` can be used as a base for directly using tkinter for UI layout and interactivity. For convenience, the prompt mechanism provides a basic way of setting up user input.

Additionally, the `presets` module provides some basic prompts, such as a text label, button input or text input.

The examples and API description above provides an overview of using the preset prompts.

### Creating custom prompts

As well as creating fully custom UI and interactivity using tktinter, the underlying prompt mechanism (to handle user input) can connected to "custom prompts".

When creating a custom prompt the setup function must:
- Accept an instance of `_Prompt` as an argument.
- Set the return type of the prompt using `prompt.set_return_type()`.
- Add all interactive widgets to the `prompt.widgets` set so they can be enabled and disabled.
- Add all keys bound to `gui.root` to the `prompt.keybindings` set so they can be unbound later.
- Bind user input events to `prompt.submit()`, where the argument is of the correct type.

#### Example

The following example uses both a preset and a custom prompt.

```python
import time
import tkinter as tk

from quick_tk_gui import ThreadedGUI, presets


def preset_prompt(prompt, parent_frame: tk.Widget):
    """Create a 3 button input choice prompt using a preset."""

    presets.n_button(
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

    lbl = tk.Label(parent_frame, text="Enter something:")
    lbl.pack()

    entry = tk.Entry(parent_frame)
    entry.pack()

    prompt.widgets.add(entry)  # track the interactive widgets in the custom prompt

    b = tk.Button(
        parent_frame, text="Submit", command=lambda: prompt.submit(entry.get())
    )
    b.pack()

    prompt.widgets.add(b)  # track the interactive widgets in the custom prompt

    prompt.gui.root.bind("<Return>", lambda _: prompt.submit(entry.get()))

    prompt.keybindings.add("<Return>")  # track the keybindings in the custom prompt


def app_logic(gui):
    """Run the app logic in a background thread to keep the UI responsive."""

    # Create a prompt using a preset and wait for user input
    my_preset_prompt = gui.add_prompt(setup_func=preset_prompt, parent_frame=gui.root)
    value, ts = my_preset_prompt.wait_for_response()
    print("original preset prompt:", value, ts)

    time.sleep(2)

    # Clear the existing prompt and use it again, then destroy (remove) it
    my_preset_prompt.reset()
    my_preset_prompt.enable()
    value, ts = my_preset_prompt.wait_for_response()
    print("reset preset prompt:", value, ts)
    gui.remove_prompt(my_preset_prompt)

    time.sleep(2)

    # Create a new prompt, custom defined, wait for then input the destroy it
    my_custom_prompt = gui.add_prompt(setup_func=custom_prompt, parent_frame=gui.root)
    value, ts = my_custom_prompt.wait_for_response()
    print("original custom prompt:", value, ts)
    gui.remove_prompt(my_custom_prompt)


ThreadedGUI(name="Prompt Example", app_logic=app_logic)
```
