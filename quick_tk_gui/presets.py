import tkinter as tk
from tkinter import filedialog

from .core import _Prompt


def _create_centred_container(parent_frame):
    """Create wrapper frames inside a parent so the content is horizontally and vertically centred."""

    # Create an outer container that fills the parent frame
    outer_container = tk.Frame(parent_frame)
    outer_container.pack(expand=True, fill="both")

    # Create an inner container that is in the center of the outer container
    inner_container = tk.Frame(outer_container)
    inner_container.place(relx=0.5, rely=0.5, anchor="center")

    return inner_container


def label(
    prompt: _Prompt,
    parent_frame: tk.Widget,
    label: str,
    font: tuple[str, int] = ("Arial", 14),
):

    prompt.set_return_type(bool)  # Any because there is no response

    centred_container = _create_centred_container(parent_frame)

    l = tk.Label(centred_container, text=label, font=font)
    l.pack(pady=(0, 0))


def n_button(
    prompt: _Prompt,
    parent_frame: tk.Widget,
    label: str,
    buttons: list[dict],
    label_font: tuple[str, int] = ("Arial", 14),
    button_font: tuple[str, int] = ("Arial", 12),
    vertical_spacing: int = 10,
    horizontal_spacing: int = 10,
    button_width: int = 10,
    button_height: int = 2,
):

    # Check all button values are the same type
    if not all(type(b["value"]) is type(buttons[0]["value"]) for b in buttons):
        raise TypeError("All button values must be the same type")

    # Set the return type based on the button values
    prompt.set_return_type(type(buttons[0]["value"]))

    centred_container = _create_centred_container(parent_frame)

    if label:
        l = tk.Label(centred_container, text=label, font=label_font)
        l.pack(pady=(0, vertical_spacing))

    button_frame = tk.Frame(centred_container)
    button_frame.pack()

    for b in buttons:
        value = b["value"]

        # Add and bind button
        btn = tk.Button(
            button_frame,
            text=b["label"],
            command=lambda v=value: prompt.submit(v),
            width=button_width,
            height=button_height,
            font=button_font,
            bg="lightgrey",
            fg="black",
            activebackground="lightgrey",
            activeforeground="black",
        )
        btn.pack(side="left", padx=horizontal_spacing)

        prompt.track_interactive_widget(btn)  # track all interactive widgets

        # Bind keypress events
        for key in b.get("keybindings", []):
            key_name = f"<KeyPress-{key}>"
            prompt.root.bind(key_name, lambda _, v=value: prompt.submit(v))
            prompt.track_root_keybinding(key_name)  # track all keybindings to root


def text_entry(
    prompt: _Prompt,
    parent_frame: tk.Widget,
    label: str,
    prefill: str = "",
    button: dict = {"label": "Submit", "keybindings": ["Return"]},
    label_font: tuple[str, int] = ("Arial", 14),
    entry_font: tuple[str, int] = ("Arial", 10),
    button_font: tuple[str, int] = ("Arial", 12),
    vertical_spacing: int = 10,
    entry_width: int = 30,
    button_width: int = 10,
    button_height: int = 2,
):

    prompt.set_return_type(str)

    centred_container = _create_centred_container(parent_frame)

    if label:
        l = tk.Label(centred_container, text=label, font=label_font)
        l.pack(pady=(0, vertical_spacing))

    # Add a text entry field
    entry = tk.Entry(centred_container, width=entry_width, font=entry_font)
    entry.insert(tk.END, prefill)
    entry.pack(pady=(0, vertical_spacing))

    prompt.track_interactive_widget(entry)  # track all interactive widgets

    # Set focus to the Entry widget
    entry.focus_set()

    # Add and bind button
    btn = tk.Button(
        centred_container,
        text=button["label"],
        command=lambda: prompt.submit(entry.get()),
        width=button_width,
        height=button_height,
        font=button_font,
        bg="lightgrey",
        fg="black",
        activebackground="lightgrey",
        activeforeground="black",
    )
    btn.pack()

    prompt.track_interactive_widget(btn)  # track all interactive widgets

    # Bind keypress events
    for key in button.get("keybindings", []):
        key_name = f"<KeyPress-{key}>"
        prompt.root.bind(key_name, lambda _: prompt.submit(entry.get()))
        prompt.track_root_keybinding(key_name)  # track all keybindings to root


def dropdown(
    prompt: _Prompt,
    parent_frame: tk.Widget,
    label: str,
    options: list,
    button: dict = {"label": "Submit", "keybindings": ["Return"]},
    label_font: tuple[str, int] = ("Arial", 14),
    options_font: tuple[str, int] = ("Arial", 10),
    button_font: tuple[str, int] = ("Arial", 12),
    vertical_spacing: int = 10,
    button_width: int = 10,
    button_height: int = 2,
):

    prompt.set_return_type(str)

    centred_container = _create_centred_container(parent_frame)

    if label:
        l = tk.Label(centred_container, text=label, font=label_font)
        l.pack(pady=(0, vertical_spacing))

    # The choice is handled by a stringvar
    choice = tk.StringVar(value=options[0])

    # Create and style the dropdown
    dropdown = tk.OptionMenu(
        centred_container,
        choice,
        *options,
    )
    dropdown.config(font=options_font, width=20, anchor="w")
    dropdown["menu"].config(font=options_font)
    dropdown.pack(pady=(0, vertical_spacing))

    prompt.track_interactive_widget(dropdown)  # track all interactive widgets

    # Set focus to the Dropdown widget
    dropdown.focus_set()

    # Add and bind button
    btn = tk.Button(
        centred_container,
        text=button["label"],
        command=lambda: prompt.submit(choice.get()),
        width=button_width,
        height=button_height,
        font=button_font,
        bg="lightgrey",
        fg="black",
        activebackground="lightgrey",
        activeforeground="black",
    )
    btn.pack()

    prompt.track_interactive_widget(btn)  # track all interactive widgets

    # Bind keypress events
    for key in button.get("keybindings", []):
        key_name = f"<KeyPress-{key}>"
        prompt.root.bind(key_name, lambda _: prompt.submit(choice.get()))
        prompt.track_root_keybinding(key_name)  # track all keybindings to root


def file_select(
    prompt: _Prompt,
    parent_frame: tk.Widget,
    label: str,
    button: dict = {"label": "Select File", "keybindings": ["Return"]},
    label_font: tuple[str, int] = ("Arial", 14),
    button_font: tuple[str, int] = ("Arial", 12),
    vertical_spacing: int = 10,
    button_width: int = 10,
    button_height: int = 2,
    filetypes: list[tuple[str, str]] = [("All Files", "*.*")],
):

    prompt.set_return_type(str)

    centred_container = _create_centred_container(parent_frame)

    if label:
        l = tk.Label(centred_container, text=label, font=label_font)
        l.pack(pady=(0, vertical_spacing))

    # Function to open file dialog
    def choose_file():
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            prompt.submit(filename)

    # Button to open the file dialog
    btn = tk.Button(
        centred_container,
        text=button["label"],
        command=choose_file,
        width=button_width,
        height=button_height,
        font=button_font,
        bg="lightgrey",
        fg="black",
        activebackground="lightgrey",
        activeforeground="black",
    )
    btn.pack(pady=(0, vertical_spacing))

    prompt.track_interactive_widget(btn)  # track all interactive widgets

    # Optional: bind keys
    for key in button.get("keybindings", []):
        key_name = f"<KeyPress-{key}>"
        prompt.root.bind(key_name, lambda _: choose_file())
        prompt.track_root_keybinding(key_name)  # track all keybindings to root
