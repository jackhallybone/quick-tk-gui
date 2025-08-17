import copy
import threading
import time
import tkinter as tk
from typing import Callable


class GUI:

    def __init__(
        self,
        name: str,
        initial_layout: Callable,
        app_logic: Callable,
        minsize: tuple[int, int] = (700, 400),
    ):

        self.root = tk.Tk()
        self.root.title(name)

        # Create the default user input events and variables
        self.user_input_event = threading.Event()
        self.current_input_container: tk.Widget | None = None
        self.current_input_var: tk.Variable = tk.StringVar(value="")
        self.current_input_widgets: set[tk.Widget] = set()
        self.current_input_keybindings: set[str] = set()

        # Create the initial layout from the user function
        initial_layout(self)

        # Run the app_logic user function in a background thread
        threading.Thread(target=app_logic, args=(self,), daemon=True).start()

        self.root.minsize(*minsize)

        self.root.mainloop()

    @staticmethod
    def _tk_safe_deepcopy(obj):
        """Deepcopy where possible and skip if not, for example a tkinter widget."""
        try:
            return copy.deepcopy(obj)
        except:
            return obj

    def on_main_thread(self, func, *args, **kwargs):
        """Synchronously run a function on the main (GUI) thread.

        - All arguments are deep-copied if possible for safety
        - This function blocks until the target function completes on the main thread.
        """

        # Already in the GUI thread, so just call
        if threading.current_thread() is threading.main_thread():
            return func(*args, **kwargs)

        # Deepcopy arguments that aren't Tk widgets or Tk variables
        safe_args = tuple(self._tk_safe_deepcopy(a) for a in args)
        safe_kwargs = {k: self._tk_safe_deepcopy(v) for k, v in kwargs.items()}

        done = threading.Event()
        result = {}

        def wrapper():
            try:
                result["value"] = func(*safe_args, **safe_kwargs)
            except Exception as e:
                result["error"] = e
            finally:
                done.set()

        self.root.after(0, wrapper)
        done.wait()

        if "error" in result:
            raise result["error"]
        return result.get("value")

    def close(self):
        """Close the GUI window."""
        self.on_main_thread(self.root.destroy)

    def remove_widgets(self, widgets: list[tk.Widget] | set[tk.Widget]):
        """Remove widgets from the GUI."""
        for widget in widgets:
            widget.destroy()

    def clear_frame(self, frame: tk.Widget):
        """Clear a frame of its contents (remove child widgets from the GUI)."""
        for child in frame.winfo_children():
            child.destroy()

    def unbind_keys(self, keys: list[str] | set[str]):
        """Unbind keys from the root element."""
        for key in keys:
            self.root.unbind(key)

    @staticmethod
    def set_enabled(widgets: list[tk.Widget] | set[tk.Widget], enabled: bool):
        """Set the state of one or more widgets to enabled/normal or disabled."""
        state = "normal" if enabled else "disabled"
        for widget in widgets:
            # TODO: not all widgets have states
            widget.config(state=state)  # type: ignore[attr-defined]

    def get_user_input(self, timeout=None, clock=time.time):
        """Wait for and get user input."""
        was_set = self.user_input_event.wait(timeout=timeout)
        if not was_set:
            return None, None
        timestamp = clock()  # NOTE: tested <1ms after handle_input callback fires
        value = self.current_input_var.get()
        self.user_input_event.clear()
        return value, timestamp

    def clear_current_input_ui(self):
        """Clear the current user input based on the attributes set on creation.

        This is intended to cleanly remove them from the GUI and unbind root keybindings.
        """
        if self.current_input_container:
            self.clear_frame(self.current_input_container)
            self.current_input_container = None
            self.current_input_widgets.clear()
        self.unbind_keys(self.current_input_keybindings)
        self.current_input_keybindings.clear()
        self.current_input_var = tk.StringVar(value="")
