import tkinter as tk
import Page


class About(Page.Page):
    TEXT = """# About Mothball
Mothball is a lightweight and efficient tool for stratfinding Minecraft parkour. You are using the GUI version of Mothball, which is a graphical user interface for Mothball providing a user-friendly experience which includes syntax highlighting and a file save system. If you have any questions or need help, please refer to the help pages.

The GUI version of Mothball is still in development, so there may be bugs or missing features or performance issues, though performance shouldn't be a major concern for most tasks. If you encounter any issues, please report them to anonnoob.

Original Mothball Concept (in the form of a discord bot) by CyrenArkade: [https://github.com/CyrenArkade/mothball](https://github.com/CyrenArkade/mothball)

Updated Discord Bot by anonnoob (forked from CyrenArkade): [https://github.com/anon-noob/mothball](https://github.com/anon-noob/mothball)

On that note, this GUI versrion of Mothball was created by anonnoob. You are free to use it, change it to your liking, and dominate the parkour universe, but you cannot use this for monetary gain under any circumstance.

If you are interested in the code for this GUI, you can find it [here](https://github.com/anon-noob/mothball/tree/app).

Other parkour related tools: 
    - [https://github.com/drakou111/MBS](https://github.com/drakou111/MBS) To check if a pixel pattern is constructable, supports all versions of Minecraft
    - [https://github.com/drakou111/OMF](https://github.com/drakou111/OMF) To find inputs that give optimal movement given constraints. Obviously optimal does not mean human doable, so be aware of its limitations.
    - [https://github.com/Leg0shii/ParkourCalculator](https://github.com/Leg0shii/ParkourCalculator) If abstraction and efficiency is too hard, this is a tool to simulate movement with an actual minecraft-world-like interface. Comes with AI pathfinding for general naviagation purposes, or trying to get the fastest times. As of right now, specializes in 1.8, 1.12, and 1.20 parkour.
    
Lastly, if you haven't already, download MPK/CYV to enhance your in game parkour abilities. A quick google search will take you to the right place. We recommend MPK for 1.8 - 1.12 parkour, and CYV for 1.20+ parkour.

# Good luck, and happy stratfinding!
"""

    def __init__(self, master=None):
        self.top = tk.Toplevel(master)
        super().__init__(self.top)
        self.parse_text(About.TEXT)
        self.finalize()


if __name__ == "__main__":
    root = tk.Tk()
    About(root)
    root.mainloop()
