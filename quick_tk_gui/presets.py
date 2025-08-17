import tkinter as tk

"""
When adding an input UI region, the following GUI attributes must be set:
- self.current_input_container: tk.Widget
- self.current_input_var: tk.Variable
- self.current_input_widgets: set[tk.Widget]
- self.current_input_keybindings: set[str]
"""


def _value_to_tk_var(value):
    """Return the tkinter variable matching the type of the argument."""
    if isinstance(value, bool):
        return tk.BooleanVar()
    if isinstance(value, int):
        return tk.IntVar()
    if isinstance(value, float):
        return tk.DoubleVar()
    if isinstance(value, str):
        return tk.StringVar()
    raise ValueError(f"Unsupported value type: {type(value)}")


def add_text(
    container: tk.Widget,
    text: str,
    font: tuple[str, int] = ("Arial", 14),
):
    """Add text to the container frame, centred horizontally and vertically."""

    # Create an outer container that fills the container
    outer_container = tk.Frame(container)
    outer_container.pack(expand=True, fill="both")

    # Create an inner container that is in the center of the outer container
    inner_container = tk.Frame(outer_container)
    inner_container.place(relx=0.5, rely=0.5, anchor="center")

    label = tk.Label(inner_container, text=text, font=font)
    label.pack(pady=(0, 0))


def add_n_button_input(
    gui,
    container: tk.Widget,
    prompt: str,
    buttons: list[dict],
    prompt_font: tuple[str, int] = ("Arial", 14),
    button_font: tuple[str, int] = ("Arial", 12),
    prompt_button_gap: int = 10,
    button_button_gap: int = 10,
    button_width: int = 10,
    button_height: int = 2,
):
    """Add a row of buttons to the container frame with a prompt above, all centred horizontally and vertically"""

    # Check all button values are the same type and set the input var to that type
    if not all(type(b["value"]) is type(buttons[0]["value"]) for b in buttons):
        raise TypeError("All button values must be the same type")
    input_var = _value_to_tk_var(buttons[0]["value"])

    # Create an outer container that fills the container
    outer_container = tk.Frame(container)
    outer_container.pack(expand=True, fill="both")

    # Create an inner container that is in the center of the outer container
    inner_container = tk.Frame(outer_container)
    inner_container.place(relx=0.5, rely=0.5, anchor="center")

    if prompt:
        label = tk.Label(inner_container, text=prompt, font=prompt_font)
        label.pack(pady=(0, prompt_button_gap))

    button_frame = tk.Frame(inner_container)
    button_frame.pack()

    input_widgets = set()
    input_keybindings = set()

    for b in buttons:

        # Make and add button
        btn = tk.Button(
            button_frame,
            text=b["name"],
            width=button_width,
            height=button_height,
            font=button_font,
            bg="lightgrey",
            fg="black",
            activebackground="lightgrey",
            activeforeground="black",
        )
        btn.pack(side="left", padx=button_button_gap)

        input_widgets.add(btn)

        # Bind click event
        btn.config(command=lambda b=btn, v=b["value"]: gui.handle_input(b, v))

        # Bind keypress events
        for key in b.get("keybindings", []):
            key_name = f"<KeyPress-{key}>"
            gui.root.bind(
                key_name, lambda _, b=btn, v=b["value"]: gui.handle_input(b, v)
            )
            input_keybindings.add(key_name)

    # Set the GUI variables to keep track of the input
    gui.current_input_container = container
    gui.current_input_var = input_var
    gui.current_input_widgets = input_widgets
    gui.current_input_keybindings = input_keybindings
