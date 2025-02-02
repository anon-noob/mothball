import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import json
import webbrowser
import inspect
import re
import sys, os

folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(folder_path)

from TkinterPosition import TkinterPosition
from CodeCell import Cell
import mothball_simulation_xz as xz, mothball_simulation_y as y
import FileHandler
options = FileHandler.get_options()

class Page(tk.Frame):
    def __init__(self, master=None, pack=True):
        super().__init__(master)

        self.text = ScrolledText(master, padx=5)
        self.text.configure(background="gray15", foreground="white", font=("Times new roman", 14), wrap=tk.WORD, spacing1=1, spacing3=1)
        if pack:
            self.text.pack(fill=tk.BOTH, expand=True)

        self.pos = TkinterPosition(1,0)
        self.matches = []

        for tag_name, foreground_color in options["Current-theme"]["Code"].items():
            self.text.tag_configure(tag_name, foreground=foreground_color)

        for tag_name, foreground_color in options["Current-theme"]["Output"].items():
            self.text.tag_configure(tag_name, foreground=foreground_color)
        
        self.text.tag_configure("code", background="gray12", font=("Courier", 12), borderwidth=1, relief="solid", border=1, lmargin1=5, lmargin2=5, rmargin=5)
        self.text.tag_configure("inline code", font=("Courier", 12))
        self.text.tag_configure("header", font=('Ariel', 20), foreground="light blue")
        self.text.tag_configure("header2", font=('Ariel', 16), foreground="light blue")
        self.text.tag_configure('highlight', background='yellow', foreground="black")
        self.text.tag_configure('current_highlight', background='orange', foreground="black")
        
        self.CodeCell = Cell(None, "xz", options)

        self.headings = {} # Name: (index, depth)
        self.text.bind("<Control-f>", self.open_search_widget)

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
    
    def open_search_widget(self, event=None):
        if hasattr(self, 'search_frame'):
            self.search_frame.lift()
            self.search_text(self.search_entry.get())
            self.search_entry.focus_set()
            return

        self.search_frame = tk.Frame(self.master, background="gray15", borderwidth=1, border=2, relief="solid")
        self.search_frame.place(relx=0.97, rely=0.01, anchor='ne')
        self.search_label = tk.Label(self.search_frame, text="Search:", background="gray15", foreground="white")
        self.search_label.grid(row=0, column=0)
        self.search_entry = tk.Entry(self.search_frame, background="gray15", foreground="white", border=0)
        self.search_entry.grid(row=0, column=1, columnspan=3)
        self.found_label = tk.Label(self.search_frame, text="Found",background="gray15", foreground="white")
        self.found_label.grid(row=1, column=0)
        self.results = tk.Label(self.search_frame, text="Found", background="gray15", foreground="white")
        self.results.grid(row=1, column=1, columnspan=3)
        self.nocase_search = tk.Button(self.search_frame, text="Aa", command=self.toggle_case, background="gray15", foreground="white")
        self.nocase_search.grid(row=2, column=0)
        self.search_frame.nocase = False
        
        self.up = tk.Button(self.search_frame, text="↑", background="gray15", foreground="white", command=lambda: self.next_match(-1))
        self.up.grid(row=2, column=1)

        self.down = tk.Button(self.search_frame, text="↓", background="gray15", foreground="white", command=lambda: self.next_match(1))
        self.down.grid(row=2, column=2)

        self.leave = tk.Button(self.search_frame, text="✖", background="gray15", foreground="white", command=lambda: self.hide_search_widget())
        self.leave.grid(row=2, column=3)

        self.search_entry.bind('<Key>', self.timer)
        self.text.bind('<Key>', self.hide_search_widget)
        self.search_entry.focus_set()
    
    def toggle_case(self):
        self.search_frame.nocase = not self.search_frame.nocase
        if self.search_frame.nocase:
            self.nocase_search.configure(background="green")
        else:
            self.nocase_search.configure(background="gray15")
        search_term = self.search_entry.get()
        self.search_text(search_term)

    def hide_search_widget(self, event: tk.Event = None):
        if not event or event.keysym == "Escape":
            self.search_text("")
            self.search_frame.lower()
            self.text.lift()
            self.text.focus_set()

    def timer(self, event):
        self.after(1, lambda: self.on_key_press(event))

    def on_key_press(self, event: tk.Event=None):
        if event.keysym == "Escape":
            self.hide_search_widget(event)
        elif event.keysym == "Return" or event.keysym == "Down":
            self.next_match()
        elif event.keysym == "Up":
            self.next_match(-1)
        else:
            search_term = self.search_entry.get()
            self.search_text(search_term)

    def search_text(self, search_term):
        self.text.tag_remove("current_highlight", "1.0", tk.END)
        self.text.tag_remove('highlight', '1.0', tk.END)
        self.search_frame.i = 0

        if search_term:
            self.matches = []
            start_pos = '1.0'
            while True:
                start_pos = self.text.search(search_term, start_pos, stopindex=tk.END, nocase=self.search_frame.nocase)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(search_term)}c"
                self.text.tag_add('highlight', start_pos, end_pos)
                self.matches.append((start_pos, end_pos))
                start_pos = end_pos
            
            if self.matches:
                self.text.tag_remove('highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
                self.text.tag_add('current_highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
                self.text.see(self.matches[self.search_frame.i][0])
                self.results.configure(text=f"{self.search_frame.i + 1} of {len(self.matches)}")

            else:
                self.results.configure(text=f"0 of 0")
        else:
            self.results.configure(text=f"0 of 0")

    
    def next_match(self, index_shift=1):
        if self.matches:
            self.text.tag_add('highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
            self.text.tag_remove('current_highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
            self.search_frame.i = (self.search_frame.i + index_shift) % len(self.matches)
            self.text.tag_remove('highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
            self.text.tag_add('current_highlight', self.matches[self.search_frame.i][0], self.matches[self.search_frame.i][1])
            self.text.see(self.matches[self.search_frame.i][0])
            self.results.configure(text=f"{self.search_frame.i + 1} of {len(self.matches)}")
    
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
                self.text.tag_add(tag, *l)

        new_pos = self.pos + len(code)
        
        self.text.tag_add("inline code", self.pos.string, new_pos.string)
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
