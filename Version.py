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
                releases = response.json()
                releases = sorted(releases, key=lambda r: r["tag_name"], reverse=True)
                latest_version = releases[0]

                text = latest_version.get('body')
                
            return (latest_version['tag_name'], text)
        except Exception as e:
            return ("Unable to get latest version", "")
        
if __name__ == "__main__":
    root = tk.Tk()
    Version("BETA", root)
    root.mainloop()
