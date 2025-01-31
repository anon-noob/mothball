from tkinter import ttk
import tkinter as tk
import Mothball_Pages.Introduction as I
import Mothball_Pages.MovementHelp as MH
import Mothball_Pages.OutputHelp as OH
import Mothball_Pages.OptimizationHelp as OP
import Mothball_Pages.Welcome_Page as WP
import Mothball_Pages.LearnTheBasics as LB
import Mothball_Pages.DocumentationIntro as DI
import Mothball_Pages.MovementDocumentation as MD

class MainHelpPage(tk.Frame):
    def __init__(self, master):
        # super().__init__(master)
        self.top = tk.Toplevel(master)

        self.master = master
        self.top.title("Mothball Help Page")

        self.left_frame = tk.Frame(self.top)
        self.left_frame.pack(side="left", fill="y")

        self.tree = ttk.Treeview(self.left_frame)
        
        self.tree.pack(fill='y', expand=True)

        self.right_frame = tk.Frame(self.top)
        self.right_frame.pack(side="right", expand=True, fill="both")

        self.current_page = WP.Welcome(self.right_frame)
        self.current_page_name = "learn"

        self.tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

        self.tree.insert("", "end",iid=0, text="Welcome to Mothball")
        self.tree.insert("", "end",iid=1, text="Learn the Basics")

        self.tree.insert(1, "end", iid="intro", text="Introduction")
        self.temp = I.Intro(self.right_frame, pack=False).headings

        for title, (index, depth) in self.temp.items():
            self.tree.insert("intro", "end", iid="intro " + index, text=title)
        
        self.add_to_tree(1, 'movement', 'Movement', MH.Movement)
        self.add_to_tree(1, 'outputs', 'Outputs', OH.SettersAndOutputs)
        self.add_to_tree(1, 'Optimization', 'Optimization',OP.Calculators)

        self.tree.insert("", "end",iid=2, text="Documentation")

        self.add_to_tree(2,"movementdocumentation", 'Movement', MD.MovementDocumentation)

    def add_to_tree(self, depth: int, id_name: str, display_name: str, page_object):
        last_heading = ""
        self.tree.insert(depth, "end", iid=id_name, text=display_name)
        self.temp = page_object(self.right_frame, pack=False).headings
        for title, (index, depth) in self.temp.items():
            if depth == 1:
                self.tree.insert(id_name, 'end', iid=id_name + " " + index, text=title)
                last_heading = id_name + " " + index
            elif depth == 2:
                self.tree.insert(last_heading, 'end', iid=id_name + " " + index, text=title)
            


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
            except:
                try:
                    page, index = item_id.split(" ")
                    if self.current_page_name != page:
                        self.show(page)
                    self.current_page.text.see(index)
                except:
                    self.show(item_id)

    def clear_frame(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()
    
    def show(self, page_name):
        if self.current_page_name == page_name:
            return
        self.clear_frame()
        match page_name:
            case"intro":
                self.current_page = I.Intro(self.right_frame)
            case "movement":
                self.current_page = MH.Movement(self.right_frame)
            case "outputs":
                self.current_page = OH.SettersAndOutputs(self.right_frame)
            case "optimize":
                self.current_page = OP.Calculators(self.right_frame)
            case "welcome":
                self.current_page = WP.Welcome(self.right_frame)
            case "learn":
                self.current_page = LB.Learn(self.right_frame)
            case "doc":
                self.current_page = DI.DocumentationIntro(self.right_frame)
            case "movementdocumentation":
                self.current_page = MD.MovementDocumentation(self.right_frame)
        self.current_page_name = page_name


if __name__ == "__main__":
    root = tk.Tk()
    a = MainHelpPage(root)
    tk.Button(root, text="Example Button").pack()
    # print(a.master)
    root.mainloop()