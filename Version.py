import tkinter as tk
import Page
import requests

class Version(Page.Page):
        
    def __init__(self, version, master=None):
        self.top = tk.Toplevel(master)
        super().__init__(self.top)
        a,b = self.check_updates()
        self.parse_text(f"""You are on Mothball version {version}\nLatest version {a} changelog:\n{b}""")
        self.finalize()

    def check_updates(self):
        try:
            response = requests.get("https://api.github.com/repos/anon-noob/mothball/releases")
            if response.status_code == 200:
                latest_release = response.json()[0]
                latest_version = latest_release.get("tag_name")
                text = latest_release.get('body')
                
            return (latest_version, text)
        except Exception as e:
            return ("Unable to get latest version", "")
        
if __name__ == "__main__":
    root = tk.Tk()
    Version("BETA", root)
    root.mainloop()
