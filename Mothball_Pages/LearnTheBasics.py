import sys, os
# import tkinter as tk

folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(folder_path)

# from ballgui import HelpPage
from Mothball_Pages.HelpPage import Page

class Learn(Page):
    def __init__(self, master = None, pack=True):
        super().__init__(master, pack)
        self.master = master

        self.heading("Learn the Basics!")
        self.insert_text("New to Mothball? Start your journey here! Learn the key functions to create simple simulations and extract information from them.")
        self.finalize()

if __name__ == "__main__":
    import tkinter as tk
    r = tk.Tk()
    a = (r)
    r.mainloop()