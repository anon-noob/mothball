import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import webbrowser
from TkinterPosition import TkinterPosition

class Credits(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.top = tk.Toplevel(master)

        self.pos = TkinterPosition(1,0)

        self.text = ScrolledText(self.top)
        self.text.configure(background="gray15", foreground="white", font=("Ariel", 12), wrap=tk.WORD, spacing1=1, spacing3=1)
        self.text.pack(fill=tk.BOTH, expand=True)
        
        self.text.tag_configure("header", font=('Ariel', 20), foreground="light blue")

        self.heading("Credits")
        self.insert_text("To CyrenArkade for the original Mothball concept (in the form of a discord bot): ")
        self.link("https://github.com/CyrenArkade/mothball")
        self.insert_text("\nTo anonnoob (myself) for updating Mothball and creating the GUI version\n")
        self.insert_text("To hammsamichz for helping with the help pages\n")
        self.insert_text("To everyone else who has contributed to Mothball, whether it be through code, suggestions, or bug reports\n")
        self.insert_text("And to you for using Mothball, thank you!\n\n")

        self.heading("Major News")
        self.insert_text("The latest snapshot of minecraft has released and it has reverted the movement changes, which means that 45 strafing is back, AND sprint sneaking is also back! The inertia changes are still in place, and will be reflected in Mothball soon. Very few jumps will be affected by this inertia change, but it is important to note that inertia is effectively gone in the sense of technical parkour jumps.\n\n")
        self.insert_text("Anyway, I would like to thank everyone helping us convince the development team to revert the necessary changes. It is a great example of how a community can come together to make a change. I would also like to thank the developers for listening to the community and reverting the changes. Most importantly, i would like to thank the man that started it all, Erasmian (youtube: ")
        self.link("https://www.youtube.com/@3rasmian")
        self.insert_text("), for making the video and creating the petition that started it all. Thank you, keep 45 strafing, keep sprint sneaking, and let's continue to celebrate the longevity of minecraft parkour!")
        self.text.configure(state="disabled")

    def insert_text(self, content: str):
        self.text.insert(tk.END, content)            
        if "\n" in content:
            index = content.rindex("\n")

            self.pos = self.pos.add_row(content.count("\n")).reset_column() + (len(content) - index - 1)
        else:
            self.pos += len(content)
    
    def heading(self, title: str):
        self.text.insert(tk.END, title + "\n")
        self.text.tag_add("header", self.pos.string, (self.pos + len(title)).string)
        self.pos = self.pos.add_row(1).reset_column()
    
    def link(self, link: str):
        self.text.insert(tk.END, link)
        self.text.tag_configure(f"link {link}", foreground="light blue", underline=True)
        self.text.tag_add(f"link {link}", self.pos.string, (self.pos + len(link)).string)
        self.text.tag_bind(f"link {link}", "<Button-1>", func=lambda e: webbrowser.open_new(link))
        self.pos += len(link)


if __name__ == "__main__":
    root = tk.Tk()
    Credits(root)
    root.mainloop()