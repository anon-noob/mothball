import os
import sys
from tkinter import ttk
import tkinter as tk
import Page as Page

if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

with open(os.path.join(base_path, "Mothball_Pages/Introduction.txt")) as f:
    introduction = f.read()
    introductionHEADINGS = Page.Page.get_headings(introduction)

with open(os.path.join(base_path, "Mothball_Pages/DocumentationIntro.txt")) as f:
    documentationIntro = f.read()
    documentationIntroHEADINGS = Page.Page.get_headings(documentationIntro)

with open(os.path.join(base_path, "Mothball_Pages/LearnTheBasics.txt")) as f:
    learnTheBasics = f.read()
    learnTheBasicsHEADINGS = Page.Page.get_headings(learnTheBasics)

with open(os.path.join(base_path, "Mothball_Pages/MovementDocumentation.txt")) as f:
    movementDocumentation = f.read()
    movementDocumentationHEADINGS = Page.Page.get_headings(movementDocumentation)

with open(os.path.join(base_path, "Mothball_Pages/MovementHelp.txt")) as f:
    movementHelp = f.read()
    movementHelpHEADINGS = Page.Page.get_headings(movementHelp)

with open(os.path.join(base_path, "Mothball_Pages/OptimizationHelp.txt")) as f:
    optimizationHelp = f.read()
    optimizationHelpHEADINGS = Page.Page.get_headings(optimizationHelp)

with open(os.path.join(base_path, "Mothball_Pages/OutputHelp.txt")) as f:
    outputHelp = f.read()
    outputHelpHEADINGS = Page.Page.get_headings(outputHelp)

with open(os.path.join(base_path, "Mothball_Pages/SetterHelp.txt")) as f:
    setterHelp = f.read()
    setterHelpHEADINGS = Page.Page.get_headings(setterHelp)

with open(os.path.join(base_path, "Mothball_Pages/WelcomePage.txt")) as f:
    welcomePage = f.read()
    welcomePageHEADINGS = Page.Page.get_headings(welcomePage)


class MainHelpPage(tk.Frame):
    def __init__(self, master):
        self.top = tk.Toplevel(master)

        self.master = master
        self.top.title("Mothball Help Page")

        self.left_frame = tk.Frame(self.top)
        self.left_frame.pack(side="left", fill="y")

        self.tree = ttk.Treeview(self.left_frame)
        
        self.tree.pack(fill='y', expand=True)

        self.right_frame = tk.Frame(self.top)
        self.right_frame.pack(side="right", expand=True, fill="both")

        self.current_page = Page.Page(self.right_frame)
        self.current_page_name = "welcome"
        self.current_page.parse_text(welcomePage)
        self.current_page.text.configure(state="disabled")

        self.tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

        self.tree.insert("", "end",iid=0, text="Welcome to Mothball")
        self.tree.insert("", "end",iid=1, text="Learn the Basics")
        self.tree.insert("", "end",iid=2, text="Documentation")

        self.add_to_tree(1, 'intro', "Introduction", introductionHEADINGS)
        self.add_to_tree(1, 'movement', "Movement", movementHelpHEADINGS)
        self.add_to_tree(1, 'setters', "Setters", setterHelpHEADINGS)
        self.add_to_tree(1, 'outputs', "Outputs", outputHelpHEADINGS)
        self.add_to_tree(1, 'optimize', "Optimization", optimizationHelpHEADINGS)
        
        self.add_to_tree(2, 'movementdocumentation', 'Movement Functions', movementDocumentationHEADINGS)

    def add_to_tree(self, depth: int, id_name: str, display_name: str, HEADINGS: dict):
        last_heading1 = ""
        last_heading2 = ""
        self.tree.insert(depth, "end", iid=id_name, text=display_name)
        for title, (index, depth) in HEADINGS.items():
            if depth == 1:
                self.tree.insert(id_name, 'end', iid=id_name + " " + index, text=title)
                last_heading1 = id_name + " " + index
            elif depth == 2:
                self.tree.insert(last_heading1, 'end', iid=id_name + " " + index, text=title)
                last_heading2 = id_name + " " + index
            elif depth == 3:
                self.tree.insert(last_heading2, 'end', iid=id_name + " " + index, text=title)


    def on_treeview_select(self, event):
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            try: 
                item_id = int(item_id)
                if item_id == 0:
                    self.show("welcome")
                elif item_id == 1:
                    self.show("learn")
                elif item_id == 2:
                    self.show("doc")

            except ValueError:
                try:
                    page, index = item_id.split(" ")
                    if self.current_page_name != page:
                        self.show(page)
                    self.current_page.text.see(index)
                except:
                    self.show(item_id)

    def clear_page(self):
        self.current_page.text.configure(state="normal")
        for tag_name in self.current_page.tags:
            self.current_page.text.tag_remove(tag_name, "1.0", tk.END)
        self.current_page.text.delete("1.0", tk.END)
        self.current_page.pos.row = 1
        self.current_page.pos = self.current_page.pos.reset_column()
        self.current_page.images = {}
        
    
    def show(self, page_name):
        if self.current_page_name == page_name:
            return
        self.clear_page()
        match page_name:
            case"intro":
                self.current_page.parse_text(introduction)
            case "movement":
                self.current_page.parse_text(movementHelp)
            case "outputs":
                self.current_page.parse_text(outputHelp)
            case "optimize":
                self.current_page.parse_text(optimizationHelp)
            case "setters":
                self.current_page.parse_text(setterHelp)
            case "welcome":
                self.current_page.parse_text(welcomePage)
            case "learn":
                self.current_page.parse_text(learnTheBasics)
            case "doc":
                self.current_page.parse_text(documentationIntro)
            case "movementdocumentation":
                self.current_page.parse_text(movementDocumentation)
        self.current_page_name = page_name
        self.current_page.text.configure(state="disabled")



if __name__ == "__main__":
    root = tk.Tk()
    a = MainHelpPage(root)
    tk.Button(root, text="Example Button").pack()
    # print(a.master)
    root.mainloop()
