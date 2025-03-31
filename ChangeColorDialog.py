import tkinter as tk
from CodeCell import Cell
import json
from tkinter import colorchooser
import FileHandler

# REWRITE TIME

class ChangeColorDialog:
    default_text = """version(1.21) 
sprint(8, slow=3) sprintair.wd walk.s water(3) stop stopair
outx(0.03125, label=hey I'm an x axis output) vec
wall(1.8125, repeat(sprintjump.wa(4), 2)) zb(2.2, z output)
var(new_var, 37) print(new_var: {new_var})
print(help\, its been 4 years) # comments are \# cool #
func(hello, param, code=print(hello {param} {new_var} times))
hello(mothballer)
"""
    def __init__(self, main_frame, options):
        self.main_frame = main_frame
        self.top = tk.Toplevel()
        self.top.option_add("*Button*Background", "gray12")
        self.top.option_add("*Button*Foreground", "White")
        self.top.option_add("*Label*Background", "gray12")
        self.top.option_add("*Label*Foreground", "White")
        self.top.configure(bg="gray12")
        self.top.title("Change Colors")
        tk.Label(self.top, text="Change Code Colors").grid(row=0, column=0)
        tk.Label(self.top, text="Change Output Colors").grid(row=0, column=4)
        self.side_display = Cell(self.top, 'xz', options)
        self.side_display.configure(width=100)
        self.side_display.grid(row=1, column=2, rowspan=20)
        self.side_display.eval_button.destroy()
        self.side_display.add_cell.destroy()
        self.side_display.add_cell_y.destroy()
        self.side_display.delete_cell.destroy()
        self.side_display.title_frame.destroy()
        self.side_display.text.insert("1.0", ChangeColorDialog.default_text)
        self.side_display.evaluate()
        self.side_display.text.configure(width=60)
        self.side_display.label2.configure(width=60)
        self.side_display.output.configure(width=60)
        self.side_display.text.insert(tk.END, "# parenthesis # (( { ( {{}} ) } ))\n( 4..5 #ERRORS#")
        self.side_display.colorize_code()
        self.side_display.adjust_height()
        self.side_display.adjust_height(self.side_display.output)
        self.side_display.text.configure(state="disabled")
        self.side_display.text.tag_configure("bold", background="gray")
        self.side_display.output.tag_configure("bold", background="gray")
        self.side_display.label2.configure(state="normal")
        self.side_display.label2.delete("1.0", tk.END)
        self.side_display.label2.insert("1.0", "Output is shown below (Executed at <time goes here>)")
        self.side_display.label2.configure(state="disabled")
        self.side_display.colorize_output()

        self.options = options

        tag_names = ["fast-movers", "slow-movers", "stoppers", "setters", "inputs", "returners", "calculators", "numbers", "comment", "keyword", "string", "custom-function", "custom-function-parameter","error", "nest-mod1", "nest-mod2", "nest-mod0"]
        code_label_names = ["Fast movement", "Slow movement", "Stop movement", "Setters", "inputs", "Returners", "Calculators", "Numbers", "Comments", "Keyword arguments", "Strings", "Defined functions", "Defined Function Parameters", "Errors", "Brackets 1", "Brackets 2", "Brackets 3"]
        i = 1

        self.tag_name_to_canvas: dict[str, tuple[tk.Canvas, tuple]] = {}
        for label_text, tag_name in zip(code_label_names, tag_names):
            x = tk.Button(self.top, text=label_text, command=lambda e = tag_name: self.ask_and_set_color(e, "code"))
            x.bind("<Enter>", func=lambda event, tag=tag_name: self.highlight(event, tag, "code"))
            x.bind("<Leave>", func=lambda event, tag=tag_name: self.unhighlight(event, tag, "code"))
            x.grid(row=i, column=0)
            
            c = tk.Canvas(self.top, width=15, height=15)
            a = c.create_rectangle(0,0,15,15, fill=options["Current-theme"]["Code"][tag_name], outline="white")
            self.tag_name_to_canvas[tag_name] = (c, a)
            c.grid(row=i, column=1)

            i += 1
        
        tag_names = ["z-label", "x-label", "label", "warning", "text", "positive-number", "negative-number"]
        output_label_names = ["Z outputs", "X outputs", "Vec/Y outputs", "Warnings", "Text", "Positive numbers", "Negative numbers"]

        i = 1
        for label_text, tag_name in zip(output_label_names, tag_names):
            x = tk.Button(self.top, text=label_text, command=lambda e = tag_name: self.ask_and_set_color(e, "output"))
            x.bind("<Enter>", func=lambda event, tag=tag_name: self.highlight(event, tag, "output"))
            x.bind("<Leave>", func=lambda event, tag=tag_name: self.unhighlight(event, tag, "output"))
            x.grid(row=i, column=4)
            
            c = tk.Canvas(self.top, width=15, height=15)
            a = c.create_rectangle(0,0,15,15, fill=options["Current-theme"]["Output"][tag_name], outline="white")
            self.tag_name_to_canvas[tag_name] = (c, a)
            c.grid(row=i, column=3)

            i += 1

        self.theme_selected = tk.StringVar()
        self.theme_selected.set(self.options["Current-theme"]["Name"])
        theme_options = list(self.options["Themes"].keys())
        a = tk.OptionMenu(self.top, self.theme_selected, *theme_options, command=self.select_theme)
        a.grid(row=14, column=4)
        a.configure(background="gray12", foreground="white", borderwidth=0)
        tk.Button(self.top, text="Apply and Save Theme", command=self.set_theme).grid(row=15, column=4)
        tk.Button(self.top, text="Save Theme", command=self.save_theme).grid(row=16, column=4)
        
        self.top.transient(self.main_frame)
        self.top.grab_set()
        self.top.resizable(False, False)
    
    def ask_and_set_color(self, tag_name, code_or_output: str):
        code_or_output = code_or_output.capitalize()
        self.top.lift()
        self.top.focus_set()
        color = colorchooser.askcolor(title="Pick color")
        if color:
            hex_color = color[1]
            self.options["Current-theme"][code_or_output][tag_name] = hex_color
            self.side_display.options["Current-theme"][code_or_output][tag_name] = hex_color
            if code_or_output == "Code":
                self.side_display.text.configure(state="normal")
                self.side_display.text.tag_configure(tag_name, foreground=hex_color)
                self.side_display.colorize_code()
                self.side_display.text.configure(state="disabled")
                
            elif code_or_output == "Output":
                self.side_display.output.configure(state="normal")
                self.side_display.output.tag_configure(tag_name, foreground=hex_color)
                self.side_display.colorize_output()
                self.side_display.output.configure(state="disabled")

            a = self.tag_name_to_canvas[tag_name][1]
            self.tag_name_to_canvas[tag_name][0].itemconfigure(a, fill=hex_color)

    def highlight(self, event, tag, code_or_output: str):
        if code_or_output == "code":
            index_pairs = self.side_display.text_color_to_indexes[tag]
            indexes = []
            for pair in index_pairs:
                indexes.append(pair[0])
                indexes.append(pair[1])
            self.side_display.text.configure(state="normal")
            self.side_display.text.tag_add("bold", *indexes)
            self.side_display.text.configure(state="disabled")
        elif code_or_output == "output":
            index_pairs = self.side_display.output_color_to_indexes[tag]
            indexes = []
            for pair in index_pairs:
                indexes.append(pair[0])
                indexes.append(pair[1])
            self.side_display.output.configure(state="normal")
            self.side_display.output.tag_add("bold", *indexes)
            self.side_display.output.configure(state="disabled")

    
    def unhighlight(self,event, tag, code_or_output: str):
        if code_or_output == "code":
            index_pairs = self.side_display.text_color_to_indexes[tag]
            self.side_display.text.configure(state="normal")
            for pair in index_pairs:
                self.side_display.text.tag_remove("bold", pair[0], pair[1])
            self.side_display.text.configure(state="disabled")
        elif code_or_output == "output":
            index_pairs = self.side_display.output_color_to_indexes[tag]
            self.side_display.output.configure(state="normal")
            for pair in index_pairs:
                self.side_display.output.tag_remove("bold", pair[0], pair[1])
            self.side_display.output.configure(state="disabled")

    def set_theme(self):
        self.main_frame.change_colors(self.options)
        self.save_theme()
    
    def save_theme(self):
        theme = self.options["Current-theme"]
        if self.theme_selected.get() != "Default":
            theme["Name"] = "Custom"
            print(f"TRUE {self.theme_selected.get()} TRUE")
            self.options["Themes"]["Custom"] = theme
            self.options["Current-theme"] = theme
            self.side_display.options = self.options
        else:
            self.options["Current-theme"] = theme
            self.side_display.options = self.options

        with open(FileHandler.get_path_to_options(), "w") as file:
            json.dump(self.options, file)

    def select_theme(self, var):
        theme_name = var
        t = self.options["Themes"][theme_name]
        self.options["Current-theme"] = t
        self.side_display.options["Current-theme"] = t

        # Update the gui
        for tag_name, color in t["Code"].items():
            self.side_display.text.tag_configure(tag_name, foreground=color)
        for tag_name, color in t["Output"].items():
            self.side_display.output.tag_configure(tag_name, foreground=color)

    
if __name__ == "__main__":
    with open("Mothball Settings/Options.json", "r") as file:
        options = json.load(file)
    r = tk.Tk()
    a = ChangeColorDialog(r, options)
    r.mainloop()
