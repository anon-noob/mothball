import mothball_simulation_xz as msxz
import tkinter as tk
from tkinter import ttk
import mothball_simulation_y as msy
import json
from utils import *
from TkinterPosition import TkinterPosition
import re
import datetime
    

class Cell(tk.Frame):
    def __init__(self, parent, mode: str, options: dict, grandparent = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.width = 500
        self.mode = mode # Either "xz" or "y"
        self.FUNCTIONS_TO_TYPE = {} # Combines all of the mappings of FUNCTIONS_BY_TYPE so it maps a function ailas to the appropiate type
        self.parent = parent
        self.execution_time = None
        self.has_changed = False
        self.grandparent = grandparent
        
        if self.mode == "xz":
            self.inputs = ["w","a","s","d", "wa", "wd", "sa", "sd"]
    
            for func_type, func_aliases in msxz.Player.FUNCTIONS_BY_TYPE.items():
                for func_alias in func_aliases:
                    self.FUNCTIONS_TO_TYPE[func_alias] = func_type
        else:
            self.inputs = []
            for func_type, func_aliases in msy.Player.FUNCTIONS_BY_TYPE.items():
                for func_alias in func_aliases:
                    self.FUNCTIONS_TO_TYPE[func_alias] = func_type
        

        self._pos = TkinterPosition(1,0)

        self.configure(background="gray12", border=5)
        self.label = ttk.Label(self, text=f"Code Cell {mode.upper()}", background="gray12", foreground="white", font=("Ariel",12))
        self.label.grid(row=1, column=1, columnspan=4)
        
        self.text = tk.Text(self, state='normal', bg="gray12", fg="white", font=("Courier", 12), wrap=tk.WORD, undo=True, maxundo=-1)
        self.text.grid(row=2, column=1, columnspan=4, sticky="nsew")
        self.text.bind('<KeyPress>', lambda event: self.timed(event))
        # self.text.bind('<KeyPress>', self.timed)

        self.label2 = tk.Text(self, background="gray12", foreground="white", height = 1, font=("Courier", 12), wrap=tk.WORD)
        self.label2.insert("1.0", "Output is shown below ")
        self.label2.configure(state="disabled")
        self.label2.tag_configure("grayed", foreground="gray")
        self.label2.grid(row=3, column=1, columnspan=4, sticky="nsew")
        
        self.output = tk.Text(self, bg="gray12", fg="white", font=("Courier", 12), wrap=tk.WORD)
        self.output.insert("1.0", "Run some functions and the output will show here!")
        self.output.configure(state="disabled")
        self.output.grid(row=4, column=1, columnspan=4, sticky="nsew")

        self.raw_output = []

        self.eval_button = tk.Button(self, text="Run", command=self.evaluate, foreground="white", background="gray12")
        self.bind_hover(self.eval_button)
        self.eval_button.grid(row=5, column=1)
        self.bind_all("<Control-r>", lambda x: self.evaluate())

        self.adjust_height()        
        self.adjust_height(widget=self.output)

        self.options = options

        # Linter
        for tag_name, foreground_color in self.options["Current-theme"]["Code"].items():
            self.text.tag_configure(tag_name, foreground=foreground_color)

        for tag_name, foreground_color in self.options["Current-theme"]["Output"].items():
            self.output.tag_configure(tag_name, foreground=foreground_color)

        self.output.tag_add("placeholder", "1.0", tk.END)

        self.text.bind("<Key>", self.timed)
        self.timer = 0
        self.timer_id = None

        self.text_color_to_indexes: dict[str, list] = {
            'fast-movers': [],
            'slow-movers': [],
            'stoppers': [],
            "setters": [],
            "returners": [],
            "inputs": [],
            "calculators": [],
            "numbers": [],
            "comment": [],
            "nest-mod1": [],
            "nest-mod2": [],
            "nest-mod0": [],
            "keyword": [],
            "variable": [],
            "string": [],
            "backslash": [],
            "comment-backslash": [],
            "custom-function-parameter": [],
            "custom-function": [],
            "error": []
        }

        self.output_color_to_indexes: dict[str, list] = {
            "z-label": [],
            "x-label": [],
            "label": [],
            "warning": [],
            "text": [],
            "positive-number": [],
            "negative-number": [],
            "placeholder": []
        }

        self.text.bind("<Control-o>", lambda e: self.grandparent.load())
        self.label.bind("<Double-1>", lambda e: self.edit_cell_name())
    
    def edit_cell_name(self):
        self.label.grid_forget()
        self.entry = tk.Entry(self, background="gray12", foreground="white", font=("Ariel",12))
        old = self.label.cget("text")
        self.entry.insert(0, old)
        self.entry.grid(row=1, column=1, columnspan=4)
        self.entry.bind("<Return>", lambda e: self.set_cell_name(old, self.entry.get()))
    
    def set_cell_name(self, old_name, new_name):
        self.entry.grid_forget()
        if not new_name or new_name.isspace():
            new_name = old_name
        self.label = ttk.Label(self, text=new_name, background="gray12", foreground="white", font=("Ariel",12))
        self.label.grid(row=1, column=1, columnspan=4)
        self.label.bind("<Double-1>", lambda e: self.edit_cell_name())
        if self.grandparent: self.grandparent.has_unsaved_changes = True

    def adjust_width(self, width: int):
        self.width = width
        self.text.configure(width=width)
        self.output.configure(width=width)
        self.label2.configure(width=width)

    def adjust_height(self, event=0, widget = None):
        if not widget:
            widget = self.text
        
        widget.config(height=widget.count('1.0', 'end', 'displaylines')[0])

        self.update_idletasks() 
    
    def timed(self, event: tk.Event = 0):
        if self.timer_id is not None and event and event.keysym not in ["Control_L", "Control_R", "Shift_L", "Shift_R", "Caps_Lock", "Escape", "Down", "Up", "Left", "Right", "Alt_R", "Alt_L"]:
            self.after_cancel(self.timer_id)
        
        if event and event.keysym not in ["Control_L", "Control_R", "Shift_L", "Shift_R", "Caps_Lock", "Escape", "Down", "Up", "Left", "Right", "Alt_R", "Alt_L"]:
            self.after("idle",self.adjust_height)
            self.timer_id = self.after(250, self.colorize_code)
            if not self.has_changed:
                self.has_changed = True
                if self.grandparent: self.grandparent.has_unsaved_changes = True
                self.label2.configure(state="normal")
                self.label2.tag_add("grayed", "1.22", tk.END)
                self.label2.configure(state="disabled")
        

    def parse(self, text: str) -> list[str]:
        """
        Parses the text, separating whenever the following symbols is encountered: `(){}\\#.| \\n\\t,=+*-/:`
        
        Returning a list containing all elements
        """
        tokens = []
        follows_backslash = False
        word = ""
        for char in text:
            if follows_backslash:
                word += char
                tokens.append(word)
                word = ""
                follows_backslash = False

            elif char in "(){}\\#.| \n\t,=+*-/:":
                tokens.append(word) if word else None
                tokens.append(char)
                word = ""
                
                if char == "\\":
                    follows_backslash = True

            else:
                word += char
        
        return tokens
    
    def colorize_code(self, event=0, start_position = (1,0)):
        "Color the text, does the syntax highlighting logic"
        tokens = self.parse(self.text.get("1.0", tk.END))
        self._pos = TkinterPosition(start_position[0],start_position[1])
        self.text_color_to_indexes: dict[str, list] = {
            'fast-movers': [],
            'slow-movers': [],
            'stoppers': [],
            "setters": [],
            "returners": [],
            "inputs": [],
            "calculators": [],
            "numbers": [],
            "comment": [],
            "nest-mod1": [],
            "nest-mod2": [],
            "nest-mod0": [],
            "keyword": [],
            "variable": [],
            "string": [],
            "backslash": [],
            "comment-backslash": [],
            "custom-function-parameter": [],
            "custom-function": [],
            "error": []
        }

        self.text.tag_remove("fast-movers", "1.0", tk.END)
        self.text.tag_remove("slow-movers", "1.0", tk.END)
        self.text.tag_remove("stoppers", "1.0", tk.END)
        self.text.tag_remove("setters", "1.0", tk.END)
        self.text.tag_remove("returners", "1.0", tk.END)
        self.text.tag_remove("inputs", "1.0", tk.END)
        self.text.tag_remove("calculators", "1.0", tk.END)
        self.text.tag_remove("numbers", "1.0", tk.END)
        self.text.tag_remove("comment", "1.0", tk.END)
        self.text.tag_remove("nest-mod1", "1.0", tk.END)
        self.text.tag_remove("nest-mod2", "1.0", tk.END)
        self.text.tag_remove("nest-mod0", "1.0", tk.END)
        self.text.tag_remove("error", "1.0", tk.END)
        self.text.tag_remove("keyword", "1.0", tk.END)
        self.text.tag_remove("variable", "1.0", tk.END)
        self.text.tag_remove("string", "1.0", tk.END)
        self.text.tag_remove("backslash", "1.0", tk.END)
        self.text.tag_remove("comment-backslash", "1.0", tk.END)
        self.text.tag_remove("custom-function-parameter", "1.0", tk.END)
        self.text.tag_remove("custom-function", "1.0", tk.END)

        parenthesis_stack = ParenthesisStack()
        nest_depth = 0
        function_stack = FunctionStack()
        last_token = ""
        last_nonspace_token = ""
        last_nonspace_token_position = ("","")
        last_function = ""

        in_comment = False
        in_bracket = False
        follows_dot = False
        follows_backslash = False

        current_parameter_type = None

        if self.mode == "xz":
            defined_variables = set(msxz.Player().local_vars)
        elif self.mode == 'y':
            defined_variables = set(msy.Player().local_vars)

        defined_functions = set()
        local_variables_stack = []
        inside_main_function = False
        inner_function_stack = []



        for token in tokens:
            # if function_stack.peek():
            #     print(f"{function_stack.peek().name}, current: {function_stack.peek().current_parameter}")
            # else:
            #     print('EMPTY')

            if token == "\\":
                follows_backslash = True
                if in_comment:
                    self.apply_tag(token, "comment-backslash")
                elif not in_comment:
                    self.apply_tag(token, "backslash")

            elif in_comment or (not in_comment and token == "#"):
                if (follows_backslash and token in "(){},\\#"):
                    self.apply_tag(token, "comment-backslash")
                else:
                    if token == "\n":
                        self._pos = self._pos.add_row(1).reset_column()
                    elif token == "#":
                        in_comment = not in_comment
                    self.apply_tag(token, "comment")

            elif follows_backslash and token in "\#(),{}=:":
                self.apply_tag(token, "backslash")
            
            elif current_parameter_type == str and (not isinstance(function_stack.peek().current_parameter, str) and function_stack.peek().current_parameter.name == "variable_name") and token != ",":
            # elif current_parameter_type == str and nest_depth and function_stack.peek().current_parameter.name == "variable_name") and token != ",":
                self.apply_tag(token, "variable")
                defined_variables.add(token)
            
            elif current_parameter_type == str and function_stack.peek_function_name() == "function" and function_stack.peek().current_parameter.name == "name" and token not in "(),\\{}=":
                self.apply_tag(token, "custom-function")
                if local_variables_stack:
                    local_variables_stack.append(local_variables_stack[-1].union(set()))
                else:
                    local_variables_stack.append(set())
                
                if not inside_main_function:
                    inside_main_function = True
                    defined_functions.add(token)
                elif inside_main_function:
                    inner_function_stack.append(token)
                
            elif current_parameter_type == str and not token.isspace() and function_stack.peek_function_name() == "function" and function_stack.peek().current_parameter.name == 'args' and token not in "(),\\{}=":
                self.apply_tag(token, "custom-function-parameter")
                local_variables_stack[-1].add(token)

            elif current_parameter_type == str and token not in "(),\\{}=" and not in_bracket and function_stack.peek().current_parameter.name not in ['sequence', 'value','code', 'func']:
                self.apply_tag(token, "string")
                if token == "\n":
                    self._pos = self._pos.add_row(1).reset_column()
            
            elif local_variables_stack and token in local_variables_stack[-1]:
                self.apply_tag(token, "custom-function-parameter")
                
            # elif token in defined_variables and ((function_stack.is_empty() and token not in defined_functions) or (function_stack.peek().current_parameter and function_stack.peek().current_parameter.name not in ["sequence"])): # PLEASE CHECK LOGIC !
            # elif token in defined_variables and ((function_stack.is_empty() and token not in defined_functions) or (function_stack.peek().current_parameter and function_stack.peek().current_parameter.name not in ["sequence"])): # PLEASE CHECK LOGIC !
            elif token in defined_variables and nest_depth and (function_stack.is_empty() or (function_stack.peek().current_parameter and function_stack.peek().current_parameter.name not in ["sequence"])): # PLEASE CHECK LOGIC !
            # elif token in defined_variables and nest_depth and (function_stack.peek().current_parameter and function_stack.peek().current_parameter.name not in ["sequence"]): # PLEASE CHECK LOGIC !
                # print(function_stack.peek().current_parameter.name, function_stack.peek().current_parameter.name == "sequence")
                self.apply_tag(token, "variable")

            else:
                func_tag = self.get_tag_from_string(token, defined_functions.union(set(inner_function_stack)))
                if follows_dot and token in self.inputs:
                    self.apply_tag(token, "inputs")

                elif func_tag is not None:
                    self.apply_tag(token, func_tag)
                    last_function = token
                
                elif token in "({":
                    parenthesis_stack.push(self._pos.string, token)
                    self.apply_tag(token, "error")
                    nest_depth += 1

                    if token == "(" and not last_token.isspace() and last_function:
                        try: 
                            if self.mode == "xz":
                                function_stack.push(msxz.Player.FUNCTIONS[last_function])
                            elif self.mode == "y":
                                function_stack.push(msy.Player.FUNCTIONS[last_function])
                            current_parameter_type = function_stack.peek_current_parameter_annotation()
                        except KeyError:
                            function_stack.push(last_function)
                            current_parameter_type = function_stack.peek_current_parameter_annotation()

                    elif token == "{":
                        in_bracket = not in_bracket

                elif token in ")}":
                    if parenthesis_stack.matches_parenthesis_stack(token):
                        self.apply_tag(token, f"nest-mod{nest_depth % 3}")
                        position = parenthesis_stack.pop()[0]
                        self.text.tag_remove("error", position[0], position[1])
                        self.text_color_to_indexes["error"].remove((position[0],position[1]))
                        self.text_color_to_indexes[f"nest-mod{nest_depth % 3}"].append((position[0],position[1]))
                        self.text.tag_add(f"nest-mod{nest_depth % 3}", position[0], position[1])
                        nest_depth -= 1

                        if token == ")":
                            a = function_stack.pop()
                            if not function_stack.is_empty():
                                current_parameter_type = function_stack.peek_current_parameter_annotation()
                            else:
                                current_parameter_type = None
                            if a is not None and a.name == "function" and local_variables_stack:
                                # print(local_variables_stack)
                                local_variables_stack.pop()

                                # if len(inner_function_stack) == 1:
                                #     inside_main_function = False
                                # else:
                                #     inner_function_stack.pop()
                        
                        elif token == "}":
                            in_bracket = not in_bracket
                            
                    else:
                        self.apply_tag(token, "error")

                elif token == ",":
                    if not function_stack.is_empty() and not function_stack.peek_after_keyword(): # positional
                        function_stack.peek_next_positional_parameter()
                        current_parameter_type = function_stack.peek_current_parameter_annotation()
                    
                    self.apply_tag(token, "none")
                
                elif token == "=":
                    if not function_stack.is_empty() and last_nonspace_token in function_stack.peek_remaining_keywords():
                        self.text.tag_remove("string", last_nonspace_token_position[0].string, last_nonspace_token_position[1].string)
                        self.text.tag_remove("setters", last_nonspace_token_position[0].string, last_nonspace_token_position[1].string)
                        self.text.tag_remove("custom-function-parameter", last_nonspace_token_position[0].string, last_nonspace_token_position[1].string)

                        try:
                            self.text_color_to_indexes['string'].remove((last_nonspace_token_position[0].string, last_nonspace_token_position[1].string))
                        except ValueError:
                            try:
                                self.text_color_to_indexes['setters'].remove((last_nonspace_token_position[0].string, last_nonspace_token_position[1].string))
                            except ValueError:
                                try:
                                    self.text_color_to_indexes['custom-function-parameter'].remove((last_nonspace_token_position[0].string, last_nonspace_token_position[1].string))
                                except ValueError:
                                    pass
                        
                        self.text_color_to_indexes['keyword'].append((last_nonspace_token_position[0].string, last_nonspace_token_position[1].string))

                        self.text.tag_add("keyword", last_nonspace_token_position[0].string, last_nonspace_token_position[1].string)
                        current_parameter_type = function_stack.peek_get_keyword_type(last_nonspace_token)
                        function_stack.peek_remove_keyword(last_nonspace_token)
                    
                        if function_stack.peek_function_name() == "function":
                            local_variables_stack[-1].remove(last_nonspace_token)
                    
                    self.apply_tag(token, "none")
                
                elif token == ".":
                    if follows_dot:
                        self.apply_tag(token, "error")
                    elif last_nonspace_token.isnumeric():
                        self.apply_tag(token, "numbers")
                    else:
                        self.apply_tag(token, "none")
                    follows_dot = True

                elif token.isnumeric():
                    self.apply_tag(token, "numbers")
                    if follows_dot:
                        # self.text.tag_remove(tk.ALL, last_nonspace_token_position[0].string, last_nonspace_token_position[1].string)
                        self.text.tag_add("numbers", last_nonspace_token_position[0].string, last_nonspace_token_position[1].string)
                else:
                    last_function = ""
                    if token == "\n":
                        self._pos = self._pos.add_row(1).reset_column()
                    else:
                        self._pos = self._pos + len(token)
            
            last_token = token
            if not token.isspace():
                last_nonspace_token = token
                last_nonspace_token_position = (self._pos - len(last_nonspace_token),self._pos)
            if token != ".":
                follows_dot = False
            if token != "\\":
                follows_backslash = False
        
        
    def apply_tag(self, item: str, tag: str):
        new_pos = self._pos + len(item)
        self.text.tag_add(tag, self._pos.string, new_pos.string)
        try:
            self.text_color_to_indexes[tag].append((self._pos.string, new_pos.string))
        except KeyError:
            pass
        self._pos = self._pos + len(item)
    
    def get_tag_from_string(self, string: str, local_functions):
        a = self.FUNCTIONS_TO_TYPE.get(string)
        if a is not None:
            return a
        else:
            if string in local_functions:
                return "custom-function"
    
    def evaluate(self, start_row = 1):
        "Runs the simulation"
        self.output_color_to_indexes: dict[str, list] = {
            "z-label": [],
            "x-label": [],
            "label": [],
            "warning": [],
            "text": [],
            "positive-number": [],
            "negative-number": [],
            "placeholder": []
        }

        string = self.text.get("1.0", tk.END)
        if self.mode == "xz":
            player = msxz.Player()
        elif self.mode == "y":
            player = msy.Player()
        
        try:
            player.simulate(string)
            self.raw_output = player.output
            self.colorize_output(start_row=start_row)
        except BaseException as e:
            self.output.configure(state="normal")
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", f"Error: {e}")
            self.adjust_height(widget=self.output)
            self.output.configure(state="disabled")
            self.raw_output = [(f"Error: {e}","None")]
        
        if self.grandparent: self.grandparent.has_unsaved_changes = True
        self.execution_time = datetime.datetime.now().replace(microsecond=0)
        self.has_changed = False
        self.label2.configure(state="normal")
        self.label2.delete("1.0", tk.END)
        self.label2.tag_remove("grayed", "1.0", tk.END)
        self.label2.insert(tk.END, f"Output is shown below (Executed at {str(self.execution_time)})")
        self.label2.configure(state="disabled")

        
    
    def colorize_output(self, start_row = 1):
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)

        row_index = start_row
        column_index = 0

        for line in self.raw_output:
            column_index = 0
            
            # for string, tag_name in line:
            string, expr_type = line
            if expr_type == "normal":
                string = re.split(r"(\n)", string)
                string = [(s, "text") for s in string]
            else:
                string = self.separate(string, expr_type)


            for string_to_insert, tag_name in string:
                
                self.output.insert(f"{row_index}.{column_index}", string_to_insert)
                if string_to_insert == "\n":
                    row_index += 1
                    column_index = 0
                else:
                    self.output.tag_add(tag_name, f"{row_index}.{column_index}", f"{row_index}.{column_index+len(string_to_insert)}")
                    if tag_name and tag_name != "none":
                        # print(f"tagname {tag_name}")
                        self.output_color_to_indexes[tag_name].append((f"{row_index}.{column_index}", f"{row_index}.{column_index+len(string_to_insert)}"))
                    column_index += len(string_to_insert)

            self.output.insert(f"{row_index}.{column_index}", "\n")
            row_index += 1

        self.output.delete(f"{row_index}.{column_index}", tk.END) # Delete last whitespace
        self.output.configure(state="disabled") 
        self.adjust_height(widget=self.output)

    def separate(self, string: str, expr_type: str):
        """
        Internal function.
        
        Separates strings in the form `label: a` or `label: a + b` into a list `[label, :, a, +, b]` 
        """
        result: list[tuple[str, str]] = []

        expr_type_to_tag_name = {
            "expr": "label",
            "x-expr": "x-label",
            "z-expr": "z-label",
            "warning": "warning"
        }

        a, b = string.split(": ")
        tag_name = expr_type_to_tag_name.get(expr_type)
        if tag_name is None:
            return [(string, "none")]
        result.append((a, tag_name))
        result.append((": ", ""))

        if expr_type == "warning":
            result.append((b, "text"))
            return result
        
        b = b.split(" ")
         
        # Either 1 or 3 items
        b_float = float(b[0])
        if b_float >= 0: # positive number
            result.append((b[0], "positive-number"))
        else: # Negative number
            result.append(('-', ""))
            result.append((b[0][1:], "negative-number"))

        if len(b) == 3:
            sign = b[1]
            number = b[2]
            result.append((f" {sign} ", ""))
            result.append((number, f"{'positive' if sign == '+' else 'negative'}-number"))
        
        return result
    
    def bind_hover(self, button: tk.Button):
        button.bind("<Enter>", func=lambda e: self.on_hover(button))
        button.bind("<Leave>", func=lambda e: self.off_hover(button))

    def on_hover(self, button: tk.Button):
        button.configure(background="DeepSkyBlue4")

    def off_hover(self, button: tk.Button):
        button.configure(background="gray12")


if __name__ == "__main__":
    with open("Mothball Settings/Options.json") as f:
        options = json.load(f)
    r = tk.Tk()
    a = Cell(r, "xz", options) # Test
    a.grid(row=0, column=0, sticky="nswe")
    r.grid_rowconfigure(0, weight=1)
    r.grid_columnconfigure(0, weight=1)
    r.mainloop()
