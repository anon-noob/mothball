import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import webbrowser
from TkinterPosition import TkinterPosition

class About(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.top = tk.Toplevel(master)

        self.pos = TkinterPosition(1,0)

        self.text = ScrolledText(self.top)
        self.text.configure(background="gray15", foreground="white", font=("Ariel", 12), wrap=tk.WORD, spacing1=1, spacing3=1)
        self.text.pack(fill=tk.BOTH, expand=True)
        
        self.text.tag_configure("header", font=('Ariel', 20), foreground="light blue")

        self.heading("About Mothball")
        self.insert_text("Mothball is a lightweight and efficient tool for stratfinding Minecraft parkour. You are using the GUI version of Mothball, which is a graphical user interface for Mothball providing a user-friendly experience which includes syntax highlighting and a file save system. If you have any questions or need help, please refer to the help pages.\n\n")
        self.insert_text("The GUI version of Mothball is still in development, so there may be bugs or missing features or performance issues, though performance shouldn't be a major concern for most tasks. If you encounter any issues, please report them to anonnoob.\n\n")
        self.insert_text(f"Original Mothball Concept (in the form of a discord bot) by CyrenArkade: ")
        self.link("https://github.com/CyrenArkade/mothball")
        self.insert_text("\n\n")
        self.insert_text("Updated Discord Bot by anonnoob (forked from CyrenArkade): ")
        self.link("https://github.com/anon-noob/mothball")
        self.insert_text("\n\n")
        self.insert_text("On that note, this GUI versrion of Mothball was created by anonnoob. You are free to use it, change it to your liking, and dominate the parkour universe, but you cannot use this for monetary gain under any circumstance.\n\n")
        self.insert_text("If you are interested in the code for this GUI, you can find it here: [insert link here]\n\n")
        self.insert_text("Other parkour related tools: \n")
        self.insert_text("    - ")
        self.link("https://github.com/drakou111/MBS")
        self.insert_text(" To check if a pixel pattern is constructable, supports all versions of Minecraft\n")
        self.insert_text("    - ")
        self.link("https://github.com/drakou111/OMF")
        self.insert_text(" To find inputs that give optimal movement given constraints. Obviously optimal does not mean human doable, so be aware of its limitations.\n")
        self.insert_text("    - ")
        self.link("https://github.com/Leg0shii/ParkourCalculator")
        self.insert_text(" If abstraction and efficiency is too hard, this is a tool to simulate movement with an actual minecraft-world-like interface. Comes with AI pathfinding for general naviagation purposes, or trying to get the fastest times. As of right now, specializes in 1.8, 1.12, and 1.20 parkour.\n\n")
        self.insert_text("Lastly, if you haven't already, download MPK/CYV to enhance your in game parkour abilities. A quick google search will take you to the right place. We recommend MPK for 1.8 - 1.12 parkour, and CYV for 1.20+ parkour.\n\n")
        self.heading("Good luck, and happy stratfinding!")
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
    About(root)
    root.mainloop()