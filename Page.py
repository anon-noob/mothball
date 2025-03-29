import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import webbrowser
import inspect
import re
import os
import sys
from PIL import Image, ImageTk
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
        self.text.bind("<Configure>", self.resize_image_on_resize)

        self.tags = []

        self.images: dict[str, tuple[str, ImageTk.PhotoImage]] = {} # string is a path to source

        for tag_name, foreground_color in options["Current-theme"]["Code"].items():
            self.text.tag_configure(tag_name, foreground=foreground_color)
            self.tags.append(tag_name)

        for tag_name, foreground_color in options["Current-theme"]["Output"].items():
            self.text.tag_configure(tag_name, foreground=foreground_color)
            self.tags.append(tag_name)
        
        self.text.tag_configure("code", background="gray12", font=("Courier", 12), borderwidth=1, relief="solid", border=1, lmargin1=5, lmargin2=5, rmargin=5)
        self.text.tag_configure("inline code", font=("Courier", 12))
        self.text.tag_configure("header", font=('Ariel', 20), foreground="light blue")
        self.text.tag_configure("header2", font=('Ariel', 17), foreground="light blue")
        self.text.tag_configure("header3", font=('Ariel', 15), foreground="light blue")
        self.text.tag_configure('highlight', background='yellow', foreground="black")
        self.text.tag_configure('current_highlight', background='orange', foreground="black")
        
        self.tags += ["code", "inline code", "header", "header2", "header3", "highlight", "current_highlight"]
        self.CodeCell = Cell(None, "xz", options)

        self.headings = {} # Name: (index, depth)
        self.text.bind("<Control-f>", self.open_search_widget)

    def reset_code_processor(self):
        self.CodeCell.text.delete("1.0", tk.END)
    
    def insert_text(self, content: str):
        # print("TEXT", content, self.pos)
        self.text.insert(tk.END, content)            
        if "\n" in content:
            self.pos = self.pos.add_row(content.count("\n")).reset_column() + (len(content) - content.rindex("\n") - 1)
        else:
            self.pos += len(content)
        # print("AFTER TEXT", self.pos)
    
    def heading(self, title: str):
        self.text.insert(tk.END, title)
        self.text.tag_add("header", self.pos.string, (self.pos + len(title)).string)
        self.pos = self.pos.add_row(1).reset_column()
    
    def heading2(self, title: str):
        self.text.insert(tk.END, title)
        self.text.tag_add("header2", self.pos.string, (self.pos + len(title)).string)
        self.pos = self.pos.add_row(1).reset_column()

    def heading3(self, title: str):
        self.text.insert(tk.END, title)
        self.text.tag_add("header3", self.pos.string, (self.pos + len(title)).string)
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
    
    def link(self, link: str, display: str):
        if link.endswith(".png") or link.endswith(".jpg"):
            try:
                # Determine the correct path for the image
                if getattr(sys, "frozen", False):
                    base_path = sys._MEIPASS  # Path for PyInstaller executable
                else:
                    base_path = os.getcwd()  # Path for script execution

                image_path = os.path.join(base_path, "images", link)
                image = Image.open(image_path)

                text_width = self.text.winfo_width()
                img_width, img_height = image.size
                new_width = text_width
                new_height = int(img_height * (new_width / img_width))
                photo = ImageTk.PhotoImage(image)

                self.images[self.pos] = (image_path, photo)
                self.text.image_create(tk.END, image=photo)

            except Exception as e:
                self.insert_text(display)
            
        else:
            self.text.insert(tk.END, display)
            self.text.tag_configure(f"link {link}", foreground="light blue", underline=True)
            self.text.tag_add(f"link {link}", self.pos.string, (self.pos + len(display)).string)
            self.text.tag_bind(f"link {link}", "<Button-1>", func=lambda e: webbrowser.open_new(link))
            self.pos += len(display)
    
    def inline_code(self, code: str):
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
        # print("CODE", code, self.pos)
        code = code + "\n"
        # code = code 
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
        # print("OLD", old_pos)

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

    def parse_text(self, text):
        # Regex to match different components in the markdown
        pattern = r'([#]+ .+?\n)|(```.*?```\n)|(`.*?`)|(\[.*?\]\(.*?\))|([^#`\[\]]+)'

        # TEMPORARY FIX: ([^#\[\]`]+) ignores brackets
        
        # Find all the components using regex
        components = re.findall(pattern, text, re.DOTALL)

        # Extract the non-empty matches
        result = [match[0] or match[1] or match[2] or match[3] or match[4] for match in components]
        
        for text in result:
            # print("TEXT:", repr(text))
            self.process_text(text)
            # print("NEW POS:", self.pos)

        self.text.event_generate("<Configure>")
            
    def process_text(self, text: str):
        if text.startswith("# "):
            self.heading(text[2:])
        elif text.startswith("## "):
            self.heading2(text[3:])
        elif text.startswith("### "):
            self.heading3(text[4:])
        
        elif text.startswith("`") and text.endswith("`"):
            self.inline_code(text.strip("`"))
        elif text.startswith("```") and text.endswith("```\n"):
            args = ""
            for i in text[3:]:
                if i == "\n":
                    break
                args += i

            t = text[4+len(args):len(text)-5]
            args = args.split("/")
            # print(args, t)
            # should be args[0] = mothball
            if "output" in args:
                self.code_snippet_with_output(t)
            elif "signature" in args:
                if "y" in args:
                    self.show_function_signature(t, "y")
                else:
                    self.show_function_signature(t, "xz")
            else:
                self.code_snippet(t)

        elif text.startswith("[") and text.endswith(")") and "](" in text:
            display = text[1:text.index("]")]
            link = text[text.index("(")+1:len(text)-1]
            self.link(link, display)
        else:
            self.insert_text(text)
    
    @staticmethod
    def get_headings(text: str):
        lines = text.split("\n")
        headings = {}
        in_code = False
        pos = TkinterPosition(1,0)
        for line in lines:
            if line.startswith("```"):
                in_code = not in_code
            elif not in_code:
                if line.startswith("# "):
                    headings[line[2:]] = (pos.string, 1)
                elif line.startswith("## "):
                    headings[line[3:]] = (pos.string, 2)
                elif line.startswith("### "):
                    headings[line[4:]] = (pos.string, 3)
            pos = pos.add_row(1)
        
        return headings

    def resize_image_on_resize(self, event):
        for index, (src, img) in self.images.items():
            image = Image.open(src)

            img_width, img_height = image.size
            new_width = self.text.winfo_width()
            new_height = int(img_height * (new_width / img_width))

            image = image.resize((new_width, new_height), Image.LANCZOS)
            image = ImageTk.PhotoImage(image)
            old_image = self.images[index][1]
            self.images[index] = (src, image)
            del old_image
            self.text.image_configure(index, image=image)
        


if __name__ == "__main__":
    r = tk.Tk()
    a = Page()

    a.parse_text("""# If you see this...
Just know that you're amazing!

```mothball
Hope all goes well!
```
""")
    print(a.tags)
    r.mainloop()

