import tkinter as tk

from .core import UserPrompt


def _create_centred_container(parent):
    """Create wrapper frames inside a parent so the content is horizontally and vertically centred."""

    # Create an outer container that fills the parent frame
    outer_container = tk.Frame(parent)
    outer_container.pack(expand=True, fill="both")

    # Create an inner container that is in the center of the outer container
    inner_container = tk.Frame(outer_container)
    inner_container.place(relx=0.5, rely=0.5, anchor="center")

    return inner_container


def n_button(
    prompt: UserPrompt,
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

    centred_container = _create_centred_container(prompt.frame)

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

        # Bind keypress events
        keys = set()
        for key in b.get("keybindings", []):
            key_name = f"<KeyPress-{key}>"
            prompt.gui.root.bind(key_name, lambda _, v=value: prompt.submit(v))
            keys.add(key_name)

        # Keep track of interactive widgets and keybindings
        prompt.widgets.add(btn)
        prompt.keybindings.update(keys)