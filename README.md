# quick-tk-gui

A helper class to quickly create and thread basic [tkinter](https://docs.python.org/3/library/tkinter.html) GUIs, with an optional feature for handling basic user input.

## Getting started

```
pip install -e .
```

The following snippet uses the `ThreadedGUI` class to create a responsive GUI where the user code runs in a background thread. It also uses the additional "prompt" handling mechanism to capture user input.

It is not necessary to use the "prompt" input mechanism from this package, and Tkinter can be used as normal from `gui.root` which `= tk.Tk()`.

Tkinter updates to the GUI from the app code (which is in the background thread) must be scheduled to run on the main (UI) thread using `gui.run_on_ui_thread()`. This is a blocking function which waits for the update to complete.

```python
from quick_tk_gui import ThreadedGUI, presets


def build_ui(gui):
    """Create an initial UI layout (this runs on the main thread during init)."""

    # Add a button array prompt to the GUI using the n_button preset UI
    gui.prompt = gui.add_prompt(
        setup_func=presets.n_button,
        parent_frame=gui.root,
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

    # Automatically close the GUI window
    gui.close()


ThreadedGUI(name="Example GUI", build_ui=build_ui, app_logic=app_logic)
```

## Timing

Many factors impact the timing of visual updates and user input capture.

When a prompt is added, a timestamp is taken as close to the visual render as possible and saved to the `presentation_timestamp` attribute. Similarly, the `wait_for_response()` method returns a timestamp taken as close to the user input as possible.

### Clock

The timestamp of the user response returned by `prompt.wait_for_response()` is taken from the `gui` clock. By default this uses `time.time()` and can be accessed with `gui.now`.

A different clock function can be set using `gui.set_clock()`. For example, to use the [sounddevice Stream](https://python-sounddevice.readthedocs.io/en/0.3.15/api/streams.html#sounddevice.Stream) clock:

```python
gui.set_clock(clock=lambda: stream.time)
```

## Examples

### Basic Threaded GUI

The `ThreadedGUI` class can be used to create a GUI and manage it from user code (in the `app_logic` function) which runs in a background thread.

This handles the threading setup and provides a thread-safe wrapper `gui.run_on_ui_thread()` to edit the GUI from the app (background) thread. Tkinter can be used as normal from `gui.root` which `= tk.Tk()`.

```python
import time
import tkinter as tk

from quick_tk_gui import ThreadedGUI


def build_ui(gui):
    """Create an initial UI layout (this runs on the main thread during init)."""
    gui.label = tk.Label(gui.root, text="Example Text", font=("Arial", 14))
    gui.label.place(relx=0.5, rely=0.5, anchor="center")


def app_logic(gui):
    """Run the app logic in a background thread to keep the UI responsive."""

    # Mock some blocking user code, while the GUI remains responsive
    time.sleep(3)

    # Synchronously (ie, blocking the user code) update the UI on the UI thread
    gui.run_on_ui_thread(lambda: gui.label.config(text="Updated text!"))


ThreadedGUI(name="Threading Example", build_ui=build_ui, app_logic=app_logic)
```

### Prompt Example (preset and custom)

Optionally, the `ThreadedGUI` class can create a "prompt" which handles basic user interactivity (it creates a `_Prompt` instance in the background). The `presets` module provides some basic UIs, or these can be defined by the user and attached to the "prompts" mechanism.

#### Interactivity

A `prompt` instance provides the mechanisms to `enable()` and `disable()` interactivity, get the timestamp and value of a response using `wait_for_response()`, and `reset()` or `destroy()` when finished.

#### Thread Safety

The interactivity methods of a `prompt` instance are internally wrapped in the `gui.run_on_ui_thread()` method so can be used directly from the app code (background thread).

#### Creating custom prompts

When creating a custom prompt the setup function must:
- Accept an instance of `_Prompt` as an argument
- Set the return type of the prompt using `prompt.set_return_type()`
- Add all interactive widgets to the `prompt.widgets` set so the prompt can be enabled and disabled
- Add all `gui.root` keybindings to the `prompt.keybindings` set so they can be unbound later
- Bind response events to `prompt.submit()`, where the argument is of the return type

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
