import tkinter as tk
import Page
import requests

class Version(Page.Page):
        
    def __init__(self, version, master=None):
        self.top = tk.Toplevel(master)
        super().__init__(self.top)
        self.version = version
        a = self.check_for_update()
        self.parse_text(f"Mothball version {version}" + "\n" + a)
        self.finalize()

    def check_for_update(self):
        try:
            response = requests.get("https://api.github.com/repos/anon-noob/mothball/releases")
            if response.status_code == 200:
                latest_version = response.json()[0].get("tag_name")
                if latest_version != self.version:
                    return f"Update available: {latest_version}"
                else:
                    return "You are using the latest version."
            else:
                return "Failed to check for updates."
        except Exception as e:
            return f"Error checking for updates: {e}"
        
if __name__ == "__main__":
    root = tk.Tk()
    Version("VERSION HERE", root)
    root.mainloop()
