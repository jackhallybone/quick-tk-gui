import copy
import threading
import time
import tkinter as tk
from typing import Any, Callable


class ThreadedGUI:
    """A thread-handling wrapper for running a Ktinter GUI alongside app code."""

    def __init__(
        self,
        name: str,
        app_logic: Callable,
        build_ui: Callable | None = None,
        min_size: tuple[int, int] = (700, 400),
    ):
        """Initialise a ThreadedGUI instance, creating an initial GUI layout and starting the app code."""

        self._lock = threading.Lock()

        self.root = tk.Tk()
        self.root.title(name)

        self._clock: Callable = time.time

        self._prompts: set[_Prompt] = set()  # track the sources in the UI

        if build_ui:
            build_ui(self)

        threading.Thread(target=app_logic, args=(self,), daemon=True).start()

        self.root.minsize(*min_size)

        self.root.mainloop()

    @staticmethod
    def _deepcopy_or_original(obj: Any) -> Any:
        """Return a deepcopy where possible, or the original."""
        try:
            return copy.deepcopy(obj)
        except:
            return obj

    def run_on_ui_thread(self, func: Callable, *args, **kwargs) -> Any:
        """Synchronously run (ie, blocking) a function on the main (ktinter) thread."""

        # Already in the GUI thread, so just call
        if threading.current_thread() is threading.main_thread():
            return func(*args, **kwargs)

        # Deepcopy arguments (allowing arguments like tk widgets from skipping)
        safe_args = tuple(self._deepcopy_or_original(a) for a in args)
        safe_kwargs = {k: self._deepcopy_or_original(v) for k, v in kwargs.items()}

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
        with self._lock:
            self._clock = clock

    @property
    def now(self) -> float:
        """The current time from the ThreadedGUI clock."""
        with self._lock:
            return self._clock()

    # Prompts

    def add_prompt(
        self, setup_func: Callable, parent_frame: tk.Widget, *args, **kwargs
    ) -> "_Prompt":
        """Add a prompt to the UI by running it's setup function."""

        def create_prompt():
            """Create a new _Prompt object and run the setup function."""
            prompt = _Prompt(self, parent_frame)
            setup_func(prompt, parent_frame, *args, **kwargs)
            self.root.update_idletasks()
            prompt.presentation_timestamp = (
                self.now
            )  # take timestamp as early after draw as possible
            with self._lock:
                self._prompts.add(prompt)
            return prompt

        return self.run_on_ui_thread(create_prompt)

    def __contains__(self, prompt: "_Prompt") -> bool:
        with self._lock:
            return prompt in self._prompts

    def remove_prompt(self, prompt: "_Prompt"):
        """Remove a prompt from the UI."""
        prompt._must_exist_in_ui()
        prompt._destroy()
        with self._lock:
            self._prompts.remove(prompt)

    def clear_prompts(self):
        """Remove all prompts from the UI."""
        with self._lock:
            prompts = list(self._prompts)
        for prompt in prompts:
            self.remove_prompt(prompt)


class _Prompt:
    """A prompt object which contains states and variables for interactivity for the UI."""

    def __init__(self, gui: ThreadedGUI, parent_frame: tk.Widget):
        """Initialise a _Prompt object, which begins "empty" and is populated by an external setup function."""
        self.gui = gui
        self.frame = parent_frame
        self.event = threading.Event()
        # self.value: tk.Variable = # must be set using self.set_return_type()
        self.timestamp = tk.DoubleVar()
        self.widgets: set[tk.Widget] = set()
        self.keybindings: set[str] = set()
        self.presentation_timestamp: float | None = None

    def _must_exist_in_ui(self):
        """Raise an error if the prompt has been destroyed."""
        if self not in self.gui:
            raise RuntimeError(
                "This prompt has been destroyed and can no longer be used."
            )

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
        """Enable the interactive widgets in the prompt."""
        self._must_exist_in_ui()
        self.gui.run_on_ui_thread(self._set_enabled, True)

    def disable(self):
        """Disable the interactive widgets in the prompt."""
        self._must_exist_in_ui()
        self.gui.run_on_ui_thread(self._set_enabled, False)

    def submit(self, value: Any):
        """UI callback to submit the response where the type of `value` matching the prompt return type."""

        def _submit():
            """If the prompt is active (widgets enabled), on submit, set the return values."""
            self.timestamp.set(
                self.gui.now
            )  # take timestamp as close to callback fire as possible
            if all(
                [w["state"] == "normal" for w in self.widgets if "state" in w.keys()]
            ):
                self.value.set(value)
                self.event.set()

        self._must_exist_in_ui()
        self.gui.run_on_ui_thread(_submit)

    def wait_for_response(
        self, timeout=None, disable=True
    ) -> tuple[Any, float] | tuple[None, None]:
        """Wait (blocking the calling thread) until the user responds to the UI prompt."""
        self._must_exist_in_ui()
        was_set = self.event.wait(timeout=timeout)
        if not was_set:
            return None, None
        if disable:
            self.disable()
        self.event.clear()  # reset
        return self.value.get(), self.timestamp.get()

    def reset(self):
        """Reset the response variables and user input events."""

        def _reset():
            """Set the response variables to falsy and clear the response event."""
            self._clear_tk_var(self.value)
            self._clear_tk_var(self.timestamp)
            self.event.clear()

        self._must_exist_in_ui()
        self.gui.run_on_ui_thread(_reset)

    def _destroy(self):
        """Destroy the prompt (remove and unbind it from the UI)."""

        def _do_destroy():
            for child in self.frame.winfo_children():
                child.destroy()
            self.widgets.clear()
            for key in self.keybindings:
                self.gui.root.unbind(key)
            self.keybindings.clear()
            self.reset()

        self.gui.run_on_ui_thread(_do_destroy)
