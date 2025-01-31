import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import json
import webbrowser
import inspect
import re
import sys, os
import FileHandler

folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(folder_path)

from TkinterPosition import TkinterPosition
from CodeCell import Cell
import mothball_simulation_xz as xz, mothball_simulation_y as y

class Page(tk.Frame):
    def __init__(self, master=None, pack=True):
        super().__init__(master)

        self.text = ScrolledText(master)
        self.text.configure(background="gray15", foreground="white", font=("Times new roman", 14), wrap=tk.WORD, spacing1=1, spacing3=1)
        if pack:
            self.text.pack(fill=tk.BOTH, expand=True)

        self.pos = TkinterPosition(1,0)

        options = FileHandler.get_options()

        for tag_name, foreground_color in options["Current-theme"]["Code"].items():
            self.text.tag_configure(tag_name, foreground=foreground_color)

        for tag_name, foreground_color in options["Current-theme"]["Output"].items():
            self.text.tag_configure(tag_name, foreground=foreground_color)
        
        self.text.tag_configure("code", background="gray12", font=("Courier", 12))
        self.text.tag_configure("inline code", font=("Courier", 12))
        self.text.tag_configure("header", font=('Ariel', 20), foreground="light blue")
        self.text.tag_configure("header2", font=('Ariel', 16), foreground="light blue")
        
        self.CodeCell = Cell(None, "xz", options)

        self.headings = {} # Name: (index, depth)

    def reset_code_processor(self):
        self.CodeCell.text.delete("1.0", tk.END)
    
    def insert_text(self, content: str):
        # print("TEXT", content, self.pos)
        self.text.insert(tk.END, content)            
        if "\n" in content:
            index = content.rindex("\n")

            self.pos = self.pos.add_row(content.count("\n")).reset_column() + (len(content) - index - 1)
        else:
            self.pos += len(content)
        # print("TEXT", self.pos)
    
    def heading(self, title: str):
        self.headings[title] = (self.pos.string, 1)
        self.text.insert(tk.END, title + "\n")
        self.text.tag_add("header", self.pos.string, (self.pos + len(title)).string)
        self.pos = self.pos.add_row(1).reset_column()
    
    def heading2(self, title: str):
        self.headings[title] = (self.pos.string, 2)
        self.text.insert(tk.END, title + "\n")
        self.text.tag_add("header2", self.pos.string, (self.pos + len(title)).string)
        self.pos = self.pos.add_row(1).reset_column()
    

    
    def link(self, link: str):
        self.text.insert(tk.END, link)
        self.text.tag_configure(f"link {link}", foreground="light blue", underline=True)
        self.text.tag_add(f"link {link}", self.pos.string, (self.pos + len(link)).string)
        self.text.tag_bind(f"link {link}", "<Button-1>", func=lambda e: webbrowser.open_new(link))
        self.pos += len(link)
    
    def inline_code(self, code: str):
        # print(self.pos)
        self.reset_code_processor()
        self.text.insert(tk.END, code)

        self.CodeCell.text.insert("1.0", code)
        self.CodeCell.colorize_code()

        for tag, pairs in self.CodeCell.text_color_to_indexes.items():
            l = []
            for pair in pairs:
                begin, end = pair
                begin = self.string_to_position(begin).add_row(self.pos.row-1) + self.pos.column
                end = self.string_to_position(end).add_row(self.pos.row-1) + self.pos.column
                l.append(begin.string)
                l.append(end.string)
            if l:
                # print(l)
                self.text.tag_add(tag, *l)
        # print(code, "\n")

        new_pos = self.pos + len(code)
        
        self.text.tag_add("inline code", self.pos.string, new_pos.string)
        # print("POSITIONS", self.pos.string, new_pos.string)
        self.pos = new_pos

        
    def code_snippet(self, code: str):
        self.reset_code_processor()
        code = code + "\n"
        self.text.insert(tk.END, code)

        self.CodeCell.text.insert("1.0", code)
        self.CodeCell.colorize_code()

        for tag, pairs in self.CodeCell.text_color_to_indexes.items():
            l = []
            for pair in pairs:
                begin, end = pair
                begin = self.string_to_position(begin).add_row(self.pos.row-1) + self.pos.column
                end = self.string_to_position(end).add_row(self.pos.row-1) + self.pos.column
                l.append(begin.string)
                l.append(end.string)
            if l:
                self.text.tag_add(tag, *l)

        if "\n" in code:
            index = code.rindex("\n")

            new_pos = self.pos.add_row(code.count("\n")).reset_column() + (len(code) - index - 1)
        else:
            new_pos = self.pos + len(code)
        
        self.text.tag_add("code", self.pos.string, new_pos.string)
        self.pos = new_pos

    def code_snippet_with_output(self, code: str):
        self.reset_code_processor()
        code = code + "\n"
        self.text.insert(tk.END, code + "-----------------------------\n")
        self.CodeCell.text.insert("1.0", code)
        self.CodeCell.colorize_code()

        for tag, pairs in self.CodeCell.text_color_to_indexes.items():
            l = []
            for pair in pairs:
                begin, end = pair
                begin = self.string_to_position(begin).add_row(self.pos.row-1) + self.pos.column
                end = self.string_to_position(end).add_row(self.pos.row-1) + self.pos.column
                l.append(begin.string)
                l.append(end.string)
            if l:
                self.text.tag_add(tag, *l)

        # self.text.insert(tk.END, "Output\n")
        code += "-----------------------------\n"
        new_pos = self.pos.add_row(code.count("\n")).reset_column()

        self.text.tag_add("code", self.pos.string, new_pos.string)
        self.pos = new_pos

        self.CodeCell.evaluate()
        output = self.CodeCell.output.get("1.0", tk.END)
        self.text.insert(tk.END, output)

        for tag, pairs in self.CodeCell.output_color_to_indexes.items():
            l = []
            for pair in pairs:
                begin, end = pair
                begin = self.string_to_position(begin).add_row(self.pos.row-1) + self.pos.column
                end = self.string_to_position(end).add_row(self.pos.row-1) + self.pos.column
                l.append(begin.string)
                l.append(end.string)
            if l:
                self.text.tag_add(tag, *l)

        new_pos = self.pos.add_row(output.count("\n")).reset_column()
        self.text.tag_add("code", self.pos.string, new_pos.string)
        self.pos = new_pos

    def string_to_position(self, string: str):
        a,b = string.split('.')
        a = int(a)
        b = int(b)
        return TkinterPosition(a,b)

    def show_function_signature(self, func: str, module = "xz"):
        if module == "xz":
            f = xz.Player.FUNCTIONS[func]
            params = inspect.signature(f).__repr__()
        elif module == "y":
            f = y.Player.FUNCTIONS[func]
            params = inspect.signature(f).__repr__()
        params = params.removeprefix("<Signature (").removesuffix(")>").split(", ")
        if 'self' in params:
            params.remove('self')

        l = []

        regex = r"(\*?\w+)(?:: ([\w\.]+))?(?: = (\w+))?"
        for p in params:
            x = re.findall(regex,p)
            if x:
                l.append(x[0])
            elif p in "/*":
                l.append(p)
        
        self.colorize(f.__name__, l, module)
    
    def colorize(self, func: str, args, module):

        tag = self.CodeCell.get_tag_from_string(func, [])
        old_pos = self.pos

        if module == "xz":
            all_aliases = [x for x,y in xz.Player.FUNCTIONS.items() if y.__name__ == func and x != func]
        elif module == "y":
            all_aliases = [x for x,y in y.Player.FUNCTIONS.items() if y.__name__ == func and x != func]
        
        if all_aliases:
            self.insert_and_apply_tag("Aliases: ", "backslash")
            self.insert_and_apply_tag(" ".join(all_aliases), tag)
            self.text.insert(tk.END, "\n")
            self.pos = self.pos.add_row(1).reset_column()


        self.insert_and_apply_tag(func, tag)
        self.insert_and_apply_tag("(", "nest-mod1")

        for arg in args:
            if isinstance(arg, tuple):
                arg_name, datatype, default = arg
                if datatype == "numpy.float32":
                    datatype = "float"

                self.insert_and_apply_tag(arg_name, "custom-function-parameter")
                
                if datatype:
                    self.insert_and_apply_tag(": ", "none")

                    self.insert_and_apply_tag(datatype, "inputs")
                
                if default:
                    self.insert_and_apply_tag(" = ", "none")

                    if default == "None":
                        self.insert_and_apply_tag(default, "comment")
                    elif default.isnumeric():
                        self.insert_and_apply_tag(default, "numbers")
                    else:
                        self.insert_and_apply_tag(default, "string")

            else:
                self.insert_and_apply_tag(arg, "setters")
        
            self.insert_and_apply_tag(", ", "none")

        self.pos -= 2
        self.text.delete(self.pos.string, tk.END)
        self.insert_and_apply_tag(")", "nest-mod1")

        self.text.insert(tk.END, "\n")
        self.pos = self.pos.add_row(1).reset_column()

        self.text.tag_add("code", old_pos.string, self.pos.string)

    def insert_and_apply_tag(self, text, tag):
        self.text.insert(tk.END, text)
        self.text.tag_add(tag, self.pos.string, (self.pos+len(text)).string)
        self.pos += len(text)
    
    def finalize(self):
        self.text.configure(state="disabled")

if __name__ == "__main__":
    r = tk.Tk()
    a = Page()
    a.heading("A New Beginning")
    a.insert_text("Hello world, and this is my code!\n")
    a.code_snippet_with_output("print(Hello world\, let's KAKU IT!)\nf(7) w.d(2) s.wd(4)")
    a.insert_text("And now, we say this\n\n")
    a.show_function_signature('s')
    a.insert_text("Got it?\n")
    a.heading2("Another example")
    a.show_function_signature('outvz')
    r.mainloop()