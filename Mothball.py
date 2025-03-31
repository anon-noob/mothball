import FileHandler
if __name__ == "__main__":
    FileHandler.create_directories()

import requests
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesnocancel, showinfo, showerror
import json
import os
from ChangeColorDialog import ChangeColorDialog
from SetttingsDialog import Settings
from CodeCell import Cell
import MainHelpPage
import About_Mothball
import Credits
from tkinter.filedialog import askopenfile, asksaveasfile
import sys
import Version


class MainNotebookGUI(tk.Tk, tk.Frame):

    FRAMES: dict[int, Cell] = {}
    VERSION: str = "v0.3-alpha"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.current_width = 500
        self.user_directory = os.path.expanduser("~") # maybe

        self.bind("<Control-s>", func=lambda e: self.save())
        self.bind("<Control-o>", func=lambda e: self.load())
        self.bind("<Control-n>", func=lambda e: self.new())


        try:
            if getattr(sys, "frozen", False):
                apppath = sys._MEIPASS # When run as an exe
            else:
                apppath = "" # Otherwise (run as a script)
            icopath = os.path.join(apppath, "Assets", "The_HPK_Cube.ico") # This has to change depending on the os probably
            self.iconbitmap(icopath)
        except:
            pass

        self.file_name = ""

        self.options = FileHandler.get_options()
        try:
            self.fontsize = self.options["Default-Font-Size"]
            # print(self.fontsize)
        except KeyError:
            self.fontsize = 12
            FileHandler.create_directories(force_update=True)

        self.canvas = tk.Canvas(self, background="gray12")
        self.canvas.pack(side='right', fill='both', expand=True)
        
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollbar.pack(side='right', fill='y')
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_content = ttk.Frame(self.canvas)
        self.scrollable_content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.id = self.canvas.create_window((0, 0), window=self.scrollable_content, anchor='nw')

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.createbox(row=0, mode="xz")
        
        self.title("Parkour Simulator - A Mothball Upgrade - Unnamed")

        self.canvas.bind('<Configure>', lambda e: self._on_configure(e, self.id))

        try:
            if getattr(sys, "frozen", False):
                apppath = sys._MEIPASS
            else:
                apppath = ""

            # Windows: Use .ico
            icopath = os.path.join(apppath, "images", "cube.ico")
            self.iconbitmap(icopath)

            # macOS/Linux: Use .png
            iconpath_png = os.path.join(apppath, "images", "cube.png")
            if os.path.exists(iconpath_png):
                icon_image = tk.PhotoImage(file=iconpath_png)
                self.wm_iconphoto(True, icon_image)
        except Exception as e:
            print(f"Error setting icon: {e}")


        self.help_window = False
        self.about_window = False
        self.credits_window = False
        self.version_window = False
        self.has_unsaved_changes = False
        
        self.scrollable_content.grid_rowconfigure(0, weight=1)
        self.scrollable_content.grid_columnconfigure(0, weight=1)


        ###############################################
        menubar = tk.Menu(self, background="gray12")
        self.config(menu=menubar)

        fileMenu = tk.Menu(menubar, tearoff=False)
        fileMenu.add_command(label="New", command=self.new)
        fileMenu.add_command(label="Save", command=self.save)
        fileMenu.add_command(label="Save as", command=self.save_as)
        fileMenu.add_command(label="Open", command=self.load)
        menubar.add_cascade(label="File", menu=fileMenu)

        optionsMenu = tk.Menu(menubar, tearoff=False)
        optionsMenu.add_command(label="Colors", command=self.edit_colors)
        optionsMenu.add_command(label="Settings", command=self.settings)
        menubar.add_cascade(label="Options", menu=optionsMenu)

        helpMenu = tk.Menu(menubar, tearoff=False)
        helpMenu.add_command(label="About Mothball", command=self.show_about)
        helpMenu.add_command(label="Mothball Tutorial", command=self.show_tutorial)
        helpMenu.add_command(label="Credits", command= self.show_credits)
        menubar.add_cascade(label="Help", menu=helpMenu)

        updateMenu = tk.Menu(menubar, tearoff=False)
        updateMenu.add_command(label="Changelog", command=self.show_current_version_changelog)
        updateMenu.add_command(label="Check For Updates", command=lambda x=True: self.check_updates(x))
        menubar.add_cascade(label="Update", menu=updateMenu)

        self.protocol("WM_DELETE_WINDOW", self.on_destroy)

        self.canvas.bind_all("<Control-equal>", lambda e, x=2: self.change_font_size(e, x))
        self.canvas.bind_all("<Control-minus>", lambda e, x=-2: self.change_font_size(e, x))

        # self.after("idle",self.check_updates)

    def _on_configure(self, event: tk.Event, widget_id, delay = 500):
        if event.type == tk.EventType.Configure:
            if hasattr(self, '_resize_after_id'):
                self.after_cancel(self._resize_after_id)
            self._resize_after_id = self.after(delay, self._resize_widgets, event, widget_id)

    def _resize_widgets(self, event, widget_id):
        if event is not None:
            # print(self.current_width)
            event.widget.itemconfigure(widget_id, width=event.width-8)
            self.current_width = event.width
        for widget in MainNotebookGUI.FRAMES.values():
            widget.adjust_width(self.current_width)
            self.update_idletasks()
            widget.adjust_height()
            widget.adjust_height(widget=widget.output)
            widget.colorize_code()

    def createbox(self, row, mode: str):
        "Creates a box below it"
        if row == 0 and MainNotebookGUI.FRAMES:
            MainNotebookGUI.FRAMES[0].destroy()
            del MainNotebookGUI.FRAMES[0]

        new_cell = Cell(self.scrollable_content, mode=mode, options=self.options, grandparent=self, fontsize=self.fontsize)

        # Add a frame to hold the buttons
        button_frame = tk.Frame(new_cell, background="gray12")
        button_frame.pack(side="bottom", fill="x")

        # Add and Delete buttons
        new_cell.eval_button.pack_configure(expand=True, fill="x")

        new_cell.add_cell.configure(command=lambda a=row + 1: self.createbox(a, "xz"))

        new_cell.add_cell_y.configure(command=lambda a=row + 1: self.createbox(a, "y"))

        new_cell.delete_cell.configure(command=lambda a=row + 1: self.deletecell(a))

        new_cell.grid(row=row + 1, sticky="nswe")

        # Update the scroll region of the canvas
        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Add to dictionary
        frames = MainNotebookGUI.FRAMES
        frames[len(frames) + 1] = []

        for i in range(len(frames), row + 1, -1):
            frames[i] = frames[i - 1]

            # Represents changing the data manually
            frames[i].add_cell.configure(command=lambda a=i: self.createbox(a, "xz"))
            frames[i].add_cell_y.configure(command=lambda a=i: self.createbox(a, "y"))
            frames[i].delete_cell.configure(command=lambda a=i: self.deletecell(a))
            frames[i].grid(row=i)

        frames[row + 1] = new_cell
        self._resize_widgets(None, self.id)
        self.update_idletasks()
    
    def deletecell(self, row):
        if self.options["Settings"]["Ask before deleting a cell"] and MainNotebookGUI.FRAMES[row].text.get("1.0", tk.END):
            a = askyesnocancel("Confirm", "Delete cell?")
            if not a:
                return

        frames = MainNotebookGUI.FRAMES

        frames[row].destroy()

        for i in range(row, len(frames)):
            frames[i] = frames[i + 1]
        
            # Represents changing the datas manually
            frames[i].add_cell.configure(command = lambda a = i: self.createbox(a,"xz"))
            frames[i].add_cell_y.configure(command = lambda a = i: self.createbox(a,"y"))
            frames[i].delete_cell.configure(command = lambda a = i: self.deletecell(a))
            frames[i].grid(row=i)
        
        del frames[max(frames.keys())]
        self.update_idletasks()

        if len(MainNotebookGUI.FRAMES) == 0:
            frame = StarterFrame(self.scrollable_content)
            frame.xz_button.configure(command=lambda a = 0: self.createbox(a, "xz"))
            frame.y_button.configure(command=lambda a = 0: self.createbox(a, "y"))
            frame.pack(fill="x")
            MainNotebookGUI.FRAMES[0] = frame
        
        self.event_generate('<Configure>')

    
    def _on_mousewheel(self, event: tk.Event):
        a = self.winfo_containing(event.x_root, event.y_root)
        if a and a.winfo_toplevel() == self:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def edit_colors(self):
        ChangeColorDialog(self, self.options)
    
    def settings(self):
        Settings(self, self.options)

    def new(self):
        if self.has_unsaved_changes:
            a = askyesnocancel("Save file?", "You have unsaved changes. Save file before opening a new file?")
            if a is True:
                self.save()
            elif a is None:
                return "break"


        for a, frame in MainNotebookGUI.FRAMES.items():
            frame.destroy()
        MainNotebookGUI.FRAMES = {}

        frame = StarterFrame(self.scrollable_content)
        frame.xz_button.configure(command=lambda a = 0: self.createbox(a, "xz"))
        frame.y_button.configure(command=lambda a = 0: self.createbox(a, "y"))
        frame.pack(fill="x") # 2 ?
        
        MainNotebookGUI.FRAMES[0] = frame

        self.file_name = ""
        self.title(f"Parkour Simulator - A Mothball Upgrade - Unnamed")
        self.has_unsaved_changes = False
    
    def save(self):
        if not self.file_name:
            self.save_as()
        else:
            data = {"fileName": self.file_name}
            for i, frame in MainNotebookGUI.FRAMES.items():
                data[i] = {"name": frame.label.cget("text"),
                           "mode": frame.mode,
                           "code": frame.text.get("1.0", tk.END), 
                      "exec_time": str(frame.execution_time),
                    "has_changed": frame.has_changed,
                     "raw_output": frame.raw_output}
            
            with open(os.path.join(self.user_directory, "Documents", "Mothball", "Notebooks", f"{self.file_name}.json"), "w") as file:
                json.dump(data, file, indent=4)

            self.has_unsaved_changes = False

    def save_as(self):
        file = asksaveasfile(confirmoverwrite=True, initialdir=os.path.join(self.user_directory, "Documents", "Mothball", "Notebooks"), defaultextension=".json")
        if not file:
            return
        
        self.file_name = file.name.split("/")[-1].removesuffix(".json")
        # print(self.file_name)
        self.title(f"Parkour Simulator - A Mothball Upgrade - {self.file_name}")

        data = {"fileName": self.file_name}
        for i, frame in MainNotebookGUI.FRAMES.items():
            data[i] = {"name": frame.label.cget("text"),
                       "mode": frame.mode,
                       "code": frame.text.get("1.0", tk.END), 
                  "exec_time": str(frame.execution_time),
                "has_changed": frame.has_changed,
                 "raw_output": frame.raw_output}
        
        json.dump(data, file, indent=4)

        self.has_unsaved_changes = False

    def load(self):
        if self.has_unsaved_changes:
            if not askyesnocancel("Unsaved Changes", "You have unsaved changes. Open new file anyway?"):
                return "break"

        file = askopenfile(initialdir=os.path.join(self.user_directory, "Documents", "Mothball", "Notebooks"), defaultextension=".json")
        if not file:
            return "break"
        data = json.load(file)
        file.close()
        
        for a, frame in MainNotebookGUI.FRAMES.items():
            frame.destroy()
        MainNotebookGUI.FRAMES = {}
        
        
        self.file_name = file.name.split("/")[-1].removesuffix(".json")
        self.title(f"Parkour Simulator - A Mothball Upgrade - {self.file_name}")

        frame_count = 1
        while True:
            frame_data = data.get(str(frame_count))
            if frame_data is None:
                MainNotebookGUI.FRAMES[frame_count-1].adjust_height()
                MainNotebookGUI.FRAMES[frame_count-1].colorize_code()
                break
            self.createbox(row=frame_count-1, mode=frame_data['mode'])
            MainNotebookGUI.FRAMES[frame_count].label.configure(text=frame_data["name"])
            MainNotebookGUI.FRAMES[frame_count].text.insert("1.0", frame_data["code"].removesuffix("\n"))
            MainNotebookGUI.FRAMES[frame_count].raw_output = frame_data["raw_output"]
            MainNotebookGUI.FRAMES[frame_count].colorize_output()
            MainNotebookGUI.FRAMES[frame_count].label2.configure(state="normal")
            if frame_data['exec_time'] != "None":
                MainNotebookGUI.FRAMES[frame_count].label2.insert(tk.END, f"(Executed at {frame_data['exec_time']})")
                if frame_data["has_changed"]:
                    MainNotebookGUI.FRAMES[frame_count].has_changed = frame_data["has_changed"]
                    MainNotebookGUI.FRAMES[frame_count].label2.tag_add("grayed", "1.22", tk.END)

            MainNotebookGUI.FRAMES[frame_count].label2.configure(state="disabled")

            frame_count += 1

        self.has_unsaved_changes = False

        return "break"
    
    def change_settings(self, new_options: dict):
        self.options = new_options

    def change_colors(self, new_options: dict):
        self.options = new_options

        for frame in MainNotebookGUI.FRAMES.values():
            frame.options = new_options
            for tag_name, foreground_color in new_options["Current-theme"]["Code"].items():
                frame.text.tag_configure(tag_name, foreground=foreground_color)

            for tag_name, foreground_color in new_options["Current-theme"]["Output"].items():
                frame.output.tag_configure(tag_name, foreground=foreground_color)
            frame.colorize_code()

    def show_tutorial(self):
        if not self.help_window:
            self.help_window = MainHelpPage.MainHelpPage(None)
            self.help_window.top.bind("<Destroy>", func= self.l)
        else:
            self.help_window.top.focus()
    
    def show_about(self):
        if not self.about_window:
            self.about_window = About_Mothball.About(None)
            self.about_window.top.bind("<Destroy>", func= self.m)
        else:
            self.about_window.top.focus()
    
    def show_credits(self):
        if not self.credits_window:
            self.credits_window = Credits.Credits(None)
            self.credits_window.top.bind("<Destroy>", func= self.n)
        else:
            self.credits_window.top.focus()
    
    def show_current_version_changelog(self):
        if not self.version_window:
            self.version_window = Version.Version(self.VERSION, None)
            self.version_window.top.bind("<Destroy>", func= self.o)
        else:
            self.version_window.focus()

    # idfk
    def l(self, e):
        self.help_window = False
    
    def m(self, e):
        self.about_window = False
    
    def n(self, e):
        self.credits_window = False
    
    def o(self, e):
        self.version_window = False
    
    def on_destroy(self):
        if self.has_unsaved_changes:
            a = askyesnocancel("Save file?", "You have unsaved changes. Save file?")
            if a is True:
                self.save()
            elif a is None:
                return

        with open(FileHandler.get_path_to_options(), "w+") as file:
            json.dump(self.options, file, indent=4)

        self.destroy()
    
    def check_updates(self, show_message = False):
        text = f"You're using Mothball version {MainNotebookGUI.VERSION}. "
        try:
            response = requests.get("https://api.github.com/repos/anon-noob/mothball/releases")
            if response.status_code == 200:
                latest_release = response.json()[0]
                latest_version = latest_release.get("tag_name")
                if latest_version != MainNotebookGUI.VERSION:
                    showinfo("Update found", text + f"The new update {latest_version} can be found on Github.")
                    
                elif show_message:
                    showinfo("No updates found", "You are on the latest version.")

            elif show_message:
                showerror("Unable to check for updates.")
        except Exception as e:
            if show_message:
                showerror("Unable to check for updates.")
    
    def change_font_size(self, e, change: int):
        self.fontsize += change
        self.options["Default-Font-Size"] = self.fontsize
        for frame in MainNotebookGUI.FRAMES.values():
            for text_widget in (frame.label, frame.text, frame.label2, frame.output):
                current_font = str(text_widget.cget("font"))
                font_family, font_size = current_font.rsplit(" ", 1)
                font_family = font_family.strip("{}")
                new_font_size = min(max(4, int(font_size) + change), 40)
                text_widget.configure(font=(font_family, new_font_size))
            frame.adjust_height(e)
            frame.adjust_height(e, frame.output)
    
class StarterFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(background="gray12")
        self.xz_button = tk.Button(self, text="Add Cell XZ", background="gray12", foreground="white")
        self.xz_button.pack()
        self.y_button = tk.Button(self, text="Add Cell Y", background="gray12", foreground="white")
        self.y_button.pack()
    
    def adjust_width(self, event):
        pass


        

if __name__ == "__main__":
    app = MainNotebookGUI()
    app.geometry("520x400")
    app.mainloop()
