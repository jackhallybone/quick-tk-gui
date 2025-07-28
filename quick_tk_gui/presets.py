import time
import tkinter as tk

"""
Presets should overwrite:
 - `gui.user_input_var` with the correct tkinter Var type
 - `gui.all_input_widgets` with a list of the current input widgets
"""


def n_button_row(
    gui,
    parent,
    prompt: str,
    button_bindings: dict[str, bool | int | float | str],
    keybindings: dict[str, str],
):
    """Add a labelled row of buttons to the layout."""

    # Check that all keybindings are bound to buttons that are defined
    missing_buttons = [
        btn for btn in keybindings.values() if btn not in button_bindings
    ]
    if missing_buttons:
        raise ValueError(f"Keybindings reference undefined buttons: {missing_buttons}")

    # Check that the output types of all the buttons are the same
    value_types = {type(v) for v in button_bindings.values()}
    if len(value_types) > 1:
        raise TypeError(f"Button values must all be the same type, got: {value_types}")

    # Choose an output type var based on the button output type
    first_value = next(iter(button_bindings.values()))
    if isinstance(first_value, bool):
        gui.user_input_var = tk.BooleanVar()
    elif isinstance(first_value, int):
        gui.user_input_var = tk.IntVar()
    elif isinstance(first_value, float):
        gui.user_input_var = tk.DoubleVar()
    elif isinstance(first_value, str):
        gui.user_input_var = tk.StringVar()
    else:
        raise ValueError(
            f"Button value of type {type(first_value)} is not yet supported"
        )

    def on_click(value):
        """When the input is enabled, read the button click events."""
        if gui.input_enabled.get():
            print("click event", time.time())
            gui.user_input_var.set(value)
            gui.user_input_event.set()

    def on_keypress(event):
        """When the input is enabled, read the keypress events."""
        if gui.input_enabled.get():
            key = event.char
            button = keybindings.get(key)
            if button is not None:
                print("key event", time.time())
                value = button_bindings.get(button)
                gui.user_input_var.set(value)
                gui.user_input_event.set()

    # Create an outer container that fills the parent
    outer_container = tk.Frame(parent)
    outer_container.pack(expand=True, fill="both")

    # Create an inner container that is in the center of the outer container
    inner_container = tk.Frame(outer_container)
    inner_container.place(relx=0.5, rely=0.5, anchor="center")

    if prompt:
        label = tk.Label(inner_container, text=prompt, font=("Arial", 14))
        label.pack(pady=(0, 5))

    button_frame = tk.Frame(inner_container)
    button_frame.pack()

    # Create n buttons and bind the click events
    button_widgets = []
    for i, (name, value) in enumerate(button_bindings.items()):
        btn = tk.Button(
            button_frame,
            text=name,
            width=10,
            height=2,
            font=("Arial", 13),
            command=lambda value=value: on_click(value),
        )
        btn.grid(row=0, column=i, padx=10, pady=10)
        button_widgets.append(btn)

    if keybindings:
        # Bind keypress events
        gui.root.bind("<Key>", on_keypress)

    # Collect the handles for the input widgets, overwriting any old ones
    gui.all_input_widgets = button_widgets
