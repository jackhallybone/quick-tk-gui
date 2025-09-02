import tkinter as tk
from tkinter import filedialog, ttk

from .core import _Prompt


def centred_frame(parent_frame: tk.Widget | ttk.Widget) -> ttk.Widget:
    """Create wrapper frames inside a parent so the content is horizontally and vertically centred."""

    # Create an outer container that fills the parent frame
    outer_container = ttk.Frame(parent_frame)
    outer_container.pack(expand=True, fill="both")

    # Create an inner container that is in the center of the outer container
    inner_container = ttk.Frame(outer_container)
    inner_container.place(relx=0.5, rely=0.5, anchor="center")

    return inner_container


def label(
    prompt: _Prompt,
    parent_frame: tk.Widget | ttk.Widget,
    label: str,
    label_style: str = "",
):

    prompt.set_return_type(str)  # Any because it is not used

    centred_container = centred_frame(parent_frame)

    l = ttk.Label(centred_container, text=label, style=label_style)
    l.pack()


def n_button_prompt(
    prompt: _Prompt,
    parent_frame: tk.Widget | ttk.Widget,
    label: str,
    buttons: list[dict],  # {"label": str, "value": Any, "keybindings": list[str]}
    label_style: str = "",
    button_style: str = "",
    vertical_spacing: int = 10,
    button_spacing: int = 10,
    max_buttons_in_row: int = 4,
):

    # Check all button values are the same type
    if not all(type(b["value"]) is type(buttons[0]["value"]) for b in buttons):
        raise TypeError("All button values must be the same type")

    # Set the return type based on the button values
    prompt.set_return_type(type(buttons[0]["value"]))

    centred_container = centred_frame(parent_frame)

    if label:
        l = ttk.Label(centred_container, text=label, style=label_style)
        l.pack(pady=(0, vertical_spacing))

    button_frame = ttk.Frame(centred_container)
    button_frame.pack()

    for i, b in enumerate(buttons):
        value = b["value"]

        # Add and bind button
        btn = ttk.Button(
            button_frame,
            text=b["label"],
            command=lambda v=value: prompt.submit(v),
            style=button_style,
        )
        row = i // max_buttons_in_row
        col = i % max_buttons_in_row
        btn.grid(row=row, column=col, padx=button_spacing, pady=button_spacing)

        prompt.track_interactive_widget(btn)  # track all interactive widgets

        # Bind keypress events
        for key in b.get("keybindings", []):
            key_name = f"<KeyPress-{key}>"
            prompt.root.bind(key_name, lambda _, v=value: prompt.submit(v))
            prompt.track_root_keybinding(key_name)  # track all keybindings to root


def text_entry_prompt(
    prompt: _Prompt,
    parent_frame: tk.Widget | ttk.Widget,
    label: str,
    button: dict,  # {"label": str, "keybindings": list[str]}
    entry_prefill: str = "",
    label_style: str = "",
    entry_style: str = "",
    button_style: str = "",
    vertical_spacing: int = 10,
):

    prompt.set_return_type(str)

    centred_container = centred_frame(parent_frame)

    if label:
        l = ttk.Label(centred_container, text=label, style=label_style)
        l.pack(pady=(0, vertical_spacing))

    # Add a text entry field
    entry = ttk.Entry(centred_container, style=entry_style)
    if entry_prefill:
        entry.insert(tk.END, entry_prefill)
    entry.pack(pady=(0, vertical_spacing))

    prompt.track_interactive_widget(entry)  # track all interactive widgets

    # Set focus to the Entry widget
    entry.focus_set()

    # Add and bind button
    btn = ttk.Button(
        centred_container,
        text=button["label"],
        command=lambda: prompt.submit(entry.get()),
        style=button_style,
    )
    btn.pack()

    prompt.track_interactive_widget(btn)  # track all interactive widgets

    # Bind keypress events
    for key in button.get("keybindings", []):
        key_name = f"<KeyPress-{key}>"
        prompt.root.bind(key_name, lambda _: prompt.submit(entry.get()))
        prompt.track_root_keybinding(key_name)  # track all keybindings to root


def dropdown_prompt(
    prompt: _Prompt,
    parent_frame: tk.Widget | ttk.Widget,
    label: str,
    options: list[str],
    button: dict,  # {"label": str, "keybindings": list[str]}
    label_style: str = "",
    dropdown_style: str = "",
    button_style: str = "",
    vertical_spacing: int = 10,
):

    prompt.set_return_type(str)

    centred_container = centred_frame(parent_frame)

    if label:
        l = ttk.Label(centred_container, text=label, style=label_style)
        l.pack(pady=(0, vertical_spacing))

    # Create and style the dropdown
    dropdown = ttk.Combobox(centred_container, values=options, style=dropdown_style)
    dropdown.pack(pady=(0, vertical_spacing))

    prompt.track_interactive_widget(dropdown)  # track all interactive widgets

    # Set focus to the Dropdown widget
    dropdown.focus_set()

    # Add and bind button
    btn = ttk.Button(
        centred_container,
        text=button["label"],
        command=lambda: prompt.submit(dropdown.get()),
        style=button_style,
    )
    btn.pack()

    prompt.track_interactive_widget(btn)  # track all interactive widgets

    # Bind keypress events
    for key in button.get("keybindings", []):
        key_name = f"<KeyPress-{key}>"
        prompt.root.bind(key_name, lambda _: prompt.submit(dropdown.get()))
        prompt.track_root_keybinding(key_name)  # track all keybindings to root


def file_select_prompt(
    prompt: _Prompt,
    parent_frame: tk.Widget | ttk.Widget,
    label: str,
    button: dict,  # {"label": str, "keybindings": list[str]}
    filetypes: list[tuple[str, str]] = [("All Files", "*.*")],
    label_style: str = "",
    button_style: str = "",
    vertical_spacing: int = 10,
):

    prompt.set_return_type(str)

    centred_container = centred_frame(parent_frame)

    if label:
        l = ttk.Label(centred_container, text=label, style=label_style)
        l.pack(pady=(0, vertical_spacing))

    # Function to open file dialog
    def choose_file():
        if prompt.is_enabled:
            filename = filedialog.askopenfilename(filetypes=filetypes)
            if filename:
                prompt.submit(filename)

    # Button to open the file dialog
    btn = ttk.Button(
        centred_container, text=button["label"], command=choose_file, style=button_style
    )
    btn.pack()

    prompt.track_interactive_widget(btn)  # track all interactive widgets

    # Optional: bind keys
    for key in button.get("keybindings", []):
        key_name = f"<KeyPress-{key}>"
        prompt.root.bind(key_name, lambda _: choose_file())
        prompt.track_root_keybinding(key_name)  # track all keybindings to root
