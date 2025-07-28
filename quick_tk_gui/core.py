import copy
import threading
import time
import tkinter as tk


class GUI:

    def __init__(self, name: str, initial_layout, main, minsize=(700, 400)):

        self.root = tk.Tk()
        self.root.title(name)

        # Create the default user input events and variables
        self.user_input_event = threading.Event()
        self.user_input_var = tk.StringVar()
        self.input_enabled = tk.BooleanVar()
        self.all_input_widgets = []

        # Create the initial layout from the user function
        initial_layout(self)

        self.disable_input()

        # Run the main user function in a background thread
        threading.Thread(target=main, args=(self,), daemon=True).start()

        self.root.minsize(*minsize)

        self.root.mainloop()

    def close(self):
        """Close the GUI window."""
        self.root.destroy()

    def run_on_main_thread(self, func, *args, **kwargs):
        """Run a function on the main thread with copies of all data for safety."""
        args_copy = copy.deepcopy(args)
        kwargs_copy = copy.deepcopy(kwargs)
        self.root.after(0, func, *args_copy, **kwargs_copy)

    def enable_input(self):
        """Enable input state flag and all registered input widgets."""

        def enable_all_input_widgets():
            self.input_enabled.set(True)
            for input in self.all_input_widgets:
                input.config(state="normal")

        self.run_on_main_thread(enable_all_input_widgets)

    def disable_input(self):
        """Disable input state flag and all registered input widgets."""

        def disable_all_input_widgets():
            self.input_enabled.set(False)
            for input in self.all_input_widgets:
                input.config(state="disabled")

        self.run_on_main_thread(disable_all_input_widgets)

    def get_user_input(self, toggle_enable=True, clock=time.time):
        """Wait for and get user input, enabling and disabling widgets."""

        if toggle_enable:
            self.enable_input()
        self.user_input_event.wait()
        timestamp = clock()  # NOTE: tested <1ms after callback fires
        value = self.user_input_var.get()
        self.user_input_event.clear()
        if toggle_enable:
            self.disable_input()

        return value, timestamp
