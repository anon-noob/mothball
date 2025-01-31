import tkinter as tk
import json
import FileHandler

class Settings:
    def __init__(self, main_frame, options: dict):
        self.options = options
        self.main_frame = main_frame
        self.top = tk.Toplevel()
        self.top.option_add("*Checkbutton*Background", "gray12")
        self.top.option_add("*Checkbutton*Foreground", "White")
        self.top.option_add("*Button*Background", "gray12")
        self.top.option_add("*Button*Foreground", "White")
        self.top.option_add("*Label*Background", "gray12")
        self.top.option_add("*Label*Foreground", "White")
        self.top.configure(bg="gray12")
        self.top.title("Change Colors")

        self.label = tk.Label(self.top, text="Settings", font=("Ariel", 12))
        self.label.grid()
        self.b = tk.Checkbutton(self.top, text="Ask before deleting a cell", command=lambda: self.toggle("Ask before deleting a cell"), font=("Ariel", 12))
        if self.options["Settings"]["Ask before deleting a cell"]: self.b.select()
        self.b.grid()
        self.apply = tk.Button(self.top, text="Apply and Save", command=self.apply_and_save)
        self.apply.grid()

        self.top.transient(self.main_frame)
        self.top.grab_set()
    
    def toggle(self, item):
        self.options["Settings"][item] = not self.options["Settings"][item]

    def apply_and_save(self):
        with open(FileHandler.get_path_to_options(), "w") as file:
            json.dump(self.options, file)
        self.main_frame.change_settings(self.options)
        self.top.destroy()

if __name__ == "__main__":
    with open("Mothball Settings/Options.json", "r") as file:
        options = json.load(file)
    r = tk.Tk()
    a = Settings(r, {"Settings":{"Ask before deleting a cell": True}})
    r.mainloop()