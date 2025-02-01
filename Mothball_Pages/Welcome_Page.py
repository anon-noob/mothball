import sys, os
# import tkinter as tk

folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(folder_path)

# from ballgui import HelpPage
from Mothball_Pages.HelpPage import Page

class Welcome(Page):
    def __init__(self, master = None, pack=True):
        super().__init__(master, pack)

        self.heading("Welcome to Mothball!")
        self.insert_text("Click on the left to read about what Mothball has to offer.")
        self.finalize()


if __name__ == "__main__":
    import tkinter as tk
    r = tk.Tk()
    a = Welcome(r)
    print(a.headings)
    r.mainloop()
