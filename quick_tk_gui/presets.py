import tkinter as tk

"""
When adding an input UI region, the following GUI attributes must be set:
- self.current_input_container: tk.Widget
- self.current_input_var: tk.Variable
- self.current_input_widgets: set[tk.Widget]
- self.current_input_keybindings: set[str]
"""


def _type_to_tk_var(py_type: type) -> tk.Variable:
    """Return the tkinter variable matching the type of the argument."""
    if py_type is bool:
        return tk.BooleanVar()
    if py_type is int:
        return tk.IntVar()
    if py_type is float:
        return tk.DoubleVar()
    if py_type is str:
        return tk.StringVar()
    raise ValueError(f"Unsupported value type: {py_type}")


def _centred_container(container):

    # Create an outer container that fills the container
    outer_container = tk.Frame(container)
    outer_container.pack(expand=True, fill="both")

    # Create an inner container that is in the center of the outer container
    inner_container = tk.Frame(outer_container)
    inner_container.place(relx=0.5, rely=0.5, anchor="center")

    return inner_container


def add_text(
    container: tk.Widget,
    text: str,
    font: tuple[str, int] = ("Arial", 14),
):
    """Add text to the container frame, centred horizontally and vertically."""

    centred_container = _centred_container(container)

    label = tk.Label(centred_container, text=text, font=font)
    label.pack(pady=(0, 0))


def add_n_button_input(
    gui,
    container: tk.Widget,
    prompt: str,
    buttons: list[dict],
    prompt_font: tuple[str, int] = ("Arial", 14),
    button_font: tuple[str, int] = ("Arial", 12),
    vertical_spacing: int = 10,
    horizontal_spacing: int = 10,
    button_width: int = 10,
    button_height: int = 2,
):
    """Add a row of buttons to the container frame with a prompt above, all centred horizontally and vertically.

    The format of the button definition is:
        {"name": "click me", "value": 1, "keybindings": ["1"]}
    """

    def handle_input(gui, button, value):
        """Fire the value associated with the button if it is enabled."""
        if str(button["state"]) == "normal":
            gui.current_input_var.set(value)
            gui.user_input_event.set()

    # Check all button values are the same type and set the input var to that type
    if not all(type(b["value"]) is type(buttons[0]["value"]) for b in buttons):
        raise TypeError("All button values must be the same type")
    input_var = _type_to_tk_var(type(buttons[0]["value"]))

    centred_container = _centred_container(container)

    if prompt:
        label = tk.Label(centred_container, text=prompt, font=prompt_font)
        label.pack(pady=(0, vertical_spacing))

    button_frame = tk.Frame(centred_container)
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
        btn.pack(side="left", padx=horizontal_spacing)

        input_widgets.add(btn)

        # Bind click event
        btn.config(command=lambda b=btn, v=b["value"]: handle_input(gui, b, v))

        # Bind keypress events
        for key in b.get("keybindings", []):
            key_name = f"<KeyPress-{key}>"
            gui.root.bind(
                key_name, lambda _, b=btn, v=b["value"]: handle_input(gui, b, v)
            )
            input_keybindings.add(key_name)

    # Set the GUI variables to keep track of the input
    gui.current_input_container = container
    gui.current_input_var = input_var
    gui.current_input_widgets = input_widgets
    gui.current_input_keybindings = input_keybindings


def add_text_input(
    gui,
    container: tk.Widget,
    prompt: str,
    prefill: str = "",
    button: dict = {"name": "Submit", "keybindings": ["Return"]},
    prompt_font: tuple[str, int] = ("Arial", 14),
    entry_font: tuple[str, int] = ("Arial", 10),
    button_font: tuple[str, int] = ("Arial", 12),
    vertical_spacing: int = 10,
    entry_width: int = 30,
    button_width: int = 8,
    button_height: int = 1,
):
    """Add a text entry field with prompt and submit button, all centred horizontally and vertically."""

    def handle_input(gui, button, entry):
        """Fire the value in the entry box if the button and entry are enabled."""
        if str(button["state"]) == "normal" and str(entry["state"]) == "normal":
            value = entry.get()
            gui.current_input_var.set(value)
            gui.user_input_event.set()

    input_var = _type_to_tk_var(str)

    centred_container = _centred_container(container)

    if prompt:
        label = tk.Label(centred_container, text=prompt, font=prompt_font)
        label.pack(pady=(0, vertical_spacing))

    entry = tk.Entry(centred_container, width=entry_width, font=entry_font)
    entry.insert(tk.END, prefill)
    entry.pack(pady=(0, vertical_spacing))

    # Move focus (keyboard input) to the entry box
    entry.focus_set()

    # Make and add button
    btn = tk.Button(
        centred_container,
        text=button["name"],
        width=button_width,
        height=button_height,
        font=button_font,
        bg="lightgrey",
        fg="black",
        activebackground="lightgrey",
        activeforeground="black",
    )
    btn.pack(pady=(0, 0))

    input_widgets = {btn}

    # Bind click event
    btn.config(command=lambda btn=btn, entry=entry: handle_input(gui, btn, entry))

    # Bind keypress events
    input_keybindings = set()
    for key in button.get("keybindings", []):
        key_name = f"<KeyPress-{key}>"
        gui.root.bind(
            key_name, lambda _, btn=btn, entry=entry: handle_input(gui, btn, entry)
        )
        input_keybindings.add(key_name)

    # Set the GUI variables to keep track of the input
    gui.current_input_container = container
    gui.current_input_var = input_var
    gui.current_input_widgets = input_widgets
    gui.current_input_keybindings = input_keybindings
