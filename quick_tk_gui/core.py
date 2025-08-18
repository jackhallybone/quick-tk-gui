import copy
import threading
import time
import tkinter as tk
from typing import Callable


class ThreadedGUI:

    def __init__(
        self,
        name: str,
        app_logic: Callable,
        build_ui: Callable | None = None,
        min_size: tuple[int, int] = (700, 400),
    ):

        self.root = tk.Tk()
        self.root.title(name)

        self._clock: Callable = time.time

        if build_ui:
            build_ui(self)

        threading.Thread(target=app_logic, args=(self,), daemon=True).start()

        self.root.minsize(*min_size)

        self.root.mainloop()

    @staticmethod
    def _tk_safe_deepcopy(obj):
        """Deepcopy where possible and skip if not, for example a tkinter widget."""
        try:
            return copy.deepcopy(obj)
        except:
            return obj

    def run_on_ui_thread(self, func, *args, **kwargs):
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
        self.run_on_ui_thread(self.root.destroy)

    def set_clock(self, clock: Callable):
        """Set the clock function to use when getting times/timestamp."""
        self._clock = clock

    @property
    def now(self):
        """Get the current time from the GUI clock."""
        return self._clock()

    def add_prompt(self, setup_func: Callable, parent: tk.Widget, *args, **kwargs):
        """Add a prompt (`UserPrompt`), using a setup function, to the GUI."""

        def create_prompt():
            prompt = UserPrompt(self, parent)
            setup_func(prompt, *args, **kwargs)
            return prompt

        return self.run_on_ui_thread(create_prompt)


class UserPrompt:

    def __init__(self, gui: ThreadedGUI, parent: tk.Widget):
        self.gui = gui
        self.frame = parent
        self.event = threading.Event()
        # self.value = # must be set using self.set_return_type()
        self.timestamp = tk.DoubleVar()
        self.widgets = set()
        self.keybindings = set()

    @staticmethod
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

    @staticmethod
    def _clear_tk_var(var: tk.Variable):
        """Reset a tkinter variable to it falsy value depending on type."""
        if isinstance(var, tk.BooleanVar):
            var.set(False)
        elif isinstance(var, tk.IntVar):
            var.set(0)
        elif isinstance(var, tk.DoubleVar):
            var.set(0.0)
        elif isinstance(var, tk.StringVar):
            var.set("")
        else:
            raise ValueError(f"Unsupported variable type: {var}")

    def set_return_type(self, py_type: type):
        """Set the return type, and value variable, of the prompt."""
        self.value = self._type_to_tk_var(py_type)

    def _set_enabled(self, enabled: bool):
        """Set the state for all interactive widgets in the `self.widgets` set."""
        state = "normal" if enabled else "disabled"
        for widget in self.widgets:
            try:
                widget.config(state=state)
            except tk.TclError:
                pass

    def enable(self):
        """Enable the prompt."""
        self.gui.run_on_ui_thread(self._set_enabled, True)

    def disable(self):
        """Disable the prompt."""
        self.gui.run_on_ui_thread(self._set_enabled, False)

    def submit(self, value):
        """A callback to submit the response, where the type of `value` matches the prompt return type."""

        def _submit():
            self.timestamp.set(time.time())  # capture time as early as possible
            if all(
                [w["state"] == "normal" for w in self.widgets if "state" in w.keys()]
            ):
                self.value.set(value)
                self.event.set()

        self.gui.run_on_ui_thread(_submit)

    def wait_for_response(self, timeout=None, disable=True):
        """Wait (in the background/app thread) until the user responds to the prompt."""
        was_set = self.event.wait(timeout=timeout)
        if not was_set:
            return None, None
        if disable:
            self.disable()
        self.event.clear()  # reset
        return self.value.get(), self.timestamp.get()

    def _reset(self):
        """Set the response variables to falsy and clear the response event."""
        self._clear_tk_var(self.value)
        self._clear_tk_var(self.timestamp)
        self.event.clear()

    def reset(self):
        """Reset the response variables and events."""
        self.gui.run_on_ui_thread(self._reset)

    def destroy(self):
        """Destroy the prompt (remove and unbind it from the GUI)."""

        def _destroy():
            for child in self.frame.winfo_children():
                child.destroy()
            self.widgets.clear()
            for key in self.keybindings:
                self.gui.root.unbind(key)
            self.keybindings.clear()
            self._reset()

        self.gui.run_on_ui_thread(_destroy)
