import tkinter as tk
import Page

class Credits(Page.Page):
    TEXT = """# Credits
To CyrenArkade for the original Mothball concept (in the form of a discord bot): [https://github.com/CyrenArkade/mothball](https://github.com/CyrenArkade/mothball)
To anonnoob (myself) for updating Mothball and creating the GUI version
To hammsamichz for helping with the help pages
To everyone else who has contributed to Mothball, whether it be through code, suggestions, or bug reports
And to you for using Mothball, thank you!

# Major News
The latest version of minecraft has released and it has reverted the movement changes, which means that 45 strafing is back, AND sprint sneaking is also back! The inertia changes are still in place, and are now in Mothball by doing `version(1.21.5)`. Few jumps will be affected by this inertia change, but it is important to note that inertia is effectively gone in the sense of technical parkour jumps.

Thank you to the developers for listening to the community and reverting the changes. Most importantly, I would like to thank the man that started it all, Erasmian (youtube: [https://www.youtube.com/@3rasmian](https://www.youtube.com/@3rasmian)), for making the video and creating the petition that started it all.
"""
    def __init__(self, master=None):
        self.top = tk.Toplevel(master)
        super().__init__(self.top)
        self.parse_text(Credits.TEXT)
        self.finalize()

if __name__ == "__main__":
    root = tk.Tk()
    Credits(root)
    root.mainloop()
