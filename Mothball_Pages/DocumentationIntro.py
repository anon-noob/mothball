import sys, os
# import tkinter as tk

folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(folder_path)

# from ballgui import HelpPage
from Mothball_Pages.HelpPage import Page

class DocumentationIntro(Page):
    def __init__(self, master = None, pack=True):
        super().__init__(master, pack)
        self.master = master

        self.heading("Documentation")
        self.insert_text("Here, you will find information for each built-in function that Mothball has to offer, including the function signature, what it represents in game, and version differences if applicable. To learn how to use these functions to accurately simulate a parkour jump, see the advanced tutorial.")
        self.finalize()

if __name__ == "__main__":
    import tkinter as tk
    r = tk.Tk()
    a = (r)
    r.mainloop()